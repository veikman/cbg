# -*- coding: utf-8 -*-
'''Style examples and defaults.'''

from . import style

## Color iterables:

BLACK = (style.COLOR_BLACK,)
WHITE = (style.COLOR_WHITE,)
GRAY_50 = (style.COLOR_GRAY_50,)

## Custom OOP representations:

ARIAL = style.FontFamily('Arial', 0.6, 1.1)
ME_TITLE = style.FontSize(4)
ARIAL_CENTERED = style.Type(ARIAL, anchor='middle')

FONTSCHEME = { style.MAIN: ARIAL_CENTERED }

COLORSCHEME = { style.MAIN: BLACK
              , style.ACCENT: GRAY_50
              , style.CONTRAST: WHITE
              }

WARDROBE = style.Wardrobe(ME_TITLE, FONTSCHEME, COLORSCHEME)