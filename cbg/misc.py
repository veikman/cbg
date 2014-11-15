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

Copyright 2014 Viktor Eikman

'''

import collections


def listlike(object_):
    '''True if object_ is an iterable container.'''
    if (isinstance(object_, collections.Iterable)
            and not isinstance(object_, str)):
        return True
    return False
