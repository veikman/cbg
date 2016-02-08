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
import cbg.cursor


class CardPresenter(presenter.SVGPresenter):
    '''Abstract superclass SVG presenter for one side of a playing card.'''

    cursor_class = cbg.cursor.FromTop

    @classmethod
    def new(cls, *args, **kwargs):
        inst = super().new(*args, **kwargs)
        inst._prune_dud_presenters()
        return inst

    def _prune_dud_presenters(self):
        '''Delete completely superfluous elements.'''
        for element in self.iter():
            if element == self:
                continue
            if not len(element) and not element.text and not element.attrib:
                element.getparent().remove(element)


class CardFront(CardPresenter):
    '''Example behaviour for the front of a card.

    Inheritors of this class typically have Wardrobe set to something
    that generates a thick frame, such as cbg.sample.wardrobe.Frame.

    '''
    recursion_attribute_name = presenter.RECURSION_FRONT

    def present(self):
        self.insert_frame(fill=color.WHITE)
        self.recurse()
        self.insert_frame()


class CardBack(CardPresenter):
    '''Example behaviour for the back of a card.

    This starts a third of the way down on the assumption that a simple
    deck will only have a word or two on the back of each card, naming
    the deck itself.

    '''
    recursion_attribute_name = presenter.RECURSION_BACK

    def present(self):
        self.cursor.slide(self.size[1] / 3)
        self.recurse()
