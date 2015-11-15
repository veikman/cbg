# -*- coding: utf-8 -*-
'''Largely abstract geometry for describing cards.

numpy is used here mainly for conveniences like matrix multiplication.

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

import cbg.misc as misc


class Array(numpy.ndarray):
    '''A point, area, grid system etc.

    This is just the bare minimum needed to subclass a numpy array for
    use as a convenient superclass elsewhere.

    '''

    def __new__(cls, data, *args, **kwargs):
        obj = numpy.asarray(numpy.array(data)).view(cls)
        return obj

    def __array_finalize__(self, obj):
        pass


class Rectangle(Array):
    '''A 2D surface area. In fact, a rectangle.

    In this class, the main array provided by the superclass represents the
    width × height footprint of the area as two numbers, typically in mm.

    '''

    class EdgePoint(Array):
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
        self.upper_left = self.EdgePoint(self * (0, 0), (1, 1))
        self.upper_right = self.EdgePoint(self * (1, 0), (-1, 1))
        self.lower_left = self.EdgePoint(self * (0, 1), (1, -1))
        self.lower_right = self.EdgePoint(self * (1, 1), (-1, -1))

    def corners(self):
        '''In clockwise order starting nearest to the geometric origin.

        1  2

        4  3

        '''
        return (self.upper_left, self.upper_right,
                self.lower_right, self.lower_left)

    def corner_offsets(self, offsets, x_first=False):
        '''A generator of 4 pairs of points, each at symmetric offsets.

        The offsets argument is expected to be a Point, or treatable as
        such, where the x coordinate is larger than the y coordinate.
        This produces a pattern like the following:

          2  3
        1      4

        8      5
          7  6

        Used to generate frames.

        '''
        for corner in self.corners():

            def new(coordinates):
                return self.EdgePoint(coordinates, corner.displacement_factors)

            x = corner.displaced(offsets)
            y = corner.displaced(offsets[::-1])  # Axes flipped to favour y.

            if x_first:
                yield new(x), new(y)
            else:
                yield new(y), new(x)

            x_first = not x_first
