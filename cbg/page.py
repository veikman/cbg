# -*- coding: utf-8 -*-

import logging
import os
import string

import lxml.builder
import numpy

from . import exc
from . import size
from . import svg


class Page():
    '''A logical printable page, populated by neatly layed out cards.'''
    number = 0

    def __init__(self, dimensions=size.A4, left_to_right=True):
        '''Initialize.

        The "left_to_right" flag denotes the direction from which cards
        are added. This is normally used to get front and back sides
        matched up for duplex printing.

        '''
        self.full_size = dimensions
        self.left_to_right = left_to_right

        self.__class__.number += 1
        self.number = self.__class__.number
        logging.info('Creating page {}.'.format(self.number))

        head = dict()
        head['xmlns'] = svg.NAMESPACE_SVG
        head['xml'] = svg.NAMESPACE_XML
        head['baseProfile'] = 'full'
        head['version'] = '1.1'
        head['width'], head['height'] = svg.mm(self.full_size.footprint)

        self.xml = lxml.builder.E.svg(lxml.builder.E.defs, head)
        self.printable = self.full_size.footprint - 2 * self.full_size.margins

        self.row_heights = []
        self._new_row()

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
            raise exc.PrintableAreaTooSmall()
        if space_x < row_x + card_x:
            ## The current row must be getting too long.
            ## We need to see if the next row would work.
            occupied_y += row_y
            row_x = 0
        if space_y < occupied_y + card_y:
            ## A new row would not be high enough.
            return False

        x = row_x if self.left_to_right else space_x - row_x - footprint[0]
        return self.full_size.margins + (x, occupied_y)

    def add(self, footprint, xml):
        if not self.can_fit(footprint):
            raise exc.PageFull()
        if self.printable[0] < self.row_size[0] + footprint[0]:
            self.row_heights.append(self.row_size[1])
            self._new_row()
        self.xml.append(xml)

        ## Adjust envelope of current row to reflect the addition.
        self.row_size = (self.row_size[0] + footprint[0], self.row_size[1])
        if self.row_size[1] < footprint[1]:
            self.row_size = (self.row_size[0], footprint[1])

    def save(self, destination_folder, name):
        filename = '{:03d}_{}.svg'.format(self.number, name)
        s = lxml.etree.tostring(self.xml, pretty_print=True)
        with open(destination_folder + '/' + filename, mode='bw') as f:
            f.write(s)


class Queue(list):
    def __init__(self, title, side):
        super().__init__()
        self.title = title
        self.side = side

    def save(self, destination_folder):
        try:
            os.mkdir(destination_folder)
        except OSError:
            logging.debug('Destination folder already exists.')

        for letter, page in zip(string.ascii_letters, self):
            name = '_'.join(map(str, (self.title, letter, self.side)))
            page.save(destination_folder, name)
