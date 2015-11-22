# -*- coding: utf-8 -*-
'''SVG code for grid layouts.

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

import numpy
import lxml.etree

from cbg.svg import presenter
from cbg import size


class Square(presenter.FieldBase):
    '''A square map tile.'''

    size = size.CardSize((3, 3), border_outer=0.4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_frame()


class Empty(Square):
    '''To be subclassed with a presenter.

    Referenced as an attribute of a content class. Declaring the subclass
    in a similar manner makes the subclass a drop-in replacement.

    '''
    pass


class Affected(Square):
    '''As Empty.'''
    pass


class SquareGrid(presenter.SVGPresenter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The field as a whole may contain e.g. a text label over the grid,
        # provided by a subclass. To enable filtering, clipping etc. of the
        # grid alone, it is grouped here.
        grid_as_group = lxml.etree.Element('g')

        for coordinates, cell in numpy.ndenumerate(self.content_source.array):
            origin = coordinates * cell.presenter_class_front.size
            origin += tuple(self.origin)
            origin += (6, self.cursor.displacement + 5)
            presenter = cell.presenter_class_front(cell, origin=origin,
                                                   parent_presenter=self)
            grid_as_group.append(presenter.xml)

        self.xml.append(grid_as_group)
