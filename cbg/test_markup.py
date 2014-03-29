# -*- coding: utf-8 -*-

import unittest

from . import elements
from . import markup

class Tokens(unittest.TestCase):
    def setUp(self):
        self.text_nosep = elements.Paragraph(None, 'a_b_d')
        self.text_overlap = elements.Paragraph(None, 'a_bc:_d')
        self.text_noparams = elements.Paragraph(None, 'a_b:_d')
        self.short_noparams = markup.Shorthand('b', 'x')
        self.overlap_noparams = markup.Shorthand('bc', 'x')

    def test_magic(self):
        self.assertEqual(str(self.short_noparams), '_b_')

    def test_nosep_positive(self):
        self.assertTrue(self.short_noparams.apply_to(self.text_nosep))
        self.assertEqual(self.text_nosep.string, 'axd')

    def test_noparams_positive(self):
        self.assertTrue(self.short_noparams.apply_to(self.text_noparams))
        self.assertEqual(self.text_noparams.string, 'axd')

    def test_overlap(self):
        self.assertFalse(self.short_noparams.apply_to(self.text_overlap))
        self.assertFalse(self.overlap_noparams.apply_to(self.text_noparams))
        
