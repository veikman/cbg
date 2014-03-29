# -*- coding: utf-8 -*-

import textwrap
import re
import logging

import lxml.etree
import numpy

from . import misc

NAMESPACE_SVG = 'http://www.w3.org/2000/svg'
NAMESPACE_XML = 'http://www.w3.org/XML/1998/namespace'

## An early draft used the svgwrite module.
## The svgwrite module included two more namespaces by default:
# ev = 'http://www.w3.org/2001/xml-events'
# xlink = 'http://www.w3.org/1999/xlink'

LOWER_RIGHT_CORNER = 'lower_right_corner'

class SVGPresenter():
    '''A superclass with a set of methods for producing SVG code.
    
    Different subclasses of this are composited onto main card objects
    and each of their fields.
    
    '''

    def __init__(self, parent, wardrobe, size=None):
        self.parent = parent
        self.wardrobe = wardrobe
        self.size = size

        self._from_top = None
        self._from_bottom = None
        self.point = dict()
        if self.size:
            self._from_top = CursorFromTop(self)
            self._from_bottom = CursorFromBottom(self)
            self.point[LOWER_RIGHT_CORNER] = LowerRightCorner(self)

        ## Insert new elements from top by default.
        self.top_down()
        self.origin = None

    def __call__(self):
        '''Produce SVG XML.'''
        raise NotImplementedError

    @property
    def g(self):
        '''The closest SVG representer on the same card that has a size.
       
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
            initial_indent=initial, subsequent_indent=subsequent)

    @property
    def _characters_per_line(self):
        '''The maximum number of characters printable on each line.'''
        space = self.g.size.footprint[0] \
                    - 2 * self.g.size.outer - 2 * self.g.size.inner
        character_height = float(self.wardrobe.size)
        character_width = self.wardrobe.width_to_height * character_height
        return int(space / character_width)

    def insert_text(self, tree, content, ii='', si='', lead='', follow=True):
        '''Insert text that can be multiple lines.
        
        If inserted from the bottom of the card, the text block will
        still read from top to bottom.
        
        "ii" is initial indent and "si" is subsequent indent.
        "lead" is an eyecatching word or phrase that starts the
        paragraph, following the initial indent. The lead is printed
        in bold type.
        
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

    def insert_tagbox(self, tree, content):
        lines = self._wrap(content, '', '')

        ## If there is text to be drawn, draw a thick line under it,
        ## which we can call a box. Otherwise, make the line thin, not
        ## so box-like.
        textheight = len(lines) * self.wardrobe.size.line_height
        extra = self.g.size.inner
        boxheight = textheight + extra

        ## Determine the vertical level of the line. Don't "move" yet.
        self.g.cursor.slide(boxheight/2)
        line_level = self.g.origin + (0, self.g.cursor.slide(0))
        self.g.cursor.slide(-boxheight/2)

        ## Determine the two anchor points of the line.
        a = line_level + (self.g.size.outer, 0)
        b = line_level + (self.g.size.footprint[0] - self.g.size.outer, 0)

        ## Encode the line.
        self.wardrobe.mode_accent(stroke=True)
        attrib = self._attrdict_line(a, b, boxheight)
        if not lines:
            attrib['stroke-dasharray'] = '3mm, 3mm'
        lxml.etree.SubElement(tree, 'line', attrib)

        if lines:
            ## Add text to the box.
            self.wardrobe.reset()
            self.wardrobe.emphasis(bold=True, stroke=True)
            self.wardrobe.mode_contrast(fill=True)

            self.g.cursor.slide(extra/2)
            self.insert_text(tree, content)
            self.g.cursor.slide(extra/2)
        else:
            self.g.cursor.slide(extra)
        self.g.cursor.slide(self.g.size.inner)

    def put_circle(self, tree, content, positionstring):
        '''Put a figure in a small circle along the border.'''
        radius = self.wardrobe.size.base
        point = self.g.origin + self.g.point[positionstring].displace(radius)

        attrib = self._attrdict_circle(point, radius)
        lxml.etree.SubElement(tree, 'circle', attrib)

        self.wardrobe.emphasis(bold=True, stroke=True)
        self.wardrobe.mode_contrast(fill=True)
        point = point + (0, self.wardrobe.size.base/4)
        attrib = self._attrdict_text(point)
        lxml.etree.SubElement(tree, 'text', attrib).text = content

    def _attrdict_text(self, position):
        ret = self.wardrobe.dict_svg_font()
        ret['x'], ret['y'] = mm(position)
        ret['{' + NAMESPACE_XML + '}space'] = 'preserve'
        return ret

    def _attrdict_line(self, a, b, width):
        if width is None:
            width = self.inner
        ret = self.wardrobe.dict_svg_stroke(width)
        ret['x1'], ret['y1'] = mm(a)
        ret['x2'], ret['y2'] = mm(b)
        return ret

    def _attrdict_rect(self, offset, size, rounding=None):
        ret = self.wardrobe.dict_svg_fill()
        ret['width'], ret['height'] = mm(size)
        ret['x'], ret['y'] = mm(self.origin + offset)
        if rounding is not None:
            ret['rx'] = mm(rounding)
            ret['ry'] = mm(rounding)
        return ret

    def _attrdict_circle(self, position, radius):
        ret = self.wardrobe.dict_svg_fill()
        ret['cx'], ret['cy'] = mm(position)
        ret['r'] = mm(radius)
        return ret

    def _true_parent(self, object_):
        '''A fairly ugly and fragile method of looking above.'''
        if hasattr(object_, 'dresser'):
            if isinstance(object_.dresser, SVGPresenter):
                if object_.dresser.size is not None:
                    return object_.dresser
        if hasattr(object_, 'parent'):
            return self._true_parent(object_.parent)
        s = 'Unable to locate true parent of {} after searching to {}.'
        raise Exception(s.format(self, object_.__class__))

class SVGCard(SVGPresenter):
    '''An object composited to a playing card, producing SVG code.
    
    When outputting SVG, the card is a generic 'g' (group) element, intended
    for assignment to a parent (a page).
    
    '''

    def __call__(self, origin):
        self.wardrobe.reset()
        
        ## jump() is used here in preference to slide() because we are
        ## working with shallow copies, whose cursors actually share state.
        self.bottom_up().jump(1.6 * self.size.outer)
        self.top_down().jump(self.size.outer)

        ## The card-level origin is an offset relative to the page.
        ## All the child representers use this to write coordinates.
        self.origin = numpy.array(origin)

        ## The tree is the group--i.e. 'g'--level XML entity, under which
        ## all child representers create their subelements.
        tree = lxml.etree.Element('g')
        ## We start by adding a card frame to it, then call the children.
        self._frame(tree)
        for field in self.parent:
            field.dresser(tree)

        return tree

    def _frame(self, tree):
        attrib = self._attrdict_rect(0, self.size.footprint,
                                 rounding=self.size.outer)
        lxml.etree.SubElement(tree, 'rect', attrib)

        self.wardrobe.mode_contrast(fill=True)
        attrib = self._attrdict_rect(self.size.outer,
                                 self.size.footprint - 2 * self.size.outer,
                                 rounding=self.size.inner)
        lxml.etree.SubElement(tree, 'rect', attrib)

class SVGField(SVGPresenter):
    '''A specialized representer of some piece of content on the card.'''

    def __call__(self, tree):
        for paragraph in self.parent:
            self.set_up_paragraph()
            self.insert_text(tree, str(paragraph))

    def set_up_paragraph(self):
        self.wardrobe.reset()
        self.top_down()

class GraphicsElementCorner():
    '''An immobile alternative to the cursor.'''
    def __init__(self, parent):
        self.parent = parent

    def displace(self, offsets):
        '''Produce coordinates within card, at offsets from corner.
        
        Positive offsets always move toward the next corner on each axis.
        This is to allow blind addition with card origin to get absolute
        coordinates on the page.

        '''
        if not misc.listlike(offsets):
            offsets = (offsets, offsets)
        displacement = [f * o for f, o in zip(self.factors, offsets)]
        return self.position + displacement

class LowerRightCorner(GraphicsElementCorner):
    def __init__(self, parent):
        super().__init__(parent)
        self.position = self.parent.size.footprint
        self.factors = (-1, -1)

class GraphicsElementInsertionCursor():
    '''A direction from which to insert new elements on a card.'''
    def __init__(self, parent):
        self.parent = parent
        self.displacement = 0
        self.flip_line_order = False

    def jump(self, position):
        self.displacement = position

    def slide(self, distance):
        '''Return an appropriate height for the next insertion, and move.'''
        raise NotImplementedError

    def text(self, size, envelope):
        '''A direction-sensitive line feed.'''
        raise NotImplementedError

class CursorFromTop(GraphicsElementInsertionCursor):
    def slide(self, height):
        '''Move first, then suggest insertion at new location.'''
        self.displacement += height
        return self.displacement

    def text(self, size, envelope):
        relevant = self.slide(size)
        self.slide(envelope - size)
        return relevant

class CursorFromBottom(GraphicsElementInsertionCursor):
    def __init__(self, *args):
        super().__init__(*args)
        self.flip_line_order = True

    def slide(self, height):
        '''Insert first, then move (up). State position from top of card.'''
        ret = self.displacement
        self.displacement += height
        return self.parent.size.footprint[1] - ret

    def text(self, size, envelope):
        self.slide(envelope - size)
        return self.slide(size)

def mm(value):
    '''Strings of coordinate pairs etc. in millimetres, for SVG.'''
    if misc.listlike(value):
        return [mm(axis) for axis in value]
    else:
        ## Preserve a maximum of three decimals (0.1µm accuracy).
        return re.sub(r'\.([0-9]{0,4})[0-9]*$', r'.\1', str(value)) + 'mm'
