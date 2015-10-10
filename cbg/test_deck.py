# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest
import unittest.mock

import cbg.card as card
import cbg.deck as deck
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


class TitleField(cbg.elements.CardContentField):
    key = keys.TITLE
    presenter_class = cbg.svg.presenter.SVGField


class CardSubclass(card.HumanReadablePlayingCard):
    field_classes = (TitleField,)


class Card(unittest.TestCase):
    def test_empty(self):
        card.HumanReadablePlayingCard()

    def test_data_empty(self):
        with self.assertRaises(CardSubclass.SpecificationError):
            card.HumanReadablePlayingCard(**{keys.DATA: {}})

    def test_creation(self):
        o = unittest.mock.patch.object
        with o(card.HumanReadablePlayingCard, '_process') as m:
            card.HumanReadablePlayingCard(**DUMMY)
            m.assert_called_once_with(**DUMMY)

    def test_sorting(self):
        c = CardSubclass(**{keys.TITLE: 't1'})
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
