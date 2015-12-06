# -*- coding: utf-8 -*-
'''Classes and functions that draw visual details on cards in SVG code.

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

import textwrap
import logging

import lxml.etree
import numpy

import cbg.misc as misc
import cbg.sample as sample
import cbg.svg.cursor
from cbg.svg import path
from cbg.svg import shapes


NAMESPACE_SVG = 'http://www.w3.org/2000/svg'
NAMESPACE_XML = 'http://www.w3.org/XML/1998/namespace'

# An early draft of CBG used the svgwrite module.
# The svgwrite module included two more namespaces by default:
# ev = 'http://www.w3.org/2001/xml-events'
# xlink = 'http://www.w3.org/1999/xlink'


class SVGPresenter():
    '''An abstract base class with a set of methods for producing SVG code.

    Different subclasses of this are defined for cards and each of their
    fields. Card presenters are instantiated as a page is layed out, and
    instantiate the field presenters of each of their card's fields.

    Some state information is shared by card and field presenters.

    '''

    wardrobe = sample.wardrobe.WARDROBE

    # Canvas size is typically set for cards only.
    size = None

    def __init__(self, content_source, parent_presenter=None, defs=None,
                 origin=None):
        '''Produce SVG XML based on some content: the content_source object.

        In this base class, just create an empty SVG 'g' (group) element.
        Each card and field is represented by one of these elements.
        An XML tree structure is built within the group by appending the
        presenter's tree to higher-level presenters, and ultimately to
        a page.

        Because we're working towards a complete page, coordinates must
        be absolute. If the presenter has a canvas of its own, the
        absolute coordinates of the origin of that canvas must be provided.

        '''
        self.content_source = content_source
        self.parent_presenter = parent_presenter

        # The defs element is maintained at the second highest level of the
        # SVG document, by the page. Refer to the Page class.
        #
        # When a chain of presenters is instantiated in the application
        # model, the top presenter receives a reference to the defs element,
        # which is manipulated through the "define" method of the presenter.
        self._defs = defs

        if self.size is not None and origin is None:
            raise ValueError('A presenter with a size must have an origin.')
        self._origin = numpy.array(origin) if origin is not None else origin

        self._reset_cursors()
        self.wardrobe.reset()

        self.xml = lxml.etree.Element('g')

    def _reset_cursors(self):
        self._cursor = None  # Pointer to currently active cursor.
        self._from_top = None
        self._from_bottom = None

        if self is self.canvas_owner:
            self._from_top = cbg.svg.cursor.FromTop(self)
            self._from_bottom = cbg.svg.cursor.FromBottom(self)

        self.top_down()

    def _presenter_with(self, attribute_name, select_value):
        '''A method used to make methods for upward presenter tree search.'''

        value = getattr(self, attribute_name)
        if value is None:
            if self.parent_presenter is None:
                # Recurse upwards.
                s = 'No presenter with attribute "{}".'
                raise AttributeError(s.format(attribute_name))
            else:
                return self.parent_presenter._presenter_with(attribute_name,
                                                             select_value)
        elif select_value:
            return value
        else:
            return self

    @property
    def cursor(self):
        return self._presenter_with('_cursor', True)

    @property
    def cursor_from_top(self):
        return self._presenter_with('_from_top', True)

    @property
    def cursor_from_bottom(self):
        return self._presenter_with('_from_bottom', True)

    @property
    def canvas_owner(self):
        return self._presenter_with('size', False)

    @property
    def defs(self):
        return self._presenter_with('_defs', True)

    @property
    def origin(self):
        return self._presenter_with('_origin', True)

    def define(self, xml):
        '''Take an etree oject. Add as a definition if new, else ignore.'''

        id_ = xml.get('id')

        if id_ is None:
            s = 'Definitions must have a set "id" attribute. "{}" does not.'
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

    def top_down(self):
        self.canvas_owner._cursor = self.cursor_from_top

    def bottom_up(self):
        self.canvas_owner._cursor = self.cursor_from_bottom

    def line_feed(self):
        return self.cursor.text(self.wardrobe.size.base,
                                self.wardrobe.size.line_height)

    def insert_text(self, content, ii='', si='', lead='', follow=True):
        '''Insert text that can be multiple lines.

        If inserted from the bottom of the card, the text block will
        still read from top to bottom.

        "ii" is initial indent and "si" is subsequent indent.
        "lead" is a word or phrase that starts the paragraph, following
        the initial indent. Leads are highlighted.

        '''
        size = self.canvas_owner.size
        card_width = size[0]
        margin = size.outer + 2 * size.inner
        horizontal = self.wardrobe.horizontal(card_width, margin)

        lines = self._wrap(lead + content, ii, si)
        first = [True] + [False] * (len(lines) - 1)
        if self.cursor.flip_line_order:
            lines = lines[::-1]
            first = first[::-1]

        for line, top in zip(lines, first):
            position = self.origin + (horizontal, self.line_feed())
            attrib = self._attrdict_text(position)
            element = lxml.etree.SubElement(self.xml, 'text', attrib)

            if top and lead:
                self._formatted_paragraph_lead(element, line, ii, lead)
            else:
                element.text = line

        if follow:
            self.cursor.slide(self.wardrobe.size.after_paragraph)

    def insert_tagbox(self, content):
        lines = self._wrap(content, '', '')

        # If there is text to be drawn, draw a thick line under it,
        # which we can call a box. Otherwise, make the line thin, not
        # so box-like.
        textheight = len(lines) * self.wardrobe.size.line_height
        extra = self.canvas_owner.size.inner
        boxheight = textheight + extra

        # Determine the vertical level of the line. Don't "move" yet.
        self.cursor.slide(boxheight / 2)
        line_level = self.origin + (0, self.cursor.slide(0))
        self.cursor.slide(-boxheight / 2)

        # Determine the two anchor points of the line.
        size = self.canvas_owner.size
        a = line_level + (size.outer, 0)
        b = line_level + (size[0] - size.outer, 0)

        # Encode the line.
        self.wardrobe.mode_accent(stroke=True)
        attrib = self._attrdict_line(a, b, boxheight)
        if not lines:
            attrib['stroke-dasharray'] = '3, 3'
        lxml.etree.SubElement(self.xml, 'line', attrib)

        if lines:
            # Add text to the box.
            self.wardrobe.reset()
            self.wardrobe.emphasis(bold=True, stroke=True)
            self.wardrobe.mode_contrast(fill=True)

            self.cursor.slide(extra / 2)
            self.insert_text(content)
            self.cursor.slide(extra / 2)
        else:
            self.cursor.slide(extra)
        self.cursor.slide(self.canvas_owner.size.inner)

    def put_path(self, pathfinder):
        '''Add the effects of a cbg.svg.path.Pathfinder to a tree.

        Automatically stroke the path with the thickness of the card size's
        border, on the assumption that we're making a frame.

        '''
        attrib = pathfinder.attrdict()
        attrib['fill'] = 'none'
        attrib.update(self.wardrobe.dict_svg_stroke(self.size.outer))
        lxml.etree.SubElement(self.xml, 'path', attrib)

    def put_circle(self, content, origin):
        '''Put a figure in a small circle along the border.

        The origin argument must refer to something with the EdgePoint
        API.

        '''
        radius = self.wardrobe.size.base
        point = self.origin + origin.displaced(radius)

        attrib = self._attrdict_circle(point, radius)
        lxml.etree.SubElement(self.xml, 'circle', attrib)

        self.wardrobe.emphasis(bold=True, stroke=True)
        self.wardrobe.mode_contrast(fill=True)
        point = point + (0, self.wardrobe.size.base / 4)
        attrib = self._attrdict_text(point)
        lxml.etree.SubElement(self.xml, 'text', attrib).text = content

    def insert_frame(self):
        '''Frame the object in a border.'''

        o = self.size.outer
        pathfinder = path.Pathfinder()

        joins = self.size.corner_offsets((1.5 * o, 0.5 * o))
        for corner, pair in zip(self.size.corners(), joins):
            a, b = map(lambda p: p + self.origin, pair)
            c = corner.displaced((0.5 * o, 0.5 * o)) + self.origin
            if pathfinder:
                pathfinder.lineto(a)
            else:
                pathfinder.moveto(a)
            pathfinder.quadratic_bezier_curveto(c, b)

        pathfinder.closepath()
        self.put_path(pathfinder)

    def insert_rect(self, offset, size, rounding=None):
        '''Put a rectangle anywhere.'''
        position = self.origin + offset
        extra = self.cursor.transform.attrdict(position=position)
        shape = shapes.Rect.new(position, size, rounding=rounding,
                                wardrobe=self.wardrobe, **extra)
        self.xml.append(shape)
        return shape

    def _wrap(self, content, initial, subsequent):
        return textwrap.wrap(content, width=self._characters_per_line,
                             initial_indent=initial,
                             subsequent_indent=subsequent)

    @property
    def _characters_per_line(self):
        '''The maximum number of characters printable on each line.'''
        space = self.canvas_owner.size.interior_width
        character_height = float(self.wardrobe.size)
        character_width = self.wardrobe.width_to_height * character_height
        return int(space / character_width)

    def _formatted_paragraph_lead(self, text_element, line, ii, lead):
        '''Set the first part of a line in bold.'''
        span = lxml.etree.SubElement(text_element, 'tspan',
                                     {'style': 'font-weight:bold'})
        span.text = lead
        try:
            span.tail = line.partition(ii + lead)[2]
        except IndexError:
            s = ('Failed to split line "{}" after paragraph lead "{}". '
                 'Lead too long for a word to fit after it?')
            logging.critical(s.format(line, lead))
            raise

    def _attrdict_text(self, position):
        ret = self.wardrobe.dict_svg_font()
        ret['x'], ret['y'] = misc.rounded(position)
        ret.update(self.cursor.transform.attrdict(position=position))
        ret['{{{}}}space'.format(NAMESPACE_XML)] = 'preserve'
        return ret

    def _attrdict_line(self, a, b, width):
        if width is None:
            width = self.inner
        ret = self.wardrobe.dict_svg_stroke(width)
        ret['x1'], ret['y1'] = misc.rounded(a)
        ret['x2'], ret['y2'] = misc.rounded(b)
        return ret

    def _attrdict_circle(self, position, radius):
        ret = self.wardrobe.dict_svg_fill()
        ret['cx'], ret['cy'] = misc.rounded(position)
        ret['r'] = misc.rounded(radius)
        return ret


class CardBase(SVGPresenter):
    '''Superclass SVG presenter for one side of a playing card.'''

    size = sample.size.STANDARD_EURO

    def _represent_fields(self, attribute_name):
        for field in self.content_source:
            presenter_class = getattr(field, attribute_name)
            if presenter_class:
                presenter = presenter_class(field, parent_presenter=self)
                self.xml.append(presenter.xml)


class CardFront(CardBase):
    '''Example behaviour for the front of a card. Frames the content.'''

    def __init__(self, content_source, **kwargs):
        super().__init__(content_source, **kwargs)

        # jump() is used here in preference to slide() because we are
        # working with shallow copies, whose cursors actually share state.
        self.bottom_up()
        self.cursor.jump(1.6 * self.size.outer)
        self.top_down()
        self.cursor.jump(self.size.outer)

        self._represent_fields('presenter_class_front')
        self.insert_frame()


class CardBack(CardBase):
    '''Example behaviour for the back of a card.

    This starts a third of the way down on the assumption that a simple
    deck will only have a word or two on the back of each card, naming
    the deck itself.

    '''

    def __init__(self, content_source, **kwargs):
        super().__init__(content_source, **kwargs)

        self.cursor.jump(self.size[1] / 3)

        self._represent_fields('presenter_class_back')


class FieldBase(SVGPresenter):
    '''Presenter of some piece of content on the card, such as a title.'''

    def insert_paragraphs(self):
        '''An almost-bare-bones insertion of typical all-text content.'''
        for paragraph in self.content_source:
            self.set_up_paragraph()
            self.insert_text(str(paragraph))

    def set_up_paragraph(self):
        '''To be overridden.'''
        self.top_down()
        self.wardrobe.reset()


class FieldOfText(FieldBase):
    '''A tiny bit of added default behaviour.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_paragraphs()
