# -*- coding: utf-8 -*-
'''Classes and functions that draw visual details on cards in SVG code.'''

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


import textwrap
import logging

import lxml.etree
import numpy

import cbg.misc
import cbg.geometry
from cbg.svg import svg
from cbg.svg import path
from cbg.svg import shapes
from cbg.svg import misc


# Card-level presenter side tokens.
RECURSION_FRONT = 'presenter_class_front'
RECURSION_BACK = 'presenter_class_back'

# XML namespace names.
NAMESPACE_SVG = 'http://www.w3.org/2000/svg'
NAMESPACE_XML = 'http://www.w3.org/XML/1998/namespace'

# An early draft of CBG used the svgwrite module.
# The svgwrite module included two more namespaces by default:
# ev = 'http://www.w3.org/2001/xml-events'
# xlink = 'http://www.w3.org/1999/xlink'


class SVGPresenter(cbg.misc.SearchableTree, svg.SVGElement):
    '''An abstract base class with a set of methods for producing SVG code.

    Different subclasses of this are defined for cards and each of their
    fields. Card presenters are instantiated as a page is layed out, and
    instantiate the field presenters of each of their card's fields.

    Some state information is shared by card and field presenters.

    '''

    TAG = 'g'

    # A recursion attribute name is only set for card presenters.
    recursion_attribute_name = None

    # Size refers to a reserved footprint, rather than a canvas.
    # Must be set for cards.
    size = None

    # Cursors handle the spacing of contents along an axis.
    # Like size, a cursor class must be set for cards.
    # Like size, a cursor is inherited by subordinate presenters, by default.
    cursor_class = None

    @classmethod
    def new(cls, field, parent=None, origin=None, size=None, cursor=None,
            **kwargs):
        '''Produce SVG XML based on a field object.

        In this base class, just create an empty SVG 'g' (group) element.
        Each card and field is represented by one of these elements.
        An XML tree structure is built within the group by appending the
        presenter's tree to higher-level presenters, and ultimately to
        a page or other image.

        Because we're working towards a complete page, coordinates used
        to instantiate shapes, text etc. must be absolute and should
        normally be limited to an assigned area. This is aided by the
        algorithmic finding of an origin and size for a metaphorical
        local canvas. That canvas is not enforced by means of any masked
        SVG object or the like. It is only a convenience, and artistic
        license is applicable. In truth, any presenter may draw anywhere.

        '''
        inst = super().new(**kwargs)
        inst.field = field
        inst.parent = parent
        inst.origin = inst._determine_origin(origin)
        inst.size = inst._determine_size(size)
        inst.cursor = inst._determine_cursor(cursor)

        # A wardrobe class must be composited onto each implementation.
        inst.wardrobe = cls.Wardrobe()

        # Populate the instance's xml object by drawing stuff.
        inst.present()

        return inst

    def _determine_origin(self, origin):
        '''Return the absolute coordinates of the upper left corner of self.

        The coordinates of the upper left corner are referred to as
        self.origin, but are relative to (0, 0), the geometric origin of
        the SVG image itself. (0, 0) is used as a fallback here.

        Arithmetically, self.origin should be treated as the origin of a
        coordinate system local to the presenter. It is an aid to placing
        elements on each card in proper relation to the image as a whole.

        '''
        if origin is None:
            try:
                origin = self.parent.origin
            except AttributeError:
                logging.debug('Defaulting to origin (0, 0).')
                origin = (0, 0)
        assert origin is not None
        return numpy.array(origin)  # For ease of multiplication etc.

    def _determine_size(self, size):
        '''Return the (x, y) extent of self's canvas starting from self.origin.

        The size has many possible sources. In order of decreasing priority:

        * A keyword argument to new(), which is the argument to this method.
        * A field property, set in reaction to field (non-)population.
        * A presenter class property, which should always be set for cards.
        * The parent presenter's size.

        An exception is raised if none of these sources can be used.

        '''
        if size is None:
            size = self.field.presenter_size_override
        if size is None:
            size = self.__class__.size
        if size is None:
            try:
                size = self.parent.size
            except AttributeError:
                s = 'No size defined for presenting {}.'
                logging.error(s.format(self.field))
                raise
        assert size is not None
        return numpy.array(size)  # For ease of multiplication etc.

    def _determine_cursor(self, cursor):
        '''Return a cursor object, or None.'''
        if cursor is None:
            if self.cursor_class:
                cursor = self.cursor_class(self)
        if cursor is None:
            try:
                cursor = self.parent.cursor
            except AttributeError:
                logging.debug('No cursor.')
        return cursor

    def present(self):
        '''To be overridden for all the SVG drawing work.'''
        self.recurse()

    def recurse(self, **kwargs):
        '''Present all inner fields at once.'''
        return tuple(self._iterate_through_recursion(**kwargs))

    def _iterate_through_recursion(self, **kwargs):
        '''Iterate through the presentation of inner fields.

        This could have been handled by each field, except that
        presenters are allowed to control the order of events, as a
        means of controlling occlusion in the resulting image.

        '''
        card = self._search_single(lambda p: p.recursion_attribute_name)

        if card is None:
            s = 'Unable to recursively present subordinate fields.'
            raise Exception(s)

        yield from self._represent_child_fields(card.recursion_attribute_name,
                                                **kwargs)

    def _represent_child_fields(self, attribute_name, **kwargs):
        '''Generate presenters for content fields within the parent field.'''
        for field in self.field:
            presenter_class = getattr(field, attribute_name)
            if presenter_class:
                presenter = presenter_class.new(field, parent=self, **kwargs)
                self.append(presenter)
                yield (field, presenter)

    def define(self, xml):
        '''Take an etree oject. Add as a definition if new, else ignore.'''

        id_ = xml.get('id')

        if id_ is None:
            s = 'Definitions must have an "id" attribute set. "{}" does not.'
            raise ValueError(s.format(lxml.etree.tostring(xml)))

        # Avoid duplicates by ID, to keep the SVG clean.
        for element in self.defs.iter():
            if element.get('id') == id_:
                if lxml.etree.tostring(element) == lxml.etree.tostring(xml):
                    logging.debug('Excluding duplicate definition.')
                    return
                else:
                    s = 'Dissimilar definitions with shared ID ({}).'
                    raise ValueError(s.format(id_))

        self.defs.append(xml)

    @property
    def defs(self):
        '''Access registered definitions.

        The defs element is maintained at the second highest level of the
        SVG object hierarchy.

        '''
        return self.image.defs

    @property
    def image(self):
        '''Access the top-level SVG element: the image.'''
        image = self._search_single(lambda p: p.tag == 'svg')

        if image is None:
            s = 'Cannot trace SVG lineage from {} to its parent image.'
            raise Exception(s)
        elif image.getparent() is not None:  # lxml method.
            s = 'Failed to identify parent image: Candidate has a parent.'
            raise Exception(s)

        return image

    def _presenter_with(self, attribute_name, select_value):
        '''A method used to make methods for upward presenter tree search.'''

        value = getattr(self, attribute_name)
        if value is None:
            if self.parent is None:
                # Recurse upwards.
                s = 'No presenter with attribute "{}".'
                raise AttributeError(s.format(attribute_name))
            else:
                return self.parent._presenter_with(attribute_name,
                                                   select_value)
        elif select_value:
            return value

        else:
            return self

    def line_feed(self):
        '''Advance the cursor by the height of a line of text.'''
        return self.cursor.text(self.wardrobe.font_size,
                                self.wardrobe.line_height)

    def insert_frame(self, thickness=None, outside_radius=None):
        '''Create a border inside the edges of the canvas.'''

        if thickness is None:
            thickness = self.wardrobe.mode.thickness
        if outside_radius is None:
            outside_radius = 2 * thickness

        middle = thickness / 2
        area = cbg.geometry.Rectangle(self.size)
        pathfinder = path.Path.Pathfinder()

        corners = area.corners(offset=middle)
        joins = area.corner_offsets((outside_radius - middle, middle))

        for corner, pair in zip(corners, joins):
            a, b = map(lambda p: p + self.origin, pair)
            c = corner + self.origin
            if pathfinder:
                pathfinder.lineto(a)
            else:
                pathfinder.moveto(a)
            pathfinder.quadratic_bezier_curveto(c, b)

        pathfinder.closepath()
        self.append(path.Path.new(pathfinder,
                                  fill='none', wardrobe=self.wardrobe))

    def insert_circle(self, centerpoint=None, radius=None):
        '''Put a circle anywhere.'''
        if centerpoint is None:
            # Put it in the middle of the local canvas.
            centerpoint = self.origin + self.size / 2

        if radius is None:
            radius = self.wardrobe.mode.thickness

        shape = shapes.Circle.new(centerpoint, radius,
                                  wardrobe=self.wardrobe)
        self.append(shape)
        return shape

    def insert_rect(self, offset, size, rounding=None):
        '''Put a rectangle anywhere.

        Deprecated. Rect should be called directly.

        '''
        position = self.origin + offset
        shape = shapes.Rect.new(position, size, rounding=rounding,
                                wardrobe=self.wardrobe)
        self.append(shape)
        return shape

    def insert_paragraph(self, content, initial_indent='',
                         subsequent_indent='', lead='', follow=True):
        '''Insert text that can be multiple lines.

        If inserted from the bottom of the card, the text block will
        still read from top to bottom.

        "subsequent_indent" is used for indentation after the first line,
        as in the textwrap package.

        "lead" is a word or phrase that starts the paragraph, following
        the initial indent. Leads are highlighted.

        '''
        lines = self._wrap(lead + content, initial_indent, subsequent_indent)
        first = [True] + [False] * (len(lines) - 1)
        if self.cursor.flip_line_order:
            lines = lines[::-1]
            first = first[::-1]

        x_relative = self.wardrobe.horizontal_anchor(self.size[0])
        for line, top in zip(lines, first):
            position = self.origin + (x_relative, self.line_feed())
            element = misc.Text.new(position, wardrobe=self.wardrobe)
            self.append(element)

            if top and lead:
                self._formatted_paragraph_lead(element, line, initial_indent,
                                               lead)
            else:
                element.text = line

        if follow:
            self.cursor.slide(self.wardrobe.after_paragraph)

    def _wrap(self, content, initial, subsequent):
        return textwrap.wrap(content, width=self._characters_per_line,
                             initial_indent=initial,
                             subsequent_indent=subsequent)

    @property
    def _characters_per_line(self):
        '''The maximum number of characters printable on each line.'''
        return int(self.size[0] / self.wardrobe.character_width)

    def _formatted_paragraph_lead(self, text_element, line, ii, lead):
        '''Set the first part of a line in bold.'''
        span = misc.Text.Span.new(text=lead, font_weight='bold')
        text_element.append(span)
        try:
            span.tail = line.partition(ii + lead)[2]
        except IndexError:
            s = ('Failed to split line "{}" after paragraph lead "{}". '
                 'Lead too long for a word to fit after it?')
            logging.critical(s.format(line, lead))
            raise


class FramedLayout(SVGPresenter):
    '''Automatic indentation to the inside of a parent presenter's frame.

    The frame is expected to be drawn by a parent presenter, governed by
    the thickness attribute of that presenter's wardrobe.

    The advantage of separating this layouting function from the framing
    presenter itself is that you can easily have two of these layouts per
    card, proceeding in opposite directions, by using opposite cursor
    classes.

    '''

    def _determine_origin(self, _):
        '''An override.'''
        frame = self.parent.wardrobe.mode.thickness
        origin = (self.parent.origin[0] + frame, self.parent.origin[1] + frame)
        return super()._determine_origin(origin)

    def _determine_size(self, _):
        '''An override.'''
        frame = self.parent.wardrobe.mode.thickness
        size = (self.parent.size[0] - 2 * frame,
                self.parent.size[1] - 2 * frame)
        return super()._determine_size(size)


class IndentedPresenter(SVGPresenter):
    '''A presenter that reduces its own canvas on creation.

    Like FramedLayout, but independent of a parent, and controllable in
    its particulars.

    The primary use case for this class is to follow FramedLayout for the
    presentation of pure text elements that need some clear space to the
    inside of the frame. Therefore, the default indentation is purely
    horizontal.

    '''

    indentation = cbg.misc.Compass(0, 0.8)

    def _determine_origin(self, origin):
        '''An override.'''
        origin = super()._determine_origin(origin)
        return numpy.array((origin[0] + self.indentation.left,
                            origin[1] + self.indentation.top))

    def _determine_size(self, size):
        '''An override.'''
        size = super()._determine_size(size)
        return numpy.array((size[0] - self.indentation.horizontal,
                            size[1] - self.indentation.vertical))


class TextPresenter(IndentedPresenter):
    '''A presenter that handles pure text contents pretty well on its own.'''

    def insert_paragraphs(self):
        '''An almost-bare-bones insertion of typical all-text content.'''
        for paragraph in self.field:
            self.set_up_paragraph()
            self.insert_paragraph(str(paragraph))

    def set_up_paragraph(self):
        '''To be overridden.'''
        pass

    def present(self):
        self.insert_paragraphs()
