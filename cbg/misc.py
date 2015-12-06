# -*- coding: utf-8 -*-
'''Miscellania.

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

import collections


def listlike(object_):
    '''True if object_ is an iterable container.'''
    if (isinstance(object_, collections.Iterable)
            and not isinstance(object_, str)):
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
