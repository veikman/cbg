# -*- coding: utf-8 -*-
'''Modelling of SVG transformation operations.

The creation of the "transform" SVG attribute is handled in the wardrobe
module.

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


class _Transformation(list):
    name = None

    def __init__(self, *args, extended_locally=False):
        self._extended_locally = extended_locally
        super().__init__(args)

    def to_string(self, extension=None):
        data = self[:]
        if self._extended_locally and extension is not None:
            # Complement data with the stated coordinates. Not doing so is
            # legal in SVG, and therefore raises no exception here.
            data.extend(extension)
        return '{}({})'.format(self.name, ','.join(map(str, data)))


class Matrix(_Transformation):
    name = 'matrix'

    def __init__(self, a=1, b=0, c=0, d=1, e=0, f=0):
        super().__init__(a, b, c, d, e, f)


class Translate(_Transformation):
    name = 'translate'

    def __init__(self, x=0, y=0):
        super().__init__(x, y)


class Scale(_Transformation):
    name = 'scale'

    def __init__(self, x=1, y=None):
        super().__init__(x, x if y is None else y)


class Rotate(_Transformation):
    name = 'rotate'

    def __init__(self, a, x=None, y=None):
        if x is None and y is None:
            # This is legal in SVG, but means rotation about the origin.
            # Rotation about the origin of the coordinate system
            # is inherently undesirable for creating printable cards.
            # A hook is created for supplying coordinates later.
            super().__init__(a, extended_locally=True)
        elif x is not None and y is not None:
            # Rotate around the specified point, ignoring later extension.
            super().__init__(a, x, y)
        else:
            s = 'Rotation around a point requires x and y coordinates.'
            raise ValueError(s)


class SkewX(_Transformation):
    name = 'skewX'

    def __init__(self, a):
        super().__init__(a)


class SkewY(_Transformation):
    name = 'skewY'

    def __init__(a):
        super().__init__(a)
