'''CONDEMNED'''  

import collections
import logging
import os

import lxml.builder
import numpy

import cbg.sample.size as size
from cbg.svg import presenter


class Page():
    '''A logical printable page, populated by neatly layed out cards.'''

    class PageFull(Exception):
        '''Not an error. Footprint cannot be fitted into current layout.'''
        pass

    class PrintableAreaTooSmall(Exception):
        '''Footprint too large for page type. Layout impossible.'''
        pass

    def __init__(self, dimensions=size.A4, side='', left_to_right=True):
        '''Initialize.

        The "left_to_right" flag denotes the direction from which cards
        are added. This is normally used to get front and back sides
        matched up for duplex printing.

        '''
        self.full_size = dimensions
        self.side = side
        self.left_to_right = left_to_right

        head = dict()
        head['xmlns'] = presenter.NAMESPACE_SVG
        head['xml'] = presenter.NAMESPACE_XML
        head['baseProfile'] = 'full'
        head['version'] = '1.1'

        # The size of the page is explicitly specified in millimetres.
        x, y = self.full_size
        head['width'] = '{}mm'.format(x)
        head['height'] = '{}mm'.format(y)

        # Because this library is print-friendly, we want all objects
        # on the page to have their measurements in mm as well.
        # This can be done explicitly for most measurements, but not all,
        # e.g. not for coordinates to rotate around:
        # "transform=rotate(a,x,y)" <-- real-world don't work for x, y.
        # For this reason, we apply a view box at the page level, which
        # equates all subordinate user-space coordinates to millimetres.
        head['viewBox'] = ' '.join(map(str, (0, 0, x, y)))

        self.xml = lxml.builder.E.svg(lxml.builder.E.defs, head)
        self.printable = self.full_size - 2 * self.full_size.margins

        self.row_heights = []
        self._new_row()

    @property
    def defs(self):
        '''Convenient access to the top-level defs container.

        This library supports the SVG convention of maintaining filters
        etc. as invisible definition elements in "defs".

        '''
        return self.xml.find('defs')

    def _new_row(self):
        self.row_size = numpy.array([0, 0])

    def can_fit(self, footprint):
        '''Determine whether a new item could be placed on the page.'''
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
            raise self.PrintableAreaTooSmall()
        if space_x < row_x + card_x:
            # The current row must be getting too long.
            # We need to see if the next row would work.
            occupied_y += row_y
            row_x = 0
        if space_y < occupied_y + card_y:
            # A new row would not be high enough.
            return False

        x = row_x if self.left_to_right else space_x - row_x - footprint[0]
        return self.full_size.margins + (x, occupied_y)

    def add(self, footprint, xml):
        if not self.can_fit(footprint):
            raise self.PageFull()

        if self.printable[0] < self.row_size[0] + footprint[0]:
            self.row_heights.append(self.row_size[1])
            self._new_row()

        self.xml.append(xml)

        # Adjust envelope of current row to reflect the addition.
        self.row_size = (self.row_size[0] + footprint[0], self.row_size[1])
        if self.row_size[1] < footprint[1]:
            self.row_size = (self.row_size[0], footprint[1])

    def save(self, filepath):
        if self.side:
            filepath += '_' + self.side
        filepath += '.svg'
        s = lxml.etree.tostring(self.xml, pretty_print=True)
        with open(filepath, mode='bw') as f:
            f.write(s)


class Queue(collections.UserList):
    '''A list of pages.

    Based on UserList because it can be desirable to change the order
    of the pages after the queue has been populated, as in the example
    application's duplex mode.

    '''
    def __init__(self, title):
        super().__init__()
        self.title = title

    def save(self, destination_folder):
        try:
            os.mkdir(destination_folder)
        except OSError:
            logging.debug('Destination folder already exists.')

        for number, page in enumerate(self):
            name = '{}_{:03d}'.format(self.title, number + 1)
            page.save(os.path.join(destination_folder, name))
