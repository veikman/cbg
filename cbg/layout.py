# -*- coding: utf-8 -*-
'''Image layouting logic.'''

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


import collections
import logging
import math
import os

import cbg.svg.transform as transform
from cbg.svg.image import Image


class Queue(collections.UserList):
    '''A list of images.

    Based on UserList because it can be desirable to change the order
    of the images after the queue has been populated, as in the example
    application's duplex mode, implemented in this module.

    '''
    def __init__(self, title):
        super().__init__()
        self.title = title

    def new_image_arbitrary(self, *args, **kwargs):
        self.append(Image.new(*args, **kwargs))

    def save(self, destination_folder):
        try:
            os.mkdir(destination_folder)
        except OSError:
            logging.debug('Destination folder already exists.')

        for number, image in enumerate(self):
            name = '{}_{:03d}'.format(self.title, number + 1)
            image.save(os.path.join(destination_folder, name))


class Layouter(Queue):
    '''A manager of the SVG authoring process.

    This could have been an abstract base class, but it turns out
    to be useful in its simplicity.

    '''

    def __init__(self, name, card_list, image_size=None, image_margins=None,
                 arc=None):
        logging.debug('Instantiating layouter.')

        super().__init__(name)

        if not card_list:
            raise ValueError('No cards selected for layouting.')

        self.cards = card_list

        # The keyword arguments are not used by all types of layouter.
        self.image_size = image_size
        self.image_margins = image_margins
        self.arc = arc

        # Predict the smallest and largest numbers cards will have.
        # This informaton can be used by subclasses, for a progress bar etc.
        self.n_min = 1
        self.n_max = len(self.cards)

    @classmethod
    def name_side(self, obverse, reverse):
        if obverse and reverse:
            raise ValueError('Both sides are not to be named.')
        elif not obverse and not reverse:
            raise ValueError('Neither side cannot be named.')

        if obverse:
            return 'obverse'
        elif reverse:
            return 'reverse'

    def run(self, include_obverse, include_reverse):
        '''All the work from layouts to saving the resulting image queue.'''
        if include_obverse:
            self.layout(True, False)

        if include_reverse:
            self.layout(False, True)

        self.sort_images()

    def layout(self, include_obverse, include_reverse):
        '''Treat the obverse side, or the reverse, or both at once.'''
        assert include_obverse or include_reverse

        self.on_layout_start(include_obverse, include_reverse)

        for card_number, card_copy in enumerate(self.cards, start=self.n_min):

            if include_obverse:
                self.consider_copy(card_number, card_copy,
                                   card_copy.presenter_class_front,
                                   True, False)
            if include_reverse:
                self.consider_copy(card_number, card_copy,
                                   card_copy.presenter_class_back,
                                   False, True)

    def on_layout_start(self, obverse, reverse):
        '''Prepare for a round of layouts.'''
        pass

    def consider_copy(self, number, card_copy, presenter_class,
                      obverse, reverse):
        '''Adding a single copy of a card to the latest image.'''
        if not presenter_class:
            s = '{} has no presenter class for the {} side.'
            logging.debug(s.format(card_copy,
                                   self.name_side(obverse, reverse)))
            return

        if not self or not self[-1].can_fit(presenter_class.size):
            self.new_image(card_copy, obverse, reverse)

        origin = self.get_origin(presenter_class.size)
        image = self[-1]
        presenter = presenter_class.new(card_copy, origin=origin,
                                        parent=image)
        self.affix_copy(number, presenter)

    def new_image(self, card, obverse, reverse):
        '''Use image size specifiable via CLI.'''
        name_suffix = self.get_name_suffix(card, obverse, reverse)
        self.new_image_arbitrary(dimensions=self.image_size,
                                 padding=self.image_margins,
                                 left_to_right=obverse,
                                 name_suffix=name_suffix)

    def affix_copy(self, card_number, presenter):
        '''Add one copy of a card to the latest image.'''
        # Using add(), the image will calculate how much space will be left.
        self[-1].add(presenter.size, presenter)

    def get_first_card_size(self, obverse=True):
        if obverse:
            return self.cards[0].presenter_class_front.size
        else:
            return self.cards[0].presenter_class_back.size

    def get_origin(self, card_size):
        return self[-1].free_spot(card_size)

    def get_name_suffix(self, card, obverse, reverse):
        '''Produce a descriptive addition to the filename of a new image.'''
        pass

    def n_normal(self, card_number):
        '''Statistical feature scaling for the given card number.

        Return 0.5 if there is just one card, else 0 to 1.

        '''
        try:
            return (card_number - self.n_min) / (self.n_max - self.n_min)
        except ZeroDivisionError:
            return 0.5

    def sort_images(self):
        '''To be overridden.'''
        pass


class Neighbours(Layouter):
    def run(self, obverse, reverse):
        '''One round of layouting for both sides of cards.'''
        self.layout(True, True)
        self.sort_images()


class Duplex(Layouter):
    def on_layout_start(self, obverse, reverse):
        '''Make sure we start afresh for reverse after obverse.

        In duplex mode, this method is called once for the obverse of each
        card, and once for the reverse, with the expectation that the
        obverse of any card will never appear in an image together with the
        reverse of any card.

        Unfortunately, this will produce a blank page if called for games
        where the cards have no presenters for the reverse side.

        '''
        self.new_image(None, obverse, reverse)

    def get_name_suffix(self, card, obverse, reverse):
        return self.name_side(obverse, reverse)

    def sort_images(self):
        # Alternate between front sheets and back sheets.
        midpoint = len(self) // 2
        tmp = []
        for pair in zip(self[:midpoint], self[midpoint:]):
            tmp.extend(pair)
        self.data = tmp


class Singles(Layouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_margins = (0, 0)

    def get_name_suffix(self, card, obverse, reverse):
        return str(card)

    def new_image(self, card, obverse, reverse):
        '''Use card size as image size, individually for each card.'''
        if obverse:
            self.image_size = card.presenter_class_front.size
        else:
            self.image_size = card.presenter_class_back.size
        super().new_image(card, obverse, reverse)


class Fan(Layouter):

    def __init__(self, *args, **kwargs):
        '''Do some trigonometry in preparation for layouting.

        All of the calculations here serve the purpose of automatically
        adjusting the angle of rotation through the fan and the size of
        the fan's single image to its precise dimensions.

        '''
        super().__init__(*args, **kwargs)

        # Override keyword argument.
        self.image_margins = (0, 0)

        # Of no arc was specified on creation, make one up.
        self.arc = self.arc or min((0.15 * (self.n_max - 1), 1))

        # The radius of the rotation transformation is based on the height
        # of each card. Cards are assumed to be uniform for this purpose.
        cx, cy = self.get_first_card_size()

        # The horizontal midpoint of the upper edge of a card is the basis of
        # calculations below. That point is what describes the "outer arc".
        outer_radius = cy * 3

        # The horizontal midpoint of the lower edge describes a corresponding
        # "inner arc".
        inner_radius = outer_radius - cy

        def corner_height(n):
            '''The height in mm of a card corner over the outer arc.'''
            angle = self._n_angle(n)
            corner_over_midpoint = (cx / 2) * math.sin(angle)
            midpoint_over_pivot = outer_radius * math.cos(angle)
            return corner_over_midpoint + midpoint_over_pivot - outer_radius

        # The outer arc segment's chord helps determine the width of the image.
        # NOTE: This will not have the desired results if arc > π.
        outer_chord = 2 * outer_radius * math.sin(self.arc / 2)
        # The outermost cards extend a little further.
        chord_margin = (cx / 2) * math.cos(self.arc / 2)

        # The sagitta of the inner arc helps determine the height of the image.
        inner_sagitta = inner_radius * (1 - math.cos(self.arc / 2))
        # Again this is extended by the outermost cards.
        sagitta_margin = (cx / 2) * math.sin(self.arc / 2)
        # It's also extended by the tallest corner of any single card,
        # which can pass above the outer radius. Call it radial margin.
        try:
            self.radial_margin = max(map(corner_height,
                                         range(self.n_min, self.n_max)))
        except ValueError:
            # Empty range. Just one card.
            self.radial_margin = 0

        # We can now determine the center point of the rotation, which
        # is not inside the image.
        self.pivot = ((outer_chord / 2) + chord_margin,
                      outer_radius + self.radial_margin)

        # We can also determine how big the image needs to be to fit the fan.
        # This overrides any specification from keyword arguments.
        self.image_size = (outer_chord + 2 * chord_margin,
                           sum((self.radial_margin, cy, inner_sagitta,
                                sagitta_margin)))

    def get_origin(self, card_size):
        '''An override. Put every card in the middle, near or at the top.'''
        return ((self.image_size[0] - card_size[0]) / 2, self.radial_margin)

    def get_name_suffix(self, *args):
        return 'fan'

    def affix_copy(self, card_number, presenter):
        '''An override. Rotate each card. Bypass the image's intelligence.'''
        # SVG doesn't handle radians.
        angle = math.degrees(self._n_angle(card_number))
        rotation = transform.Rotate(angle, x=self.pivot[0], y=self.pivot[1])
        # Override whatever other transformations are applied.
        presenter.attrib['transform'] = rotation.to_string()

        # Ignore what fits on the page.
        # Append directly to the image XML object.
        self[-1].append(presenter)

    def _n_angle(self, card_number):
        '''The angle of rotation for card number n, in radians.'''
        return (self.n_normal(card_number) - 0.5) * self.arc