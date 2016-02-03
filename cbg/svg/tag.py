# -*- coding: utf-8 -*-
'''Tag presentation support.'''

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


from cbg.svg import presenter
from cbg.svg import shapes


class TagBanner(presenter.SVGPresenter):
    '''A moderately fancy banner with specified text on top.

    Abstract base class. Methods need to be overridden for the choice
    of wardrobe modes depending on the circumstances.

    Intended primarily for use with tag fields, like those in the tag module.

    '''

    def present(self):
        self._insert_banner_box()
        self._insert_banner_text()
        self.cursor.slide(self.wardrobe.mode.thickness)

    def _choose_box_mode(self):
        raise NotImplementedError

    def _choose_text_mode(self):
        raise NotImplementedError

    def _insert_banner_box(self):
        '''Draw the graphics.

        If there is text to be drawn, draw a thick line (a box) under it.
        Otherwise, make the line thin, just the wardrobe's thickness.

        '''
        self._choose_text_mode()
        if self.wardrobe.literate:
            n_lines = len(self._wrap(str(self.field), '', ''))
        else:
            # We assume that a non-text wardrobe was chosen because there is
            # no text to display.
            n_lines = 0

        self._choose_box_mode()

        textheight = n_lines * self.wardrobe.line_height
        boxheight = textheight + self.wardrobe.mode.thickness

        # Determine the vertical level of the line.
        self.cursor.slide(boxheight / 2)
        y_offset = self.cursor.offset
        self.cursor.slide(-boxheight / 2)

        # Determine the two anchor points of the line.
        a = self.origin + (0, y_offset)
        b = self.origin + (self.size[0], y_offset)

        # Encode the line.
        line = shapes.Line.new(a, b, wardrobe=self.wardrobe,
                               stroke_width=boxheight)
        self.append(line)

    def _insert_banner_text(self):
        self._choose_box_mode()
        if self.field:
            # Add text to the box.
            self.cursor.slide(self.wardrobe.mode.thickness / 2)
            self._choose_text_mode()
            self.insert_paragraph(str(self.field))
            self._choose_box_mode()
            self.cursor.slide(self.wardrobe.mode.thickness / 2)
        else:
            self.cursor.slide(self.wardrobe.mode.thickness)
