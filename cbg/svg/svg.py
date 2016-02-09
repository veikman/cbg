# -*- coding: utf-8 -*-
'''Basic SVG production conveniences.'''

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


import itertools
import logging
import collections

import lxml.etree


# XML namespace names.
NAMESPACE_XML = 'http://www.w3.org/XML/1998/namespace'
NAMESPACE_XLINK = 'http://www.w3.org/1999/xlink'
NAMESPACE_SVG = 'http://www.w3.org/2000/svg'

# An early draft of CBG used the svgwrite module.
# The svgwrite module included another namespace by default:
# ev = 'http://www.w3.org/2001/xml-events'


class KeyValuePairs(dict):
    '''A temporary container for building structured SVG strings.'''

    def __str__(self):
        def iterate():
            for k, v in sorted(self.items()):
                yield ':'.join((python_to_svg_key(k), str(v)))

        return ';'.join(iterate())


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
    #
    #                  # CSS font properties:
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
    def new(cls, children=None, set_id=False, text=None, tail=None,
            nsmap=None, **attributes):
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
        # Note that the nsmap argument (lxml's namespace map convenience)
        # exists here because it must be None or a dict, not a string.

        # Suck some arguments into a style attribute.
        cls._filter_arguments('style', cls._keywords_style, attributes)

        # Instantiate with the keyword properties of the XML node.
        instance = cls(nsmap=nsmap, **attributes)

        # lxml treats internal and trailing content as attributes.
        if text is not None:
            instance.text = text
        if tail is not None:
            instance.tail = tail

        # Note prefabricated child elements, in case they're relevant to an ID.
        if children:
            for c in children:
                instance.append(c)

        # Generate ID based on finalized instance.
        if set_id:
            instance.set_id()

        return instance

    @classmethod
    def _filter_arguments(cls, attribute_name, roster, subject):
        '''Alter subject dictionary.

        This is intended primarily to place arguments to new() in the
        SVG "style" attribute without forcing the user to specify that,
        by means of inference from a list of legal style keywords.

        '''

        # Fetch the unfiltered, explicit content of the attribute:
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
            svg_key = python_to_svg_key(python_key)
            if svg_key in roster:
                value = subject.pop(python_key)
                caught[svg_key] = value  # On collision, override caught.

        # Destroy dummy values using a copy as a stable index:
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

    def append(self, element):
        '''An override.

        Meant only to help troubleshoot the common mistake of not returning
        an instance when overriding new().

        '''
        try:
            super().append(element)
        except TypeError:
            s = 'Cannot append {} to {}.'
            logging.error(s.format(repr(element), repr(self)))
            raise


class IDElement(SVGElement):
    '''A very minor tweak to set an ID by default.'''

    @classmethod
    def new(cls, set_id=True, **attributes):
        return super().new(set_id=set_id, **attributes)


class WardrobeStyledElement(SVGElement):

    @classmethod
    def new(cls, wardrobe=None, transform_ext=None, transform_ext_auto=None,
            **attributes):
        '''Use a provided wardrobe.

        CBG provides a wardrobe class as a convenience for generating
        certain common stylistic attributes systematically.

        '''
        if wardrobe:
            if transform_ext is None:
                transform_ext = transform_ext_auto

            auto = wardrobe.to_svg_attributes(transform_ext)
            auto.update(attributes)
            attributes = auto

        return super().new(**attributes)


def python_to_svg_key(string_key):
    '''SVG uses dashes as word separators in its attribute data.'''
    return string_key.replace('_', '-')


def svg_to_python_key(string_key):
    '''Python uses underscores as word separators in its variable names.'''
    return string_key.replace('-', '_')
