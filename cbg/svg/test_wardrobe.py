# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import logging

import cbg.keys as keys
import cbg.svg.wardrobe as wr


def suppress(logging_level):
    '''Temporarily silence logging up to the named level.

    This function returns a function-altering function.

    '''
    def decorator(method):
        def replacement(instance, *args, **kwargs):
            logging.disable(logging_level)
            method(instance, *args, **kwargs)
            logging.disable(logging.NOTSET)
        return replacement
    return decorator


class Basics(unittest.TestCase):
    def test_default_wardrobe_is_a_noop(self):
        self.assertEqual(wr.Wardrobe().to_svg_attributes(), {})

    def test_mode_single_argument_indirect(self):
        m = wr.Mode(italic=True)
        self.assertEqual(m.style, 'italic')

    def test_mode_single_argument_direct(self):
        m = wr.Mode(style='oblique')
        self.assertEqual(m.style, 'oblique')

    def test_mode_redundant_arguments_favour_the_direct(self):
        m = wr.Mode(style='oblique', italic=True)
        self.assertEqual(m.style, 'oblique')


class Font(unittest.TestCase):
    def test_style_default(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(font=wr.Font('Wax'))}
            font_size = 4

        ref = {keys.STYLE: 'font-family:Wax;font-size:4.0'}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_style_stroke_default_color_is_included(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(font=wr.Font('Wax'),
                                      thickness=0.02)}
            font_size = 3

        ref = {keys.STYLE: ('font-family:Wax;font-size:3.0;stroke:#000000;'
                            'stroke-width:0.06')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_style_stroke_specified_color(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(font=wr.Font('Wax'),
                                      stroke_colors=('#ffffff',),
                                      thickness=0.03)}
            font_size = 3

        ref = {keys.STYLE: ('font-family:Wax;font-size:3.0;stroke:#ffffff;'
                            'stroke-width:0.09')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)


class Color(unittest.TestCase):
    def test_fill_black(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(fill_colors=('#000000',))}

        ref = {}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_fill_nonblack(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(fill_colors=('#ba11ad',))}

        ref = {keys.STYLE: ('fill:#ba11ad')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_multiple_colors_currently_ignored(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(fill_colors=('#ba11ad', '#f1eece'))}

        ref = {keys.STYLE: ('fill:#ba11ad')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_fill_and_stroke(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(fill_colors=('#facade',),
                                      stroke_colors=('#f1eece',))}

        ref = {keys.STYLE: ('fill:#facade;stroke:#f1eece;stroke-width:1')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)

    def test_stroke(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(stroke_colors=('#f1eece',))}

        ref = {keys.STYLE: ('stroke:#f1eece;stroke-width:1')}
        self.assertEqual(Wardrobe().to_svg_attributes(), ref)


class MultiModal(unittest.TestCase):

    @suppress(logging.ERROR)
    def test_not_found(self):
        with self.assertRaises(KeyError):
            wr.Wardrobe().set_mode(wr.CONTRAST)

    def test_switch(self):
        class Wardrobe(wr.Wardrobe):
            modes = {wr.MAIN: wr.Mode(fill_colors=('#ba11ad',)),
                     'pig': wr.Mode(fill_colors=('#facade',))}
            modes['label'] = modes['pig'].copy(font=wr.Font('Googe Light'))
            font_size = 2

        w = Wardrobe()
        ref = {keys.STYLE: ('fill:#ba11ad')}
        self.assertEqual(w.to_svg_attributes(), ref)

        w.set_mode('pig')
        ref = {keys.STYLE: ('fill:#facade')}
        self.assertEqual(w.to_svg_attributes(), ref)

        w.set_mode('label')
        ref = {keys.STYLE:
               'fill:#facade;font-family:Googe Light;font-size:2.0'}
        self.assertEqual(w.to_svg_attributes(), ref)

        w.reset()
        ref = {keys.STYLE: ('fill:#ba11ad')}
        self.assertEqual(w.to_svg_attributes(), ref)


class Duplication(unittest.TestCase):
    def test_single(self):
        m0 = wr.Mode(bolder=True)
        self.assertEqual(m0.weight, 'bolder')
        self.assertEqual(m0.style, None)
        m1 = m0.copy(weight='bold', italic=True)
        self.assertEqual(m0.weight, 'bolder')
        self.assertEqual(m0.style, None)
        self.assertEqual(m1.weight, 'bold')
        self.assertEqual(m1.style, 'italic')
        m2 = m0.copy(weight=None, oblique=True)
        self.assertEqual(m0.weight, 'bolder')
        self.assertEqual(m0.style, None)
        self.assertEqual(m1.weight, 'bold')
        self.assertEqual(m1.style, 'italic')
        self.assertEqual(m2.weight, None)
        self.assertEqual(m2.style, 'oblique')

    def test_multiple(self):
        class Wardrobe0(wr.Wardrobe):
            modes = {'a': wr.Mode(font=wr.Font('Vot'), bold=True),
                     'b': wr.Mode(font=wr.Font('Geb'))}
            font_size = 9

            def reset(self):
                self.mode = self.modes['a']

        w = Wardrobe0()
        ref = {keys.STYLE: 'font-family:Vot;font-size:9.0;font-weight:bold'}
        self.assertEqual(w.to_svg_attributes(), ref)

        w.set_mode('b')
        ref = {keys.STYLE: 'font-family:Geb;font-size:9.0'}
        self.assertEqual(w.to_svg_attributes(), ref)

        class Wardrobe1(Wardrobe0):
            modes = Wardrobe0.copy_modes(weight='lighter')

        w = Wardrobe1()
        ref = {keys.STYLE: 'font-family:Vot;font-size:9.0;font-weight:lighter'}
        self.assertEqual(w.to_svg_attributes(), ref)

        w.set_mode('b')
        ref = {keys.STYLE: 'font-family:Geb;font-size:9.0;font-weight:lighter'}
        self.assertEqual(w.to_svg_attributes(), ref)
