# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg


class _Map(cbg.content.grid.Map):
    class Empty(cbg.content.grid.Map.Empty):
        key = 'empty'


class _DefaultEmpty(cbg.content.grid.DefaultEmptyMap):
    class Empty(cbg.content.grid.Map.Empty):
        key = 'empty'


class _AOE(cbg.content.grid.AreaOfEffect):
    class Affected(cbg.content.grid.AreaOfEffect.Affected):
        key = 'affected'


class Basics(unittest.TestCase):
    def test_not_in_spec(self):
        m = _Map()
        self.assertEqual(m.shape, ())
        self.assertFalse(m)

    def test_1x1(self):
        m = _Map({'snärf': [(0, 0)]})
        self.assertEqual(m.shape, (1, 1))
        self.assertTrue(m)
        self.assertEqual(str(m), '(1, 1) map: [[None]]')

    def test_2x2(self):
        m = _Map({'empty': [(0, 0), (0, 1), (1, 0), (1, 1)]})
        self.assertEqual(m.shape, (2, 2))
        self.assertTrue(m)
        self.assertEqual(str(m), '(2, 2) map: [[None None]\n [None None]]')

    def test_default_empty_triangle(self):
        m = _DefaultEmpty({'empty': [(0, 0), (0, 1), (1, 0)]})
        self.assertEqual(m.shape, (2, 2))
        self.assertTrue(m)
        self.assertEqual(str(m), '(2, 2) map: [[. .]\n [. .]]')

    def test_nominal_aoe(self):
        m = _AOE({'affected': [(0, 0)]})
        self.assertEqual(m.shape, (3, 3))
        self.assertTrue(m)
        self.assertEqual(str(m), '(3, 3) map: [[. . .]\n [. A .]\n [. . .]]')

    def test_1x2_aoe(self):
        m = _AOE({'affected': [(0, 0), (1, 0)]})
        self.assertEqual(m.shape, (3, 4))
        self.assertTrue(m)
        s = ('(3, 4) map: ['
             '[. . . .]\n '
             '[. A A .]\n '
             '[. . . .]]')
        self.assertEqual(str(m), s)

    def test_complex_aoe(self):
        m = _AOE({'affected': [(1, 0), (2, 0), (2, 2)]})
        self.assertEqual(m.shape, (5, 4))
        self.assertTrue(m)
        s = ('(5, 4) map: ['
             '[. . . .]\n '
             '[. A A .]\n '
             '[. . . .]\n '
             '[. . A .]\n '
             '[. . . .]]')
        self.assertEqual(str(m), s)
