# -*- coding: utf-8 -*-
'''Cursors for use by SVG presenters.'''

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


class _GraphicsElementInsertionCursor():
    '''A direction from which to insert new elements on a card.

    Abstract base class.

    '''

    flip_line_order = False

    def __init__(self, space=None, displacement=0):
        '''Take a presenter with access to size information.'''
        self.space = space
        self.displacement = displacement

    @property
    def offset(self):
        '''A (vertical) offset for use with presenter origin coordinates.'''
        raise NotImplementedError

    def jump(self, position):
        self.displacement = position

    def slide(self, distance):
        '''Return an appropriate height for the next insertion, and move.'''
        raise NotImplementedError

    def text(self, font_size, line_height, n_lines=1):
        '''A direction-sensitive line feed.

        Return a position appropriate for starting text insertion.

        The "line_height" argument refers to the height in mm to feed past.

        '''
        raise NotImplementedError


class FromTop(_GraphicsElementInsertionCursor):

    @property
    def offset(self):
        return self.displacement

    def slide(self, height):
        '''Move first, then suggest insertion at new location.'''
        self.displacement += height
        return self.offset

    def text(self, font_size, line_height, n_lines=1):
        y_insertion = self.slide(font_size)
        self.slide(n_lines * line_height - font_size)
        return y_insertion


class FromBottom(_GraphicsElementInsertionCursor):
    flip_line_order = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.space is None:
            raise ValueError('Upward cursors require space.')

    @property
    def offset(self):
        return self.space - self.displacement

    def slide(self, height):
        '''Insert first, then move (up). State position from top of card.'''
        original_offset = self.offset
        self.displacement += height
        return original_offset

    def text(self, font_size, line_height, n_lines=1):
        self.slide(n_lines * line_height - font_size)
        return self.slide(font_size)
