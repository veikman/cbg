# -*- coding: utf-8 -*-
'''Common card and page sizes.'''

import numpy

class CardSize():
    def __init__(self, footprint, border_outer, border_inner):
        self.footprint = numpy.array(footprint)
        self.outer = border_outer
        self.inner = border_inner

MINI_EURO = CardSize((44, 68), 1.9, 0.8)
STANDARD_EURO = CardSize((59, 92), 1.9, 1)
SHORT_EURO = CardSize((59, 90), 1.9, 1) ## More likely to print as 3×3.

A4 = [210, 290]