# -*- coding: utf-8 -*-
'''Miscellaneous elements from SVG specifications.'''

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


from cbg.svg import svg
import cbg.misc


class Image(svg.SVGElement):
    '''An embedded image. Not to be confused with the SVG document root.'''

    TAG = 'image'

    @classmethod
    def new(cls, position, size, content_path, **kwargs):
        kwargs['x'], kwargs['y'] = cbg.misc.rounded(position)
        kwargs['width'], kwargs['height'] = cbg.misc.rounded(size)
        kwargs['{{{}}}href'.format(svg.NAMESPACE_XLINK)] = content_path
        return super().new(**kwargs)


class Text(svg.SVGElement):
    '''Printed text content on a card.

    A text argument when instantiating this class is not mandatory,
    because empty SVG text elements are surprisingly convenient.

    '''
    TAG = 'text'

    class Span(svg.SVGElement):
        TAG = 'tspan'

    @classmethod
    def new(cls, position, **kwargs):
        kwargs['x'], kwargs['y'] = cbg.misc.rounded(position)
        return super().new(transform_ext_auto=position, **kwargs)


class Mask(svg.IDElement):
    TAG = 'mask'
    _id_prefix = 'm'


class ClipPath(svg.IDElement):
    TAG = 'clipPath'
    _id_prefix = 'cP'
