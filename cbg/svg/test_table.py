# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''

import unittest

import cbg.content.field as field
import cbg.svg.table as table
import cbg.svg.wardrobe as wardrobe


class ColumnWidthAutoAdjustment(unittest.TestCase):

    def _adapt(self, specification, ref):
        f = field.Table(specification=specification)

        class Implementation(table.TablePresenter):
            class Wardrobe(wardrobe.Wardrobe):
                font_size = 5
                modes = {wardrobe.MAIN: wardrobe.Mode(font=wardrobe.Font('F'))}

            _characters_per_line = 10

            def present(inst):
                array, _ = inst._adapt_to_space()
                self.assertEqual(array.tolist(), ref)

        Implementation.new(f, size=(1, 2))

    def test_no_break(self):
        self._adapt((('h1', 'h2'),),
                    [['h1', 'h2']])

    def test_one_break(self):
        self._adapt((('h1', 'h2'),
                     ('c1a c1b', 'c2a'),
                     ('c1c c1d c1e', 'c2b')),
                    [['h1', 'h2'],
                     ['c1a c1b', 'c2a'],
                     ['c1c c1d\nc1e', 'c2b']])
        #                     ^^ new!

    def test_multiple_breaks(self):
        # Wider input resulting in multiple added newlines.
        self._adapt((('h', 'h h h', 'h'),
                     ('c c c c c c', 'c', 'c c c'),),
                    [['h', 'h h\nh', 'h'],
                     ['c c\nc c\nc c', 'c', 'c c\nc']])
