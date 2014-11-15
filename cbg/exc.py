# -*- coding: utf-8 -*-
'''All exceptions in the package.

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


class SpecificationError(Exception):
    '''A human error in the design of a specification for a deck.'''
    pass


class MarkupError(SpecificationError):
    '''Failure to parse CBG-specific markup.'''
    pass


class PageFull(Exception):
    '''Not an error. Footprint cannot be fitted into current page layout.'''
    pass


class PrintableAreaTooSmall(Exception):
    '''Footprint too large for page type. Layout impossible.'''
    pass
