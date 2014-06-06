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
            self.metadata = {DEFAULTS: {COPIES: 1}}
 
        default_copies = 1
        if DEFAULTS in self.metadata:
            if COPIES in self.metadata[DEFAULTS]:
                default_copies = self.metadata[DEFAULTS][COPIES]

        for cardtitle, specs in self.raw.items():
            if cardtitle == METADATA:
                continue
            copies = default_copies
            if COPIES in specs:
                copies = specs[COPIES]
            type_ = cardtype(cardtitle, specs)
            self[type_] = copies

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