# -*- coding: utf-8 -*-

import unittest

import lxml.builder

from . import style
from . import wardrobe

class Font(unittest.TestCase):
    def setUp(self):
        wardrobe.WARDROBE.reset()

    @property
    def xml(self):
        return lxml.etree.Element('mock', wardrobe.WARDROBE.dict_svg_font())

    def test_style_default(self):
        s = 'font-family:Arial;font-size:4.0mm;'
        self.assertEqual(self.xml.get(style.STYLE), s)
        self.assertEqual(self.xml.get(style.TEXT_ANCHOR), 'middle')

    def test_style_stroke_regular(self):
        wardrobe.WARDROBE.emphasis(stroke=True)
        s = 'font-family:Arial;font-size:4.0mm;stroke:#000000;stroke-width:0.08mm'
        self.assertEqual(self.xml.get(style.STYLE), s)

    def test_style_stroke_invert(self):
        wardrobe.WARDROBE.emphasis(stroke=True)
        wardrobe.WARDROBE.mode_contrast(stroke=True)
        s = 'font-family:Arial;font-size:4.0mm;stroke:#ffffff;stroke-width:0.08mm'
        self.assertEqual(self.xml.get(style.STYLE), s)

    def test_style_contrast(self):
        wardrobe.WARDROBE.mode_contrast(fill=True)
        s = 'font-family:Arial;font-size:4.0mm;fill:#ffffff;'
        self.assertEqual(self.xml.get(style.STYLE), s)

class Color(unittest.TestCase):
    def setUp(self):
        wardrobe.WARDROBE.reset()

    @property
    def xml(self):
        return lxml.etree.Element('mock', **wardrobe.WARDROBE.dict_svg_fill())

    def test_black(self):
        self.assertEqual(self.xml.get(style.STYLE), '')

    def test_accent(self):
        wardrobe.WARDROBE.mode_accent(fill=True)
        self.assertEqual(self.xml.get(style.STYLE), 'fill:#888888;')

    def test_contrast(self):
        wardrobe.WARDROBE.mode_contrast(fill=True)
        self.assertEqual(self.xml.get(style.STYLE), 'fill:#ffffff;')

class Duplicator(unittest.TestCase):
    def test_color(self):
        original = wardrobe.WARDROBE
        self.assertEqual(original.colors[style.MAIN], wardrobe.BLACK)
        new = original.but.colors_main(wardrobe.GRAY_50)
        self.assertIsNot(original, new)
        self.assertNotEqual(original.colors, new.colors)
        self.assertEqual(new.colors[style.MAIN], wardrobe.GRAY_50)
