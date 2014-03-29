# -*- coding: utf-8 -*-

import unittest
import unittest.mock

from . import card
from . import deck

FIRST = 'First'
SECOND = 'Second'
THIRD = 'Third'

SPEC = { deck.METADATA: {}
       , FIRST: {card.DATA: None, deck.COPIES: 3}
       , SECOND: {card.DATA: None, deck.COPIES: 1}
       , THIRD: {card.DATA: None, deck.COPIES: 2}
       }

class CardSubclass(card.HumanReadablePlayingCard):
    def process(self):
        self.dresser = True

    @property
    def sorting_keys(self):
        return self.title


class Card(unittest.TestCase):
    def test_safeguards(self):
        with self.assertRaises(NotImplementedError):
            card.HumanReadablePlayingCard('t', {card.DATA: None})

    def test_creation(self):
        o = unittest.mock.patch.object
        with o(card.HumanReadablePlayingCard, 'process') as m:
            card.HumanReadablePlayingCard('t', {card.DATA: None})
            m.assert_called_once_with()

    def test_sorting(self):
        c = CardSubclass('t', {card.DATA: None})
        self.assertEqual(c.sorting_keys, 't')

    def test_attribute_preservation(self):
        c = CardSubclass('t', {card.DATA: None})
        self.assertIsNotNone(c.dresser)

class Deck(unittest.TestCase):
    def setUp(self):
        o = unittest.mock.patch.object
        with o(deck.Deck, 'read_raw', return_value=SPEC) as m:
            self.deck = deck.Deck('deck', 'path', CardSubclass)
            m.assert_called_once_with()

    def test_sorting_singles(self):
        sorted_ = [c.title for c in self.deck.singles_sorted]
        self.assertListEqual(sorted_, [FIRST, SECOND, THIRD])

    def test_sorting_copies(self):
        sorted_ = [c.title for c in self.deck.all_sorted]
        self.assertListEqual(sorted_, [FIRST, FIRST, FIRST,
                                       SECOND, THIRD, THIRD])

    def test_attribute_preservation(self):
        for type_ in self.deck:
            self.assertIsNotNone(type_.dresser)
            break
        self.assertIsNotNone(self.deck.singles_sorted[0].dresser)
        self.assertIsNotNone(self.deck.all_sorted[0].dresser)
