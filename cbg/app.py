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
import os
import glob
import logging
import re
import subprocess
import math

import cbg.content.deck
import cbg.sample.size
import cbg.layout


class Application():
    '''A template for a CBG console application.

    Some features of this template use a variety of external programs
    with little regard to their availability, which means that portability
    is limited. Tested on Ubuntu GNOME with appropriate extras.

    '''

    # Default raster resolution is the capacity of an HP LaserJet 1010.
    default_dpi = 600

    class ExternalError(Exception):
        '''Raised when a subprocess cannot be called, or fails.'''
        pass

    def __init__(self, name_full, decks, name_short=None,
                 folder_specs='specs', folder_svg='svg', folder_png='png'):
        '''Constructor.

        The "decks" argument is expected to refer to a dictionary of
        card type classes indexed by file name strings, like this:

        {'example': cbg.content.card.Card}

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
        self.folder_png = folder_png

        self.args = self.check_cli(self.make_cli())
        self.configure_logging()

    def make_cli(self):
        '''Create, but do not run, a command-line argument parser.'''

        d = 'Generate playing card graphics for {}.'.format(self.name_full)
        e = ('Syntax for card selection: [AMOUNT:][tag=]REGEX',
             'AMOUNT defaults to no change (whitelist) or zero (blacklist).',
             'REGEX with "tag=" refers to one card tag, else titles.',
             '',
             'This card graphics application was made with the CBG library.',
             'CBG Copyright 2014-2016 Viktor Eikman',
             'CBG is free software, and you are welcome to redistribute it',
             'under the terms of the GNU General Public License.')

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
        parser.add_argument('--no-fronts', '--no-obverse',
                            dest='include_obverse', default=True,
                            action='store_false', help=s)
        s = ('include the reverse side of cards in layouting; '
             'implicit in duplex and neighbour modes')
        parser.add_argument('-B', '--backs', '--reverse',
                            dest='include_reverse', default=False,
                            action='store_true', help=s)

        group = parser.add_mutually_exclusive_group()
        s = 'send output to printer through lp (GNU+Linux only)'
        group.add_argument('-p', '--print', action='store_true', help=s)
        s = ('call APP to display output; APP should handle a folder name as '
             'its argument and defaults to eog or evince depending on output')
        group.add_argument('-d', '--display', metavar='APP', nargs='?',
                           const='', help=s)
        s = 'list cards as serialized data on console'
        group.add_argument('--list-cards', default=False,
                           action='store_true', help=s)
        s = 'list images as serialized data on console'
        group.add_argument('--list-images', default=False,
                           action='store_true', help=s)

        s = 'include the title of the first depicted card in each filename'
        parser.add_argument('--card-in-filename', default=False,
                            action='store_true', help=s)
        s = 'include the title of the first deck represented in each filename'
        parser.add_argument('--deck-in-filename', default=False,
                            action='store_true', help=s)
        s = 'do not include the title of the game in each filename'
        parser.add_argument('--no-game-in-filename', dest='game_in_filename',
                            default=True, action='store_false', help=s)
        s = 'an arbitrary suffix to each filename'
        parser.add_argument('--filename-suffix', default='', help=s)

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

        def nonnegative_int(value):
            '''Type-checking function for argparse.'''
            value = int(value)
            if value < 0:
                s = 'not a non-negative integer: {}'.format(value)
                raise argparse.ArgumentTypeError(s)
            return value

        group = product.add_mutually_exclusive_group()
        s = ('bitmap output via Inkscape; the default resolution in dots per '
             'inch (DPI) is {}').format(self.default_dpi)
        group.add_argument('-r', '--rasterize', metavar='DPI', nargs='?',
                           const=self.default_dpi, type=nonnegative_int,
                           help=s)
        s = 'produce a document from SVG data, format inferred from filename'
        group.add_argument('--document', metavar='FILENAME', help=s)

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

        parser.set_defaults(layouter_cls=cbg.layout.Layouter,
                            side_in_filename=False, arc=0)
        s = 'optional non-standard layouting modes'
        subparsers = parser.add_subparsers(dest='layouting', title=s,
                                           help='each takes its own help flag')

        s = 'Alternate between front sheets and back sheets.'
        duplex = subparsers.add_parser('duplex', description=s)
        duplex.set_defaults(layouter_cls=cbg.layout.Duplex,
                            side_in_filename=True)
        s = 'Do not include the word "obverse" or "reverse" in each filename.'
        duplex.add_argument('--no-side-in-filename', dest='side_in-filename',
                            default=True, action='store_false', help=s)

        s = 'Treat both sides of cards similarly.'
        neighbours = subparsers.add_parser('neighbours', description=s)
        neighbours.set_defaults(layouter_cls=cbg.layout.Neighbours)

        s = 'Draw cards in the shape of a hand fan, for display purposes.'
        fan = subparsers.add_parser('fan', description=s)
        fan.set_defaults(layouter_cls=cbg.layout.Fan)
        fan.add_argument('--arc', metavar='RADIANS', type=arc,
                         default=0, help='the angle the cards will span')

        s = 'Give each card its own image.'
        singles = subparsers.add_parser('singles', description=s)
        singles.set_defaults(layouter_cls=cbg.layout.Singles,
                             card_in_filename=True)

        return parser

    def check_cli(self, parser):
        '''CLI argument parsing, sanity checks and repackaging.'''

        args = parser.parse_args()

        if not any((args.include_obverse, args.include_reverse)):
            parser.error('asked to process neither side of cards')

        if args.layouting == 'duplex' or args.layouting == 'neighbours':
            args.include_reverse = True
            if not args.include_obverse:
                s = 'layouting mode requires both sides of each card'
                parser.error(s)

        if args.print:
            # Rasterization is implied.
            args.rasterize = self.default_dpi

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
        self.delete_old_files(self.folder_png)

        # Collect and sieve through deck specifications.
        decks = self.read_deck_specs()

        # Consider console output before generating SVG.
        if self.args.list_cards:
            presentation = dict()
            for deck in decks:
                presentation[deck.title] = {str(t): c for t, c in deck.items()}

            print(cbg.serialization.Serialization.dumps(presentation))
            return 0

        # Produce SVG, treat it and exit application appropriately.
        try:
            return self._output(self.vectorize(decks))
        except self.ExternalError as e:
            logging.error(str(e))
            return 1

    def _output(self, images):
        '''Consider showing on screen, printing etc.

        Return an exit status: 0 if successful, else a positive integer.

        '''

        if self.args.rasterize is not None:
            logging.debug('Producing raster graphics.')
            try:
                os.mkdir(self.folder_png)
            except FileExistsError:
                logging.debug('Destination folder for PNG already exists.')

            for image in images:
                image.filepath = self.rasterize(image.filepath)

        elif self.args.document:
            filepath = self.args.document
            if filepath.lower().endswith('.pdf'):
                self.convert_to_pdf(filepath)
            else:
                s = 'Unrecognized output filename suffix.'
                logging.error(s)
                return 1

        if self.args.display is not None:
            if self.args.document:
                filename = self.args.document
                viewer = self.args.display or 'evince'
            elif self.args.rasterize:
                filename = self.folder_png
                viewer = self.args.display or 'eog'
            else:
                filename = self.folder_svg
                viewer = self.args.display or 'eog'
            self._external_process([viewer, filename])
        elif self.args.list_images:
            presentation = dict()
            for image in images:
                presentation[image.filename] = tuple(map(str, image.subjects))
            print(cbg.serialization.Serialization.dumps(presentation))
        elif self.args.print:
            self.print_output()

        return 0

    def _external_process(self, cmd):
        def log_output(text):
            for line in text.splitlines():
                logging.debug('Subprocess output: {}'.format(line))

        try:
            o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            s = 'External application "{}" not found.'
            raise self.ExternalError(s.format(cmd[0]))
        except subprocess.CalledProcessError as e:
            logging.debug('Call {} failed.'.format(cmd))
            log_output(e.output)
            s = 'External application "{}" terminated with error: {}.'
            raise self.ExternalError(s.format(cmd[0], e.returncode))
        else:
            logging.debug('Call {} succeeded.'.format(cmd))
            log_output(o)
            return o

    def delete_old_files(self, folder):
        '''Use globbing to get a valid relative path.'''
        for f in glob.glob(folder + '/*'):
            try:
                os.remove(f)
                logging.debug('Deleted "{}".'.format(f))
            except IsADirectoryError:
                # Directories are permitted to remain, on the assumption
                # that they are being used to house xlink'd raster graphics.
                pass

    def read_deck_specs(self):
        logging.debug('Reading specifications.')

        for filename_base, card_cls in self.decks.items():
            deck = cbg.content.deck.Deck(card_cls, directory=self.folder_specs,
                                         filename_base=filename_base)
            deck.control_selection(self.args.whitelist, self.args.blacklist,
                                   self.args.gallery, self.args.deck_sample)
            yield deck

    def vectorize(self, decks):
        '''Compose SVG images and save them.

        Return a layouter, which is a list of the images with some extra
        information attached.

        '''

        logging.debug('Producing vector graphics.')

        # Flatten specifications to a single list of cards for layouting.
        cards = sorted(card for deck in decks for card in deck.flat())

        try:
            os.mkdir(self.folder_svg)
        except FileExistsError:
            logging.debug('Destination folder for SVG already exists.')

        layouter = self.args.layouter_cls(cards,
                                          image_size=self.args.image_size,
                                          image_margins=self.args.margins,
                                          arc=self.args.arc)
        layouter.run(self.args.include_obverse, self.args.include_reverse)

        title_filename = self.name_short if self.args.game_in_filename else ''
        layouter.save(self.folder_svg,
                      side=self.args.side_in_filename,
                      card=self.args.card_in_filename,
                      deck=self.args.deck_in_filename,
                      game=title_filename,
                      suffix=self.args.filename_suffix)

        return layouter

    def rasterize(self, svg_filepath):
        '''Go from vector graphics to a bitmap using Inkscape.'''
        dpi = self.args.rasterize or self.default_dpi
        logging.debug('Rasterizing {}.'.format(svg_filepath))
        basename = os.path.basename(svg_filepath).rpartition('.')[0]
        png_filename = '{}.png'.format(basename)
        png_filepath = os.path.join(self.folder_png, png_filename)
        cmd = ['inkscape', '-e', png_filepath, '-d', str(dpi), svg_filepath]
        self._external_process(cmd)
        return png_filepath

    def convert_to_pdf(self, filepath):
        '''Author a PDF with librsvg.'''

        logging.debug('Authoring PDF.')

        command = ['rsvg-convert', '-f', 'pdf', '-o', filepath]
        command.extend(self.all_svg_filepaths())
        self._external_process(command)

    def all_svg_filepaths(self):
        return sorted(glob.glob('{}/*.svg'.format(self.folder_svg)))

    def print_output(self):
        '''Print graphics from individual image files: one per page.

        lp prints SVG as text, not graphics. Hence we use the rasterized
        forms here.

        '''

        logging.debug('Printing.')

        for png in sorted(glob.glob('{}/*'.format(self.folder_png))):
            cmd = (['lp', '-o', 'media={}'.format(self.args.print_size), png])
            self._external_process(cmd)

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
