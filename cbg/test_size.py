# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''


import unittest

import numpy

import cbg


class Area(unittest.TestCase):
    def test_making_point(self):
        p = cbg.size.Area.Point((2, 3))
        self.assertEqual(p.all(), numpy.array((2, 3)).all())
        self.assertEqual(p.dtype, float)

    def test_making_edgepoint(self):
        p = cbg.size.Area.EdgePoint((2, 3), (1, -1))
        self.assertEqual(p.all(), numpy.array((2, 3)).all())
        self.assertEqual(p.dtype, float)

        d = p.displaced(1)
        self.assertEqual(d.all(), numpy.array((3, 2)).all())
