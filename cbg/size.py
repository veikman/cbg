# -*- coding: utf-8 -*-
'''Common card and page sizes.'''

import numpy

class CardSize():
    '''A card in millimetres.'''
    def __init__(self, footprint, border_outer, border_inner):
        self.footprint = numpy.array(footprint)
        self.outer = border_outer
        self.inner = border_inner

class PageSize():
    '''A page in millimetres.'''
    def __init__(self, footprint, margins):
        self.footprint = numpy.array(footprint)
        self.margins = numpy.array(margins)

MINI_EURO = CardSize((44, 68), 1.9, 0.8)
STANDARD_EURO = CardSize((59, 92), 1.9, 1)
SHORT_EURO = CardSize((59, 90), 1.9, 1) ## More likely to print as 3×3.

A4 = PageSize((210, 290), (16, 9))
