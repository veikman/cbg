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
from cbg import geometry
from cbg.svg import svg
from cbg.sample import size


class Image(cbg.misc.SearchableTree, svg.SVGElement):
    '''An SVG image document root.

    This class represents a complete SVG image, using the "svg" tag
    and forming the root element of an SVG XML document. It is not
    related to the SVG element type tagged "image", which is modelled
    in cbg.svg.misc.

    For the purpose of printing cards, an image constitutes a printable
    page.

    Implementation detail: Unlike basic SVGElements, an image holds a
    lot of Python state information. In handling images, as per the
    general recommendations for lxml subclasses, it is important to
    keep a reference to the image alive as long as its Python API
    features are needed.

    '''

    TAG = 'svg'

    class Definitions(svg.SVGElement):
        '''An SVG convention.

        Filters etc. are defined in a "defs" element, which makes them
        invisible.

        '''
        TAG = 'defs'

    class Full(Exception):
        '''Not an error. Footprint cannot be fitted into current layout.'''
        pass

    class TooSmall(Exception):
        '''Card footprint too large even for clear image. Layout impossible.'''
        pass

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

        obj = super().new(children=(cls.Definitions.new(),), nsmap=nsmap,
                          **kwargs)

        obj.dimensions = geometry.Rectangle(dimensions)

        # Cards depicted in an image should be available when the time comes
        # to name the image file and describe its contents.
        obj.subjects = []

        return obj

    @property
    def defs(self):
        '''Convenient access to the top-level defs container.'''
        return self.find('defs')

    def can_fit(self, footprint):
        '''Determine whether a new item could be placed on the page.

        This base class is somewhat naive.

        '''
        return True

    def add(self, card, xml):
        self.subjects.append(card)
        self.append(xml)

    def save(self, filepath):
        '''Prune dud presenters and save SVG code to the named file.'''
        for element in self.iter():
            if element == self:
                continue
            if not len(element) and not element.text and not element.attrib:
                element.getparent().remove(element)

        with open(filepath, mode='bw') as f:
            f.write(lxml.etree.tostring(self, pretty_print=True))


class LayoutFriendlyImage(Image):
    '''Conveniences for placing cards.

    This subclass adds support for margins (as padding) and layout order,
    and prevents overlaps, eventually raising an exception if too full.

    '''

    @classmethod
    def new(cls, *args, padding=size.A4_MARGINS, left_to_right=True, **kwargs):
        '''Create an image.

        The "padding" flag measures out a margin between the limits of
        the image and its actual contents. In the case of a page, it
        functions as a margin necessary to make the contents printable
        on a regular desktop printer. It is formulated as (x, y).

        The "left_to_right" flag denotes the direction from which cards
        are added. This is normally used to get front (obverse) and
        back (reverse) sides matched up for duplex printing on a page.

        '''
        obj = super().new(*args, **kwargs)

        obj.padding = cbg.misc.Compass(*padding[::-1])
        obj.printable = obj.dimensions - obj.padding.reduction

        obj.left_to_right = left_to_right
        obj.row_heights = []
        obj._new_row()

        return obj

    def _new_row(self):
        self.row_size = geometry.InstantArray((0, 0))

    def can_fit(self, footprint):
        '''An override.'''
        free = self.free_spot(footprint)
        if free is not False and free is not None:
            return True
        else:
            return False

    def free_spot(self, footprint):
        '''Find where a new card would be placed, if possible.

        If the card would fit, as indicated by looking only at a numpy array
        of its size, return a numpy array describing the coordinates that
        the top left corner of the card would have on the page.

        If the card would not fit, return False.

        '''
        space_x, space_y = self.printable
        row_x, row_y = self.row_size
        card_x, card_y = footprint
        occupied_y = sum(self.row_heights)

        if space_x < card_x or space_y < card_y:
            s = 'Card can never fit image of selected size.'
            raise self.TooSmall(s)
        if space_x < row_x + card_x:
            # The current row must be getting too long.
            # We need to see if the next row would work.
            occupied_y += row_y
            row_x = 0
        if space_y < occupied_y + card_y:
            # A new row would not be high enough.
            return False

        x = row_x if self.left_to_right else space_x - row_x - footprint[0]
        return (self.padding.left + x, self.padding.top + occupied_y)

    def add(self, card, xml):
        '''An override.'''
        if not self.can_fit(xml.size):
            raise self.Full('Cannot add another card to image: Image full.')

        if self.printable[0] < self.row_size[0] + xml.size[0]:
            self.row_heights.append(self.row_size[1])
            self._new_row()

        super().add(card, xml)

        # Adjust envelope of current row to reflect the addition.
        self.row_size = (self.row_size[0] + xml.size[0], self.row_size[1])
        if self.row_size[1] < xml.size[1]:
            self.row_size = (self.row_size[0], xml.size[1])
