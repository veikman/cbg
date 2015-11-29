# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import lxml.etree

import cbg.svg.page as page
import cbg.svg.presenter as presenter


class DefsField(unittest.TestCase):
    def setUp(self):
        self.page = page.Page()
        self.presenter = presenter.CardBase(None, origin=(0, 0),
                                            defs=self.page.defs)

    def test_default_empty(self):
        self.assertEqual(len(self.page.defs), 0)

    def test_addition(self):
        self.assertEqual(len(self.page.defs), 0)
        self.presenter.define(lxml.etree.Element('e', id='1'))
        self.assertEqual(len(self.page.defs), 1)
        self.presenter.define(lxml.etree.Element('f', id='3'))
        self.assertEqual(len(self.page.defs), 2)

    def test_no_addition_same_object(self):
        e = lxml.etree.Element('e', id='5')
        self.presenter.define(e)
        self.assertEqual(len(self.page.defs), 1)
        self.presenter.define(e)
        self.assertEqual(len(self.page.defs), 1)

    def test_no_addition_recreated(self):
        self.presenter.define(lxml.etree.Element('e', id='7'))
        self.assertEqual(len(self.page.defs), 1)
        self.presenter.define(lxml.etree.Element('e', id='7'))
        self.assertEqual(len(self.page.defs), 1)

    def test_conflict(self):
        self.presenter.define(lxml.etree.Element('e', id='5'))
        self.assertEqual(len(self.page.defs), 1)
        with self.assertRaises(ValueError):
            self.presenter.define(lxml.etree.Element('f', id='5'))
