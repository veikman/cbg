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

Copyright 2014-2016 Viktor Eikman

'''

from cbg.svg import wardrobe
from cbg.sample import font
from cbg.sample import color


class Grayscale(wardrobe.Wardrobe):
    modes = {wardrobe.MAIN: wardrobe.Mode(fill_colors=(color.BLACK,)),
             wardrobe.ACCENT: wardrobe.Mode(fill_colors=(color.GRAY_50,),
                                            stroke_colors=(color.BLACK,)),
             wardrobe.CONTRAST: wardrobe.Mode(fill_colors=(color.WHITE,),
                                              stroke_colors=(color.BLACK,))}


class Frame(wardrobe.Wardrobe):
    modes = {wardrobe.MAIN: wardrobe.Mode(thickness=2)}


class BasicTextWardrobe(Grayscale):
    modes = {wardrobe.MAIN: wardrobe.Mode(font=font.ARIAL, anchor='middle')}
    font_size = 4


class MiniEuroMain(BasicTextWardrobe):
    font_size = 4


class MiniEuroSmall(BasicTextWardrobe):
    font_size = 2.9


class StandardEuroMain(BasicTextWardrobe):
    font_size = 5


class StandardEuroSmall(BasicTextWardrobe):
    font_size = 3.4


class FinePrint(BasicTextWardrobe):
    font_size = 2.6
