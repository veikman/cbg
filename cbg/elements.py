# -*- coding: utf-8 -*-

import copy

from . import misc


class CardContentField(list):
    '''Superclass for any type of human-readable text content.

    Instantiated for ideal field types, and then copied and adopted
    by cards.

    '''
    def __init__(self, markupstring, dresser_class):
        super().__init__()
        self.markupstring = markupstring
        self.dresser_class = dresser_class

        ## To be determined later:
        self.parent = None
        self.dresser = None

    def composite(self, parent):
        '''Produce a copy of this field to place on a parent card.'''
        c = copy.copy(self)
        c.parent = parent
        c.dresser = self.dresser_class(c)
        return c

    def fill(self, content):
        '''Intended for use as a single point of entry.'''
        if misc.listlike(content):
            ## Act like list.extend().
            ## The purpose of this is to permit both lists and simple
            ## strings in YAML markup, for most field types.
            parts = content  # Not sorted. Preserve rule order.
        else:
            parts = (content,)
        for p in parts:
            self.append(Paragraph(self, p))

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        pass

    def substitute_tokens(self, roster):
        for p in self:
            p.substitute_tokens(roster)


class Paragraph():
    '''A level below a content field in organization.'''
    def __init__(self, parent, content):
        self.parent = parent
        self.raw = content  # Useful for comparisons against other specs.
        self.string = str(self.raw)

    def substitute_tokens(self, roster):
        for substitution in roster:
            substitution.apply_to(self)

    def __str__(self):
        return self.string
