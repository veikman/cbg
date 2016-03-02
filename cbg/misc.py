# -*- coding: utf-8 -*-
'''Miscellania.'''

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


###########
# IMPORTS #
###########


import collections
import logging


#####################
# INTERFACE CLASSES #
#####################


class Compass():
    '''A simple container of something for each cardinal direction.

    Used, for instance, for padding.

    This could have been a namedtuple, but they're not editable.

    '''

    def __init__(self, *args):
        '''Interpret arguments as for CSS shorthand properties like padding.'''

        if len(args) == 1:
            args = 4 * args
        elif len(args) == 2:
            args = (args[0], args[1], args[0], args[1])
        elif len(args) == 3:
            args = (args[0], args[1], args[2], args[1])

        try:
            self.top, self.right, self.bottom, self.left = args
        except:
            s = 'Invalid number of arguments: {} {}.'
            raise ValueError(s.format(len(args), args))

    @property
    def horizontal(self):
        return self.left + self.right

    @property
    def vertical(self):
        return self.top + self.bottom

    @property
    def reduction(self):
        return (self.horizontal, self.vertical)


class Formattable():
    '''Anything that can reformat source material for presentation.'''

    @classmethod
    def format_text(cls, content):
        '''Convert from e.g. integer in YAML specs to a presentable string.

        This method is intended to be overridden for the integration
        of a string templating system.

        '''
        return str(content)


class SearchableTree():
    '''Search fundamentals for fields and their presenters, etc.

    Upward search requires a "parent" attribute, while downward search
    requires iterability. A one-to-many tree structure is thus presupposed.

    '''

    def _search_single(self, hit_function, down=False):
        '''Recursive search for a single field in the tree structure.'''

        if hit_function(self):
            return self

        if down:
            for child in self:
                try:
                    ret = child._search_single(hit_function, down=down)
                    if ret is not None:
                        return ret
                except AttributeError:
                    '''Assume irrelevant, non-searchable content.'''
                    pass
        else:
            if self.parent is None:
                s = 'Tree search failed: Reached {}, which has no parent.'
                raise AttributeError(s.format(type(self)))

            return self.parent._search_single(hit_function, down=down)


#######################
# INTERFACE FUNCTIONS #
#######################


def listlike(object_):
    '''True if object_ is an iterable container.'''
    if (isinstance(object_, collections.Iterable) and
            not isinstance(object_, str)):
        return True
    return False


def make_listlike(object_):
    '''Package object in a tuple if not already listlike.

    The purpose of this is to permit both lists and simple
    strings in YAML markup, for most field types.

    '''
    if listlike(object_):
        return object_
    return (object_,)


def rounded(value):
    '''Round off numbers, for e.g. SVG output.

    Coordinate pairs etc. are reduced to 0.1 µm accuracy for readability.

    Measurements are also converted to strings, as a convenience for
    working with lxml.

    '''
    if listlike(value):
        return [rounded(axis) for axis in value]
    return str(round(value, 4))
