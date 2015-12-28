# -*- coding: utf-8 -*-
'''Terrain diagrams on a grid layout.

The classes in this module are designed to work from specifications
shaped like a 1-deep string-indexed unordered hash map of iterables of
two-dimensional coordinate pairs. In YAML it looks like this:

<keyword for grid field>:
  <keyword for content type A>:
     - <coordinate pair>
     - ...
  <keyword for content type B>:
     - ...

All named coordinate pairs exist on the map, but CBG will determine
an offset so that a full set of pairs like (10, 10), (10, 11) are
treated just like (0, 0), (0, 1), leaving no dead space on either
axis.

Each content type has its own field class, with its own presenter(s),
which will determine whether to fill each cell, draw a border around
multiple cells, connect cells with an arrow etc.

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

# TODO: Automatically populate maps from all (composited) cell subclasses.

# TODO: Permit a more graphical type of instruction, with single-character
# keys, for each layer of a map.


import numpy

from cbg.content import field
from cbg import geometry


class Map(field.BaseSpecifiableField, field.Array):
    '''A two-dimensional grid forming a map of e.g. RPG scene terrain.'''

    class ListOfIndirectPoints(geometry.ListOfPoints):
        '''A means of interpreting raw specifications.'''

        def __init__(self, specification):
            '''Capture all coordinate pairs that are to appear on the map.'''
            super().__init__()
            for content_type, coordinate_pairs in specification.items():
                self.extend(coordinate_pairs)

    class Cell(field.Atom):
        '''A piece of the map.'''

        def __repr__(self):
            '''For use in the printing of maps to console (debugging).

            It would be possible to reverse such operations, reading a
            layer of a map from text-based art.

            '''
            return '?'

    class Empty(Cell):
        '''Clear space on the map.'''

        def __repr__(self):
            return '.'

    # By default, the map will only be large enough to show its
    # specified contents, with no surrounding wall or lip of extra cells.
    cell_padding = 0

    def in_spec(self):
        '''Stub out the shape with undefined values.

        Subclasses must add content, including empty cell objects.

        '''
        points = self.ListOfIndirectPoints(self.specification)

        # Pad out appropriately.
        shape = tuple(map(lambda x: x + 2 * self.cell_padding, points.shape))
        self.resize(shape, refcheck=False)

        # Growth pads with zeros.
        self.fill(None)

    def __str__(self):
        return '{} map: {}'.format(self.shape, super().__str__())


class DefaultEmptyMap(Map):
    '''A map of nothing but empty space, by default.'''

    def in_spec(self):
        super().in_spec()

        # Rather than using fill(), we instantiate individual emptinesses.
        for position in self:
            position[...] = self.Empty()


class AreaOfEffect(DefaultEmptyMap):
    '''A diagram illustrating the shape and size of an affected area.'''

    # The diagram is padded with a layer of empty cells, ideally cropped
    # by a frame, fading over a gradient, or otherwise de-emphasized in
    # rendering.
    cell_padding = 1

    class Affected(Map.Cell):
        def __repr__(self):
            return 'A'

    def in_spec(self):
        super().in_spec()

        points = self.ListOfIndirectPoints(self.specification)
        offset = points.offset
        for point in points:
            x, y = numpy.array(point) + offset + self.cell_padding
            self[y][x] = self.Affected()
