# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.content.tag as tag


tag.TagField.presenter_class = lambda *_: None


class Basics(unittest.TestCase):
    def setUp(self):
        tag.Tag.registry.clear()
        self.t0 = tag.Tag('aa')
        self.t1 = tag.Tag('c c')
        self.t2 = tag.Tag('2')

    def test_unfilled_boolean(self):
        f = tag.TagField()
        self.assertFalse(f)
        self.assertEqual(len(f), 0)

    def test_nothing_in_spec(self):
        f = tag.TagField()
        f.not_in_spec()
        self.assertFalse(f)
        self.assertEqual(len(f), 0)

    def test_from_spec(self):
        f = tag.TagField()

        f.in_spec(('aa', 'c c'))
        self.assertIn(self.t0, f)
        self.assertIn(self.t1, f)
        self.assertNotIn(self.t2, f)
        self.assertTrue(f)
        self.assertEqual(len(f), 2)

        f.in_spec(('2',))
        self.assertIn(self.t0, f)
        self.assertIn(self.t1, f)
        self.assertIn(self.t2, f)
        self.assertEqual(len(f), 3)

    def test_to_string(self):
        f = tag.TagField()

        f.in_spec(('aa'))
        self.assertEqual(str(f), 'Aa')

        f.in_spec(('c c'))
        self.assertEqual(str(f), 'Aa, c c')

        f.in_spec(('2'))
        self.assertEqual(str(f), '2, aa, c c')


class Advanced(unittest.TestCase):
    def setUp(self):
        tag.AdvancedTag.registry.clear()
        self.t1 = tag.AdvancedTag('t1')
        self.t2 = tag.AdvancedTag('t2', subordinate_to=self.t1)
        self.t3 = tag.AdvancedTag('t3', subordinate_to=self.t1)
        self.f = tag.AdvancedTagField()

    def test_no_hierarchical_relationship(self):
        self.assertIsNone(self.t1.subordinate_to)

    def test_hierarchical_relationship(self):
        self.assertIs(self.t1, self.t2.subordinate_to)

    def test_hierarchy_classes(self):
        self.assertEqual(len(self.f.masters), 0)
        self.assertEqual(len(self.f.subordinates), 0)

        self.f.in_spec('t1')
        self.assertEqual(len(self.f.masters), 0)  # Subordinates still absent.
        self.assertEqual(len(self.f.subordinates), 0)

        self.f.in_spec('t2')
        self.assertEqual(len(self.f.masters), 1)
        self.assertEqual(len(self.f.subordinates), 1)

        self.f.in_spec('t3')
        self.assertEqual(len(self.f.masters), 1)
        self.assertEqual(len(self.f.subordinates), 2)

    def test_hierarchy_printing(self):
        self.assertEqual(str(self.f), '')

        self.f.in_spec('t1')
        self.assertEqual(str(self.f), 'T1')

        self.f.in_spec('t3')
        self.assertEqual(str(self.f), 'T1 (t3)')

        self.f.in_spec('t2')
        self.assertEqual(str(self.f), 'T1 (t2, t3)')


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
            tag.AdvancedTagField().in_spec(t2)
