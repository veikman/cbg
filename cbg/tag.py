# -*- coding: utf-8 -*-
'''Tag support for deck-building game cards.

Any property of a card that does not require unique or elaborate text
can be formulated as a tag, to be explained elsewhere.

Tags can be used to control the appearance of cards, and will not,
themselves, necessarily be printed.

'''

from . import elements
from . import exc

class Tag():
    all_ = list()

    def __init__(self, specstring, syntactic=False, printing=True,
                 subordinate_to=None, sorting_value=0):
        self.string = elements.Paragraph(self, specstring)
        self.syntactic = syntactic
        self.printing = printing

        self.subordinate_to = subordinate_to
        if self.subordinate_to and self.subordinate_to.syntactic is not self.syntactic:
            s = 'Tag "{}" does not mix with its master, "{}".'
            raise exc.SpecificationError(s.format(self, self.subordinate_to))
        self.sorting_value = sorting_value

        ## Automatically keep track of which tags have been created for
        ## a game, as a potential roster for markup recognition.
        self.__class__.all_.append(self)

    def __str__(self):
        return str(self.string)

    def __lt__(self, other):
        '''Tags in printed lists are sorted alphabetically.'''
        return str(self) < str(other)

    @property
    def printstring(self):
        return str(self)[0].upper() + str(self)[1:]

    def substitute_tokens(self, roster):
        self.string.substitute_tokens(roster)

class SetOfTags(set):
    '''Sorted alphabetically when refined to a string.'''
    def __init__(self, parent, tags):
        self.parent = parent
        super().__init__(tags)
        for t in self.subordinates:
            if t.subordinate_to not in self:
                s = 'Tag "{}" lacks master "{}".'
                raise exc.SpecificationError(s.format(t, t.subordinate_to))

    def __str__(self):
        ret = list()
        for t in sorted(self):
            if t.subordinate_to or not t.printing:
                continue
            s = t.printstring
            if t in self.masters:
                subs = sorted([str(s) for s in self.subordinates
                                            if s.subordinate_to == t])
                s += ' ({})'.format(', '.join(subs))
            ret.append(s)
        return ', '.join(ret)

    @property
    def subordinates(self):
        return {t for t in self if t.subordinate_to}

    @property
    def masters(self):
        return {t.subordinate_to for t in self.subordinates}

    def syntactic(self):
        '''A (copied) subset of self, containing only syntactic tags.'''
        return self.__class__(self.parent, (t for t in self if t.syntactic))

    def semantic(self):
        return self.__class__(self.parent, (t for t in self if not t.syntactic))

    def substitute_tokens(self, roster):
        for t in self:
            t.substitute_tokens(roster)

class FieldOfTags(elements.CardContentField):
    '''Use a SetOfTags instead of a paragraph as content.
    
    Do not convert markup tokens. That's done later.
    
    '''
    def __init__(self, markupstring, dresser, roster):
        super().__init__(markupstring, dresser)
        self.roster = roster

    def fill(self, content):
        '''Take a list of strings. Convert to actual tag objects.'''
        super().append(SetOfTags(self, {self._tagify(s) for s in content}))

    def not_in_spec(self):
        '''An empty tag list is still useful. Can be added to later.'''
        self.fill([])

    def _tagify(self, string):
        for tag in self.roster:
            if string == tag.string.raw:
                return tag

        s = 'Tag markup "{}" does not appear in roster: "{}".'
        s = s.format(string, [str(t) for t in self.roster])
        raise exc.SpecificationError(s)
