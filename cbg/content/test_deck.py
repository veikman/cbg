# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import logging
import unittest
import unittest.mock

import cbg.test_misc
import cbg.content.card as card
import cbg.content.deck as deck
import cbg.keys as keys
import cbg


FIRST = 'First'
SECOND = 'Second'
THIRD = 'Third'

SPEC = {keys.METADATA: {keys.DEFAULTS: {keys.COPIES: 2}},
        FIRST: {keys.DATA: {}, keys.METADATA: {keys.COPIES: 3}},
        SECOND: {keys.DATA: {}, keys.METADATA: {keys.COPIES: 1}},
        THIRD: {keys.DATA: {}, keys.METADATA: {}}
        }

DUMMY = {keys.DATA: {keys.TITLE: 't0'}}


class TitleField(cbg.content.text.TextField):
    key = keys.TITLE
    presenter_class_front = cbg.svg.presenter.TextPresenter


class CardSubclass(card.Card):
    plan = (TitleField,)


class Card(unittest.TestCase):
    @cbg.test_misc.suppress(logging.ERROR)
    def test_no_spec(self):
        with self.assertRaises(CardSubclass.SpecificationError):
            card.Card()

    @cbg.test_misc.suppress(logging.ERROR)
    def test_empty_spec(self):
        with self.assertRaises(CardSubclass.SpecificationError):
            card.Card({keys.DATA: {}})

    def test_creation(self):
        o = unittest.mock.patch.object
        with o(card.Card, 'layout') as m:
            card.Card(DUMMY)
            m.assert_called_once_with()

    def test_sorting(self):
        c = CardSubclass({keys.TITLE: 't1'})
        self.assertEqual(c.sorting_keys, 't1')


class Deck(unittest.TestCase):
    def setUp(self):
        self.deck = deck.Deck(CardSubclass, SPEC)

    def test_sorting_singles(self):
        sorted_ = [c.title for c in self.deck.singles_sorted()]
        self.assertListEqual(sorted_, [FIRST, SECOND, THIRD])

    def test_sorting_copies(self):
        sorted_ = [c.title for c in self.deck.all_sorted()]
        self.assertListEqual(sorted_, [FIRST, FIRST, FIRST,
                                       SECOND, THIRD, THIRD])
