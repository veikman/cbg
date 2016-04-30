# -*- coding: utf-8 -*-
'''Basic shapes available in the SVG specification.'''

# This file is part of CBG.
#
# CBG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CBG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CBG.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2016 Viktor Eikman


import numpy

from cbg import misc
from cbg import geometry
from cbg.svg import svg


class Shape(svg.SVGElement):
    '''Base class for modelling SVG shapes.'''

    @classmethod
    def transformation_extension(cls, *args):
        '''Produce extra data needed for SVG transformations of an instance.

        The arguments to this method should be identical to the positional
        arguments needed to instantiate the same class.

        '''
        # In this default version, assume the first argument is a centerpoint,
        # hence directly useful for transformations.
        return args[0]


class Rect(Shape):
    '''A rectangle.'''

    TAG = 'rect'

    @classmethod
    def new(cls, position, size, rounding=None, **kwargs):
        kwargs['x'], kwargs['y'] = misc.rounded(position)
        kwargs['width'], kwargs['height'] = misc.rounded(size)

        if rounding is not None:
            kwargs['rx'] = kwargs['ry'] = misc.rounded(rounding)

        return super().new(**kwargs)

    @classmethod
    def from_presenter(cls, presenter, rounding=None):
        '''A convenience based on the CBG presenter API.'''
        t = presenter.wardrobe.mode.thickness
        rounding = t if rounding is True else rounding
        position, size = presenter.origin + t / 2, presenter.size - t
        center = cls.transformation_extension(position, size)
        attrib = presenter.wardrobe.to_svg_attributes(transform_ext=center)
        return cls.new(position, size, rounding=rounding, **attrib)

    @classmethod
    def transformation_extension(cls, position, size):
        return numpy.array(position) + numpy.array(size) / 2


class Circle(Shape):
    '''A circle.'''

    TAG = 'circle'

    @classmethod
    def new(cls, centerpoint, radius, **kwargs):
        kwargs['cx'], kwargs['cy'] = misc.rounded(centerpoint)
        kwargs['r'] = misc.rounded(radius)
        return super().new(**kwargs)


class Ellipse(Shape):
    '''An ellipse.'''

    TAG = 'ellipse'

    @classmethod
    def new(cls, centerpoint, radii, **kwargs):
        kwargs['cx'], kwargs['cy'] = misc.rounded(centerpoint)
        kwargs['rx'], kwargs['ry'] = misc.rounded(radii)
        return super().new(**kwargs)


class Line(Shape):
    '''A single-segment line.'''

    TAG = 'line'

    @classmethod
    def new(cls, point1, point2, **kwargs):
        kwargs['x1'], kwargs['y1'] = misc.rounded(point1)
        kwargs['x2'], kwargs['y2'] = misc.rounded(point2)
        return super().new(**kwargs)

    @classmethod
    def transformation_extension(cls, *points):
        return geometry.ListOfPoints(points).mean


class PolyLine(Shape):
    '''A multi-segment line.'''

    TAG = 'polyline'

    @classmethod
    def new(cls, points, **kwargs):
        coordinate_pairs = (','.join(misc.rounded(p) for p in points))
        kwargs['points'] = ' '.join(coordinate_pairs)
        return super().new(**kwargs)

    @classmethod
    def transformation_extension(cls, points):
        return geometry.ListOfPoints(points).mean


class Polygon(PolyLine):
    '''A polygon.'''

    TAG = 'polygon'
