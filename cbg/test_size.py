# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''


import unittest

import numpy

import cbg


class ArrayConstructor(unittest.TestCase):
    @classmethod
    def totuple(cls, a):
        try:
            return tuple(cls.totuple(i) for i in a)
        except TypeError:
            return a

    def compare(self, ref):
        a = cbg.size.Array(ref)
        self.assertTupleEqual(self.totuple(a), ref)
        return a

    def test_1x1_int(self):
        a = self.compare((1,))
        self.assertEqual(a.dtype, numpy.dtype('int'))

    def test_1x2_int(self):
        a = self.compare((2, 3))
        self.assertEqual(a.dtype, numpy.dtype('int'))

    def test_1x2_float(self):
        a = self.compare((1.5, 2.5))
        self.assertEqual(a.dtype, numpy.dtype('float'))

    def test_2x2_int(self):
        a = self.compare(((1, 2), (3, 4)))
        self.assertEqual(a.dtype, numpy.dtype('int'))

    def test_2x2_none(self):
        a = self.compare(((None, None), (None, None)))
        self.assertEqual(a.dtype, numpy.dtype('object'))


class Rectangle(unittest.TestCase):
    def compare(self, point, ref):
        self.assertEqual(tuple(point), ref)

    def test_edgepoint(self):
        p = cbg.size.Rectangle.EdgePoint((2, 3), (1, -1))
        self.compare(p, (2, 3))
        self.assertEqual(p.dtype, numpy.int64)

        self.assertEqual(str(p), '[2 3]')
        self.assertEqual(repr(p), 'EdgePoint([2, 3])')

        d = p.displaced(1)
        self.compare(d, (3, 4))

        d = p.displaced((0, 1))
        self.compare(d, (2, 2))

        d = p.displaced((10, 10))
        self.compare(d, (12, -7))

    def test_corners(self):
        a = cbg.size.Rectangle((4, 3))
        self.compare(a, (4, 3))

        ps = a.corners()
        self.assertEqual(len(ps), 4)
        for p, ref in zip(ps, ((0, 0), (4, 0), (4, 3), (0, 3),)):
            self.compare(p, ref)

        ps = tuple(a.corner_offsets((1, 0)))
        self.assertEqual(len(ps), 4)
        for p, ref in zip(ps, (((0, 1), (1, 0),),
                               ((3, 0), (4, 1),),
                               ((4, 2), (3, 3),),
                               ((1, 3), (0, 2),),)):
            for p, ref in zip(p, ref):
                self.compare(p, ref)
