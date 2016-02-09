# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import logging

import lxml.etree

import cbg.test_misc
import cbg.svg.card as card
import cbg.svg.image as image
import cbg.sample.wardrobe


class DefsElement(unittest.TestCase):

    class Presenter(card.CardPresenter):
        Wardrobe = cbg.sample.wardrobe.MiniEuroMain

        def recurse(self):
            pass

    def setUp(self):
        self.image = image.Image.new()
        self.presenter = self.Presenter.new(unittest.mock.MagicMock(),
                                            origin=(0, 0),
                                            parent=self.image)

    def test_default_empty(self):
        self.assertEqual(len(self.image.defs), 0)

    def test_addition(self):
        self.assertEqual(len(self.image.defs), 0)
        self.presenter.define(lxml.etree.Element('e', id='1'))
        self.assertEqual(len(self.image.defs), 1)
        self.presenter.define(lxml.etree.Element('f', id='3'))
        self.assertEqual(len(self.image.defs), 2)

    def test_no_addition_same_object(self):
        e = lxml.etree.Element('e', id='5')
        self.presenter.define(e)
        self.assertEqual(len(self.image.defs), 1)
        self.presenter.define(e)
        self.assertEqual(len(self.image.defs), 1)

    def test_no_addition_recreated(self):
        self.presenter.define(lxml.etree.Element('e', id='7'))
        self.assertEqual(len(self.image.defs), 1)
        self.presenter.define(lxml.etree.Element('e', id='7'))
        self.assertEqual(len(self.image.defs), 1)

    @cbg.test_misc.suppress(logging.ERROR)
    def test_conflict(self):
        self.presenter.define(lxml.etree.Element('e', id='5'))
        self.assertEqual(len(self.image.defs), 1)
        with self.assertRaises(ValueError):
            self.presenter.define(lxml.etree.Element('f', id='5'))
