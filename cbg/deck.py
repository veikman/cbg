# -*- coding: utf-8 -*-

import yaml
import collections
import copy
import logging


METADATA = 'DECK METADATA'
DEFAULTS = 'DEFAULTS'
COPIES = 'copies'


class Deck(collections.Counter):
    '''The right number of copies of every card that belongs in a deck.'''

    def __init__(self, decktitle, filepath, cardtype):
        super().__init__()
        self.title = decktitle
        self.filepath = filepath
        self.raw = self.read_raw()

        try:
            self.metadata = self.raw[METADATA]
        except KeyError:
            s = 'Deck specification in {} has no metadata.'
            logging.warning(s.format(self.filepath))
            self.metadata = {}

        for cardtitle, specs in self.raw.items():
            if cardtitle == METADATA:
                continue
            type_ = cardtype(cardtitle, specs)
            copies = specs[COPIES] if COPIES in specs else self.default_copies
            self[type_] = copies

    @property
    def default_copies(self):
        '''The normal number of copies of each card in the deck.

        Prefer explicit metadata. In its absence, return 1.

        '''
        return self.metadata.get(DEFAULTS, {COPIES: 1}).get(COPIES, 1)

    def read_raw(self):
        with open(self.filepath, encoding='utf-8') as f:
            return yaml.load(f)

    @property
    def singles_sorted(self):
        keys = {f.sorting_keys: f for f in self}
        return [keys[k] for k in sorted(keys)]

    @property
    def all_sorted(self):
        '''Produce literal copies of all cards in the deck.'''
        ret = list()
        for type_ in self.singles_sorted:
            for copy_ in range(0, self[type_]):
                ret.append(copy.copy(type_))
        return ret

    def __lt__(self, other):
        return self.title < other.title

    def __str__(self):
        return '<{} deck>'.format(self.title)
