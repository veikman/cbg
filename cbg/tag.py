# -*- coding: utf-8 -*-
'''Tag support for deck-building game cards.'''


from . import elements
from . import exc


class Tag():
    '''A word or phrase used to provide categorical information.

    Any property of a card that does not require unique or elaborate
    text can be formulated as a tag to be explained elsewhere.

    Tags can be used as purely or partly graphical switches to control
    the appearance of cards.

    Non-printing tags will not themselves be represented in SVG.

    By default, tags come in two categories: Syntactic and semantic.
    More categories can be added by subclassing.

    '''
    registry = list()

    def __init__(self, specstring, full_name=None,
                 syntactic=False, printing=True,
                 subordinate_to=None, sorting_value=0):
        self.string = elements.Paragraph(self, specstring)
        self.full_name = full_name if full_name is not None else specstring
        self.syntactic = syntactic
        self.printing = printing

        self.subordinate_to = subordinate_to
        if self.subordinate_to:
            if self.subordinate_to.syntactic is not self.syntactic:
                s = 'Tag "{}" does not mix with its master, "{}".'
                s = s.format(self, self.subordinate_to)
                raise exc.SpecificationError(s)
        self.sorting_value = sorting_value

        ## Automatically keep track of which tags have been created for
        ## a game, as a potential roster for markup recognition.
        self.__class__.registry.append(self)

    def __str__(self):
        return str(self.string)

    def __lt__(self, other):
        '''Tags in printed lists are sorted alphabetically.'''
        return str(self) < str(other)

    @property
    def semantic(self):
        return not self.syntactic


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
            s = str(t).capitalize()
            if t in self.masters:
                subordinate_strings = []
                for so in self.subordinates:
                    if so.subordinate_to == t and so.printing:
                        subordinate_strings.append(str(so))
                if subordinate_strings:
                    subordinate_strings.sort()
                    s += ' ({})'.format(', '.join(subordinate_strings))
            ret.append(s)
        return ', '.join(ret)

    @property
    def subordinates(self):
        return {t for t in self if t.subordinate_to}

    @property
    def masters(self):
        return {t.subordinate_to for t in self.subordinates}

    def syntactic(self):
        return self.subset(lambda t: t.syntactic)

    def semantic(self):
        return self.subset(lambda t: t.semantic)

    def subset(self, selector_function):
        '''A (copied) subset of self, containing only filtered tags.'''
        return self.__class__(self.parent, filter(selector_function, self))


class FieldOfTags(elements.CardContentField):
    '''A content field that uses a SetOfTags as if it were a paragraph.'''
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
