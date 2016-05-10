# -*- coding: utf-8 -*-
'''Tabular presentation. Good for stat blocks.'''

# This file is part of CBG.
#
# CBG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CBG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CBG.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2016 Viktor Eikman


import numpy

from cbg.svg import presenter


class TablePresenter(presenter.IndentedPresenter):
    '''A table layout.

    Columns widths are currently determined automatically. Prefabricated
    multi-line cell contents are not respected.

    '''

    @classmethod
    def requirements_by_column(cls, array):
        '''A generator of character lengths by column of passed array.

        Generate one 2-tuple of integers per column of the array (table).
        The first integer measures the longest word in any row of the column.
        The second measures the longest complete line.

        '''
        def longest_word(cell):
            return max(map(lambda w: len(w), str(cell).split()))

        def longest_line(cell):
            return max(map(lambda l: len(l), str(cell).splitlines()))

        # Iterate over each column.
        for col_i in range(array.shape[-1]):
            cells = tuple(numpy.nditer(array[..., col_i], flags=['refs_ok']))
            yield (max(map(longest_word, cells)),
                   max(map(longest_line, cells)))

    @classmethod
    def line_break(cls, string, target_width):
        '''Insert line breaks into a string. Each line fits passed width.'''
        split = string.split()
        lines = []
        while split:
            line = []
            while split:
                width_with_word = len(' '.join(line + [split[0]]))
                if width_with_word <= target_width:
                    line.append(split.pop(0))
                else:
                    break
            lines.append(' '.join(line))
        return '\n'.join(lines)

    def present(self):
        array, width_requirements = self._adapt_to_space()

        contents = array.tolist()
        if self.cursor.flip_line_order:
            contents = contents[::-1]

        for row in contents:
            self._insert_row(row, width_requirements)

        self.cursor.slide(self.wardrobe.after_paragraph)

    def _insert_row(self, row, width_requirements):
        cwidth = self.wardrobe.character_width
        max_lines = max(map(lambda c: len(c.splitlines()), row))
        y_init = self.line_feed(n_lines=max_lines)

        for col_i, cell in enumerate(row):
            lines = cell.splitlines()
            space = max_lines * self.wardrobe.line_height

            # Create a cursor local to the cell.
            # Use the presenter's overall cursor class.
            cursor = type(self.cursor)(space=space)

            def x_offsetter():
                init = cwidth * sum(map(lambda i: width_requirements[i][1],
                                        range(col_i)))
                space = cwidth * width_requirements[col_i][1]

                return init + self.wardrobe.mode.anchor_offset(space,
                                                               column=col_i)

            def y_offsetter():
                local = cursor.text(self.wardrobe.font_size,
                                    self.wardrobe.line_height)

                # Because we've got double cursors, skim one line height.
                return y_init + local - self.wardrobe.line_height

            self._insert_text_block(lines, x_offsetter, y_offsetter,
                                    column=col_i)

    def _adapt_to_space(self):
        '''Make columns of text in a copy of self.field's contents.'''
        array = self.field.copy()
        requirements = tuple(self.requirements_by_column(array))

        if sum(r[0] for r in requirements) > self._characters_per_line:
            s = 'Minimal column widths too large for available space.'
            raise ValueError(s)

        while sum(r[1] for r in requirements) > self._characters_per_line:
            deltas = tuple(r[1] - r[0] for r in requirements)
            max_delta = max(deltas)
            assert max_delta > 0
            target_col_i = deltas.index(max_delta)
            self._rebreak_column(array, target_col_i,
                                 requirements[target_col_i])

            # Check requirements again after having adjusted one column.
            requirements = tuple(self.requirements_by_column(array))

        return array, requirements

    def _rebreak_column(self, array, col_i, prior_requirements):
        min_width, max_width = prior_requirements
        for i in numpy.ndindex(array.shape):
            self._rebreak_cell(array, i, min_width, max_width - 1)

    def _rebreak_cell(self, array, i, min_width, target_width):
        row_i, col_i = i
        assert target_width >= min_width
        original = self.field[row_i][col_i]
        if len(original) <= min_width:
            # Not possible or no point to breaking further.
            return
        array[row_i][col_i] = self.line_break(array[row_i][col_i],
                                              target_width)
