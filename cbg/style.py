# -*- coding: utf-8 -*-
'''Style information for playing cards.

The code here needs to be easily adaptable for sensitivity to context,
as with the dual-syntax coloring of some Dominion cards (e.g. "Treasure-
Reaction").

'''

import copy

from . import svg
from . import misc

## SVG code keywords.
STYLE = 'style'
TEXT_ANCHOR = 'text-anchor'
FILL = 'fill'

BOLD = 'bold'
ITALIC = 'italic'

ALIGN_START = 'start'
ALIGN_MIDDLE = 'middle'
ALIGN_END = 'end'

COLOR_BLACK = '#000000' ## Default in SVG.
COLOR_WHITE = '#ffffff'
COLOR_GRAY_50 = '#888888'

## Internal keywords.
MAIN = 'main'
CONTRAST = 'contrast'
ACCENT = 'accent'


class Wardrobe():
    '''A set of fonts, colors and other presentation-layer assets.
    
    The "fonts" and "colors" arguments are both expected to be
    dictionaries whose keys are the mode strings of this module,
    and whose values are tuples or similar iterables, containing
    at least one appropriate object for each mode likely to be used.
    
    '''
    def __init__(self, size, fonts, colors):
        self.size = size
        self.fonts = fonts
        self.colors = colors
        self.reset()
        self._sanity()

    def reset(self):
        self._force_bold = False
        self._force_italic = False
        self._stroke_enabled = False

        self._font_mode = MAIN
        self._color_mode_fill = MAIN
        self._color_mode_stroke = MAIN

    def emphasis(self, bold=False, italic=False, stroke=False):
        self._force_bold = bold
        self._force_italic = italic
        self._stroke_enabled = stroke

    def mode_contrast(self, font=False, fill=False, stroke=False):
        self._set_color(CONTRAST, font, fill, stroke)
        
    def mode_accent(self, font=False, fill=False, stroke=False):
        self._set_color(ACCENT, font, fill, stroke)

    def dict_svg_font(self):
        font = copy.copy(self.fonts[self._font_mode])
        if self._force_bold:
            font.weight = BOLD
        if self._force_italic:
            font.style = ITALIC
        attrib = font.dict_svg()
        attrib[STYLE] += self.size.dict_svg()[STYLE]
        attrib[STYLE] += self.dict_svg_fill()[STYLE]
        if self._stroke_enabled:
            attrib[STYLE] += self.dict_svg_stroke()[STYLE]
        return attrib

    def dict_svg_fill(self):
        color = self.colors[self._color_mode_fill][0]
        if color == COLOR_BLACK:
            ## No need to include fill attribute if the color is SVG default.
            return {STYLE: ''}
        else:
            return {STYLE: 'fill:{};'.format(color)}

    def dict_svg_stroke(self, thickness=None):
        color = self.colors[self._color_mode_stroke][0]
        if thickness is None:
            thickness = self.size.stroke
        s = 'stroke:{};stroke-width:{}mm'
        return {STYLE: s.format(color, thickness)}

    def color_iterable(self):
        '''Return the raw list of color strings for the current color mode.
        
        Most modes will only have one color.
        
        This is likely to be interesting only for gradients or
        multi-color ribbons. Not everything drawn to cards can treat
        multiple colors properly, so every other method returns the
        first color only.
        
        '''
        return self.colors[self._color_mode_fill]

    @property
    def width_to_height(self):
        '''Used to compute when to wrap a line of text.'''
        font = self.fonts[self._font_mode]
        factor = font.family.width_to_height
        if self._force_italic or font.weight == BOLD:
            factor *= font.family.bold_to_roman
        return factor

    def horizontal(self, space_width, margin=0):
        a = self.fonts[self._font_mode].anchor
        if a == ALIGN_START:
            return margin
        elif a == ALIGN_MIDDLE:
            return space_width/2
        elif a == ALIGN_END:
            return space_width - margin
        else:
            s = 'Unrecognized SVG text anchor (alignment): "{}".'
            raise ValueError(s.format(a))

    def _set_color(self, mode, font, fill, stroke):
        if font:
            self._font_mode = mode
        if fill:
            self._color_mode_fill = mode
        if stroke:
            self._color_mode_stroke = mode
        self._sanity()

    def _sanity(self):
        '''Modes need to be available only as they're called upon.'''
        if self._font_mode not in self.fonts:
            s = 'Wardrobe lacks font for mode "{}".'
            raise KeyError(s.format(self._font_mode))

        if self._color_mode_fill not in self.colors:
            s = 'Wardrobe lacks color for mode "{}" (fill).'
            raise KeyError(s.format(self._color_mode_fill))
        if not misc.listlike(self.colors[self._color_mode_fill]):
            s = 'Color for mode "{}" (fill) is not iterable: {}.'
            raise TypeError(s.format(self._color_mode_fill,
                                     self.colors[self._color_mode_fill]))
 
        if self._color_mode_stroke not in self.colors:
            s = 'Wardrobe lacks color for mode "{}" (stroke).'
            raise KeyError(s.format(self._color_mode_stroke))
        if not misc.listlike(self.colors[self._color_mode_stroke]):
            s = 'Color for mode "{}" (stroke) is not iterable: {}.'
            raise TypeError(s.format(self._color_mode_stroke,
                                     self.colors[self._color_mode_stroke]))

class FontSize():
    '''A set of properties shared by all fonts in a wardrobe.'''
    def __init__(self, base, stroke_factor=0.02,
                 line_height_factor=1.2, after_paragraph_factor=0.3):
        self.base = base
        self.stroke = stroke_factor * self.base
        self.line_height = line_height_factor * self.base
        self.after_paragraph = after_paragraph_factor * self.base

    def dict_svg(self):
        return {STYLE: 'font-size:{};'.format(svg.mm(float(self)))}

    def __int__(self):
        return int(self.base)

    def __float__(self):
        return float(self.base)

class FontFamily():
    '''An ugly band-aid over our lack of real typesetting abstractions.
    
    The numbers passed to instantiate this class are used to estimate how
    long a given piece of text is going to be
    
    They are based on rough estimates of slightly broader-than-average
    letters, to cover most cases. Lines of unusually slim or broad
    characters are going to look bad.
    
    '''
    def __init__(self, name, width_to_height, bold_to_roman):
        self.name = name
        self.width_to_height = width_to_height
        self.bold_to_roman = bold_to_roman
        
    def __str__(self):
        return self.name

class Type():
    def __init__(self, family, weight=None, style=None, anchor='start'):
        self.family = family
        self.weight = weight
        self.style = style
        self.anchor = anchor

    @property
    def stylestring(self):
        s = 'font-family:{};'
        base = s.format(self.family)
        if self.weight is not None:
            base += 'font-weight:{};'.format(self.weight)
        if self.style is not None:
            base += 'font-style:{};'.format(self.style)
        return base

    def dict_svg(self):
        return {STYLE: self.stylestring, TEXT_ANCHOR: self.anchor}
