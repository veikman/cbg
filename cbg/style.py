# -*- coding: utf-8 -*-
'''Style information for playing cards.

This module is intended to be easily adaptable for sensitivity to
context. An example to follow here would be the dual syntactic coloring
of some cards in the game Dominion by Donald X. Vaccarino, such as the
"Treasure-Reaction" hybrids.

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

import copy

from . import misc


# SVG code keywords.
STYLE = 'style'
TEXT_ANCHOR = 'text-anchor'
FILL = 'fill'

BOLD = 'bold'
ITALIC = 'italic'

ALIGN_START = 'start'
ALIGN_MIDDLE = 'middle'
ALIGN_END = 'end'

COLOR_BLACK = '#000000'  # Default in SVG.
COLOR_WHITE = '#ffffff'
COLOR_GRAY_50 = '#888888'

# Internal keywords.
MAIN = 'main'
CONTRAST = 'contrast'
ACCENT = 'accent'

KEYS = (MAIN, CONTRAST, ACCENT)


class Wardrobe():
    '''A set of fonts, colors and other presentation-layer assets.

    The "fonts" and "colors" arguments are both expected to be
    dictionaries whose keys are the mode strings of this module,
    and whose values are tuples or similar iterables, containing
    at least one appropriate object for each mode likely to be used.

    '''
    def __init__(self, size, fonts, colors):
        self._native_size = size
        self.fonts = fonts
        self.colors = colors
        self.reset()
        self._sanity()
        self.but = Duplicator(self)

    @property
    def size(self):
        return self._current_size

    @size.setter
    def size(self, value):
        self._current_size = value

    def reset(self):
        self.size = self._native_size

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
            # No need to include fill attribute if the color is SVG default.
            return {STYLE: ''}
        else:
            return {STYLE: 'fill:{};'.format(color)}

    def dict_svg_stroke(self, thickness=None):
        color = self.colors[self._color_mode_stroke][0]
        if thickness is None:
            thickness = self.size.stroke
        s = 'stroke:{};stroke-width:{}'
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
            return space_width / 2
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


class Duplicator():
    '''A wardrobe design tool for small differences.'''
    def __init__(self, parent):
        for dictname in ('fonts', 'colors'):
            for key in KEYS:
                # Create a method for respawning parent with a difference.
                self._closure(parent, dictname, key)

    def _closure(self, parent, dictname, key):
        '''This method is just a scope for its local variables.'''
        def f(new_value):
            duplicate = copy.deepcopy(parent)
            getattr(duplicate, dictname)[key] = new_value
            return duplicate
        setattr(self, '{}_{}'.format(dictname, key), f)


class FontFamily():
    '''An ugly band-aid over our lack of real typesetting abstractions.

    The numbers passed to instantiate this class are used to estimate how
    long a given piece of text is going to be. A higher number for width-
    to-height signifies a squat, broad font family.

    The numbers should be based on rough estimates of slightly broader-
    than-average letters, to cover most cases. Lines of unusually slim
    or broad characters are going to look bad.

    '''
    def __init__(self, name, width_to_height=0.6, bold_to_roman=1.1):
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
