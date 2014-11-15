# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import numpy

from . import svg


class Millimetre(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(svg.mm(1), '1mm')

    def test_double(self):
        self.assertEqual(svg.mm((1, 2)), ['1mm', '2mm'])

    def test_float_trim_negative(self):
        self.assertEqual(svg.mm(1.2), '1.2mm')

    def test_float_trim_positive(self):
        self.assertEqual(svg.mm(1.23456789), '1.2345mm')

    def test_numpy(self):
        self.assertEqual(svg.mm(numpy.array((4, 7, 8))),
                         ['4mm', '7mm', '8mm'])
