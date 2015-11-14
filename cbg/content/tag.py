# -*- coding: utf-8 -*-
'''Tag support for cards. A tag is a short phrase for categorization.

Any property of a card that does not require unique or elaborate
text on the card can be reduced to a tag. The tag itself would have to
be explained elsewhere.

Tags can also be used inside CBG applications, to drive programmatic
logic. For example, the choice of color scheme for a card, or the text
on its back, can be a result of its tags.

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
import cbg.misc
from cbg.content import field


class Tag(field.Paragraph):
    '''A word or phrase used to provide categorical information.

    Unlike regular paragraphs, a tag needs to be defined with a key on
    initialization, as a means of controlling for misspelled tags in specs,
    and to enable some special features of tags in the AdvancedTag
    subclass.

    '''

    registry = dict()

    class TaggingError(Exception):
        '''Used to signal contradictory content.'''
        pass

    def __init__(self, key):
        '''Register a unique tag.'''
        super().__init__(content=key)

        # Automatically keep track of which tags have been created for
        # a game, as a roster for specification recognition.
        if key in self.registry:
            raise self.TaggingError('"{}" defined more than once.'.format(key))
        self.registry[key] = self

    @classmethod
    def get(cls, key):
        '''Act like a dictionary. Check raw content against tag roster.'''
        try:
            return cls.registry[key]
        except KeyError as e:
            s = 'Tag markup "{}" does not appear in roster.'
            raise cls.TaggingError(s.format(key)) from e

    def __lt__(self, other):
        '''Tags sort alphabetically.'''
        return str(self) < str(other)


class TagField(field.ContainerList):
    '''A content field that uses a set of tags as its sole paragraph.

    A tag field is intended to programmatically expandable as part of
    the logic of a CBG application.

    '''

    key = keys.TAGS
    content_class = Tag  # Expected to support Tag's "get()" API.

    def in_spec(self, content):
        '''Take an iterable of strings. Convert to tag objects.

        May be called several times.

        '''
        for key in cbg.misc.make_listlike(content):
            self.append(self.content_class.get(key))
        self.sort()

    def not_in_spec(self):
        '''An empty tag list is still useful.'''
        self.in_spec(())

    def as_set(self, selector_function=lambda t: True):
        '''A subset of tags in the field.'''
        return set(filter(selector_function, self))

    def as_string(self, selection):
        '''Meant to be overridden, as for CBG's advanced tags.

        This method is intended to be called directly when different
        kinds of tags are to be printed on different parts of a card,
        hence the "selection" argument.

        '''
        return ', '.join(map(str, selection)).capitalize()

    def __str__(self):
        return self.as_string(self)


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

        # A syntactic tag in a game would commonly be something like
        # "reaction" or "phase 1". A non-syntactic tag is treated as
        # semantic, typically "animal", "item", etc. This categorization
        # will obviously not be meaningful in every game. Consider it
        # an example of something you can do with the base class.
        self.syntactic = syntactic

        # A non-printing tag is invisible on cards. Use it to sort decks
        # or for arbitrary logic.
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


class AdvancedTagField(TagField):
    '''Support for AdvancedTag features.'''

    content_class = AdvancedTag

    def in_spec(self, raw):
        super().in_spec(raw)
        for t in self.subordinates:
            if t.subordinate_to not in self:
                s = 'Tag "{}" lacks master "{}".'.format(t, t.subordinate_to)
                raise self.content_class.TaggingError(s)

    @property
    def syntactic(self):
        return self.as_set(lambda t: t.syntactic)

    @property
    def semantic(self):
        return self.as_set(lambda t: t.semantic)

    @property
    def subordinates(self):
        return self.as_set(lambda t: t.subordinate_to)

    @property
    def masters(self):
        '''Tags with subordinates actually present in the field.'''
        return {t.subordinate_to for t in self.subordinates}

    def as_string(self, selection):
        '''An override.

        An example of a meaningful selection would be self.semantic,
        to produce a string of semantic tags only.

        '''
        return super().as_string(self._generate_strings(selection))

    def _generate_strings(self, selection):
        '''Hide non-printing tags and group masters with their subordinates.'''
        for t in sorted(selection):
            if t not in self or t.subordinate_to or not t.printing:
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

            yield s
