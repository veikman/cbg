# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg


class Basics(unittest.TestCase):
    def test_basics(self):
        m = cbg.content.grid.Map()
        self.assertFalse(m)
        self.assertEqual(str(m), '(0,) map: []')

        m.in_spec((2, 2))
        self.assertTrue(m)
        self.assertEqual(str(m), '(2, 2) map: [[None None]\n [None None]]')

    def test_default_empty(self):
        m = cbg.content.grid.DefaultEmptyMap()
        m.in_spec((2, 2))
        self.assertTrue(m)
        self.assertEqual(str(m), '(2, 2) map: [[. .]\n [. .]]')

    def test_nominal_aoe(self):
        m = cbg.content.grid.AreaOfEffect()
        m.in_spec([(0, 0)])
        self.assertTrue(m)
        self.assertEqual(str(m), '(3, 3) map: [[. . .]\n [. A .]\n [. . .]]')

    def test_complex_aoe(self):
        m = cbg.content.grid.AreaOfEffect()
        m.in_spec([(1, 0), (2, 0), (2, 2)])
        self.assertTrue(m)
        s = ('(5, 4) map: ['
             '[. . . .]\n '
             '[. A A .]\n '
             '[. . . .]\n '
             '[. . A .]\n '
             '[. . . .]]')
        self.assertEqual(str(m), s)
