# -*- coding: utf-8 -*-
'''Size examples and defaults.

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

from cbg import size


A4 = size.PageSize((210, 290), (16, 9))

MINI_EURO = size.CardSize((44, 68), 1.9, 0.8)
STANDARD_EURO = size.CardSize((59, 92), 1.9, 1)

# A truncated Euro size is more likely to fit 3×3 on a desktop A4 printer.
SHORT_EURO = size.CardSize((59, 90), 1.9, 1)


# Example "Mini Euro" card font sizes:
FONT_TITLE_ME = size.FontSize(4)
FONT_TAGS_ME = size.FontSize(2.9, after_paragraph_factor=0)
FONT_BODY_ME = size.FontSize(2.9)
FONT_FINEPRINT_ME = size.FontSize(2.6)

# Example "Standard Euro" card font sizes:
FONT_TITLE_SE = size.FontSize(5)
FONT_TAGS_SE = size.FontSize(3.4, after_paragraph_factor=0)
FONT_BODY_SE = size.FontSize(3.4)
FONT_FINEPRINT_SE = size.FontSize(2.6)
