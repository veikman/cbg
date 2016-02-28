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


class Application():
    '''A template for a CBG console application.

    Some features of this template use a variety of external programs
    with little regard to their availability, which means that portability
    is limited. Tested on Ubuntu GNOME with appropriate extras.

    '''
    def __init__(self, name_full, decks, name_short=None,
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

        self.folder_specs = folder_specs
        self.folder_svg = folder_svg
        self.folder_printing = folder_printing

        self.args = self.check_cli(self.make_cli())
        self.configure_logging()

    def make_cli(self):
        '''Create, but do not run, a command-line argument parser.'''

        d = 'Generate playing card graphics for {}.'.format(self.name_full)
        e = HELP_SELECT + ('\n',) + LICENSE
        f = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description=d, epilog='\n'.join(e),
                                         formatter_class=f)

        self._add_general_cli_opts(parser)
        self._add_selection_opts(parser)
        self._add_media_opts(parser)
        self._add_layouting_mode_opts(parser)

        return parser

    def _add_general_cli_opts(self, parser):
        '''Add general options to an argument parser.

        These fall under the standard argparse heading "optional arguments",
        though all arguments to the application are optional. We could
        suppress -h/--help getting added directly to the parser, then add
        replacements for that flag in a named group, and then call
        parser.print_help() as directed by the replacement. Not worth it.

        '''
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-v', '--verbose', action='store_true',
                           help='extra logging')
        group.add_argument('-q', '--quiet', action='store_true',
                           help='less logging')

        s = 'do not include the obverse side of cards in layouting'
        parser.add_argument('--no-fronts', action='store_true', help=s)
        s = ('include the reverse side of cards in layouting; '
             'implicit in duplex and neighbour modes')
        parser.add_argument('-B', '--backs', action='store_true', help=s)

        group = parser.add_mutually_exclusive_group()
        s = 'send output to printer through lp (GNU+Linux only)'
        group.add_argument('-p', '--print', action='store_true', help=s)
        group.add_argument('-d', '--display', action='store_true',
                           help='view output')

    def _add_selection_opts(self, parser):
        '''Add deck/card filtering options to an argument parser.'''

        s = 'optional card selection arguments'
        selection = parser.add_argument_group(title=s)
        s = 'card selection blacklist entry'
        selection.add_argument('-b', '--blacklist', metavar='REGEX',
                               default=[], action='append', help=s)
        s = 'card selection whitelist entry (applied before blacklist)'
        selection.add_argument('-w', '--whitelist', metavar='REGEX',
                               default=[], action='append', help=s)
        s = 'maximum 1 copy of each card'
        selection.add_argument('-g', '--gallery', default=False,
                               action='store_true', help=s)
        s = 'maximum 1 card per deck'
        selection.add_argument('--deck-sample', default=False,
                               action='store_true', help=s)

    def _add_media_opts(self, parser):
        '''Add media options to an argument parser.'''

        product = parser.add_argument_group(title='optional media arguments')

        group = product.add_mutually_exclusive_group()
        group.add_argument('-r', '--rasterize', action='store_true',
                           help='bitmap output via Inkscape')
        s = 'produce a document from SVG data, format inferred from filename'
        group.add_argument('--document', metavar='FILENAME', help=s)

        def nonnegative_int(value):
            '''Type-checking function for argparse.'''
            value = int(value)
            if value < 0:
                s = 'not a non-negative integer: {}'.format(value)
                raise argparse.ArgumentTypeError(s)
            return value

        def numeric_2tuple(value):
            '''Type-checking function for argparse.'''
            if not re.match('^\(.*\)$', value):
                value = '({})'.format(value)

            try:
                value = ast.literal_eval(value)
                assert isinstance(value, tuple)
                assert len(value) == 2
                assert all(map(lambda x: isinstance(x, (int, float)),
                               value))
                assert all(map(lambda x: x >= 0, value))
            except:
                s = 'not a numeric 2-tuple like "0,0": {}'.format(value)
                raise argparse.ArgumentTypeError(s)

            return value

        # The DPI setting's default value is implemented conditionally, later.
        product.add_argument('--dpi', metavar='INT', type=nonnegative_int,
                             help='bitmap resolution, defaults to 600 DPI')
        s = 'paper size for printing, as a string instruction to lp'
        product.add_argument('--print-size', metavar='PAPER_FORMAT',
                             default='A4', help=s)
        s = 'exact image size, in mm'
        product.add_argument('--image-size', metavar='TUPLE',
                             type=numeric_2tuple,
                             default=cbg.sample.size.A4, help=s)
        s = 'image margins to the outermost spaces for card(s), in mm'
        product.add_argument('--margins', metavar='TUPLE', type=numeric_2tuple,
                             default=cbg.sample.size.A4_MARGINS, help=s)
        product.add_argument('--viewer-svg', metavar='APP', default='eog',
                             help='application used to display SVG images')
        product.add_argument('--viewer-raster', metavar='APP', default='eog',
                             help='application used to display bitmap images')
        product.add_argument('--viewer-doc', metavar='APP', default='evince',
                             help='application used to display documents')

    def _add_layouting_mode_opts(self, parser):
        '''Add layouting options to an argument parser.'''

        def arc(value):
            '''Type-checking function for argparse.'''
            try:
                value = float(value)
            except:
                raise argparse.ArgumentTypeError('must be a number')

            if value < 0:
                raise argparse.ArgumentTypeError('cannot be negative')
            elif value > math.pi:
                s = 'cannot exceed π radians (180°)'
                raise argparse.ArgumentTypeError(s)

            return value

        parser.set_defaults(layouter_cls=cbg.layout.Layouter, arc=0)
        s = 'optional non-standard layouting modes'
        subparsers = parser.add_subparsers(dest='layouting', title=s,
                                           help='each takes its own help flag')

        s = 'alternate between front sheets and back sheets'
        duplex = subparsers.add_parser('duplex', description=s)
        duplex.set_defaults(layouter_cls=cbg.layout.Duplex)

        s = 'treat both sides of cards similarly'
        neighbours = subparsers.add_parser('neighbours', description=s)
        neighbours.set_defaults(layouter_cls=cbg.layout.Neighbours)

        s = 'draw cards in the shape of a hand fan, for display purposes'
        fan = subparsers.add_parser('fan', description=s)
        fan.set_defaults(layouter_cls=cbg.layout.Fan)
        fan.add_argument('--arc', metavar='RADIANS', type=arc,
                         default=0, help='the angle the cards will span')

        s = 'give each card its own image'
        singles = subparsers.add_parser('singles', description=s)
        singles.set_defaults(layouter_cls=cbg.layout.Singles)

        return parser

    def check_cli(self, parser):
        '''CLI argument parsing, sanity checks and repackaging.'''

        args = parser.parse_args()

        if args.no_fronts and not args.backs:
            parser.error('asked to process neither side of cards')

        if args.layouting == 'duplex' or args.layouting == 'neighbours':
            args.backs = True
            if args.no_fronts:
                s = 'layouting mode requires both sides of each card'
                parser.error(s)

        if args.print or args.dpi:
            # Rasterization is implied.
            args.rasterize = True

        if args.dpi is None:
            # Now that the DPI setting has been checked for implying
            # rasterization, give it a default value.
            # The value is based on the author's HP LaserJet 1010's capacity.
            args.dpi = 600

        return args

    def configure_logging(self):
        if self.args.verbose:
            level = logging.DEBUG
        elif self.args.quiet:
            level = logging.WARNING
        else:
            level = logging.INFO

        logging.getLogger().setLevel(level)

    def execute(self):
        # Clean up after previous runs.
        self.delete_old_files(self.folder_svg)
        self.delete_old_files(self.folder_printing)

        # Collect and sieve through deck specifications.
        specs = collections.OrderedDict()
        for deck in sorted(self.read_deck_specs()):
            # Extract just the cards.
            try:
                specs[deck.title] = deck.all_sorted()
            except:
                s = 'An error occurred while sorting data for deck "{}".'
                logging.critical(s.format(deck.title))
                raise

        # Flatten specifications to a single list of cards for layouting.
        cards = [card for listing in specs.values() for card in listing]

        # Compose SVG images and save them.
        layouter = self.args.layouter_cls(self.name_short, cards,
                                          image_size=self.args.image_size,
                                          image_margins=self.args.margins,
                                          arc=self.args.arc)
        layouter.run(not self.args.no_fronts, self.args.backs)
        layouter.save(self.folder_svg)

        # Consider showing on screen, printing etc.
        return self._output()

    def _output(self):
        '''Treat saved SVG.'''

        if self.args.rasterize:
            if not self.rasterize():
                return 1

        elif self.args.document:
            filepath = self.args.document
            if filepath.lower().endswith('.pdf'):
                self.convert_to_pdf(filepath)
            else:
                s = 'Unrecognized output filename suffix.'
                logging.error(s)
                return 1

        if self.args.display:
            # Image viewers are assumed to be able to handle a folder name.
            if self.args.document:
                filename = self.args.document
                viewer = self.args.viewer_doc
            elif self.args.rasterize:
                filename = self.folder_printing
                viewer = self.args.viewer_raster
            else:
                filename = self.folder_svg
                viewer = self.args.viewer_svg

            try:
                subprocess.call([viewer, filename])
            except FileNotFoundError:
                logging.error('Viewer not found: "{}".'.format(viewer))
                s = 'Please name an installed viewer with a CLI flag.'
                logging.info(s)
                return 1

        elif self.args.print:
            self.print_output()

        return 0

    def delete_old_files(self, folder):
        for f in glob.glob('{}/*'.format(folder)):
            try:
                os.remove(f)
                logging.debug('Deleted "{}".'.format(f))
            except IsADirectoryError:
                # Directories are permitted to remain, on the assumption
                # that they are being used to house xlink'd raster graphics.
                pass

    def read_deck_specs(self):
        logging.debug('Reading card deck specifications.')

        for filename_base, card_cls in self.decks.items():
            deck = cbg.content.deck.Deck(card_cls, directory=self.folder_specs,
                                         filename_base=filename_base)
            deck.control_selection(self.args.whitelist, self.args.blacklist,
                                   self.args.gallery, self.args.deck_sample)
            yield deck

    def rasterize(self):
        '''Go from vector graphics to bitmaps using Inkscape.'''

        logging.debug('Rasterizing.')

        try:
            os.mkdir(self.folder_printing)
        except FileExistsError:
            pass
        except Exception as e:
            s = 'Unable to create specified bitmap/printing directory "{}": {}'
            logging.error(s.format(self.folder_printing, repr(e)))
            return False

        for svg in self.all_svg_filepaths():
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

        logging.debug('Writing PDF.')

        command = ['rsvg-convert', '-f', 'pdf', '-o', filepath]
        command.extend(self.all_svg_filepaths())
        try:
            subprocess.call(command)
        except FileNotFoundError:
            s = 'Missing utility for concatenation: {}.'
            logging.error(s.format(command[0]))

    def all_svg_filepaths(self):
        return sorted(glob.glob('{}/*.svg'.format(self.folder_svg)))

    def print_output(self):
        '''Print graphics from individual image files: one per page.

        lp prints SVG as text, not graphics. Hence we use the rasterized
        forms here.

        '''

        logging.debug('Printing.')

        for png in sorted(glob.glob('{}/*'.format(self.folder_printing))):
            subprocess.check_call(['lp', '-o',
                                   'media={}'.format(self.args.print_size),
                                   png])

        # Not sure the above operation gets the scale exactly right!
        # lp seems to like printing PNGs to fill the page.

        # Pre-2014, the following had to be done after Inkscape to get
        # the right scale. ImageMagick for PNG to PostScript:
        # $ convert -page A4 <png> -resize 100 <ps>
        # Not sure if "page" flag is appropriate at this stage but it
        # may make margins in the SVG unnecessary.

        # 2014: Unfortunately PostScript stopped working at some point.
        # evince says "assertion 'EV_IS_DOCUMENT (document)' failed"
        # when opening the PostScript file, which lp prints at
        # drastically reduced size.

        # Printing PNG in GIMP respects scale, (with and?) without the
        # margins. Perhaps this can be scripted. Apparently,
        # rasterization in GIMP can be scripted.
        # http://porpoisehead.net/mysw/index.php?pgid=gimp_svg
