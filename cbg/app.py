# -*- coding: utf-8 -*-
'''A template utility class for card graphics generator programs.'''

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


import argparse
import ast
import collections
import os
import glob
import logging
import re
import subprocess
import math

import cbg.content.deck
import cbg.sample.size
import cbg.layout


HELP_SELECT = ('Syntax for card selection: [AMOUNT:][tag=]REGEX',
               'AMOUNT defaults to no change (whitelist) or zero (blacklist).',
               'REGEX with "tag=" refers to one card tag, else titles.')

LICENSE = ('This card graphics application was made with the CBG library.',
           'CBG Copyright 2014-2016 Viktor Eikman',
           'CBG is free software, and you are welcome to redistribute it',
           'under the terms of the GNU General Public License.')

SPEC_FORMAT_YAML = 'yaml'

SUPPORTED_SPEC_FORMATS = (SPEC_FORMAT_YAML,)


class Application():
    '''A template for a CBG console application.

    Some features of this template use a variety of external programs
    without regard to their availability, which means that portability
    is very limited. Tested on Ubuntu GNOME with appropriate extras.

    '''
    def __init__(self, name_full, decks, name_short=None,
                 spec_format=SPEC_FORMAT_YAML,
                 folder_specs='specs', folder_svg='svg',
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

        assert spec_format in SUPPORTED_SPEC_FORMATS
        self.spec_format = spec_format
        self.folder_specs = folder_specs
        self.folder_svg = folder_svg
        self.folder_printing = folder_printing

        self.args = self.cli().parse_args()
        self.configure_logging()

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
        s = 'card selection blacklist entry'
        parser.add_argument('-b', '--blacklist', metavar='REGEX', default=[],
                            action='append', help=s)
        s = 'card selection whitelist entry (applied before blacklist)'
        parser.add_argument('-w', '--whitelist', metavar='REGEX', default=[],
                            action='append', help=s)
        s = '1 copy of each card'
        parser.add_argument('-g', '--gallery', help=s, action='store_true')

        parser.add_argument('-r', '--rasterize', action='store_true',
                            help='bitmap output via Inkscape')
        parser.add_argument('--dpi', default=600,  # HP LaserJet 1010 capcity.
                            help='bitmap resolution, defaults to 600 DPI')

        s = 'produce a document, format inferred from filename'
        parser.add_argument('-f', '--file-output', metavar='FILENAME', help=s)

        s = 'paper size for printing, as a string instruction to lp'
        parser.add_argument('--print-size', metavar='PAPER_FORMAT',
                            default='A4', help=s)
        s = 'image margins to the outermost spaces for card(s), in mm'
        parser.add_argument('-m', '--margins', metavar='TUPLE',
                            default=cbg.sample.size.A4_MARGINS, help=s)

        parser.add_argument('--viewer-svg', metavar='APP', default='eog',
                            help='application used to display SVG images')
        parser.add_argument('--viewer-raster', metavar='APP', default='eog',
                            help='application used to display bitmap images')
        parser.add_argument('--viewer-file', metavar='APP', default='evince',
                            help='application used to display documents')

        group = parser.add_mutually_exclusive_group()
        s = 'send output to printer through lp (GNU+Linux only)'
        group.add_argument('-p', '--print', help=s, action='store_true')
        group.add_argument('-d', '--display', help='view output',
                           action='store_true')

        group = parser.add_mutually_exclusive_group()
        s = 'alternate between front sheets and back sheets'
        group.add_argument('--duplex', help=s, action='store_true')
        s = 'treat both sides of cards similarly'
        group.add_argument('--neighbours', help=s, action='store_true')
        s = 'draw cards in the shape of a hand fan, for display purposes'
        group.add_argument('--fan', help=s, action='store_true')

        group = parser.add_mutually_exclusive_group()
        s = 'exact image size, in mm'
        group.add_argument('--image-size', default=cbg.sample.size.A4,
                           metavar='TUPLE', help=s)
        s = 'give each card its own image'
        group.add_argument('-s', '--singles', action='store_true', help=s)
        group.add_argument('--arc', metavar='RADIANS', type=float,
                           default=0, help='the angle cards span in fan mode')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-v', '--verbose', help='extra logging',
                           action='store_true')
        group.add_argument('-q', '--quiet', help='less logging',
                           action='store_true')

        return parser

    def configure_logging(self):
        if self.args.verbose:
            level = logging.DEBUG
        elif self.args.quiet:
            level = logging.WARNING
        else:
            level = logging.INFO

        logging.getLogger().setLevel(level)

    def execute(self):
        reformat = self._eval_numeric_2tuple
        try:
            self.args.image_size = reformat(self.args.image_size)
            self.args.margins = reformat(self.args.margins)
        except:
            return 1

        # Impose additional limits on the combination of CLI arguments.

        if self.args.no_fronts and not self.args.backs:
            s = 'Not processing fronts or backs.'
            logging.error(s)
            return 1

        if self.args.arc > math.pi:
            s = 'Arc of fan cannot exceed π radians (180°).'
            logging.error(s)
            return 1

        if self.args.arc:
            # If supplied, the setting implies fan mode.
            if self.args.duplex or self.args.neighbours:
                logging.error('Arc supplied in mode incompatible with fan.')
                return 1
            self.args.fan = True

        if self.args.duplex or self.args.neighbours:
            if self.args.no_fronts or not self.args.backs:
                s = 'Option set requires both sides of each card.'
                logging.error(s)
                return 1
            elif self.args.singles:
                s = 'Option set precludes controlled combination of sides.'
                logging.error(s)
                return 1

        # Get to work.

        # Clean up after previous runs.
        self.delete_old_files(self.folder_svg)
        self.delete_old_files(self.folder_printing)

        # Collect and sieve through deck specifications.
        specs = collections.OrderedDict()
        for deck in sorted(self.read_deck_specs()):
            # Actual deck objects are not preserved here.
            try:
                specs[deck.title] = deck.all_sorted()
            except:
                s = 'An error occurred while sorting data for deck "{}".'
                logging.critical(s.format(deck.title))
                raise

        # Flatten specifications to a single list of cards for layouting.
        cards = [card for listing in specs.values() for card in listing]

        # Pick a class of layouter.
        if self.args.neighbours:
            layouter_cls = cbg.layout.Neighbours
        elif self.args.duplex:
            layouter_cls = cbg.layout.Duplex
        elif self.args.singles:
            layouter_cls = cbg.layout.Singles
        elif self.args.fan:
            layouter_cls = cbg.layout.Fan
        else:
            layouter_cls = cbg.layout.Layouter

        # Compose SVG images and save them.
        layouter = layouter_cls(self.name_short, cards,
                                image_size=self.args.image_size,
                                image_margins=self.args.margins,
                                arc=self.args.arc)
        layouter.run(not self.args.no_fronts, self.args.backs)
        layouter.save(self.folder_svg)

        # Consider showing on screen, printing etc.
        return self._output()

    def _eval_numeric_2tuple(self, value):
        if isinstance(value, str):
            # Received via CLI.
            try:
                value = ast.literal_eval(value)
                assert isinstance(value, tuple)
                assert len(value) == 2
                assert all(map(lambda x: isinstance(x, (int, float)), value))
            except:
                s = 'Got malformed size specification: {}'
                logging.error(s.format(value))
                raise

        return value

    def _output(self):
        '''Treat saved SVG.'''

        if self.args.rasterize or self.args.print:
            if not self.rasterize():
                return 1
        elif self.args.file_output:
            filepath = self.args.file_output
            if filepath.lower().endswith('.pdf'):
                self.convert_to_pdf(filepath)
            else:
                s = 'Unrecognized output filename suffix.'
                logging.error(s)
                return 1

        if self.args.display:
            # Image viewers are assumed to be able to handle a folder name.
            if self.args.file_output:
                filename = self.args.file_output
                viewer = self.args.viewer_file
            elif self.args.rasterize or self.args.print:
                filename = self.folder_printing
                viewer = self.args.viewer_raster
            else:
                filename = self.folder_svg
                viewer = self.args.viewer_svg

            try:
                subprocess.call([viewer, filename])
            except FileNotFoundError:
                logging.error('No such viewer: "{}"'.format(viewer))
                s = 'Please name your preferred viewer with a CLI flag.'
                logging.info(s)
        elif self.args.print:
            self.print_output()

        return 0

    def delete_old_files(self, folder):
        for f in glob.glob('{}/*'.format(folder)):
            logging.debug('Deleting "{}".'.format(f))
            try:
                os.remove(f)
            except IsADirectoryError:
                # Directories are permitted to remain, on the assumption
                # that they are being used to house xlink'd raster graphics.
                pass

    def read_deck_specs(self):
        if self.spec_format == SPEC_FORMAT_YAML:
            import yaml

        for filename_base, card_cls in self.decks.items():
            filepath = '{}/{}.{}'.format(self.folder_specs, filename_base,
                                         self.spec_format)

            with open(filepath, encoding='utf-8') as f:
                if self.spec_format == SPEC_FORMAT_YAML:
                    raw = yaml.load(f)

            deck = cbg.content.deck.Deck(card_cls, raw, title=filename_base)

            s = '{} cards in "{}" deck.'
            logging.debug(s.format(len(deck), deck.title))

            yield self.limit_selection(deck)

    def find(self, deck_title):
        return self.specs.get(deck_title)

    def limit_selection(self, specs):
        '''Apply whitelist, blacklist and gallery mode.'''
        whitelist_exists = bool(self.args.whitelist)

        for card in specs:
            whitelisted = False
            for restriction in self.args.whitelist:
                n_restricted = self._apply_restriction(restriction, card)
                if n_restricted is not None:
                    whitelisted = True
                    # If negative: No change from default number.
                    if n_restricted >= 0:
                        specs[card] = n_restricted
                    break  # Apply only the first matching white restriction.

            if whitelist_exists and not whitelisted:
                specs[card] = 0

            for restriction in self.args.blacklist:
                n_restricted = self._apply_restriction(restriction, card)
                if n_restricted is not None:
                    if n_restricted >= 0:
                        # A not-so-black secondary filter.
                        specs[card] = n_restricted
                    else:
                        # Default behaviour on hit: Blacklisted.
                        specs[card] = 0
                    break  # Apply only the first matching black restriction.

            if specs[card] and self.args.gallery:
                specs[card] = 1

        return specs

    def rasterize(self):
        '''Go from vector graphics to bitmaps using Inkscape.'''
        try:
            os.mkdir(self.folder_printing)
        except FileExistsError:
            pass
        except Exception as e:
            s = 'Unable to create specified bitmap/printing directory "{}": {}'
            logging.error(s.format(self.folder_printing, repr(e)))
            return False

        for svg in sorted(glob.glob('{}/*.svg'.format(self.folder_svg))):
            logging.debug('Rasterizing {}.'.format(svg))
            png = '{}.png'.format(os.path.basename(svg).rpartition('.')[0])
            png = os.path.join(self.folder_printing, png)
            cmd = ['inkscape', '-e', png, '-d', str(self.args.dpi), svg]
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                return False

        return True

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
            subprocess.check_call(['lp', '-o',
                                   'media={}'.format(self.args.print_size),
                                   png])

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
