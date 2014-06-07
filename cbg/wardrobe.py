# -*- coding: utf-8 -*-
'''Style examples and defaults.'''

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
