# -*- coding: utf-8 -*-
'''A module to represent a deck of playing cards.'''

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


import collections
import copy
import logging
import os
import re

from cbg.content import elements
import cbg.serialization


class Deck(elements.DerivedFromSpec, collections.Counter):
    '''The right number of copies of every card that belongs in a deck.'''

    _untitled_base = 'untitled deck'

    def __init__(self, card_cls, raw=None, directory=None, filename_base=None):
        super().__init__()
        self.title = self.filename_base = filename_base

        if raw is None:
            # Gather data from file.
            if not directory and self.filename_base:
                s = 'Data or file path fragments needed to instantiate deck.'
                raise ValueError(s)

            raw = self._parse_spec_file(directory)

        self.metadata = {}
        if isinstance(raw, collections.abc.Mapping):
            self.metadata = raw.get(self.key_metadata, {})

            try:
                card_specs = raw[self.key_data]
            except KeyError:
                card_specs = {k: v for k, v in raw.items()
                              if k != self.key_metadata}

        elif isinstance(raw, collections.abc.Sequence):
            card_specs = raw

        else:
            s = 'Cannot interpret {} as a deck specification.'
            raise self.SpecificationError(s.format(type(raw)))

        self.title = self.metadata.get(self.key_title, self.title)
        self._populate(card_cls, card_specs)

        s = '{} unique card(s) in {} deck.'
        logging.debug(s.format(len(self), self))

    def _parse_spec_file(self, directory):
        for extension in cbg.serialization.Serialization.registry:
            filename = '.'.join((self.filename_base, extension))
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                break

        if not os.path.exists(filepath):
            raise FileNotFoundError('Could not locate {}.'.format(self))

        logging.debug('Reading raw specifications from {}.'.format(filepath))

        return cbg.serialization.Serialization.load(filepath)

    def _populate(self, card_cls, card_specs):
        '''Infer the rough data structure of the specification.'''
        if not card_specs:
            raise self.SpecificationError('No cards.')

        if isinstance(card_specs, collections.abc.Mapping):
            for key, value in card_specs.items():
                self._add_card_type(card_cls, value,
                                    backup_title=str(key))
        else:
            # List-like, continuing from the type check in __init__().
            for item in card_specs:
                self._add_card_type(card_cls, item)

    def _add_card_type(self, card_cls, card_spec, backup_title=None):
        '''Digest a bit of metadata and hand the rest off to the card class.'''

        # Discard card-level metadata, if any.
        card_metadata = card_spec.pop(self.key_metadata, {})
        deck_defaults = self.metadata.get(self.key_defaults, {})
        card_spec = card_spec.get(self.key_data, card_spec)

        # Add title if it can be inferred from a higher-level mapping key.
        if backup_title and self.key_title not in card_spec:
            card_spec[card_cls.key_title] = backup_title

        # Prefer explicit mention of the number of copies of the card type.
        copies = card_metadata.get(self.key_copies)
        if copies is None:
            copies = deck_defaults.get(self.key_copies)
        if copies is None:
            copies = card_spec.pop(self.key_copies, None)
            if copies is not None:
                s = 'Pulled number of copies from data section of specs.'
                logging.debug(s)
        if copies is None:
            # Not found in the specifications.
            copies = 1

        self[card_cls(specification=card_spec, parent=self)] = copies

    def control_selection(self, whitelist, blacklist, card_max1, deck_max1):
        whitelist_exists = bool(whitelist)
        assert isinstance(card_max1, bool)
        assert isinstance(deck_max1, bool)

        for card in self:
            whitelisted = False
            for restriction in whitelist:
                n_restricted = self._apply_restriction(restriction, card)
                if n_restricted is not None:
                    whitelisted = True
                    # If negative: No change from default number.
                    if n_restricted >= 0:
                        self[card] = n_restricted
                    break  # Apply only the first matching white restriction.

            if whitelist_exists and not whitelisted:
                self[card] = 0

            for restriction in blacklist:
                n_restricted = self._apply_restriction(restriction, card)
                if n_restricted is not None:
                    if n_restricted >= 0:
                        # A not-so-black secondary filter.
                        self[card] = n_restricted
                    else:
                        # Default behaviour on hit: Blacklisted.
                        self[card] = 0
                    break  # Apply only the first matching black restriction.

            if self[card]:
                if card_max1:
                    self[card] = 1

                if deck_max1 is True:
                    self[card] = 1
                    deck_max1 = None  # Reuse of flag to store state.
                elif deck_max1 is None:
                    self[card] = 0

    def _apply_restriction(self, restriction, card):
        '''See if a string specifying a restriction applies to a card.

        If there's a hit, return the new number of copies to process.
        Else return None.

        '''
        interpreted = re.split('^(\d+):', restriction, maxsplit=1)[1:]

        if len(interpreted) == 2:
            # The user has supplied a copy count.
            restricted_copies = int(interpreted[0])
            regex = interpreted[-1]
        else:
            # Do not change the number of copies.
            restricted_copies = -1
            regex = restriction

        if regex.startswith('tag='):
            regex = regex[4:]
            try:
                tags = card.tags
            except AttributeError:
                # No member of card class named "tags".
                # This is true of the base class.
                s = ('Tag-based filtering requires "tags" property.')
                logging.critical(s)
                raise
            if regex in map(str, tags):
                return restricted_copies
        else:
            if re.search(regex, card.title):
                return restricted_copies

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
        return str(self.title)
