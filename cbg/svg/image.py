# -*- coding: utf-8 -*-
'''A module for arranging SVG graphics at the top level, as an image.'''

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


import lxml

import cbg.misc
from cbg.svg import svg
from cbg.sample import size


class SVG(cbg.misc.SearchableTree, svg.SVGElement):
    '''An SVG image document root.

    This class represents a complete SVG image, using the "svg" tag
    and forming the root element of an SVG XML document. It is not
    related to the SVG element type tagged "image", which is modelled
    in cbg.svg.misc.

    '''

    TAG = 'svg'

    class Definitions(svg.SVGElement):
        '''An SVG convention.

        Filters etc. are defined in a "defs" element, which makes them
        invisible.

        '''
        TAG = 'defs'

    @classmethod
    def new(cls, dimensions=size.A4, **kwargs):
        '''Create an image.'''

        # Declare namespaces, in the special style of lxml.
        nsmap = {None: svg.NAMESPACE_SVG,         # Default.
                 'xlink': svg.NAMESPACE_XLINK,
                 'xml': svg.NAMESPACE_XML}

        kwargs['baseProfile'] = 'full'
        kwargs['version'] = '1.1'

        # The size of the image is explicitly specified in millimetres.
        x, y = dimensions
        kwargs['width'] = '{}mm'.format(x)
        kwargs['height'] = '{}mm'.format(y)

        # Because this library is print-friendly, we want all objects
        # in the image to have their measurements in mm as well.
        # This can be done explicitly for most measurements, but not all,
        # e.g. not for coordinates to rotate around:
        # "transform=rotate(a,x,y)" <-- real-world don't work for x, y.
        # For this reason, we apply a view box, which equates all
        # subordinate user-space coordinates (not font sizes) to millimetres.
        kwargs['viewBox'] = ' '.join(map(str, (0, 0, x, y)))

        return super().new(children=(cls.Definitions.new(),), nsmap=nsmap,
                           **kwargs)

    @property
    def defs(self):
        '''Convenient access to the top-level defs container.'''
        return self.find('defs')

    def to_string(self):
        return lxml.etree.tostring(self, pretty_print=True)

    def save(self, filepath):
        '''Prune dud presenters and save SVG code to the named file.'''
        for element in self.iter():
            if element == self:
                continue
            if not len(element) and not element.text and not element.attrib:
                element.getparent().remove(element)

        with open(filepath, mode='bw') as f:
            f.write(self.to_string())
