# -*- coding: utf-8 -*-
'''Cursors for use by SVG presenters.

------

This file is part of CBG.

CBG is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CBG is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CBG.  If not, see <http://www.gnu.org/licenses/>.

Copyright 2014-2015 Viktor Eikman

'''

import cbg.svg.transform


class GraphicsElementInsertionCursor():
    '''A direction from which to insert new elements on a card.'''

    flip_line_order = False

    def __init__(self, parent):
        self.parent = parent
        self.displacement = 0

        # In order to support such use cases as writing one half of a
        # card's text upside down, cursors carry transformers, which are
        # accessed by presenters.
        self.transform = cbg.svg.transform.Transformer()

    def jump(self, position):
        self.displacement = position

    def slide(self, distance):
        '''Return an appropriate height for the next insertion, and move.'''
        raise NotImplementedError

    def text(self, size, envelope):
        '''A direction-sensitive line feed.'''
        raise NotImplementedError


class FromTop(GraphicsElementInsertionCursor):
    def slide(self, height):
        '''Move first, then suggest insertion at new location.'''
        self.displacement += height
        return self.displacement

    def text(self, size, envelope):
        relevant = self.slide(size)
        self.slide(envelope - size)
        return relevant


class FromBottom(GraphicsElementInsertionCursor):
    flip_line_order = True

    def slide(self, height):
        '''Insert first, then move (up). State position from top of card.'''
        ret = self.displacement
        self.displacement += height
        return self.parent.size.footprint[1] - ret

    def text(self, size, envelope):
        self.slide(envelope - size)
        return self.slide(size)
