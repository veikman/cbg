# -*- coding: utf-8 -*-
'''Wrappers for SVG transformation operations.

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


class Transformer(list):
    '''A list of standard SVG transformations to apply.'''

    class Transformation(list):
        def __init__(self, name, *args, extended_locally=False):
            self._name = name
            self._extended_locally = extended_locally
            super().__init__(args)

        def to_string(self, position):
            data = self[:]
            if self._extended_locally and position is not None:
                data.extend(position)
            return '{}({})'.format(self._name, ','.join(map(str, data)))

    def _new(self, *args, **kwargs):
        self.append(self.Transformation(*args, **kwargs))

    def matrix(self, a=1, b=0, c=0, d=1, e=0, f=0):
        self._new('matrix', a, b, c, d, e, f)

    def translate(self, x=0, y=0):
        self._new('translate', x, y)

    def scale(self, x=1, y=None):
        self._new('scale', x, x if y is None else y)

    def rotate(self, a, x=None, y=None):
        if x is None and y is None:
            # Rotation about the origin of the coordinate system
            # is inherently undesirable for creating printable cards.
            # Therefore, a hook is created for rotating about self.
            self._new('rotate', a, extended_locally=True)
        elif x is not None and y is not None:
            self._new('rotate', a, x, y)
        else:
            raise ValueError('Rotation around a point requires x and y.')

    def skew_x(self, a):
        self._new('skewX', a)

    def skew_y(self, a):
        self._new('skewY', a)

    def attrdict(self, position=None):
        if self:
            iterable = (t.to_string(position) for t in self)
            return {'transform': ' '.join(iterable)}
        return {}
