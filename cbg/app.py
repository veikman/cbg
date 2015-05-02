# -*- coding: utf-8 -*-
'''A template utility class for card graphics generator programs.

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

import argparse
import collections
import os
import glob
import logging
import re
import subprocess

from . import deck
from . import page


HELP_SELECT = ('Mini-language for card selection: [AMOUNT:][tag=]REGEX',
               'AMOUNT defaults to no change (whitelist) or zero (blacklist).',
               'REGEX with "tag=" refers to one card tag, else titles.')

LICENSE = ('This card graphics application was made with the CBG library.',
           'CBG Copyright 2014-2015 Viktor Eikman',
           'CBG is free software, and you are welcome to redistribute it',
           'under the terms of the GNU General Public License.')


class Application():
    '''A template for a CBG console application.

    Some features of this template use a variety of external programs
    without regard to their availability, which means that portability
    is very limited. Tested on Ubuntu GNOME with appropriate extras.

    '''
    def __init__(self, name_full, decks, name_short=None,
                 folder_yaml='yaml', folder_svg='svg',
                 folder_printing='printing'):
        '''Constructor.

        The "decks" argument is expected to refer to a dictionary of
        card type classes indexed by file name strings, like this:

        {'example': cbg.card.HumanReadablePlayingCard}

        Note there is no path or suffix in the file name string.

        '''
        self.name_full = name_full
        self.decks = decks

        self.name_short = name_short
        if not self.name_short:
            # Default to initials.
            s = ''.join((w[0].lower() for w in self.name_full.split()))
            self.name_short = s

        self.folder_yaml = folder_yaml
        self.folder_svg = folder_svg
        self.folder_printing = folder_printing

        parser = self.cli()
        self.args = parser.parse_args()

        if self.args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def cli(self):
        '''Create, but do not run, a command-line argument parser.'''

        d = 'Generate playing card graphics for {}.'.format(self.name_full)
        e = HELP_SELECT + ('\n',) + LICENSE
        f = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description=d, epilog='\n'.join(e),
                                         formatter_class=f)

        s = 'do not include the fronts of cards'
        parser.add_argument('--no-fronts', help=s, action='store_true')
        s = 'include the backs of cards'
        parser.add_argument('-B', '--backs', help=s, action='store_true')
        s = 'card selection blacklist'
        parser.add_argument('-b', '--blacklist', nargs='+', help=s, default=[])
        s = 'card selection whitelist (applied before blacklist)'
        parser.add_argument('-w', '--whitelist', nargs='+', help=s, default=[])
        s = '1 copy of each card'
        parser.add_argument('-g', '--gallery', help=s, action='store_true')

        group = parser.add_mutually_exclusive_group()
        s = 'alternate between front sheets and back sheets'
        group.add_argument('--duplex', help=s, action='store_true')
        s = 'treat both sides of cards similarly'
        group.add_argument('--neighbours', help=s, action='store_true')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-p', '--print', help='send output to printer',
                           action='store_true')
        group.add_argument('-d', '--display', help='view output',
                           action='store_true')

        parser.add_argument('-r', '--rasterize', help='bitmap output',
                            action='store_true')
        s = 'container format inferred from filename'
        parser.add_argument('-f', '--file-output', help=s)
        parser.add_argument('-v', '--verbose', help='extra logging',
                            action='store_true')

        return parser

    def execute(self):
        if self.args.no_fronts and not self.args.backs:
            s = 'Not processing fronts or backs.'
            logging.error(s)
            return 1
        elif self.args.no_fronts or not self.args.backs:
            if self.args.duplex or self.args.neighbours:
                s = 'Option set requires both sides of each card.'
                logging.error(s)
                return 1

        self.delete_old_files(self.folder_svg)
        self.delete_old_files(self.folder_printing)

        self.specs = collections.OrderedDict()
        for d in sorted(self.read_deck_specs()):
            # Actual deck objects are not preserved here.
            self.specs[d.title] = d.all_sorted

        page_queue = page.Queue(self.name_short)

        if self.args.neighbours:
            # Just one round of layouts. Include everything.
            sides = (('', True, True, True),)
        else:
            # Two rounds of layouts.
            sides = (('front', not self.args.no_fronts, True, False),
                     ('back', self.args.backs, False, True))
        for side, requested, include_front, include_back in sides:
            if not requested:
                continue
            self.layout(page_queue, side, include_front, include_back)

        if self.args.duplex:
            # Alternate between front sheets and back sheets.
            midpoint = len(page_queue) // 2
            tmp = []
            for pair in zip(page_queue[:midpoint], page_queue[midpoint:]):
                tmp.extend(pair)
            page_queue.data = tmp
        page_queue.save(self.folder_svg)

        if self.args.rasterize or self.args.print:
            self.rasterize()
        elif self.args.file_output:
            filepath = self.args.file_output
            if filepath.lower().endswith('.pdf'):
                self.convert_to_pdf(filepath)
            else:
                s = 'Unrecognized output filename suffix.'
                logging.error(s)
                return 1

        if self.args.display:
            # A very limited selection of viewer applications.
            if self.args.file_output:
                filename = self.args.file_output
                viewer = 'evince'
            else:
                filename = sorted(glob.glob('{}/*'.format(self.folder_svg)))[0]
                viewer = 'eog'
            subprocess.call([viewer, filename])
        elif self.args.print:
            self.print_output()

        return 0

    def delete_old_files(self, folder):
        for f in glob.glob('{}/*'.format(folder)):
            logging.debug('Deleting "{}".'.format(f))
            os.remove(f)

    def read_deck_specs(self):
        for filename_base, cardtype in self.decks.items():
            path = '{}/{}.yaml'.format(self.folder_yaml, filename_base)
            specs = deck.Deck(filename_base, path, cardtype)

            s = '{} cards in "{}" deck.'
            logging.debug(s.format(len(specs), specs.title))

            yield self.limit_selection(specs)

    def layout(self, page_queue, side_name, front, back):
        '''Add to a queue of layed-out pages, full of cards.

        By default, the pages are A4 with all measurements specified in
        mm, despite the scale-free nature of SVG.

        '''
        def new_page():
            page_queue.append(page.Page(left_to_right=front, side=side_name))

        def insert(footprint, xml_gen):
            if not page_queue[-1].can_fit(footprint):
                new_page()
            xml = xml_gen(page_queue[-1].free_spot(footprint))
            page_queue[-1].add(footprint, xml)

        new_page()
        for listing in self.specs.values():
            # The requisite number of copies of each card.
            for cardcopy in listing:
                foot = cardcopy.dresser.size.footprint
                if front:
                    insert(foot, cardcopy.dresser.front)
                if back:
                    insert(foot, cardcopy.dresser.back)

        return page_queue

    def find(self, deck_title):
        return self.specs.get(deck_title)

    def limit_selection(self, specs):
        '''Apply whitelist, blacklist and gallery mode.'''
        for card in specs:
            for restriction in self.args.whitelist:
                restricted = self._apply_restriction(restriction, card)
                if restricted is None:
                    # No hit.
                    specs[card] = 0
                else:
                    # If negative: No change from default number.
                    if restricted >= 0:
                        specs[card] = restricted
                    break
            for restriction in self.args.blacklist:
                restricted = self._apply_restriction(restriction, card)
                if restricted is not None:
                    if restricted >= 0:
                        # Not-so-black secondary filter.
                        specs[card] = restricted
                    else:
                        # Default behaviour on hit: Blacklisted.
                        specs[card] = 0
                    break

            if specs[card] and self.args.gallery:
                specs[card] = 1

        return specs

    def rasterize(self):
        '''Go from vector graphics to bitmaps with Inkscape.'''
        dpi = '600'  # The capacity of an HP LaserJet 1010.
        for svg in sorted(glob.glob('{}/*'.format(self.folder_svg))):
            logging.debug('Rasterizing {}.'.format(svg))
            png = '{}.png'.format(os.path.basename(svg).rpartition('.')[0])
            png = os.path.join(self.folder_printing, png)
            subprocess.check_call(['inkscape', '-e', png, '-d', dpi, svg])

    def convert_to_pdf(self, filepath):
        '''Author a PDF with librsvg.'''
        command = ['rsvg-convert', '-f', 'pdf', '-o', filepath]
        command.extend(sorted(glob.glob('{}/*'.format(self.folder_svg))))
        try:
            subprocess.call(command)
        except FileNotFoundError:
            s = 'Missing utility for concatenation: {}.'
            logging.error(s.format(command[0]))

    def print_output(self):
        '''Print graphics from individual page files.'''
        for png in sorted(glob.glob('{}/*'.format(self.folder_printing))):
            subprocess.check_call(['lp', '-o', 'media=A4', png])

        # NOTE: lp prints SVG as text, not graphics. Hence we use the
        # rasterized forms here.

        # Not sure the above operation gets the scale exactly right!
        # lp seems to like printing PNGs to fill the page.

        # Pre-2014, the following had to be done after Inkscape to get
        # the right scale. ImageMagick for PNG to PostScript:
        # $ convert -page A4 <png> -resize 100 <ps>

        # Not sure if "page" flag is appropriate at this stage but it
        # may make margins in the SVG unnecessary.
        # 2014: Unfortunately this step stopped working at some point.
        # (evince says "assertion 'EV_IS_DOCUMENT (document)' failed"
        # when opening the PostScript file, which lp prints at
        # drastically reduced size.)

        # Printing PNG in GIMP respects scale, (with and?) without the
        # margins. Perhaps this can be scripted. Apparently,
        # rasterization in GIMP can be scripted.
        # http://porpoisehead.net/mysw/index.php?pgid=gimp_svg

    def _apply_restriction(self, restriction, card):
        '''See if a string specifying a restriction applies to a card.

        If there's a hit, return the new number of copies to process.
        Else return None.

        '''
        interpreted = re.split('^(\d+):', restriction, maxsplit=1)[1:]

        if len(interpreted) == 2:
            # The user has supplied a copy count.
            restricted_copies = int(interpreted[0])
            regex = interpreted[-1]
        else:
            # Do not change the number of copies.
            restricted_copies = -1
            regex = restriction

        if regex.startswith('tag='):
            regex = regex[4:]
            try:
                tags = card.tags
            except AttributeError:
                # No member of card class named "tags".
                # This is true of the base class.
                s = ('Tag-based filtering requires "tags" property.')
                logging.critical(s)
                raise
            if regex in map(str, tags):
                return restricted_copies
        else:
            if re.search(regex, card.title):
                return restricted_copies
