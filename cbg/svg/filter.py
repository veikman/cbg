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

Copyright 2014-2016 Viktor Eikman

'''

from cbg.svg import svg


class Filter(svg.IDElement):
    '''A filter composed of a sequence of filter effects.'''

    TAG = 'filter'
    _id_prefix = 'f'


class GaussianBlur(Filter):

    @classmethod
    def new(cls, horizontal=1, vertical=None, children=(), **attributes):
        blur = FEGaussianBlur.new(horizontal, vertical)
        return super().new(children=(blur,) + children, **attributes)


class Feather(GaussianBlur):

    @classmethod
    def new(cls, **kwargs):
        children = (FEComposite.new(in1='SourceGraphic', in2='blur',
                                    operator='atop', result='composite1'),
                    FEComposite.new(in2='composite1', operator='in',
                                    result='composite2'),
                    FEComposite.new(in2='composite2', operator='in',
                                    result='composite3'),
                    )
        return super().new(children=children, **kwargs)


class FEComposite(svg.SVGElement):
    '''Because "in" is an invalid attribute name in Python, "in1" is used.'''

    TAG = 'feComposite'
    _id_prefix = 'feC'

    @classmethod
    def new(cls, in1=None, **kwargs):
        if in1 is not None:
            kwargs['in'] = in1
        return super().new(**kwargs)


class FEGaussianBlur(svg.SVGElement):

    TAG = 'feGaussianBlur'
    _id_prefix = 'feGB'
    _id_attribute_blacklist = {'result'}

    @classmethod
    def new(cls, horizontal, vertical=None, **kwargs):
        if vertical is None:
            stdev = str(horizontal)
        else:
            stdev = ' '.join(map(str, (horizontal, vertical)))

        return super().new(stdDeviation=stdev, result='blur', **kwargs)
