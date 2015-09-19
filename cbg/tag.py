# -*- coding: utf-8 -*-
'''Tag support for deck-building game cards.

Any property of a card that does not require unique or elaborate
text on the card can be reduced to a tag. The tag itself would have to
be explained elsewhere.

Tags can also be used inside CBG applications, to drive programmatic
logic. For example, the choice of color scheme for a card can be a
result of its tags.

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

import cbg.keys as keys
import cbg.elements as elements


class Tag():
    '''A word or phrase used to provide categorical information.'''

    registry = list()
    paragraph_class = elements.Paragraph

    class TaggingError(Exception):
        pass

    def __init__(self, key):
        '''The raw text key may be active markup.

        A temporary paragraph object is used to process that string,
        hopefully into a more human-readable name.

        '''
        as_paragraph = self.paragraph_class(key)
        self.key = as_paragraph.raw
        self.string = as_paragraph.string

        # Automatically keep track of which tags have been created for
        # a game, as a roster for specification recognition.
        self.__class__.registry.append(self)

    def __str__(self):
        return str(self.string)

    def __lt__(self, other):
        '''Tags sort alphabetically.'''
        return str(self) < str(other)


class AdvancedTag(Tag):
    '''An alternate tag with some oft-useful features.

    These tags are either syntactic or semantic, with respect to their
    rule systems, and can be hierarchically related, weighted for
    sorting, and explicitly named.

    These tags can also be non-printing, in which case they should
    be ignored by graphical presenters.

    '''

    def __init__(self, key, full_name=None,
                 syntactic=False, printing=True,
                 subordinate_to=None, sorting_value=0):
        super().__init__(key)

        self.full_name = full_name if full_name is not None else self.string

        self.syntactic = syntactic
        self.printing = printing

        self.subordinate_to = subordinate_to
        if self.subordinate_to:
            if self.subordinate_to.syntactic is not self.syntactic:
                s = 'Tag "{}" does not mix with its master, "{}".'
                s = s.format(self, self.subordinate_to)
                raise self.TaggingError(s)

        # The sorting value is intended not to sort tags as such, but
        # to sort decks of cards for logical presentation.
        # This requires an override of the "sorting_keys" property of cards.
        self.sorting_value = sorting_value

    @property
    def semantic(self):
        return not self.syntactic


class SetOfTags(set):
    '''A set of tags, kept unique by the standard data type.

    Sorted alphabetically when refined to a string.

    '''
    def __str__(self):
        return ', '.join(sorted(self))

    def subset(self, selector_function):
        '''A (copied) subset of self, containing only filtered tags.'''
        return self.__class__(filter(selector_function, self))


class SetOfAdvancedTags(SetOfTags):
    '''Support for AdvancedTag features.'''

    def __init__(self, tags):
        super().__init__(tags)
        for t in self.subordinates:
            if t.subordinate_to not in self:
                s = 'Tag "{}" lacks master "{}".'
                raise Tag.TaggingError(s.format(t, t.subordinate_to))

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


class FieldOfTags(elements.CardContentField):
    '''A content field that uses a set of tags as a paragraph.'''

    key = keys.TAGS
    tag_class = Tag  # Expected to hold a registry of applicable tags.
    paragraph_class = SetOfTags

    def in_spec(self, content):
        '''Take an iterable of strings. Convert to tag objects.'''
        def _vet_string(string):
            for tag in self.tag_class.registry:
                if string == tag.key:
                    return tag

            s = 'Tag markup "{}" does not appear in roster.'
            raise Tag.TaggingError(s.format(string))

        self.append(self.paragraph_class({_vet_string(s) for s in content}))

    def not_in_spec(self):
        '''An empty tag list is still useful. Can be added to later.'''
        self.in_spec(())
