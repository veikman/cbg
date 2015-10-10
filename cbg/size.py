# -*- coding: utf-8 -*-
'''Classes for card, page and font sizes.

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

import numpy

import cbg.keys as keys
import cbg.misc as misc


class Area():
    '''A 2D surface area. In fact, a rectangle.'''

    class Point(numpy.ndarray):
        '''A point in a coordinate system.

        This is a bare minimum needed to subclass a numpy array for
        the purpose. It's used here mainly to avoid having to override
        a huge amount of magic methods with reference to a composited
        array in order to have mathematical syntactic sugar.

        '''

        def __new__(cls, position, *args, **kwargs):
            obj = numpy.asarray(numpy.array(position, dtype=float)).view(cls)
            return obj

        def __array_finalize__(self, obj):
            pass

    class EdgePoint(Point):
        '''A point on the edge of an area.

        Instances can calculate displacement from their own position
        away from an implied starting edge, which is not actually
        represented by an object.

        '''
        def __init__(self, position, displacement_factors):
            '''Do not call superclass __init__.'''
            self.displacement_factors = displacement_factors

        def displaced(self, offsets):
            '''Produce a near-copy of self at stated offsets.

            Positive offsets move towards an implied area center, whereas
            negative offsets move away.

            '''
            pairs = zip(self.displacement_factors, misc.make_listlike(offsets))
            return self.__class__(self + [f * o for f, o in pairs],
                                  self.displacement_factors)

    def __init__(self, footprint):
        self.footprint = numpy.array(footprint)
        self.upper_left = self.EdgePoint(self.footprint * (0, 0), (1, 1))
        self.upper_right = self.EdgePoint(self.footprint * (1, 0), (-1, 1))
        self.lower_left = self.EdgePoint(self.footprint * (0, 1), (1, -1))
        self.lower_right = self.EdgePoint(self.footprint * (1, 1), (-1, -1))


class CardSize(Area):
    '''A card in millimetres.'''
    def __init__(self, footprint, border_outer, border_inner):
        super().__init__(footprint)
        self.outer = border_outer
        self.inner = border_inner

    def tilted(self):
        '''A copy flipped 90°.

        Used to make landscape versions of (normally) portrait card sizes.

        '''
        return self.__class__(numpy.flipud(self.footprint),
                              self.outer, self.inner)

    @property
    def interior_width(self):
        return self.footprint[0] - 2 * self.outer - 2 * self.inner


class PageSize(Area):
    '''A page in millimetres.'''
    def __init__(self, footprint, margins):
        super().__init__(footprint)
        self.margins = numpy.array(margins)


class FontSize():
    '''A set of properties shared by all fonts in a wardrobe.'''
    def __init__(self, base, stroke_factor=0.02,
                 line_height_factor=1.17, after_paragraph_factor=0.3):
        self.base = base
        self.stroke = stroke_factor * self.base
        self.line_height = line_height_factor * self.base
        self.after_paragraph = after_paragraph_factor * self.base

    def dict_svg(self):
        return {keys.STYLE: 'font-size:{};'.format(misc.rounded(float(self)))}

    def __int__(self):
        return int(self.base)

    def __float__(self):
        return float(self.base)
