# -*- coding: utf-8 -*-
'''Common card, page and font sizes.

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

from . import style
from . import svg


class CardSize():
    '''A card in millimetres.'''
    def __init__(self, footprint, border_outer, border_inner):
        self.footprint = numpy.array(footprint)
        self.outer = border_outer
        self.inner = border_inner

    def tilted(self):
        return CardSize(numpy.flipud(self.footprint), self.outer, self.inner)

    @property
    def interior_width(self):
        return self.footprint[0] - 2 * self.outer - 2 * self.inner


class PageSize():
    '''A page in millimetres.'''
    def __init__(self, footprint, margins):
        self.footprint = numpy.array(footprint)
        self.margins = numpy.array(margins)


class FontSize():
    '''A set of properties shared by all fonts in a wardrobe.'''
    def __init__(self, base, stroke_factor=0.02,
                 line_height_factor=1.17, after_paragraph_factor=0.3):
        self.base = base
        self.stroke = stroke_factor * self.base
        self.line_height = line_height_factor * self.base
        self.after_paragraph = after_paragraph_factor * self.base

    def dict_svg(self):
        return {style.STYLE: 'font-size:{};'.format(svg.rounded(float(self)))}

    def __int__(self):
        return int(self.base)

    def __float__(self):
        return float(self.base)


A4 = PageSize((210, 290), (16, 9))

MINI_EURO = CardSize((44, 68), 1.9, 0.8)
STANDARD_EURO = CardSize((59, 92), 1.9, 1)
SHORT_EURO = CardSize((59, 90), 1.9, 1)  # More likely to print as 3×3.

# Example "Mini Euro" card font sizes:
FONT_TITLE_ME = FontSize(4)
FONT_TAGS_ME = FontSize(2.9, after_paragraph_factor=0)
FONT_BODY_ME = FontSize(2.9)
FONT_FINEPRINT_ME = FontSize(2.6)

# Example "Standard Euro" card font sizes:
FONT_TITLE_SE = FontSize(5)
FONT_TAGS_SE = FontSize(3.4, after_paragraph_factor=0)
FONT_BODY_SE = FontSize(3.4)
FONT_FINEPRINT_SE = FontSize(2.6)
