# -*- coding: utf-8 -*-
'''Size examples and defaults. All values in mm.

Printable area margin values don't really belong here. Ideally, they would
be derived from PostScript ImageableArea entries for each format supported
by a local printer, but CBG should be usable for producing documents
printable by others. This leads to guesswork about what the ultimate
user's printer might support.

'''

# Pretty common margin sizes for full-page, laser-based and ink-based printers.
MARGINS_FULLPAGE = (0, 0)
MARGINS_LASER = (4.3, 4.3)  # 12 DTP points, i.e. 1/6”.
MARGINS_INK = (12.7, 12.7)  # 36 DTP points, i.e. ½”.

# Common paper sizes.
# Margins here are suitable for centering Euro card sizes for printing, with
# some reasonable likelihood that content won't bleed. This can waste space.
A4 = (210, 290)
A4_MARGINS = (16, 9)
US_LETTER = (215.9, 279.4)
US_LETTER_MARGINS = (18.9, MARGINS_INK[1])

# Common card sizes.
MINI_EURO = (44, 68)
STANDARD_EURO = (59, 92)

# Uncommon card sizes.
SHORT_EURO = (59, 90)  # Truncated to fit 3×3 on a wider range of printers.
