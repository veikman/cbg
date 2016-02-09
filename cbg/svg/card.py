# -*- coding: utf-8 -*-
'''Classes representing whole cards in SVG code.'''

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


from cbg.sample import color
from cbg.svg import presenter
from cbg.svg.shapes import Rect
from cbg.svg import wardrobe
import cbg.cursor


class CardPresenter(presenter.SVGPresenter):
    '''Abstract superclass SVG presenter for one side of a playing card.'''

    class Wardrobe(wardrobe.Wardrobe):
        '''A wardrobe for drawing a plain background and a black frame.'''
        modes = {wardrobe.MAIN: wardrobe.Mode(fill_colors=(color.NONE,),
                                              thickness=2),
                 wardrobe.BACKGROUND: wardrobe.Mode(fill_colors=(color.WHITE,))
                 }

    cursor_class = cbg.cursor.FromTop


class CardFront(CardPresenter):
    '''Example behaviour for the front of a card.'''

    recursion_attribute_name = presenter.RECURSION_FRONT

    def present(self):
        '''Draw a white background and a rounded black frame on top.'''

        # Add background.
        t = self.wardrobe.mode.thickness  # Preserved from the main mode.
        self.wardrobe.set_mode(wardrobe.BACKGROUND)
        self.append(Rect.new(self.origin + t / 2, self.size - t,
                             rounding=t, wardrobe=self.wardrobe,))

        # Restore wardrobe thickness for use by children in layouting.
        self.wardrobe.reset()

        # Add children.
        self.recurse()

        # Add frame.
        self.append(Rect.new(self.origin + t / 2, self.size - t,
                             rounding=t, wardrobe=self.wardrobe))


class CardBack(CardPresenter):
    '''Example behaviour for the back of a card.

    This starts a third of the way down on the assumption that a simple
    deck will only have a word or two on the back of each card, naming
    the deck itself.

    '''
    recursion_attribute_name = presenter.RECURSION_BACK

    def present(self):
        '''Draw a white background without a frame, and adjust the cursor.'''
        t = self.wardrobe.mode.thickness
        self.wardrobe.set_mode(wardrobe.BACKGROUND)
        self.append(Rect.new(self.origin, self.size, rounding=1.5 * t,
                             wardrobe=self.wardrobe,))
        self.wardrobe.reset()

        self.cursor.slide(self.size[1] / 3)
        self.recurse()
