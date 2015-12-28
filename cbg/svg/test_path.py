# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.path as path


class Basics(unittest.TestCase):
    def test_triangle(self):
        pf = path.Path.Pathfinder()
        pf.moveto(0, 0)
        pf.lineto(100, 0)
        pf.lineto(50, 100)
        pf.closepath()
        s = 'M 0 0 L 100 0 L 50 100 z'
        self.assertEqual(' '.join(map(str, pf)), s)

        p = path.Path.new(pf)
        self.assertEqual(p.attrib, {'d': s})
