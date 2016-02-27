# -*- coding: utf-8 -*-
'''Fields of content included on a playing card.'''

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


import logging
import itertools

import numpy

import cbg.misc
import cbg.keys
import cbg.geometry
from cbg.content import elements


class BaseField(cbg.misc.SearchableTree, elements.Presentable):
    '''Abstract base class for organizing content on a type of card.

    Used to create classes to represent layouting contrivances as well as
    as direct containers.

    '''

    # A key is needed if contents are to be found in specs.
    key = None

    # A plan is needed if contents are to be contained by the field.
    # A plan is an iterable of field-like classes.
    plan = ()

    def __init__(self, specification=None, parent=None):
        super().__init__()

        self.specification = specification
        self.parent = parent

        self.layout()

    def layout(self):
        raise NotImplementedError

    def child_by_key(self, key):
        return self._search_single(lambda c: c.key == key, down=True)

    def child_by_key_required(self, key):
        ret = self.child_by_key(key)

        if ret is None:
            s = 'No such field on "{}": {}.'
            raise KeyError(s.format(self, key))

        return ret

    @property
    def tags(self):
        '''Search for a tag field on the card. Return it or raise a KeyError.

        In this implementation we rely upon the parent overriding this
        method.

        In the basic application model, users can filter cards based
        on this attribute.

        '''
        return self.parent.tags

    @property
    def card(self):
        '''Find an ancestor without a parent: presumably a card.'''
        return self._search_single(lambda f: f.parent is None)


class Atom(BaseField):
    '''A minimal usable field.

    This class is typically employed for details of a card layout,
    like an individual tile on a map, as seen in the grid module.

    '''

    def layout(self):
        '''A text specification is not expected, and will be ignored.'''
        pass

    def _search_single(self, hit_function, **kwargs):
        '''Recursive search for a single field in the tree structure.

        An override.

        '''
        if hit_function(self):
            return self


class BaseSpecifiableField(BaseField):
    '''A field that reacts to text specifications for each card type.

    '''

    def layout(self):
        if self.specification is None:
            self.not_in_spec()
        else:
            self.in_spec()

    def in_spec(self):
        '''Behaviour when the field's key is found in the raw specification.

        Generally, a detail of the specification is interpreted here,
        which may include implications for other parts of the card.

        For example, the mere presence of data for a specific field can
        imply a tag, which needs to be put in a different field. That
        would be the case if, for example, the card can be used to
        perform an action if there is a populated action field, and
        that implies that the card should also be decorated with an
        action tag. The tagging can be handled here, for the action
        field, by searching for the tag field via self.parent.
        Alternately, it can be handled at a higher level, such as the
        card level.

        '''
        raise NotImplementedError

    def not_in_spec(self):
        '''Behaviour when the raw specification does not mention the field.'''
        pass

    def instantiate_content_class(self, cls, specification):
        '''Encapsulate subordinate content in a child object.

        The child content class is not assumed to conform to the field
        API, unless it descends from BaseField. This is a convenience
        designed to allow arbitrary child classes.

        '''
        if issubclass(cls, BaseField):
            return cls(specification=specification, parent=self)
        else:
            return cls(specification)


class ArbitraryContainer(BaseSpecifiableField):
    '''A field for content that isn't easily subdivided.'''

    def layout(self, *args, **kwargs):
        self.content = None
        super().layout(*args, **kwargs)

    def in_spec(self):
        try:
            content_class = self.plan[0]
        except IndexError:
            content_class = None

        if content_class:
            self.content = self.instantiate_content_class(content_class,
                                                          self.specification)
        else:
            self.content = self.specification

    def __iter__(self):
        '''Act like a list of one object. For searchability.'''
        return iter((self.content,))


class _NaturalContainer(BaseSpecifiableField):
    '''Base class for basic API compatibility with ArbitraryContainer.'''

    @property
    def content(self):
        '''Defined for forwards API compatibility with ArbitraryContainer.'''
        return self


class List(BaseField, list):
    '''A one-dimensional array of subordinate fields.'''


class Array(BaseField, cbg.geometry.ObjectArray):
    '''A multi-dimensional array of subordinate fields.'''

    def __iter__(self):
        try:
            return numpy.nditer(self,
                                flags=['refs_ok'], op_flags=['readwrite'])
        except ValueError:
            # Raised by numpy if the array is empty.
            return iter(())

    def __bool__(self):
        return self.specification is not None


class Layout(BaseSpecifiableField, List):
    '''A field structured according to a plan independent of content.

    This field does not consume parts of the spec, merely passing them
    down to the members of its plan.

    '''

    def in_spec(self):
        '''All the work from terse specs to complete contents.'''

        if not self.plan:
            s = 'No contents planned for {}.'
            logging.error(s.format(self))

        for cls in self.plan:

            if cls.key:
                # Cut out the indicated part of the specification.
                try:
                    child_spec = self.specification.pop(cls.key, None)
                except AttributeError:
                    s = ('Cannot pop by key from {} specification "{}" '
                         'for field class {}.')
                    logging.error(s.format(type(self.specification).__name__,
                                           self.specification,
                                           type(self).__name__))
                    raise
            else:
                # Pass on the entire specification, to be modified by children:
                # lower-level layout fields etc. It's done this way to enable
                # easy moving of fields from the top to the bottom of a card
                # by moving them between different layouters' plans.
                child_spec = self.specification

            try:
                self.append(cls(specification=child_spec, parent=self))
            except:
                s = 'An error occurred while laying out {}.'
                logging.error(s.format(cls))
                raise

    @property
    def tags(self):
        '''Find a container with a tags field.

        Return such a field or throw a KeyError.

        A tags field is identified by the standard CBG tags key.

        The reason why this isn't implemented as a simpler method on
        cards alone is that, in the case of nested Layout fields, a
        parent container, such as the card, does not obtain a reference
        to each child container until it is fully instantiated. This
        makes it possible for a grandchild to call its card looking for
        a tag field instantiated by an intermediate container (the
        parent) still under construction. In this example the
        grandchild will find the card apparently empty. So instead of
        calling the card, we gradually seek upwards.

        '''
        def has_tags_field(field):
            return field.child_by_key(cbg.keys.TAGS) is not None

        field_with_tags = self._search_single(has_tags_field)
        if field_with_tags is None:
            s = 'No tag field visible from "{}" looking up the tree.'
            raise KeyError(s.format(self))
        else:
            return field_with_tags.child_by_key_required(cbg.keys.TAGS)


class AutoField(_NaturalContainer, List):

    def in_spec(self):
        '''Create one child for each discrete element of the specification.

        If there are multiple classes available in the plan, cycle over
        them.

        '''
        if not self.plan:
            s = '{} has no class for encapsulation of its content.'
            raise NotImplementedError(s.format(self.__class__))

        for cls, element in zip(itertools.cycle(self.plan),
                                cbg.misc.make_listlike(self.specification)):
            self.append(self.instantiate_content_class(cls, element))
