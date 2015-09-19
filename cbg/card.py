# -*- coding: utf-8 -*-
'''A module to represent the text content of a playing card at a high level.

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

import cbg.elements


class HumanReadablePlayingCard(cbg.elements.DerivedFromSpec, list):
    '''The text content of a single playing card, as a list of fields.

    Content is tracked by field type, and each field type has its own
    class, listed in the "field_classes" class attribute, a tuple.

    If there is a field corresponding to a title, it should generally
    be populated first and use the "key_title" attribute of the card
    class as its key, because that way its content will appear in
    exception messages etc., to help debug subsequent problems.

    SVG (XML) typesetting information can be composited onto instances
    as the "presenter" attribute, which is based on the "presenter_class"
    class attribute.

    The number of copies in a deck is tracked at the deck level, not here.

    '''
    field_classes = tuple()
    presenter_class = None

    _untitled_base = 'untitled card'
    _untitled_iterator = itertools.count(start=1)

    def __init__(self, **raw_data):
        '''Receive a hash map of raw data from content specifications.'''
        super().__init__()
        self._generated_title = self._generate_title()

        self.presenter = None  # Graphics encoder not mandatory.
        if self.presenter_class:
            self.presenter = self.presenter_class(self)

        for f in self.field_classes:
            # Instantiate empty fields for content.
            self.append(f(self))

        self._process(**raw_data)

    def _process(self, **raw_data):
        '''All the work from terse specs to complete contents.'''
        self._populate_fields(raw_data)

    def _populate_fields(self, raw_data):
        '''Put data from incoming raws into empty fields.

        The order is honored because field methods may be overridden
        to perform arbitrary operations on earlier fields, e.g. the
        presence of an "Action" field may automatically add an "Action"
        tag to a "Tags" field, which needs to have been initialized
        with other content first.

        '''
        for field in self:
            try:
                value = raw_data.pop(field.key)
            except KeyError:
                field.not_in_spec()
            else:
                field.in_spec(value)

        for key, value in raw_data.items():
            s = 'Unrecognized field in data spec for card "{}": "{}: {}".'
            s = s.format(self.title, key, value)
            raise self.SpecificationError(s)

    @property
    def sorting_keys(self):
        '''Used by decks to put themselves in order.'''
        return self.title

    def field_by_key(self, key, required=True):
        for f in self:
            if f.key == key:
                return f
        if required:
            s = 'No such field on card {}: {}.'
            raise KeyError(s.format(self.title, key))

    @property
    def title(self):
        '''Quick access to the card's title field's processed value, if any.

        In the absence of a title field, for the moment, use a stable
        generated title.

        '''
        try:
            return self.field_by_key(self.key_title)[0].string
        except:
            return self._generated_title

    @property
    def tags(self):
        '''Quick access to the card's tags. See the tag module.

        This method will only find a tag field with a key from the
        standard source, and assumes the existence of such a field.
        Override it for other arrangements.

        In the basic application model, users can filter cards based
        on this attribute.

        '''
        return self.field_by_key(self.key_tags)

    def __hash__(self):
        '''Treat as if immutable, because decks are counters.'''
        return hash(id(self))
