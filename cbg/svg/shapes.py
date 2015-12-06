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


class Rect(svg.SVGElement):
    '''A rectangle.'''

    TAG = 'rect'

    @classmethod
    def new(cls, position, size, rounding=None, wardrobe=None, **kwargs):
        kwargs['x'], kwargs['y'] = misc.rounded(position)
        kwargs['width'], kwargs['height'] = misc.rounded(size)

        if rounding is not None:
            kwargs['rx'] = kwargs['ry'] = misc.rounded(rounding)

        if wardrobe is not None:
            kwargs.update(wardrobe.dict_svg_fill())

        return super().new(**kwargs)
