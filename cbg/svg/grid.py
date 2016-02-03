# -*- coding: utf-8 -*-
'''SVG code for grid layouts.'''

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


import numpy

from cbg.svg import presenter


class Square(presenter.SVGPresenter):
    '''A square map tile.'''

    size = (3, 3)

    def present(self):
        self.insert_frame()


class Empty(Square):
    '''To be subclassed.

    Referenced as an attribute of a content class elsewhere.

    '''
    pass


class Affected(Square):
    '''As Empty.'''
    pass


class SquareGrid(presenter.SVGPresenter):
    '''A group of square sub-elements, without any label or explanation.

    To enable filtering, clipping etc. of the grid alone, it is grouped
    by this presenter class. Any labelling should be done by a superordinate
    presenter.

    '''

    def present(self):
        for coordinates, cell in numpy.ndenumerate(self.field):
            offset = numpy.array(coordinates) * cell.presenter_class_front.size
            origin = self.origin + (0, self.cursor.offset) + offset
            presenter = cell.presenter_class_front.new(cell, origin=origin,
                                                       parent=self)
            self.append(presenter)

        if self.field:
            self.cursor.slide(coordinates[1])
