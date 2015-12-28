# -*- coding: utf-8 -*-
'''Representation of general text-based content in card layouts.

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

Copyright 2015 Viktor Eikman

'''

import cbg.misc
from cbg.content import field


class Paragraph(field.Atom, cbg.misc.Formattable):
    '''A level below a content field in organization, for text-based fields.

    Paragraphs are normally created by a TextField, rather than the
    general layouting plan of a deck.

    '''

    def layout(self):
        self.content = self.format_text(self.specification)

    def __str__(self):
        return self.content


class TextField(field.AutoField):
    '''A field of zero or more paragraphs.'''

    plan = [Paragraph]

    def __str__(self):
        return '\n  '.join(map(str, self))
