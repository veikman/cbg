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


class Field(elements.Presentable):
    '''Superclass for any human-readable content that varies between cards.

    Abstract base class.

    Used to create classes to represent ideal field types, which are
    then instantiated by card types and (normally) populated from
    specification files.

    '''

    # A key is needed if contents are to be found in specs.
    key = None

    def in_spec(self, content):
        '''Behaviour when the field's key is found in the raw specification.'''
        raise NotImplementedError

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        raise NotImplementedError


class ContainerField(Field):
    '''A field that forces its content into a subordinate type of field.

    Abstract base class.

    '''

    # A class encapsulates and processes contents at a lower level.
    content_class = None

    def not_in_spec(self):
        '''Absence of data leaves an empty yet perhaps visible container.'''
        pass


class ContainerList(ContainerField, list):
    '''A one-dimensional array of subordinate fields.'''

    def in_spec(self, content):
        '''Encapsulate each piece of content.'''
        for raw in cbg.misc.make_listlike(content):
            self.append(self.content_class(content=raw))


class Paragraph(Field):
    '''A level below a content field in organization, for text-based fields.

    This is subclassed in the "tag" module to represent a tag in a
    horizontal list.

    '''

    def __init__(self, content=None):
        '''Initialize.

        Paragraphs are not normally instantiated, except by text fields.
        At that point, the content is already known, so not_in_spec() is
        not defined, and the content can be passed directly to this
        method for convenience.

        '''
        super().__init__()
        self.raw = ''
        self.string = ''

        if content is not None:
            self.in_spec(content)

    def in_spec(self, content):
        assert content is not None
        self.raw = content  # Useful for comparisons between specs.
        self.string = self.format_text(self.raw)

    def not_in_spec(self, _):
        raise ValueError('Calling for a default paragraph is an error.')

    @classmethod
    def format_text(cls, content):
        '''Convert from e.g. integer in YAML specs to string.

        This method is intended to be overridden for the integration
        of a string templating system.

        '''
        return str(content)

    def __str__(self):
        return self.string


class TextField(ContainerList):
    '''A field of zero or more paragraphs.'''

    content_class = Paragraph

    def __str__(self):
        return '\n  '.join(map(str, self))
