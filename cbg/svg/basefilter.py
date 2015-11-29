# -*- coding: utf-8 -*-
'''Base classes for SVG filter effects and filters. Used in the filter module.

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

import lxml.etree


class _Base():
    @property
    def id(self):
        raise NotImplementedError

    def to_svg_element(self):
        raise NotImplementedError


class Filter(_Base, list):
    '''A filter composed of filter effects, arrayed in a list.'''

    @property
    def id(self):
        return 'f_' + '_'.join(map(lambda x: x.id, self))

    def to_svg_element(self):
        e = lxml.etree.Element('filter', id=self.id)
        for child in self:
            e.append(child.to_svg_element())
        return e


class Effect(_Base, dict):
    '''Abstract superclass for filter effects (primitives).'''

    svg_name = None  # Mandatory filter effect name from SVG specifications.
    significant_attributes = ()

    @property
    def id(self):
        sa = self.significant_attributes
        values = (v for k, v in self.items() if k in sa or not sa)
        values = '-'.join(map(str, values)).replace(' ', '')
        return self.svg_name + values

    def to_svg_element(self):
        '''To be called from child class method.'''
        e = lxml.etree.Element(self.svg_name, id=self.id)
        for k, v in self.items():
            if v is not None:
                e.set(k, v)
        return e
