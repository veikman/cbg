# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''


import logging
import unittest
import unittest.mock

import cbg.test_misc
import cbg.content.card as card
import cbg.keys as keys
import cbg


OTHER = 'other'


class BaseClass(unittest.TestCase):
    @cbg.test_misc.suppress(logging.ERROR)
    def test_no_spec(self):
        with self.assertRaises(card.Card.SpecificationError):
            card.Card()

    @cbg.test_misc.suppress(logging.ERROR)
    def test_empty_spec(self):
        with self.assertRaises(card.Card.SpecificationError):
            card.Card({})

    @cbg.test_misc.suppress(logging.ERROR)
    def test_spec_without_plan(self):
        with self.assertRaises(card.Card.SpecificationError):
            card.Card({'item': 'particle'})

    def test_creation_generic(self):
        o = unittest.mock.patch.object
        with o(card.Card, 'layout') as m:
            card.Card({keys.TITLE: 'ignored',
                       'other data': 'ignored due to mocking of layout()'})
            m.assert_called_once_with()


class Subclass(unittest.TestCase):

    class CardSC(card.Card):
        class TitleField(cbg.content.text.TextField):
            key = keys.TITLE
            presenter_class_front = cbg.svg.presenter.TextPresenter

        class OtherField(cbg.content.text.TextField):
            key = OTHER
            presenter_class_front = cbg.svg.presenter.TextPresenter

        plan = (TitleField, OtherField)

    def test_creation_subclass(self):
        c = self.CardSC({keys.TITLE: 't0'})
        self.assertEqual(str(c), 't0')

    def test_creation_with_optional_field(self):
        c = self.CardSC({keys.TITLE: 't1', OTHER: 'different'})
        self.assertEqual(str(c), 't1')

    def test_creation_without_title_field(self):
        c = self.CardSC({OTHER: 'different again'})
        self.assertTrue(c._generated_title.startswith('untitled card'))
        self.assertNotEqual(c._generated_title, 'untitled card')

        # When not in spec, a text field defaults to an empty list
        # (of paragraphs).
        self.assertEqual(c.child_by_key_required(c.key_title).content, [])

        self.assertEqual(str(c), c._generated_title)

    def test_sorting(self):
        c0 = self.CardSC({keys.TITLE: 't0'}, parent='d0')
        c1 = self.CardSC({keys.TITLE: 't1'}, parent='d0')
        c2 = self.CardSC({keys.TITLE: 't0'}, parent='d1')
        self.assertLess(c0, c1)
        self.assertLess(c1, c2)
        self.assertLessEqual(c1, c2)
        self.assertEqual(c0, c0)
        self.assertNotEqual(c0, c1)
        self.assertGreaterEqual(c1, c0)
        self.assertGreater(c1, c0)
        self.assertGreater(c2, c1)

        with self.assertRaises(TypeError):
            c1 < 'sphinx'
