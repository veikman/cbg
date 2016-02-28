# -*- coding: utf-8 -*-
'''A module to represent the text content of a playing card at a high level.'''

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


import itertools
import logging

from cbg.content import elements
from cbg.content import field


class Card(elements.DerivedFromSpec, field.Layout):
    '''The content of a unique playing card, as a "master" of sorts.

    Content is tracked by field type, and each field type has its own
    class, listed in the "plan" class attribute.

    If there is a field corresponding to a title, it should generally
    be populated first and use the "key_title" attribute of the card
    class as its key, because that way its content will appear in
    exception messages etc., to help debug subsequent problems.

    The number of copies in a deck is tracked at the deck level, not here.

    '''

    _untitled_base = 'untitled card'
    _untitled_iterator = itertools.count(start=1)

    def layout(self):
        '''Put data from incoming raws into empty fields.'''

        # Produce a unique title for sorting.
        self._generated_title = self._generate_title()

        if not self.specification:
            s = 'No specification data for the "{}" card.'
            raise self.SpecificationError(s.format(self))

        try:
            super().layout()
        except:
            s = 'An error occurred while processing the "{}" card.'
            logging.error(s.format(self))
            raise

        if self.specification:
            for key, value in self.specification.items():
                s = 'Unrecognized data key "{}" not consumed: "{}".'
                logging.error(s.format(key, value))

            s = 'Specification data for the "{}" card was not consumed.'
            raise self.SpecificationError(s.format(self))

    def not_in_spec(self):
        s = 'Specification of "{}" card inadequate for basic layout.'
        raise self.SpecificationError(s.format(self))

    @property
    def sorting_keys(self):
        '''Used by decks to put themselves in order.'''
        return self.title

    @property
    def title(self):
        '''Quick access to the card's title field's processed value, if any.

        In the absence of a title field, for the moment, use a stable
        generated title.

        '''
        try:
            field = str(self.child_by_key_required(self.key_title))
            if field:
                # In spec.
                return str(field)
        except:
            pass

        return self._generated_title

    @property
    def card(self):
        '''An override of a field method.'''
        return self

    def __str__(self):
        return self.title

    def __hash__(self):
        '''Treat as if immutable, because decks are counters (hash tables).'''
        return hash(id(self))
