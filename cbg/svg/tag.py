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
from cbg.svg import wardrobe


def default_to_specified_text(method):
    def replacement(instance, text=None):
        if text is None:
            text = str(instance.field)
        return method(instance, text)
    return replacement


class TagBanner(presenter.SVGPresenter):
    '''Text atop a rectangular background line built to suit the text.

    Abstract base class.

    Intended primarily for use with tag fields, like those in the tag module.
    By default, the text is taken directly from the field specification.

    '''

    def present(self):
        self._insert_banner_line()
        self._insert_banner_text()
        self.cursor.slide(self.wardrobe.mode.thickness)

    def _choose_line_mode(self, text):
        '''Choose a wardrobe mode etc. for the line.

        No assumptions are made here in this superclass because the only
        truly standard modal key is used in _choose_text_mode().

        '''
        raise NotImplementedError

    def _choose_text_mode(self, text):
        '''Choose a wardrobe mode etc. for the text.'''
        self.wardrobe.set_mode(wardrobe.MAIN)

    @default_to_specified_text
    def _insert_banner_line(self, text):
        '''Draw the graphics.

        If there is text to be drawn, draw a thick line under it.
        Otherwise, make the line thin, just the wardrobe's thickness.

        '''
        self._choose_text_mode(text)
        if self.wardrobe.literate:
            n_lines = len(self._wrap(text, '', ''))
        else:
            # We assume that a non-text wardrobe was chosen because there is
            # no text to display.
            n_lines = 0

        self._choose_line_mode(text)

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
        line = shapes.Line.new(a, b, stroke_width=boxheight,
                               **self.wardrobe.to_svg_attributes())
        self.append(line)

    @default_to_specified_text
    def _insert_banner_text(self, text):
        self._choose_line_mode(text)
        if self.field:
            # Add text to the box.
            self.cursor.slide(self.wardrobe.mode.thickness / 2)
            self._choose_text_mode(text)
            self.insert_paragraph(text)
            self._choose_line_mode(text)
            self.cursor.slide(self.wardrobe.mode.thickness / 2)
        else:
            self.cursor.slide(self.wardrobe.mode.thickness)
