# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.svg.filter as filter_


class Basics(unittest.TestCase):
    def test_gaussian_blur(self):
        f = filter_.GaussianBlur(2)
        ret = f.to_svg_element()
        self.assertEqual(ret.tag, 'filter')
        self.assertEqual(ret.attrib, {'id': 'f_feGaussianBlur2'})
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0].tag, 'feGaussianBlur')
        self.assertEqual(ret[0].attrib, {'id': 'feGaussianBlur2',
                                         'result': 'blur',
                                         'stdDeviation': '2'})
