# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''


import unittest

import numpy

import cbg


class Area(unittest.TestCase):
    def compare(self, point, ref):
        self.assertEqual(tuple(point), ref)

    def test_making_point(self):
        p = cbg.size.Area.Point((2, 3))
        self.compare(p, (2, 3))
        self.assertEqual(p.dtype, float)

    def test_edgepoint(self):
        p = cbg.size.Area.EdgePoint((2, 3), (1, -1))
        self.compare(p, (2, 3))
        self.assertEqual(p.dtype, float)

        self.assertEqual(str(p), '[ 2.  3.]')
        self.assertEqual(repr(p), 'EdgePoint([ 2.,  3.])')

        d = p.displaced(1)
        self.compare(d, (3, 4))

        d = p.displaced((0, 1))
        self.compare(d, (2, 2))

        d = p.displaced((10, 10))
        self.compare(d, (12, -7))

    def test_corners(self):
        a = cbg.size.Area((4, 3))
        self.compare(a.footprint, (4, 3))

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
