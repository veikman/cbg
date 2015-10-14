# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.path as path


class Basics(unittest.TestCase):
    def test_triangle(self):
        pf = path.Pathfinder()
        pf.moveto(0, 0)
        pf.lineto(100, 0)
        pf.lineto(50, 100)
        pf.closepath()
        self.assertEqual(pf.attrdict(),
                         {'d': 'M 0 0 L 100 0 L 50 100 z'})
