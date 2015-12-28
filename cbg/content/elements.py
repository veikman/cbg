# -*- coding: utf-8 -*-
'''Various types of content included on a playing card.

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

Copyright 2014-2016 Viktor Eikman

'''

import itertools

import cbg.misc
import cbg.keys


class Presentable():
    '''Superclass for content owners that can be represented visually.

    Separate SVG presenter classes can be specified for the different sides
    of a card.

    '''

    presenter_class_front = None
    presenter_class_back = None

    def __init__(self):
        # Depending on content, it may be desirable to adjust the size
        # an element will take up when presented. As size is normally a
        # property of each presenter class, an override needs to happen
        # at the individual level. It also needs to be known in
        # layouting, i.e. before instantiation of presenters, in order
        # to place neighbouring elements correctly.
        self.presenter_size_override = None


class DerivedFromSpec():
    '''Superclass for anything that parses complex raw text specifications.

    The properties of subclasses are derived from plain-text specifications
    using text keys. Some keys are defined here, so that localization
    (of specifications) can be achieved by overwriting these keys in
    custom classes.

    Support for additional keys is achieved by subclassing CardContentField.

    '''

    class SpecificationError(ValueError):
        '''Used to signal unmet formal expectations.'''
        pass

    # Canonical specification keywords:
    key_metadata = cbg.keys.METADATA
    key_data = cbg.keys.DATA

    key_copies = cbg.keys.COPIES
    key_defaults = cbg.keys.DEFAULTS
    key_tags = cbg.keys.TAGS
    key_title = cbg.keys.TITLE

    # Conveniences for uniquely named items with no proper title:
    _untitled_base = 'untitled'
    _untitled_iterator = itertools.count(start=1)

    def _generate_title(self):
        '''Create a hitherto unused title. Useful mainly for hash maps.'''
        return '{} {}'.format(self._untitled_base,
                              next(self._untitled_iterator))
