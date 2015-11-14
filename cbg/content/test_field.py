# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import unittest.mock

import cbg.content.field as field


class Basics(unittest.TestCase):
    def test_text_field_instantiation(self):
        f = field.TextField()
        f.in_spec(('a', 'b'))
        self.assertEqual(len(f), 2)
        self.assertEqual(str(f[0]), 'a')
        self.assertEqual(str(f[1]), 'b')

    def test_paragraph_instantiation_bare(self):
        p = field.Paragraph()
        self.assertEqual(str(p), '')

    def test_paragraph_instantiation_zero(self):
        p = field.Paragraph(0)
        self.assertEqual(str(p), '0')

    def test_paragraph_fill(self):
        p = field.Paragraph()
        p.in_spec('a')
        self.assertEqual(str(p), 'a')
