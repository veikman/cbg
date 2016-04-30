# -*- coding: utf-8 -*-
'''SVG pathing abstraction.'''

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


import cbg.misc
from cbg.svg import svg


class Path(svg.SVGElement):
    '''A path, i.e. an arbitrary line or shape, as defined in SVG.'''

    TAG = 'path'

    class Pathfinder(list):
        '''A sequence of pathing steps. Used to create a Path.

        Refer to the SVG manual for details on appropriate parameters to
        each type of point.

        '''

        def _add(self, key, *new, absolute=False):
            if absolute:
                key = key.upper()
            self.append(key)
            for n in new:
                if cbg.misc.listlike(n):
                    for element in n:
                        self.append(element)
                else:
                    self.append(n)

        def moveto(self, *points, absolute=True):
            assert points
            self._add('m', *points, absolute=absolute)

        def closepath(self):
            self._add('z')

        def lineto(self, *points, absolute=True):
            assert points
            self._add('l', *points, absolute=absolute)

        def horizontal_lineto(self, *x, absolute=True):
            assert x
            self._add('h', *x, absolute=absolute)

        def vertical_lineto(self, *y, absolute=True):
            assert y
            self._add('v', *y, absolute=absolute)

        def curveto(self, *points, absolute=True):
            '''A cubic Bézier curve.

            In each set of three arguments, the first two are control points
            for the current position and the destination respectively, and
            the third is the destination itself.

            '''
            assert points
            assert not len(points) % 3
            self._add('c', *points, absolute=absolute)

        def smooth_curveto(self, *points, absolute=True):
            '''A cubic Bézier curve without the first control points(s).'''
            assert points
            assert not len(points) % 2
            self._add('s', *points, absolute=absolute)

        def quadratic_bezier_curveto(self, *points, absolute=True):
            assert points
            assert not len(points) % 2
            self._add('q', *points, absolute=absolute)

        def smooth_quadratic_bezier_curveto(self, *points, absolute=True):
            assert points
            self._add('t', *points, absolute=absolute)

        def elliptical_arc(self, *data, absolute=True):
            self._add('a', *data, absolute=absolute)

    @classmethod
    def new(self, data, **kwargs):
        '''Instantiate a path.

        The "data" argument typically refers to an instance of the
        Pathfinder class, populated beforehand through the use of its
        instance methods.

        '''
        assert data
        if not isinstance(data, str):
            data = ' '.join(map(str, data))

        return super().new(d=data, **kwargs)
