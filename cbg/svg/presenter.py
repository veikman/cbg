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

import cbg.elements as elements
import cbg.misc as misc
import cbg.sample as sample
from cbg.svg import cursor
from cbg.svg import path


NAMESPACE_SVG = 'http://www.w3.org/2000/svg'
NAMESPACE_XML = 'http://www.w3.org/XML/1998/namespace'

# An early draft of CBG used the svgwrite module.
# The svgwrite module included two more namespaces by default:
# ev = 'http://www.w3.org/2001/xml-events'
# xlink = 'http://www.w3.org/1999/xlink'


class SVGPresenter():
    '''An abstract base class with a set of methods for producing SVG code.

    Different subclasses of this are defined for cards and each of their
    fields. These subclasses are then instantiated by content owners in
    the same category: A card content object instantiates its card
    presenter, and so on. This is because presenters may seek to
    coordinate, traversing their content owners to do so.

    '''

    wardrobe = sample.wardrobe.WARDROBE

    # Canvas size is typically set for cards only.
    size = None

    def __init__(self, parent):
        self.parent = parent

    def front(self):
        '''Produce SVG XML for the front/main content side of the card.'''
        raise NotImplementedError

    def back(self):
        '''Produce SVG XML for the back/alternate side of the card.'''
        raise NotImplementedError

    def reset(self, origin=None):
        '''Prepare for placement.

        The card-level origin is an offset relative to the page.
        Subordinate presenters use this to determine coordinates.

        '''
        self.origin = numpy.array(origin) if origin is not None else origin

        self._from_top = None
        self._from_bottom = None
        if self.size:
            self._from_top = cursor.FromTop(self)
            self._from_bottom = cursor.FromBottom(self)

        self.wardrobe.reset()

        # Insert new elements from top by default.
        self.top_down()

    @property
    def g(self):
        '''The closest SVG representer on the same card that has a canvas size.

        The method is named after the SVG code for a group: 'g'.

        '''
        if self.size is not None:
            return self
        return self._true_parent(self.parent)

    @property
    def card(self):
        '''The top-level representation of the card, "above" the graphics.'''
        return self.g.parent

    def top_down(self):
        self.g.cursor = self.g._from_top
        return self.g.cursor

    def bottom_up(self):
        self.g.cursor = self.g._from_bottom
        return self.g.cursor

    def line_feed(self):
        return self.g.cursor.text(self.wardrobe.size.base,
                                  self.wardrobe.size.line_height)

    def _wrap(self, content, initial, subsequent):
        return textwrap.wrap(content, width=self._characters_per_line,
                             initial_indent=initial,
                             subsequent_indent=subsequent)

    @property
    def _characters_per_line(self):
        '''The maximum number of characters printable on each line.'''
        space = self.g.size.interior_width
        character_height = float(self.wardrobe.size)
        character_width = self.wardrobe.width_to_height * character_height
        return int(space / character_width)

    @classmethod
    def new_tree(cls):
        '''Create an empty SVG 'g' (group) element.

        Normally, each card is represented by one of these elements.
        An XML tree structure is built within the group by passing the tree
        on to lower-level SVG presenters for expansion (by subelements).

        '''
        return lxml.etree.Element('g')

    def insert_text(self, tree, content, ii='', si='', lead='', follow=True):
        '''Insert text that can be multiple lines.

        If inserted from the bottom of the card, the text block will
        still read from top to bottom.

        "ii" is initial indent and "si" is subsequent indent.
        "lead" is a word or phrase that starts the paragraph, following
        the initial indent. Leads are highlighted.

        '''
        card_width = self.g.size.footprint[0]
        margin = self.g.size.outer + 2 * self.g.size.inner
        horizontal = self.wardrobe.horizontal(card_width, margin)

        lines = self._wrap(lead + content, ii, si)
        first = [True] + [False] * (len(lines) - 1)
        if self.g.cursor.flip_line_order:
            lines = lines[::-1]
            first = first[::-1]

        for line, top in zip(lines, first):
            position = self.g.origin + (horizontal, self.line_feed())
            attrib = self._attrdict_text(position)
            element = lxml.etree.SubElement(tree, 'text', attrib)

            if top and lead:
                self._formatted_paragraph_lead(element, line, ii, lead)
            else:
                element.text = line

        if follow:
            self.g.cursor.slide(self.wardrobe.size.after_paragraph)

    def insert_tagbox(self, tree, content):
        lines = self._wrap(content, '', '')

        # If there is text to be drawn, draw a thick line under it,
        # which we can call a box. Otherwise, make the line thin, not
        # so box-like.
        textheight = len(lines) * self.wardrobe.size.line_height
        extra = self.g.size.inner
        boxheight = textheight + extra

        # Determine the vertical level of the line. Don't "move" yet.
        self.g.cursor.slide(boxheight / 2)
        line_level = self.g.origin + (0, self.g.cursor.slide(0))
        self.g.cursor.slide(-boxheight / 2)

        # Determine the two anchor points of the line.
        a = line_level + (self.g.size.outer, 0)
        b = line_level + (self.g.size.footprint[0] - self.g.size.outer, 0)

        # Encode the line.
        self.wardrobe.mode_accent(stroke=True)
        attrib = self._attrdict_line(a, b, boxheight)
        if not lines:
            attrib['stroke-dasharray'] = '3, 3'
        lxml.etree.SubElement(tree, 'line', attrib)

        if lines:
            # Add text to the box.
            self.wardrobe.reset()
            self.wardrobe.emphasis(bold=True, stroke=True)
            self.wardrobe.mode_contrast(fill=True)

            self.g.cursor.slide(extra / 2)
            self.insert_text(tree, content)
            self.g.cursor.slide(extra / 2)
        else:
            self.g.cursor.slide(extra)
        self.g.cursor.slide(self.g.size.inner)

    def put_path(self, tree, pathfinder):
        '''Add the effects of a cbg.svg.path.Pathfinder to a tree.

        Automatically stroke the path with the thickness of the card size's
        border, on the assumption that we're making a frame.

        '''
        attrib = pathfinder.attrdict()
        attrib['fill'] = 'none'
        attrib.update(self.wardrobe.dict_svg_stroke(self.size.outer))
        lxml.etree.SubElement(tree, 'path', attrib)

    def put_circle(self, tree, content, origin):
        '''Put a figure in a small circle along the border.

        The origin argument must refer to something with the EdgePoint
        API.

        '''
        radius = self.wardrobe.size.base
        point = self.g.origin + origin.displaced(radius)

        attrib = self._attrdict_circle(point, radius)
        lxml.etree.SubElement(tree, 'circle', attrib)

        self.wardrobe.emphasis(bold=True, stroke=True)
        self.wardrobe.mode_contrast(fill=True)
        point = point + (0, self.wardrobe.size.base / 4)
        attrib = self._attrdict_text(point)
        lxml.etree.SubElement(tree, 'text', attrib).text = content

    def _formatted_paragraph_lead(self, text_element, line, ii, lead):
        '''Set the first part of a line in bold.'''
        span = lxml.etree.SubElement(text_element, 'tspan',
                                     {'style': 'font-weight:bold'})
        span.text = lead
        try:
            span.tail = line.split(ii + lead, 1)[1]
        except IndexError:
            s = 'Failed to split line "{}" after paragraph lead.' \
                ' Lead too long for anything to fit after it?'
            logging.critical(s.format(line, lead))
            raise

    def _attrdict_text(self, position):
        ret = self.wardrobe.dict_svg_font()
        ret['x'], ret['y'] = misc.rounded(position)
        ret.update(self.g.cursor.transform.attrdict(position=position))
        ret['{{{}}}space'.format(NAMESPACE_XML)] = 'preserve'
        return ret

    def _attrdict_line(self, a, b, width):
        if width is None:
            width = self.inner
        ret = self.wardrobe.dict_svg_stroke(width)
        ret['x1'], ret['y1'] = misc.rounded(a)
        ret['x2'], ret['y2'] = misc.rounded(b)
        return ret

    def _attrdict_rect(self, offset, size, rounding=None):
        ret = self.wardrobe.dict_svg_fill()
        ret['width'], ret['height'] = misc.rounded(size)
        position = self.origin + offset
        ret['x'], ret['y'] = misc.rounded(position)
        ret.update(self.g.cursor.transform.attrdict(position=position))
        if rounding is not None:
            ret['rx'] = misc.rounded(rounding)
            ret['ry'] = misc.rounded(rounding)
        return ret

    def _attrdict_circle(self, position, radius):
        ret = self.wardrobe.dict_svg_fill()
        ret['cx'], ret['cy'] = misc.rounded(position)
        ret['r'] = misc.rounded(radius)
        return ret

    def _true_parent(self, object_):
        '''A fairly ugly and fragile method of looking above.

        It is assumed that a higher-level SVG presenter is composited
        onto an object reachable by a chain of "parent" attributes,
        and named "presenter".

        '''
        if hasattr(object_, 'presenter'):
            if isinstance(object_.presenter, SVGPresenter):
                if object_.presenter.size is not None:
                    return object_.presenter
        if hasattr(object_, 'parent'):
            return self._true_parent(object_.parent)
        s = 'Unable to locate true parent of {} after searching to {}.'
        raise Exception(s.format(self, object_.__class__))


class SVGCard(SVGPresenter):
    '''An object composited to a playing card, producing SVG code.

    When outputting SVG, the card is a generic 'g' (group) element, intended
    for assignment to a parent (a page).

    '''

    size = sample.size.STANDARD_EURO

    def front(self, origin):
        self.reset(origin=origin)
        tree = self.new_tree()

        # jump() is used here in preference to slide() because we are
        # working with shallow copies, whose cursors actually share state.
        self.bottom_up().jump(1.6 * self.size.outer)
        self.top_down().jump(self.size.outer)

        for field in self.parent:
            field.presenter.front(tree)

        self._frame(tree)
        return tree

    def back(self, origin):
        '''Start a third of the way down. No frame.'''

        self.reset(origin=origin)
        tree = self.new_tree()

        self.top_down().jump(self.size.footprint[1] / 3)

        for field in self.parent:
            field.presenter.back(tree)

        return tree

    def _frame(self, tree):
        '''Frame an XML object (tree) in a border.'''

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
        self.put_path(tree, pathfinder)


class SVGField(SVGPresenter):
    '''Presenter of some piece of content on the card, e.g. a content field.'''

    def front(self, tree):
        self.reset()
        for paragraph in self.parent:
            self.set_up_paragraph()
            self.insert_text(tree, str(paragraph))

    def back(self, tree):
        '''By default, a field is only represented on the front of a card.'''
        pass

    def set_up_paragraph(self):
        self.wardrobe.reset()
        self.top_down()

    @classmethod
    def as_stylist(cls, card, content):
        '''Instantiate for a temporary field and return the instance.

        An example use case would be a tag field presenter that controls
        what is to be written on the back of a card, based on its tags.
        The text on the back should have a completely different style
        than the tag box on the front, and therefore needs to borrow a
        presenter in the latter style.

        '''
        class TemporaryField(elements.CardContentField):
            presenter_class = cls

        tmp = TemporaryField(card)
        tmp.in_spec(content)
        return tmp.presenter
