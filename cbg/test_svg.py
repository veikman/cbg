# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import numpy

from . import svg


class Rounding(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(svg.rounded(1), '1')

    def test_tuple(self):
        self.assertEqual(svg.rounded((1, 2)), ['1', '2'])

    def test_float_preserved(self):
        self.assertEqual(svg.rounded(1.2), '1.2')

    def test_float_trimmed(self):
        self.assertEqual(svg.rounded(1.23456789), '1.2346')

    def test_numpy(self):
        self.assertEqual(svg.rounded(numpy.array((4, 7, 8))), ['4', '7', '8'])
