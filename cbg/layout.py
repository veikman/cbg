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
import itertools
import logging
import math
import re

import cbg.svg.transform as transform
import cbg.content.image


class Namer():
    '''A class that comes up with names for image files.'''

    def __init__(self, side=False, card=False, deck=False,
                 game='', suffix='', count_max=999):
        '''Initialize.

        The Boolean keyword arguments refer to whether or not to include
        each piece of information gleaned from a card. The keyword
        arguments with string defaults will be included if non-empty.

        '''
        self._side = side
        self._card = card
        self._deck = deck
        self._game = game
        self._suffix = suffix

        # count_max is only used to format the only mandatory text field.
        self._count_template = '{{:0{}d}}'.format(len(str(count_max)))
        self._count = itertools.count(start=1)

        # Prepare to delete characters not matching the set labelled W.
        self._hard_cleaner = re.compile('[\W_]+')
        self._soft_cleaner = re.compile('[\W]+')

    @classmethod
    def name_side(self, obverse, reverse=None):
        '''Return a string based on supplied Booleans.'''

        if reverse is None:
            reverse = not obverse

        if obverse and reverse:
            raise ValueError('Both sides are not to be named.')
        elif not obverse and not reverse:
            raise ValueError('Neither side cannot be named.')

        if obverse:
            return 'obverse'
        elif reverse:
            return 'reverse'

    def name_image(self, image):
        '''Return a string based on supplied SVG image object.'''

        filename = self._count_template.format(next(self._count))

        def prepend(item):
            return '_'.join((self._hard_cleaner.sub('', str(item)), filename))

        def append(item):
            return '_'.join((filename, self._hard_cleaner.sub('', str(item))))

        if self._game:
            filename = prepend(self._game)

        if self._deck:
            # This also requires images for individual cards.
            if image.subject:
                filename = append(image.subject.deck)

        if self._card:
            # This currently requires images to have been created for
            # individual cards.
            if image.subjects:
                filename = append(image.subjects[0])

        if self._side:
            # Indirect, based on layouting direction.
            filename = append(self.name_side(image.left_to_right))

        if self._suffix:
            filename = append(self._suffix)

        # Clean.
        filename = filename.lower()
        filename = self._soft_cleaner.sub('', filename)

        # Append file type.
        filename = '.'.join((filename, 'svg'))

        return filename


class Layouter(collections.UserList):
    '''A list of images. A manager of the SVG authoring process.

    This could have been an abstract base class, but it turns out
    to be useful in its simplicity.

    Based on UserList because it can be desirable to change the order
    of the images after the queue has been populated, as in the example
    application's duplex mode, implemented in this module.

    '''

    def __init__(self, card_list, image_size=None, image_margins=None,
                 arc=None):
        super().__init__()

        if not card_list:
            raise ValueError('No cards selected for layouting.')

        self.cards = card_list

        # Not all keyword arguments are used by all types of layouter.
        self.image_size = image_size
        self.image_margins = image_margins
        self.arc = arc

        # Predict the smallest and largest numbers cards will have.
        # This informaton can be used by subclasses, for a progress bar etc.
        self.n_min = 1
        self.n_max = len(self.cards)

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
                                   Namer.name_side(obverse, reverse)))
            return

        if not self or not self[-1].can_fit(presenter_class.size):
            self.new_image(card_copy, obverse)

        origin = self.get_origin(presenter_class.size)
        presenter = presenter_class.new(card_copy, origin=origin,
                                        parent=self[-1])
        self.affix_copy(card_copy, number, presenter)

    def new_image(self, card, include_obverse):
        '''Use image size specifiable via CLI.'''
        cls = cbg.content.image.LayoutFriendlyImage
        self.append(cls(dimensions=self.image_size,
                        padding=self.image_margins,
                        left_to_right=include_obverse))

    def affix_copy(self, card, card_number, presenter):
        '''Add one copy of a card to the latest image.'''
        # Using add(), the image will calculate how much space will be left.
        self[-1].add(card, presenter)

    def get_first_card_size(self, obverse=True):
        if obverse:
            return self.cards[0].presenter_class_front.size
        else:
            return self.cards[0].presenter_class_back.size

    def get_origin(self, card_size):
        return self[-1].free_spot(card_size)

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

    def set_filenames(self, directory=None, **kwargs):
        kwargs.setdefault('count_max', len(self))
        namer = Namer(**kwargs)

        for image in self:
            image.directory = directory
            image.filename = namer.name_image(image)

    def save(self, destination_folder, **kwargs):
        '''Save all images to named folder.'''
        self.set_filenames(directory=destination_folder, **kwargs)
        for image in self:
            image.save()


class Neighbours(Layouter):
    '''Obverse and reverse sides of cards as neighbours.'''

    def run(self, obverse, reverse):
        '''One round of layouting for both sides of cards.'''
        self.layout(True, True)
        self.sort_images()


class Duplex(Layouter):
    '''Obverse and reverse sides of cards on alternating images.'''

    def on_layout_start(self, obverse, reverse):
        '''Make sure we start afresh for reverse after obverse.

        In duplex mode, this method is called once for the obverse of each
        card, and once for the reverse, with the expectation that the
        obverse of any card will never appear in an image together with the
        reverse of any card.

        Unfortunately, this will produce a blank page if called for games
        where the cards have no presenters for the reverse side.

        '''
        self.new_image(None, obverse)

    def sort_images(self):
        # Alternate between front sheets and back sheets.
        midpoint = len(self) // 2
        tmp = []
        for pair in zip(self[:midpoint], self[midpoint:]):
            tmp.extend(pair)
        self.data = tmp

    def with_filenames(self, **kwargs):
        '''An override.'''
        kwargs.setdefault('side', True)
        return super().with_filenames(**kwargs)


class Singles(Layouter):
    '''One card per image.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override keyword argument.
        self.image_margins = (0, 0)

    def new_image(self, card, obverse):
        '''Use card size as image size, individually for each card.'''
        if obverse:
            self.image_size = card.presenter_class_front.size
        else:
            self.image_size = card.presenter_class_back.size
        super().new_image(card, obverse)

    def with_filenames(self, **kwargs):
        '''An override.'''
        kwargs.setdefault('card', True)
        return super().with_filenames(**kwargs)


class Fan(Layouter):
    '''A hand fan.'''

    def __init__(self, *args, **kwargs):
        '''Do some trigonometry in preparation for layouting.

        All of the calculations here serve the purpose of automatically
        adjusting the angle of rotation through the fan and the size of
        the fan's single image to its precise dimensions.

        '''
        super().__init__(*args, **kwargs)

        # If no arc was specified on creation, make one up.
        self.arc = self.arc or min((0.1 * (self.n_max - 1), 0.8))

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

    def _n_angle(self, card_number):
        '''The angle of rotation for card number n, in radians.'''
        return (self.n_normal(card_number) - 0.5) * self.arc

    def get_origin(self, card_size):
        '''An override. Put every card in the middle, near or at the top.'''
        return ((self.image_size[0] - card_size[0]) / 2, self.radial_margin)

    def new_image(self, card, include_obverse):
        '''An override. A downgrade to the BaseImage class.'''
        self.append(cbg.content.image.BaseImage(dimensions=self.image_size))

    def affix_copy(self, card, card_number, presenter):
        '''An override. Rotate each card.'''

        # SVG doesn't handle radians.
        angle = math.degrees(self._n_angle(card_number))
        rotation = transform.Rotate(angle, x=self.pivot[0], y=self.pivot[1])
        # Override whatever other transformations are applied.
        presenter.attrib['transform'] = rotation.to_string()

        super().affix_copy(card, card_number, presenter)

    def with_filenames(self, **kwargs):
        '''An override.'''
        kwargs['suffix'] = kwargs.get('suffix') or 'fan'
        return super().with_filenames(**kwargs)
