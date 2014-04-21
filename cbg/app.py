# -*- coding: utf-8 -*-
'''A basic utility class for card graphics generator programs.

@author: Viktor Eikman <viktor.eikman@gmail.com>

'''

import argparse
import os
import glob
import logging
import re
import subprocess

from . import deck
from . import page

class Application():
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
            ## Default to initials.
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
        s = 'Generate playing card graphics for {}.'.format(self.name_full)
        parser = argparse.ArgumentParser(description=s)

        parser.add_argument('-v', '--verbose', help='extra logging',
                            action='store_true')

        s = ('override card selection using "[<amount>:]<regex>" '
             'strings: the <amount> defaults to 1 copy of each card '
             'whose title matches any regex')
        parser.add_argument('-o', '--only', nargs='+', help=s, default=[])

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-p', '--print', help='send output to printer',
                            action='store_true')
        group.add_argument('-d', '--display', help='render graphics',
                            action='store_true')

        return parser

    def execute(self):
        self.delete_old_files(self.folder_svg)
        self.delete_old_files(self.folder_printing)

        queue = self.layout(self.read_deck_specs())
        queue.save(self.folder_svg)

        if self.args.display:
            filename = sorted(glob.glob('{}/*'.format(self.folder_svg)))[0]
            ## Currently just one viewing method.
            subprocess.call(['eog', filename])
        elif self.args.print:
            self.print_output()

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

    def limit_selection(self, specs):
        '''See if a user-supplied regex matches card titles.
        
        In the event of a match, don't try any more regexes on that card.
        
        '''
        for card in specs:
            for restriction in self.args.only:
                interpreted = re.split('^(\d+):', restriction, maxsplit=1)[1:]
    
                if len(interpreted) == 2:
                    ## The user has supplied a copy count.
                    copies = int(interpreted[0])
                else:
                    copies = 1
    
                regex = interpreted[-1]
                if re.search(regex, card.title):
                    specs[card] = copies
                    break
                specs[card] = 0

        return specs

    def layout(self, deck_specs):
        '''Create a queue of layed-out pages, full of cards.
        
        By default, the pages are A4 with all measurements specified in
        mm, despite the scale-free nature of SVG.

        '''
        layouts = page.Queue(self.name_short)
        layouts.append(page.Page())

        for listing in (deck.all_sorted for deck in sorted(deck_specs)):
            for cardcopy in listing:
                foot = cardcopy.dresser.size.footprint
                if not layouts[-1].can_fit(foot):
                    layouts.append(page.Page())

                xml = cardcopy.dresser(layouts[-1].free_spot(foot))
                layouts[-1].add(foot, xml)

        return layouts

    def print_output(self):
        '''Print SVG graphics, true to scale.

        lp prints SVG as text, not graphics. So we rasterize first.

        '''
        dpi = '600' ## The capacity of my HP LaserJet 1010.
        for svg in sorted(glob.glob('{}/*'.format(self.folder_svg))):
            png = '{}.png'.format(os.path.basename(svg).rpartition('.')[0])
            png = os.path.join(self.folder_printing, png)
            subprocess.check_call(['inkscape', '-e', png, '-d', dpi, svg])
            subprocess.check_call(['lp', '-o', 'media=A4', png])

        ## Not sure the above operation gets the scale exactly right!
        ## lp seems to like printing PNGs to fill the page.

        ## Previously, the following had to be done after inkscape.
        ## ImageMagick for PNG to PostScript:
        # convert -page A4 <png> -resize 100 <ps>
        ## Not sure if "page" flag is appropriate at this stage but it
        ## may make margins in the SVG unnecessary.
        ## 2014: Unfortunately this step stopped working at some point.
        ## (evince says "assertion 'EV_IS_DOCUMENT (document)' failed"
        ## when opening the PostScript file, which lp prints at
        ## drastically reduced size.)

        ## Printing PNG in GIMP respects scale, (with and?) without the
        ## margins. Perhaps this can be scripted. Apparently,
        ## rasterization in GIMP can be scripted.
        # http://porpoisehead.net/mysw/index.php?pgid=gimp_svg
