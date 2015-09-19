# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import lxml.builder

import cbg.keys as keys
import cbg.style as style
import cbg.sample


W = cbg.sample.wardrobe.WARDROBE


class Font(unittest.TestCase):
    def setUp(self):
        W.reset()

    @property
    def xml(self):
        return lxml.etree.Element('mock', W.dict_svg_font())

    def test_style_default(self):
        s = 'font-family:Arial;font-size:4.0;'
        self.assertEqual(self.xml.get(keys.STYLE), s)
        self.assertEqual(self.xml.get(keys.TEXT_ANCHOR), 'middle')

    def test_style_stroke_regular(self):
        W.emphasis(stroke=True)
        s = ('font-family:Arial;font-size:4.0;stroke:#000000;'
             'stroke-width:0.08')
        self.assertEqual(self.xml.get(keys.STYLE), s)

    def test_style_stroke_invert(self):
        W.emphasis(stroke=True)
        W.mode_contrast(stroke=True)
        s = ('font-family:Arial;font-size:4.0;stroke:#ffffff;'
             'stroke-width:0.08')
        self.assertEqual(self.xml.get(keys.STYLE), s)

    def test_style_contrast(self):
        W.mode_contrast(fill=True)
        s = 'font-family:Arial;font-size:4.0;fill:#ffffff;'
        self.assertEqual(self.xml.get(keys.STYLE), s)


class Color(unittest.TestCase):
    def setUp(self):
        W.reset()

    @property
    def xml(self):
        return lxml.etree.Element('mock', **W.dict_svg_fill())

    def test_black(self):
        self.assertEqual(self.xml.get(keys.STYLE), '')

    def test_accent(self):
        W.mode_accent(fill=True)
        self.assertEqual(self.xml.get(keys.STYLE), 'fill:#888888;')

    def test_contrast(self):
        W.mode_contrast(fill=True)
        self.assertEqual(self.xml.get(keys.STYLE), 'fill:#ffffff;')


class Duplicator(unittest.TestCase):
    def test_color(self):
        original = W
        self.assertEqual(original.colors[style.MAIN], ('#000000',))
        new = original.but.colors_main(cbg.sample.color.GRAY_50)
        self.assertIsNot(original, new)
        self.assertNotEqual(original.colors, new.colors)
        self.assertEqual(new.colors[style.MAIN], cbg.sample.color.GRAY_50)
