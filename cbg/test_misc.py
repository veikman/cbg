# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import numpy

import cbg.misc as misc


class Rounding(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(misc.rounded(1), '1')

    def test_tuple(self):
        self.assertEqual(misc.rounded((1, 2)), ['1', '2'])

    def test_float_preserved(self):
        self.assertEqual(misc.rounded(1.2), '1.2')

    def test_float_trimmed(self):
        self.assertEqual(misc.rounded(1.23456789), '1.2346')

    def test_numpy(self):
        self.assertEqual(misc.rounded(numpy.array((4, 7, 8))), ['4', '7', '8'])
