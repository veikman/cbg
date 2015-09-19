# -*- coding: utf-8 -*-
'''A module to represent a deck of playing cards.

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

import collections
import copy
import itertools

import cbg.elements


class Deck(cbg.elements.DerivedFromSpec, collections.Counter):
    '''The right number of copies of every card that belongs in a deck.'''

    _untitled_base = 'untitled deck'
    _untitled_iterator = itertools.count(start=1)

    def __init__(self, card_cls, raw, title=None):
        super().__init__()
        self.title = title

        self.metadata = {}
        if isinstance(raw, collections.abc.Mapping):
            self.metadata = raw.get(self.key_metadata, {})

            try:
                cards = raw[self.key_data]
            except KeyError:
                cards = {k: v for k, v in raw.items()
                         if k != self.key_metadata}

        elif isinstance(raw, collections.abc.Sequence):
            cards = raw

        else:
            s = 'Cannot interpret {} as a deck specification.'
            raise self.SpecificationError(s.format(type(raw)))

        self.title = self.metadata.get(self.key_title, self.title)
        if self.title is None:
            self.title = self._generate_title()

        self._populate(card_cls, cards)

    def _populate(self, card_cls, cards):
        '''Infer the rough data structure of the specification.'''
        if not cards:
            raise self.SpecificationError('No cards.')

        if isinstance(cards, collections.abc.Mapping):
            for key, value in cards.items():
                self._add_card_type(card_cls, cards[key],
                                    backup_title=str(key))
        else:
            # List-like, continuing from the type check in __init__().
            for item in cards:
                self._add_card_type(card_cls, item)

    def _add_card_type(self, card_cls, card_spec, backup_title=None):
        '''Digest a bit of metadata and hand the rest off to the card class.'''

        # Prefer explicit mention of the number of copies.
        copies = card_spec.get(self.key_metadata, {}).get(self.key_copies)

        if copies is None:
            copies = self.metadata.get(self.key_defaults,
                                       {}).get(self.key_copies)

        # Discard card-level metadata, if any.
        card_spec.pop(self.key_metadata, None)
        card_spec = card_spec.get(self.key_data, card_spec)

        if backup_title and self.key_title not in card_spec:
            card_spec[card_cls.key_title] = backup_title

        if copies is None:
            copies = card_spec.get(self.key_copies)
            if copies is not None:
                del card_spec[self.key_copies]

        if copies is None:
            # Not found in the specifications.
            copies = 1

        self[card_cls(**card_spec)] = copies

    def singles_sorted(self):
        keys = {f.sorting_keys: f for f in self}
        return [keys[k] for k in sorted(keys)]

    def all_sorted(self):
        '''Produce literal copies of all cards in the deck.'''
        ret = list()
        for card_type in self.singles_sorted():
            for copy_ in range(0, self[card_type]):
                ret.append(copy.copy(card_type))
        return ret

    def __lt__(self, other):
        return self.title < other.title

    def __str__(self):
        return '<{} deck>'.format(self.title)
