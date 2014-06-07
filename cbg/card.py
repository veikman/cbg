# -*- coding: utf-8 -*-

from . import exc


TITLE = '_title'
DATA = 'data'


class HumanReadablePlayingCard(list):
    '''Superclass for the text content of a single playing card.

    SVG (XML) typesetting information can be composited onto instances.

    The number of copies etc. is tracked at the deck level, not here.

    '''

    def __init__(self, title, specdict):
        '''If there's a data field, zoom in on that. Otherwise, all is data.'''
        super().__init__()
        self.title = title
        self.raw = specdict

        try:
            self.data = self.raw[DATA]
        except KeyError:
            self.data = self.raw

        self.dresser = None  # Graphics encoder not mandatory.
        self.process()

    def process(self):
        '''All the work from terse specs to completion.'''
        raise NotImplementedError

    @property
    def sorting_keys(self):
        '''Used by decks to put themselves in order.'''
        return self.title

    def populate_fields(self, fields):
        '''Standard procedure often called from process().'''
        for f in fields:
            ## Transform ideal, possible fields into real, empty ones.
            self.append(f.composite(self))
        for d in self.data:
            if not self._sancheck_raw_field(d, fields):
                s = 'Unrecognized field in data spec for card "{}": "{}".'
                raise exc.SpecificationError(s.format(self.title, d))
        for f in self:
            if f.markupstring in self.data:
                f.fill(self.data[f.markupstring])
            elif f.markupstring == TITLE:
                ## For convenience, the string key used to identify the
                ## card in YAML can be recycled as its title.
                f.fill(self.title)
            else:
                f.not_in_spec()

    def substitute_tokens(self, roster):
        for f in self:
            f.substitute_tokens(roster)

    def field_by_markupstring(self, string):
        for f in self:
            if f.markupstring == string:
                return f
        s = 'No such field on card {}: {}.'
        raise KeyError(s.format(self.title, string))

    def _sancheck_raw_field(self, field, roster):
        for f in roster:
            if f.markupstring == field:
                return True
        return False

    def __hash__(self):
        return hash(self.title)
