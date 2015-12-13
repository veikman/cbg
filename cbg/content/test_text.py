# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import unittest.mock

import cbg.content.text as text


class Basics(unittest.TestCase):

    def test_paragraph_instantiation_bare(self):
        p = text.Paragraph('')
        self.assertEqual(str(p), '')

    def test_paragraph_instantation_string(self):
        p = text.Paragraph('a')
        self.assertEqual(str(p), 'a')

    def test_paragraph_instantiation_zero(self):
        p = text.Paragraph(0)
        self.assertEqual(str(p), '0')

    def test_text_field_instantiation(self):
        f = text.TextField(('a', 'b'))
        self.assertEqual(len(f), 2)
        self.assertEqual(str(f), 'a\n  b')
        self.assertEqual(str(f[0]), 'a')
        self.assertEqual(str(f[1]), 'b')
