# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.svg as svg


class Basics(unittest.TestCase):
    def test_abstract_superclass(self):
        with self.assertRaises(NotImplementedError):
            svg.SVGElement.new()
