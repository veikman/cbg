# -*- coding: utf-8 -*-
'''Filter effect and filter generators.

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

from cbg.svg import basefilter


class GaussianBlur(basefilter.Filter):
    def __init__(self, horizontal=1, vertical=None):
        fe = FEGaussianBlur(horizontal, vertical)
        super().__init__((fe,))


class Feather(GaussianBlur):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.append(FEComposite(in1='SourceGraphic', in2='blur',
                                operator='atop', result='composite1'))
        self.append(FEComposite(in2='composite1', operator='in',
                                result='composite2'))
        self.append(FEComposite(in2='composite2', operator='in',
                                result='composite3'))


class FEComposite(basefilter.Effect):
    '''Because "in" is an invalid attribute name in Python, "in1" is used.'''

    svg_name = 'feComposite'
    significant_attributes = ('in', 'in2', 'operator', 'k1', 'k2', 'k3', 'k4')

    def __init__(self, in1=None, **kwargs):
        if in1 is not None:
            kwargs['in'] = in1
        super().__init__(**kwargs)


class FEGaussianBlur(basefilter.Effect):
    svg_name = 'feGaussianBlur'
    significant_attributes = ('stdDeviation',)

    def __init__(self, horizontal, vertical=None):
        if vertical is None:
            stdev = str(horizontal)
        else:
            stdev = ' '.join(map(str, (horizontal, vertical)))

        super().__init__(stdDeviation=stdev, result='blur')
