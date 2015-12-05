# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.filter as filter_


class Basics(unittest.TestCase):
    def test_gaussian_blur(self):
        ret = filter_.GaussianBlur.new(2)
        self.assertEqual(ret.tag, 'filter')
        self.assertEqual(ret.attrib, {'id': 'f_feGB_2'})
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0].tag, 'feGaussianBlur')
        self.assertEqual(ret[0].attrib, {'result': 'blur',
                                         'stdDeviation': '2'})
