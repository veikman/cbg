# -*- coding: utf-8 -*-
'''Terrain diagrams etc. on a grid layout.

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

from cbg.content import field


class Map(field.ContainerField):
    '''A two-dimensional grid forming a map.

    The map is stored as a numpy array. It would have been convenient for
    this class to inherit from cbg.geometry.Array, except that numpy
    arrays cannot be cleared, nor easily reshaped from a zero-dimensional
    shape, which is an appropriate (naturally false) default state
    awaiting specifications. Specifically, in a prototype of this class
    based on cbg.geometry.Array, attempting a self.resize from in_spec()
    triggered an exception:

        "cannot resize this array: it does not own its data".

    Owing to the zero-dimensional default, this could not be circumvented
    merely by setting data. The exception seems spurious. The prototype
    was abandoned on the assumption that the exception was an artifact
    of subclassing numpy.ndarray by the standard method.

    '''

    class Cell(field.Field):

        def in_spec(self, content):
            pass

        def __repr__(self):
            '''For use in the printing of maps to console (debugging).'''
            return '?'

    class Empty(Cell):
        def __repr__(self):
            return '.'

    def __init__(self):
        super().__init__()
        self.array = numpy.array(())

    def in_spec(self, shape):
        '''Stub out the shape with undefined values.

        numpy's "empty" is not used to represent empty cells. Subclasses
        must add content, including empty cell objects.

        '''
        self.array = numpy.empty(shape, dtype=numpy.object)

    @property
    def shape(self):
        '''Workaround for composition of array.'''
        return self.array.shape

    def __iter__(self):
        try:
            return numpy.nditer(self.array, flags=['refs_ok'])
        except ValueError:
            # Raised by numpy if the array is empty, i.e. no map in spec.
            return iter(())

    def __bool__(self):
        return bool(len(self.array))

    def __str__(self):
        return '{} map: {}'.format(self.shape, self.array)


class DefaultEmptyMap(Map):
    '''Empty map cells filling the whole area.'''
    def in_spec(self, shape):
        super().in_spec(shape)

        # Rather than using fill(), we instantiate individual emptinesses.
        for position in numpy.nditer(self.array,
                                     flags=['refs_ok'],
                                     op_flags=['writeonly']):
            position[...] = self.Empty()


class AreaOfEffect(DefaultEmptyMap):
    '''A diagram illustrating the shape and size of an affected area.

    The diagram is padded with a layer of empty cells, ideally cropped
    by a frame, fading over a gradient, or otherwise de-emphasized in
    rendering.

    '''

    class Affected(Map.Cell):
        def __repr__(self):
            return 'A'

    def in_spec(self, points):
        '''Take an iterable of Cartesian coordinate tuples: (x, y).

        Determine the effective origin of the coordinate system in the
        input and adjust for that when adding padding. The first padded
        cell will be (0, 0), and the first possibly affected cell will
        be (1, 1).

        '''
        min_x = min(map(lambda p: p[0], points))
        min_y = min(map(lambda p: p[1], points))
        max_x = max(map(lambda p: p[0], points))
        max_y = max(map(lambda p: p[1], points))

        # The bounding box is the difference on each axis + 1.
        # To that we add 2: 1 unit of padding on every side.
        shape = (max_y - min_y + 3, max_x - min_x + 3)
        super().in_spec(shape)

        for point in points:
            x, y = (numpy.array(point) - (min_x, min_y)) + (1, 1)
            self.array[y][x] = self.Affected()
