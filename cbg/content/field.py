# -*- coding: utf-8 -*-
'''Fields of content included on a playing card.

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

import cbg.misc
import cbg.keys
from cbg.content import elements


class Field(elements.Presentable, list):
    '''Superclass for any human-readable content that varies between cards.

    Used to create classes to represent ideal field types, which are
    then instantiated by card types and (normally) populated from
    specification files.

    '''

    # A key is needed if contents are to be found in specs.
    key = None

    # A paragraph class encapsulates and processes contents at a lower level.
    paragraph_class = elements.Paragraph

    def __init__(self, parent):
        '''Produce a copy of this field to place on a parent card.'''
        super().__init__()
        self.parent = parent

    def in_spec(self, content):
        '''Beaviour when the field's key is found in the raw specification.'''
        for raw in cbg.misc.make_listlike(content):
            self.append(self.paragraph_class(raw))

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        pass
