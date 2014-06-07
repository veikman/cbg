# -*- coding: utf-8 -*-

import unittest

from . import tag
from . import exc


class Basics(unittest.TestCase):
    def setUp(self):
        self.string = 'placeholder'
        self.pretty = 'Placeholder'
        self.tag = tag.Tag(self.string)

    def test_magic(self):
        self.assertEqual(self.string, str(self.tag))

    def test_pretty(self):
        self.assertEqual(self.pretty, str(self.tag).capitalize())


class Sets(unittest.TestCase):
    def setUp(self):
        self.t1 = tag.Tag('t1')
        self.t2 = tag.Tag('t2', subordinate_to=self.t1)
        self.t3 = tag.Tag('t3', subordinate_to=self.t1)
        self.list_ = tag.SetOfTags(None, (self.t2, self.t1))

    def test_relationship_simple(self):
        self.assertIsNone(self.t1.subordinate_to)
        self.assertIs(self.t1, self.t2.subordinate_to)

    def test_list_length(self):
        self.assertEqual(len(self.list_), 2)
        self.list_.add(self.t3)
        self.assertEqual(len(self.list_), 3)

    def test_hierarchy_classes(self):
        self.assertEqual(len(self.list_.masters), 1)
        self.assertEqual(len(self.list_.subordinates), 1)
        self.list_.add(self.t3)
        self.assertEqual(len(self.list_.masters), 1)
        self.assertEqual(len(self.list_.subordinates), 2)

    def test_hierarchy_printing(self):
        self.assertEqual(str(self.list_), 'T1 (t2)')
        self.list_.add(self.t3)
        self.assertEqual(str(self.list_), 'T1 (t2, t3)')


class Safeguards(unittest.TestCase):
    def setUp(self):
        self.t1 = tag.Tag('a', syntactic=True)

    def test_disparate_hierarchy(self):
        with self.assertRaises(exc.SpecificationError):
            tag.Tag('b', subordinate_to=self.t1)

    def test_open_hierarchy(self):
        t2 = tag.Tag('b', syntactic=True, subordinate_to=self.t1)
        with self.assertRaises(exc.SpecificationError):
            tag.SetOfTags(None, (t2,))
