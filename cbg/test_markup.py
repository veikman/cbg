# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

from . import elements
from . import exc
from . import markup


class Prediction(unittest.TestCase):
    def test_prediction(self):
        s = markup.Authority.expected(markup.Shorthand('a', ''))
        self.assertEqual(s, '{{a}}')


class CustomAuthority(unittest.TestCase):
    def test_single_parens(self):
        class A(markup.Authority):
            lead_in = '('
            lead_out = ')'
        markup.Shorthand('a', 'x', authority=A)
        paragraph = elements.Paragraph(None, '(a)', authority=A)
        self.assertEqual(paragraph.string, 'x')


class AutomaticConversion(unittest.TestCase):
    def setUp(self):
        markup.Authority.registry = dict()
        markup.Shorthand('b', 'y')
        markup.Shorthand('c', '{{b}}')
        markup.Shorthand('d', '{}z')
        markup.Shorthand('e', '{{d|1}}{:s}')

    def _match(self, text_in, text_out):
        paragraph = elements.Paragraph(None, text_in)
        self.assertEqual(paragraph.string, text_out)

    def test_clean_empty(self):
        self._match('', '')

    def test_clean_nonempty(self):
        self._match('a', 'a')

    def test_no_markup_tokens(self):
        self._match('b', 'b')

    def test_leftover_closer(self):
        self._match('b}}', 'b}}')

    def test_leftover_opener(self):
        with self.assertRaises(exc.MarkupError):
            self._match('{{b', '')

    def test_unknown_shorthand_empty(self):
        with self.assertRaises(exc.MarkupError):
            self._match('{{}}', '')

    def test_unknown_shorthand_nonempty(self):
        with self.assertRaises(exc.MarkupError):
            self._match('{{a}}', '')

    def test_match_solo(self):
        self._match('{{b}}', 'y')

    def test_single_match_context(self):
        self._match('a{{b}}a', 'aya')

    def test_double_match_context(self):
        self._match('a{{b}}{{b}}a', 'ayya')

    def test_separating_context(self):
        self._match('a{{b}}a{{b}}a', 'ayaya')

    def test_param_excessive_empty(self):
        self._match('{{b|}}', 'y')

    def test_param_excessive_nonempty_without_format_anchors(self):
        self._match('{{b|1}}', 'y')

    def test_param_sufficient_empty(self):
        self._match('{{d|}}', 'z')

    def test_param_sufficient_nonempty(self):
        self._match('{{d|1}}', '1z')

    def test_param_excessive_nonempty(self):
        self._match('{{d|1|2}}', '1z')

    def test_recursive(self):
        self._match('{{b}}{{c}}', 'yy')

    def test_reverse_recursive(self):
        self._match('{{c}}{{b}}', 'yy')

    def test_nesting_direct(self):
        self._match('{{d|{{b}}}}', 'yz')

    def test_nesting_indirect(self):
        self._match('{{d|{{c}}}}', 'yz')

    def test_nesting_advanced(self):
        self._match('{{e|{{e|2}}}}', '1z1z2')
