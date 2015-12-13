# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.content.tag as tag


class RegisteredTag(unittest.TestCase):
    def setUp(self):
        tag.RegisteredTag.registry.clear()
        self.t0 = tag.RegisteredTag('aa')
        self.t1 = tag.RegisteredTag('c c')
        self.t2 = tag.RegisteredTag('2')

    def test_nothing_in_spec(self):
        f = tag.RegisteredTagField([])
        self.assertFalse(f)
        self.assertEqual(len(f), 0)
        self.assertEqual(str(f), '')

    def test_from_spec(self):
        f = tag.RegisteredTagField(('aa', 'c c'))
        self.assertIn(self.t0, f)
        self.assertIn(self.t1, f)
        self.assertNotIn(self.t2, f)
        self.assertTrue(f)
        self.assertEqual(len(f), 2)
        self.assertEqual(str(f), 'Aa, c c')

    def test_addition(self):
        f = tag.RegisteredTagField(('aa', 'c c'))
        f.append(self.t2)
        self.assertIn(self.t0, f)
        self.assertIn(self.t1, f)
        self.assertIn(self.t2, f)
        self.assertEqual(len(f), 3)
        self.assertEqual(str(f), '2, aa, c c')


class AdvancedTag(unittest.TestCase):
    def setUp(self):
        tag.AdvancedTag.registry.clear()
        self.t1 = tag.AdvancedTag('t1')
        self.t2 = tag.AdvancedTag('t2', subordinate_to=self.t1)
        self.t3 = tag.AdvancedTag('t3', subordinate_to=self.t1)

    def test_no_hierarchical_relationship(self):
        self.assertIsNone(self.t1.subordinate_to)

    def test_hierarchical_relationship(self):
        self.assertIs(self.t1, self.t2.subordinate_to)

    def test_hierarchy_classes_len0(self):
        f = tag.AdvancedTagField(())
        self.assertEqual(len(f.masters), 0)
        self.assertEqual(len(f.subordinates), 0)
        self.assertEqual(str(f), '')

    def test_hierarchy_classes_len1(self):
        f = tag.AdvancedTagField(('t1',))
        self.assertEqual(len(f.masters), 0)  # Subordinates still absent.
        self.assertEqual(len(f.subordinates), 0)
        self.assertEqual(str(f), 'T1')

    def test_hierarchy_classes_len2(self):
        f = tag.AdvancedTagField(('t1', 't3'))
        self.assertEqual(len(f.masters), 1)
        self.assertEqual(len(f.subordinates), 1)
        self.assertEqual(str(f), 'T1 (t3)')

    def test_hierarchy_classes_len3(self):
        f = tag.AdvancedTagField(('t1', 't2', 't3'))
        self.assertEqual(len(f.masters), 1)
        self.assertEqual(len(f.subordinates), 2)
        self.assertEqual(str(f), 'T1 (t2, t3)')


class Safeguards(unittest.TestCase):
    def setUp(self):
        tag.AdvancedTag.registry.clear()
        self.t1 = tag.AdvancedTag('a', syntactic=True)

    def test_collision(self):
        with self.assertRaises(tag.AdvancedTag.TaggingError):
            tag.AdvancedTag('a')

    def test_disparate_hierarchy(self):
        with self.assertRaises(tag.AdvancedTag.TaggingError):
            tag.AdvancedTag('b', subordinate_to=self.t1)

    def test_open_hierarchy(self):
        t2 = tag.AdvancedTag('b', syntactic=True, subordinate_to=self.t1)
        self.assertIs(t2.subordinate_to, self.t1)

        with self.assertRaises(tag.AdvancedTag.TaggingError):
            tag.AdvancedTagField(('b'),)
