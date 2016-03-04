# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

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
        SECOND: {keys.DATA: {'also': 'this'}, keys.METADATA: {keys.COPIES: 1}},
        THIRD: {keys.DATA: {}, keys.METADATA: {}},
        }


class Deck(unittest.TestCase):
    def setUp(self):

        class CardSubclass(card.Card):
            class TitleField(cbg.content.text.TextField):
                key = keys.TITLE
                presenter_class_front = cbg.svg.presenter.TextPresenter

            class OtherField(cbg.content.text.TextField):
                key = 'also'
                presenter_class_front = cbg.svg.presenter.TextPresenter

            plan = (TitleField, OtherField)

        self.deck = deck.Deck(CardSubclass, raw=SPEC)

    def test_sorting(self):
        sorted_ = [c.title for c in sorted(self.deck)]
        self.assertListEqual(sorted_, [FIRST, SECOND, THIRD])

    def test_flat(self):
        sorted_ = [c.title for c in sorted(self.deck.flat())]
        self.assertListEqual(sorted_, [FIRST, FIRST, FIRST,
                                       SECOND, THIRD, THIRD])
