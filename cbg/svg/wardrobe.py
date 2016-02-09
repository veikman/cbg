# -*- coding: utf-8 -*-
'''A wardrobe system for managing a few of SVG's many styling options.

This module is intended to be easily adaptable for sensitivity to
context. An example to follow here would be the dual syntactic coloring
of some cards in the game Dominion by Donald X. Vaccarino, such as the
"Treasure-Reaction" hybrids.

'''

# This file is part of CBG.
#
# CBG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CBG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CBG.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2016 Viktor Eikman


import logging

import cbg.misc as misc
import cbg.keys as keys
from cbg.svg import svg


# Any hashable object can be used as a key to a wardrobe mode.
# These strings are just examples, except one.
MAIN = 'main'               # Used by default in the main Wardrobe class.
INACTIVE = 'inactive'
BACKGROUND = 'background'
CONTRAST = 'contrast'
ACCENT = 'accent'
EMPHASIS = 'emphasis'


class Font():
    '''A font, actually a font family, as handled by a wardrobe.

    An ugly band-aid over our lack of real typesetting abstractions.

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


class Mode():
    '''An operating mode for a wardrobe.

    A simple wardrobe has just one mode. Commonly, a wardrobe has two:
    A primary mode and a second one for emphasis.

    '''

    def __init__(self, font=None,
                 fill_colors=(), stroke_colors=(),
                 dasharray=None, thickness=None,
                 italic=False, oblique=False, style=None,
                 bold=False, bolder=False, lighter=False, weight=None,
                 start=False, middle=False, end=False, anchor=None,
                 small_caps=False, variant=None):

        # The majority of keyword arguments relate to typesetting.
        self.style = self._filter(italic=italic, oblique=oblique, direct=style)
        self.weight = self._filter(bold=bold, bolder=bolder,
                                   lighter=lighter, direct=weight)
        self.variant = self._filter(small_caps=small_caps, direct=variant)
        self.anchor = self._filter(start=start, middle=middle, end=end,
                                   direct=anchor)

        # If provided, "font" should be an instance of the Font class below.
        self.font = font

        # To support gradients and multi-color ribbons, colors are to
        # be provided as sequences.
        self.fill_colors = fill_colors
        self.stroke_colors = stroke_colors

        # Thickness should be a number. It is typically used for stroke
        # width, but can be to put to other uses as well.
        self.thickness = thickness
        if self.thickness is None:
            self.thickness = 0  # Meaning no stroke on text.
            if self.stroke_colors and self.font is None:
                self.thickness = 1  # Useful for testing shapes.

        # Miscellaneous.
        self.dasharray = dasharray  # Affects stroke.

    def _filter(self, direct=None, **kwargs):
        '''Select one of the possible arguments for a single attribute.'''
        if direct:
            return direct

        for key, value in kwargs.items():
            if value:
                return key

    def copy(self, **kwargs):
        '''Make a copy, treating kwargs like overriding arguments to init.'''
        attrib = self.__dict__.copy()
        attrib.update(kwargs)
        return self.__class__(**attrib)

    @property
    def character_width_to_height(self):
        '''The ratio of font character width to height.

        Used to compute when to wrap a line of text.

        '''
        if not self.font:
            return

        factor = self.font.width_to_height
        if self.style or (self.weight and self.weight != 'thinner'):
            factor *= self.font.bold_to_roman
        return factor


class Wardrobe():
    '''A set of fonts, colors and other presentation-layer assets.

    The default font size unit here is "px", meaning pixel. According to
    the SVG standard, the px unit should be treated the same as not
    specifying a unit, but viewer implementations may vary.

    SVG "px" is not literally pixels. Since CBG is otherwise based on
    millimetres, "mm" might be preferable, but disturbs baselines.

    '''
    # Commonly overridden in subclasses.
    font_size = None
    modes = {MAIN: Mode()}

    # In order to support such use cases as writing one half of a
    # card's text upside down, wardrobes can control transformations.
    transformations = list()

    # Less commonly overridden.
    font_size_unit = 'px'
    line_height_factor = 1.17
    paragraph_break_factor = 0.3

    def __init__(self):
        self.line_height = None
        self.after_paragraph = None
        if self.font_size:
            self.line_height = self.font_size * self.line_height_factor
            self.after_paragraph = self.font_size * self.paragraph_break_factor
        self.reset()

    def reset(self):
        '''To be overridden in case of an atypical default key.'''
        self.set_mode(MAIN)

    def set_mode(self, key):
        '''Set operating mode from the class's collection.'''
        try:
            self.mode = self.modes[key]
        except KeyError:
            s = '{} has no mode keyed by {}.'
            logging.error(s.format(self.__class__, key))
            raise

    @classmethod
    def copy_modes(cls, **kwargs):
        '''Apply the copy() method of Mode to every mode of the wardrobe.'''
        return {k: v.copy(**kwargs) for k, v in cls.modes.items()}

    @property
    def literate(self):
        '''True if the wardrobe can handle text.'''
        return self.font_size and self.mode.font

    @property
    def character_width(self):
        '''A number representing average character width.'''
        if not self.literate:
            return
        return self.font_size * self.mode.character_width_to_height

    def horizontal_anchor(self, space, margin=0):
        '''An X coordinate.

        The coordinate represents where in space a text SVG element
        should be placed, given its specified alignment.

        Due to lack of typesetting info, a Western-style writing system
        is assumed, going from left to right.

        '''
        if self.mode.anchor in (None, keys.ALIGN_START):
            return margin
        elif self.mode.anchor == keys.ALIGN_MIDDLE:
            return space / 2
        elif self.mode.anchor == keys.ALIGN_END:
            return space - margin
        else:
            s = 'Unrecognized SVG text anchor (alignment): "{}".'
            raise ValueError(s.format(self.mode.anchor))

    def to_svg_attributes(self, transform_ext=None):
        '''Produce a simple dictionary for use with SVGElement.

        The "position" argument is relevant only with a rotation
        transformation, and even then, only if it's configured for
        this usage.

        '''

        attrib = dict()
        style = svg.KeyValuePairs()

        if self.literate:
            style['font-family'] = str(self.mode.font)
            size_value = misc.rounded(float(self.font_size))
            style['font-size'] = size_value + self.font_size_unit

            if self.mode.weight is not None:
                style['font-weight'] = self.mode.weight

            if self.mode.style is not None:
                style['font-style'] = self.mode.style

            if self.mode.variant is not None:
                style['font-variant'] = self.mode.variant

            if self.mode.anchor is not None:
                attrib[keys.TEXT_ANCHOR] = self.mode.anchor

        if self.mode.fill_colors:
            color = self.mode.fill_colors[0]
            if color != '#000000':  # SVG default.
                style['fill'] = color

        if self.mode.thickness:
            try:
                color = self.mode.stroke_colors[0]
            except IndexError:
                # Black is the CBG default for stroke.
                color = '#000000'

            # Black is not the SVG default for stroke. It needs a color.
            style['stroke'] = color

            if self.mode.dasharray is not None:
                style['stroke-dasharray'] = self.mode.dasharray

            if self.literate:
                # Scale to font.
                style['stroke-width'] = self.font_size * self.mode.thickness
            else:
                style['stroke-width'] = self.mode.thickness

        if self.transformations:
            iterable = (t.to_string(extension=transform_ext)
                        for t in self.transformations)
            attrib['transform'] = ' '.join(iterable)

        if style:
            attrib.update({keys.STYLE: str(style)})
        return attrib
