# -*- coding: utf-8 -*-
'''Basic SVG production conveniences.

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


class SVGElement(lxml.etree.ElementBase):
    '''A Python proxy class for the production of SVG code.

    One instance of this class corresponds to one SVG element, but only
    production is supported. CBG cannot load XML files, and cannot
    create instances of this class from XML.

    The TAG attribute, whose name is mandated by lxml, must be populated
    by a subclass.

    '''

    # XML element tag (name), e.g. "rect" for a basic SVG rectangle.
    TAG = ''

    # _id_prefix is preferred over TAG when generating an ID attribute.
    _id_prefix = ''

    # _id_attribute_blacklist should be populated for element types that
    # will need an "id" attribute generated, yet which will commonly
    # have attributes irrelevant to a useful ID.
    _id_attribute_blacklist = set()

    @classmethod
    def new(cls, children=None, set_id=False, **attributes):
        '''Create a new instance, configured with convenient logic.

        This class method should be called in preference to instantiating
        the class directly, because lxml.etree.Element is just a thin
        Python proxy over a C library, and the official lxml documentation
        deprecates any overriding of its __init__() or __new__(). The
        official substitute, _init(), is inappropriate for the level of
        convenience CBG aims to provide.

        '''
        if not cls.TAG:
            s = 'SVG element class {} has no tag name.'
            raise NotImplementedError(s.format(cls.__name__))

        instance = cls(**attributes)

        if children:
            for c in children:
                instance.append(c)

        if set_id:
            instance.set_id()

        return instance

    def set_id(self):
        '''Generate and set a representative SVG "id" attribute.

        A means of up-to-date reflection of contents likely to differ
        from one instance of the class to another.

        Intended primarily for use with the "defs" section of an SVG
        document, and further intended to avoid unnecessary duplicates
        in that section.

        '''
        id_ = self.make_id()
        self.set('id', id_)
        return id_

    def make_id(self):
        '''Generate a string for use as an "id" attribute.'''
        return '_'.join(filter(lambda x: x,
                               (self._make_id_base(), self._make_id_salient(),
                                self._make_id_recursive())))

    def _make_id_recursive(self):
        return '_'.join(map(lambda x: x.make_id(), self))

    def _make_id_salient(self):
        blist = {'id'}.union(set(self._id_attribute_blacklist))
        values = tuple((v for k, v in self.attrib.items() if k not in blist))
        if values:
            return '-'.join(map(str, values)).replace(' ', '')
        return ''

    def _make_id_base(self):
        return self._id_prefix or self.tag


class IDElement(SVGElement):
    '''A very minor tweak to set an ID by default.'''

    @classmethod
    def new(cls, set_id=True, **attributes):
        return super().new(set_id=set_id, **attributes)
