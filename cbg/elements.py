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

import itertools

import cbg.misc
import cbg.keys


class DerivedFromSpec():
    '''Superclass for anything that parses complex raw text specifications.

    The properties of subclasses are derived from plain-text specifications
    using text keys. Some keys are defined here, so that localization
    (of specifications) can be achieved by overwriting these keys in
    custom classes.

    Support for additional keys is achieved by subclassing CardContentField.

    '''

    class SpecificationError(ValueError):
        '''Used to signal unmet formal expectations.'''
        pass

    # Canonical specification keywords:
    key_metadata = cbg.keys.METADATA
    key_data = cbg.keys.DATA

    key_copies = cbg.keys.COPIES
    key_defaults = cbg.keys.DEFAULTS
    key_tags = cbg.keys.TAGS
    key_title = cbg.keys.TITLE

    # Conveniences for uniquely named items with no proper title:
    _untitled_base = 'untitled'
    _untitled_iterator = itertools.count(start=1)

    def _generate_title(self):
        '''Create a hitherto unused title. Useful mainly for hash maps.'''
        return '{} {}'.format(self._untitled_base,
                              next(self._untitled_iterator))


class Paragraph():
    '''A level below a content field in organization.

    This basic form of a text element is suitable for use as a
    paragraph. It is subclassed in the "tag" module to represent a tag
    in a horizontal list.

    '''

    def __init__(self, raw):
        self.raw = raw  # Useful for comparisons between specs.
        self.string = self.process(self.raw)

    def process(self, raw):
        '''Convert from e.g. integer in YAML specs to string.

        This method is intended to be overridden for the integration
        of a string templating system.

        '''
        return str(raw)

    def __str__(self):
        return self.string


class CardContentField(list):
    '''Superclass for any type of human-readable text content on a card.

    Used to create classes to represent ideal field types, which are then
    instantiated by card types.

    '''
    key = None
    presenter_class = None
    paragraph_class = Paragraph

    def __init__(self, parent):
        '''Produce a copy of this field to place on a parent card.'''
        super().__init__()
        self.parent = parent
        self.presenter = self.presenter_class(self)

    def in_spec(self, content):
        '''Beaviour when the field's key is found in the raw specification.'''
        for raw in cbg.misc.make_listlike(content):
            self.append(self.paragraph_class(raw))

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        pass
