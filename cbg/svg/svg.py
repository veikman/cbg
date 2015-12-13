# -*- coding: utf-8 -*-
'''Basic SVG production conveniences.

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

import itertools
import logging
import collections

import lxml.etree


class SVGElement(lxml.etree.ElementBase):
    '''A Python proxy class for the production of SVG code.

    One instance of this class corresponds to one SVG element, but only
    production is supported. CBG cannot load XML files, and cannot
    create instances of this class from XML.

    The TAG attribute, whose name is mandated by lxml, must be set by
    each subclass.

    '''

    # XML element tag (name), e.g. "rect" for a basic SVG rectangle.
    TAG = ''

    # _id_prefix is included when generating an ID attribute.
    _id_prefix = ''

    # Each inheritor of this generator is uniquely ID'd, if ID'd.
    _id_iterator = itertools.count()

    # Certain keyword arguments will automatically be intercepted
    # for inclusion in the "style" SVG attribute, instead of being
    # used as attributes on their own.
    #                    CSS font properties:
    _keywords_style = {'font',
                       'font-family',
                       'font-size',
                       'font-size-adjust',
                       'font-stretch',
                       'font-style',
                       'font-variant',
                       'font-weight',
                       # CSS text properties:
                       'direction',
                       'letter-spacing',
                       'text-decoration',
                       'unicode-bidi',
                       'word-spacing',
                       # Miscellaneous CSS properties:
                       'clip',
                       'color',
                       'cursor',
                       'display',
                       'overflow',
                       'visibility',
                       # Non-CSS compositing properties
                       'clip-path',
                       'clip-rule',
                       'mask',
                       'opacity',
                       # Non-CSS filter effect properties:
                       'enable-background',
                       'filter',
                       'flood-color',
                       'flood-opacity',
                       'lighting-color',
                       # Non-CSS gradient properties:
                       'stop-color',
                       'stop-opacity',
                       # Non-CSS interactivity properties:
                       'pointer-events',
                       # Non-CSS color and painting properties:
                       'color-interpolation',
                       'color-interpolation-filters',
                       'color-profile',
                       'color-rendering',
                       'fill',
                       'fill-opacity',
                       'fill-rule',
                       'image-rendering',
                       'marker',
                       'marker-end',
                       'marker-mid',
                       'marker-start',
                       'shape-rendering',
                       'stroke',
                       'stroke-dasharray',
                       'stroke-dashoffset',
                       'stroke-linecap',
                       'stroke-linejoin',
                       'stroke-miterlimit',
                       'stroke-opacity',
                       'stroke-width',
                       'text-rendering',
                       # Non-CSS text properties:
                       'alignment-baseline',
                       'baseline-shift',
                       'dominant-baseline',
                       'glyph-orientation-horizontal',
                       'glyph-orientation-vertical',
                       'kerning',
                       'text-anchor',
                       'writing-mode'}

    @classmethod
    def new(cls, children=None, set_id=False, **attributes):
        '''Create a new instance, configured with convenient logic.

        This class method should be called in preference to instantiating
        the class directly, because lxml.etree.Element is just a thin
        Python proxy over a C library, and the official lxml documentation
        deprecates any overriding of its __init__() or __new__(). The
        official substitute, _init(), is inappropriate for the level of
        convenience CBG aims to provide.

        '''
        if not cls.TAG:
            s = 'SVG element class {} has no tag name.'
            raise NotImplementedError(s.format(cls.__name__))

        # lxml can only handle bytes and unicode.
        attributes = {str(k): str(v) for k, v in attributes.items()}

        # Suck some arguments into a style attribute.
        cls._filter_arguments('style', cls._keywords_style, attributes)

        # Instantiate.
        instance = cls(**attributes)

        # Note child elements.
        if children:
            for c in children:
                instance.append(c)

        # Generate ID based on finalized instance, in case that matters.
        if set_id:
            instance.set_id()

        return instance

    @classmethod
    def _python_to_svg_key(cls, string_key):
        return string_key.replace('_', '-')

    @classmethod
    def _svg_to_python_key(cls, string_key):
        return string_key.replace('-', '_')

    @classmethod
    def _filter_arguments(cls, attribute_name, roster, subject):
        '''Alter subject dictionary.

        This is intended primarily to place arguments to new() in the
        SVG "style" attribute without forcing the user to specify that,
        by means of inference from a list of legal style keywords.

        '''

        # Fetch unfiltered, explicit content of attribute:
        caught = subject.pop(attribute_name, {})

        # Transform, temporarily, into a dictionary with SVG keys intact:
        if caught:
            caught = (p.split(':') for p in caught.split(';') if p)
            caught = {k: v for k, v in caught}
        elif caught == '':
            caught = {}
        elif not isinstance(caught, collections.abc.Mapping):
            s = 'Discarding unexpected value for {}: {}'
            logging.warning(s.format(attribute_name, repr(caught)))
            caught = {}

        # Add new properties from subject dictionary:
        for python_key in tuple(subject):
            svg_key = cls._python_to_svg_key(python_key)
            if svg_key in roster and svg_key not in caught:
                value = subject.pop(python_key)
                caught[svg_key] = value

        # Destroy dummy values:
        for svg_key, value in tuple(caught.items()):
            if value == '':
                # A dummy inserted to pre-empt filtering by this method.
                caught.pop(svg_key)

        # Reinsert the attribute, as a string, into the subject dictionary:
        if caught:
            s = ';'.join(':'.join(map(str, p)) for p in sorted(caught.items()))
            subject[attribute_name] = s

    def set_id(self):
        '''Generate and set a representative SVG "id" attribute.

        A means of up-to-date reflection of contents likely to differ
        from one instance of the class to another.

        Intended primarily for use with the "defs" section of an SVG
        document, and further intended to avoid unnecessary duplicates
        in that section by means of possible content-specific overrides
        in subclasses.

        '''
        id_ = self.make_id()
        self.set('id', id_)
        return id_

    def make_id(self):
        '''Generate a string for use as an "id" attribute.'''
        return ''.join((self._id_prefix, str(next(self._id_iterator))))


class IDElement(SVGElement):
    '''A very minor tweak to set an ID by default.'''

    @classmethod
    def new(cls, set_id=True, **attributes):
        return super().new(set_id=set_id, **attributes)
