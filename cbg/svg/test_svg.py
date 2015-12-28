# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.svg as svg


class Basics(unittest.TestCase):
    def test_abstract_superclass(self):
        with self.assertRaises(NotImplementedError):
            svg.SVGElement.new()

    def test_element_within_element(self):

        class A(svg.SVGElement):
            TAG = 'a'

            class B(svg.SVGElement):
                TAG = 'b'

            @classmethod
            def new(cls):
                return super().new(children=(cls.B.new(),))

        a = A.new()
        self.assertIsNotNone(a.find('b'))


class ArgumentFilteringFixture(unittest.TestCase):

    roster = set(('b', 'f-f'))

    def test_filtering_inapplicable(self):
        attr = {'a': 1}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'a': 1})

    def test_filtering_applicable(self):
        attr = {'b': 2}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'c': 'b:2'})

    def test_filtering_trivial_reroute(self):
        attr = {'a': 1, 'b': 2}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'a': 1, 'c': 'b:2'})

    def test_filtering_good(self):
        attr = {'a': 1, 'b': 2, 'c': 'e:4;d:3'}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'a': 1, 'c': 'b:2;d:3;e:4'})

    def test_filtering_bad_string(self):
        attr = {'a': 1, 'b': 2, 'c': 'd::4'}
        with self.assertRaises(ValueError):
            svg.SVGElement._filter_arguments('c', self.roster, attr)

    def test_filtering_empty_string(self):
        attr = {'a': 1, 'b': 2, 'c': ''}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'a': 1, 'c': 'b:2'})

    def test_filtering_separator_bordered_string(self):
        attr = {'a': 1, 'b': 2, 'c': ';d:3;'}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'a': 1, 'c': 'b:2;d:3'})

    def test_filtering_reformat(self):
        attr = {'f_f': 2}
        svg.SVGElement._filter_arguments('c', self.roster, attr)
        self.assertEqual(attr, {'c': 'f-f:2'})


class ArgumentFilteringSVG(unittest.TestCase):

    class E(svg.SVGElement):
        TAG = 'glurd'

    def test_filtering_hyphenated(self):
        xml = self.E.new(stroke_width=2)
        self.assertEqual(xml.attrib, {'style': 'stroke-width:2'})

    def test_filtering_override(self):
        xml = self.E.new(style='stroke-width:3', stroke_width=4)
        self.assertEqual(xml.attrib, {'style': 'stroke-width:4'})
