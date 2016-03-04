# -*- coding: utf-8 -*-
'''A module for representing image contents, including owning SVG code.'''

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


import os

import cbg.misc
from cbg import geometry
from cbg.svg import image
from cbg.sample import size


class BaseImage():
    '''An image, treated as a file and as a container of cards.

    For the purpose of printing cards, an image constitutes a printable
    page.

    '''

    class Full(Exception):
        '''Not an error. Footprint cannot be fitted into current layout.'''
        pass

    class TooSmall(Exception):
        '''Card footprint too large even for clear image. Layout impossible.'''
        pass

    def __init__(self, dimensions=size.A4, **kwargs):
        self.xml = image.SVG.new(dimensions=dimensions, **kwargs)
        self.dimensions = geometry.Rectangle(dimensions)

        # Cards depicted in an image should be available when the time comes
        # to name the image file and describe its contents.
        self.subjects = []

        # Filenames are assigned by external forces, being dependent on
        # information unavailable to the image object itself.
        self.directory = None
        self.filename = None

    @property
    def filepath(self):
        assert self.filename and self.directory
        return os.path.join(self.directory, self.filename)

    @filepath.setter
    def filepath(self, value):
        self.directory, self.filename = os.path.split(value)

    def can_fit(self, footprint):
        '''Determine whether a new item could be placed in the image. Naive.'''
        return True

    def add(self, card, xml):
        self.subjects.append(card)
        self.xml.append(xml)

    def save(self):
        '''Prune dud presenters and save SVG code to the named file.'''
        self.xml.save(self.filepath)


class LayoutFriendlyImage(BaseImage):
    '''Conveniences for placing cards.

    This subclass adds support for margins (as padding) and layout order,
    and prevents overlaps, eventually raising an exception if too full.

    '''
    def __init__(self, padding=size.A4_MARGINS, left_to_right=True, **kwargs):
        '''Create an image.

        The "padding" flag measures out a margin between the limits of
        the image and its actual contents. In the case of a page, it
        functions as a margin necessary to make the contents printable
        on a regular desktop printer. It is formulated as (x, y).

        The "left_to_right" flag denotes the direction from which cards
        are added. This is normally used to get front (obverse) and
        back (reverse) sides matched up for duplex printing on a page.

        '''
        super().__init__(**kwargs)

        self._padding = cbg.misc.Compass(*padding[::-1])
        self._printable = self.dimensions - self._padding.reduction

        self.left_to_right = left_to_right
        self._row_heights = []
        self._new_row()

    def _new_row(self):
        self._row_size = geometry.InstantArray((0, 0))

    def can_fit(self, footprint):
        '''A meaningful override.'''
        free = self.free_spot(footprint)
        if free is not False and free is not None:
            return True
        else:
            return False

    def free_spot(self, footprint):
        '''Find where a new card would be placed, if possible.

        If the card would fit, as indicated by looking only at a numpy array
        of its size, return a numpy array describing the coordinates that
        the top left corner of the card would have in the image.

        If the card would not fit, return False.

        '''
        space_x, space_y = self._printable
        row_x, row_y = self._row_size
        card_x, card_y = footprint
        occupied_y = sum(self._row_heights)

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
        return (self._padding.left + x, self._padding.top + occupied_y)

    def add(self, card, xml):
        '''An override.'''
        if not self.can_fit(xml.size):
            raise self.Full('Cannot add another card to image: Image full.')

        if self._printable[0] < self._row_size[0] + xml.size[0]:
            self._row_heights.append(self._row_size[1])
            self._new_row()

        super().add(card, xml)

        # Adjust envelope of current row to reflect the addition.
        self._row_size = (self._row_size[0] + xml.size[0], self._row_size[1])
        if self._row_size[1] < xml.size[1]:
            self._row_size = (self._row_size[0], xml.size[1])
