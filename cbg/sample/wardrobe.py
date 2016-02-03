# -*- coding: utf-8 -*-
'''Style examples and defaults.'''


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
