# -*- coding: utf-8 -*-
'''Basic shapes available in the SVG specification.

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

from cbg import misc
from cbg.svg import svg


class _Shape(svg.SVGElement):
    '''Basic shape superclass.'''

    @classmethod
    def new(cls, wardrobe=None, **kwargs):
        if wardrobe is not None:
            kwargs.update(wardrobe.dict_svg_fill())

        return super().new(**kwargs)


class Rect(_Shape):
    '''A rectangle.'''

    TAG = 'rect'

    @classmethod
    def new(cls, position, size, rounding=None, **kwargs):
        kwargs['x'], kwargs['y'] = misc.rounded(position)
        kwargs['width'], kwargs['height'] = misc.rounded(size)

        if rounding is not None:
            kwargs['rx'] = kwargs['ry'] = misc.rounded(rounding)

        return super().new(**kwargs)


class Circle(_Shape):
    '''A circle.'''

    TAG = 'circle'

    @classmethod
    def new(cls, centerpoint, radius, **kwargs):
        kwargs['cx'], kwargs['cy'] = misc.rounded(centerpoint)
        kwargs['r'] = misc.rounded(radius)
        return super().new(**kwargs)


class Ellipse(_Shape):
    '''An ellipse.'''

    TAG = 'ellipse'

    @classmethod
    def new(cls, centerpoint, radii, **kwargs):
        kwargs['cx'], kwargs['cy'] = misc.rounded(centerpoint)
        kwargs['rx'], kwargs['ry'] = misc.rounded(radii)
        return super().new(**kwargs)


class Line(_Shape):
    '''A single-segment line.'''

    TAG = 'line'

    @classmethod
    def new(cls, point1, point2, **kwargs):
        kwargs['x1'], kwargs['y1'] = misc.rounded(point1)
        kwargs['x2'], kwargs['y2'] = misc.rounded(point2)
        return super().new(**kwargs)


class PolyLine(_Shape):
    '''A multi-segment line.'''

    TAG = 'polyline'

    @classmethod
    def new(cls, points, **kwargs):
        coordinate_pairs = (','.join(misc.rounded(p) for p in points))
        kwargs['points'] = ' '.join(coordinate_pairs)
        return super().new(**kwargs)


class Polygon(PolyLine):
    '''A polygon.'''

    TAG = 'polygon'
