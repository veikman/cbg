# -*- coding: utf-8 -*-
'''Tag support for cards. A tag is a short phrase for categorization.

Any property of a card that does not require unique or elaborate
text on the card can be reduced to a tag. The tag itself would have to
be explained elsewhere.

Tags can also be used inside CBG applications, to drive programmatic
logic. For example, the choice of color scheme for a card, or the text
on its back, can be a result of its tags.

An application may need several subclasses of any of the types of tags
presented here. For instance, a syntactic subclass and a semantic one.
A syntactic tag in a game would commonly be something like "reaction"
or "phase 1". A semantic tag, drawn elsewhere, would typically be
"animal", "item", etc. For such a system to retain its programmatic
value, the "tags" convenience method on card objects will typically
be overridden to combine the fields for different types of tags.

'''

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


import cbg.misc
import cbg.keys as keys
from cbg.content import field


class BaseTag(cbg.misc.Formattable):
    '''A word or phrase used to categorize cards.

    Creatable directly from text specifications, as it is little more
    than a string polymorphable to its more advanced inheritors.

    '''

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return self.format_text(self.key)

    def __lt__(self, other):
        '''Tags sort alphabetically.'''
        return str(self) < str(other)

    @classmethod
    def get(cls, key):
        '''No retrieval. Instantiate a new object.'''
        return cls(key)


class RegisteredTag(BaseTag):
    '''A tag checked against a roster, created before reading specs.

    Unlike regular paragraphs, and basic tags, a tag of this class needs
    to be defined with a key before reading specs. This is a means of
    controlling for misspelled tags in the specs.

    '''

    registry = dict()

    class TaggingError(Exception):
        '''Used to signal contradictory content.'''
        pass

    def __init__(self, key):
        '''Register a unique tag.'''
        if key in self.registry:
            raise self.TaggingError('"{}" defined more than once.'.format(key))

        super().__init__(key)

        self.registry[key] = self

    @classmethod
    def get(cls, key):
        '''Act like a dictionary. Check raw content against roster.'''
        try:
            return cls.registry[key]
        except KeyError as e:
            s = 'Tag markup "{}" does not appear in roster.'
            raise cls.TaggingError(s.format(key)) from e


class AdvancedTag(RegisteredTag):
    '''An example of an advanced type of tag with extra features.

    This advanced tag can be hierarchically related, weighted for
    sorting, and explicitly named.

    This class of tag can also be non-printing. Such tags should
    be ignored by graphical presenters.

    '''

    def __init__(self, key, full_name=None, printing=True,
                 subordinate_to=None, sorting_value=0):
        super().__init__(key)

        self.full_name = self.key if full_name is None else full_name

        # A non-printing tag is invisible on cards. Use it to sort decks
        # or for arbitrary logic.
        self.printing = printing

        self.subordinate_to = subordinate_to

        # The sorting value is intended not to sort tags as such, but
        # to sort decks of cards for logical presentation.
        # This requires an override of the "sorting_keys" property of cards.
        self.sorting_value = sorting_value

    def __str__(self):
        return self.format_text(self.full_name)


class BaseTagField(field.AutoField):
    '''A set of tags.'''

    key = keys.TAGS
    plan = [BaseTag]

    def in_spec(self):
        '''An override to check against the tag roster.'''
        for element in self.specification:
            self.append(self.plan[0].get(element))

    def as_set(self, selector_function=lambda t: True):
        '''A subset of tags in the field.'''
        return set(filter(selector_function, self))

    def as_string(self, selection):
        '''Meant to be overridden, as for CBG's advanced tags.

        This method is intended to be called directly when different
        kinds of tags are to be printed on different parts of a card,
        hence the "selection" argument.

        '''
        s = ', '.join(map(str, selection))

        try:
            i = s[0].upper()
        except IndexError:
            return ''

        try:
            return i + s[1:]
        except IndexError:
            return i

    def append(self, item):
        '''An override to ensure sorting.

        A tag field is intended to be expandable after absorbing its
        raw specification, as part of the logic of a CBG application.

        '''
        super().append(item)
        self.sort()

    def __str__(self):
        return self.as_string(self)


class RegisteredTagField(BaseTagField):

    plan = [RegisteredTag]


class AdvancedTagField(RegisteredTagField):

    plan = [AdvancedTag]

    def in_spec(self):
        super().in_spec()
        for t in self:
            if t.subordinate_to and t.subordinate_to not in self:
                s = 'Tag "{}" lacks master "{}".'.format(t, t.subordinate_to)
                raise self.plan[0].TaggingError(s)

    @property
    def subordinates(self):
        return self.as_set(lambda t: t.subordinate_to)

    @property
    def masters(self):
        '''Tags with subordinates actually present in the field.'''
        return {t.subordinate_to for t in self.subordinates}

    def as_string(self, selection):
        '''An override.'''
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
