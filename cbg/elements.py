# -*- coding: utf-8 -*-
'''A module of superclasses for types of content included on a playing card.

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

import copy

from . import misc


class CardContentField(list):
    '''Superclass for any type of human-readable text content.

    Instantiated for ideal field types, and then copied and adopted
    by cards.

    '''
    def __init__(self, markupstring, dresser_class):
        super().__init__()
        self.markupstring = markupstring
        self.dresser_class = dresser_class

        # To be determined later:
        self.parent = None
        self.dresser = None

    def composite(self, parent):
        '''Produce a copy of this field to place on a parent card.'''
        c = copy.copy(self)
        c.parent = parent
        c.dresser = self.dresser_class(c)
        return c

    def fill(self, content):
        '''Intended for use as a single point of entry.'''
        if misc.listlike(content):
            # Act like list.extend().
            # The purpose of this is to permit both lists and simple
            # strings in YAML markup, for most field types.
            parts = content  # Not sorted. Preserve rule order.
        else:
            parts = (content,)
        for p in parts:
            self.append(Paragraph(self, p))

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        pass


class Paragraph():
    '''A level below a content field in organization.'''
    def __init__(self, parent, content):
        self.parent = parent
        self.raw = content  # Useful for comparisons between specs.
        self.string = str(self.raw)

    def __str__(self):
        return self.string
