# -*- coding: utf-8 -*-
'''Standard string keys.

These are used for the extraction of certain common content out of raw
text specifications, but also to track the contents of wardrobes etc.

Presented as a module to prevent circular importation problems.

'''

# Keys for machine-readable CBG specification documents:

METADATA = 'metadata'
DATA = 'data'

COPIES = 'copies'
DEFAULTS = 'defaults'
TAGS = 'tags'
TITLE = 'title'


# SVG code keywords:

STYLE = 'style'
TEXT_ANCHOR = 'text-anchor'
FILL = 'fill'

FONT_BOLD = 'bold'
FONT_ITALIC = 'italic'
FONT_SMALL_CAPS = 'small_caps'

ALIGN_START = 'start'
ALIGN_MIDDLE = 'middle'
ALIGN_END = 'end'
