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


class Compass(unittest.TestCase):
    def test_0(self):
        with self.assertRaises(ValueError):
            misc.Compass()

    def test_1(self):
        c = misc.Compass(1)
        self.assertEqual(c.top, 1)
        self.assertEqual(c.right, 1)
        self.assertEqual(c.bottom, 1)
        self.assertEqual(c.left, 1)

    def test_2(self):
        c = misc.Compass(1, 2)
        self.assertEqual(c.top, 1)
        self.assertEqual(c.right, 2)
        self.assertEqual(c.bottom, 1)
        self.assertEqual(c.left, 2)

    def test_3(self):
        c = misc.Compass(1, 2, 3)
        self.assertEqual(c.top, 1)
        self.assertEqual(c.right, 2)
        self.assertEqual(c.bottom, 3)
        self.assertEqual(c.left, 2)

    def test_4(self):
        c = misc.Compass(1, 2, 3, 4)
        self.assertEqual(c.top, 1)
        self.assertEqual(c.right, 2)
        self.assertEqual(c.bottom, 3)
        self.assertEqual(c.left, 4)

    def test_5(self):
        with self.assertRaises(ValueError):
            misc.Compass(0, 1, 2, 3, 4)
