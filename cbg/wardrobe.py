# -*- coding: utf-8 -*-
'''Style examples and defaults.

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

Copyright 2014 Viktor Eikman

'''

from . import style
from . import fonts
from . import size


BLACK = (style.COLOR_BLACK,)
WHITE = (style.COLOR_WHITE,)
GRAY_50 = (style.COLOR_GRAY_50,)

ARIAL_CENTERED = style.Type(fonts.ARIAL, anchor='middle')

FONTSCHEME = {style.MAIN: ARIAL_CENTERED}

COLORSCHEME = {style.MAIN: BLACK,
               style.ACCENT: GRAY_50,
               style.CONTRAST: WHITE}

WARDROBE = style.Wardrobe(size.FONT_TITLE_ME, FONTSCHEME, COLORSCHEME)
