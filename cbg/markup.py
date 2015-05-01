# -*- coding: utf-8 -*-
'''A system of shorthand expressions for YAML specifications.

Loosely patterned after Mediawiki template syntax.

No SVG support (e.g. icons, layouting context) yet.

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

Copyright 2014 Viktor Eikman

'''

import re

from . import exc


class Authority():
    '''Registrar and performer of shorthand expression replacement.

    This class is to be used as a singleton. Do not instantiate it.

    There is some support for custom authorities by subclassing or
    monkey-patching, but markup lead-in and lead-out sequences must
    be dissimilar from eachother and from the parameter separator
    sequence, unless interal methods are overridden.

    '''
    registry = dict()

    lead_in = '{{'
    separator = '|'
    lead_out = '}}'

    @classmethod
    def register(cls, shorthand):
        cls.registry[shorthand.markupstring] = shorthand

    @classmethod
    def expected(cls, shorthand, *parameters):
        '''Present a shorthand expression as it would be expected in YAML.

        This can be used to generate YAML specs programmatically.

        '''
        s = cls.lead_in + shorthand.markupstring
        if parameters:
            s += cls.separator + cls.separator.join(parameters)
        s += cls.lead_out
        return s

    @classmethod
    def parse(cls, string):
        '''Look for and expand all registered shorthand expressions.'''
        while True:
            shorthand = cls._find_deep_shorthand(string)
            if not shorthand:
                return string
            string = re.sub(re.escape(shorthand), cls._expand(shorthand),
                            string)

    @classmethod
    def _find_deep_shorthand(cls, string):
        '''Find a good candidate for expansion.

        Return the last shorthand string with no shorthand inside it.

        '''
        try:
            last_in = string.rindex(cls.lead_in)
        except ValueError:
            # No shorthand opener.
            return

        remainder = last_in + len(cls.lead_in)
        try:
            matching_out = remainder + string[remainder:].index(cls.lead_out)
        except ValueError:
            s = 'Open shorthand expression in "{}": "{}" not found.'
            raise exc.MarkupError(s.format(string, cls.lead_out))

        return string[last_in:matching_out + len(cls.lead_out)]

    @classmethod
    def _expand(cls, shorthand):
        '''Suggest a replacement for named shorthand expression.'''
        pattern = (re.escape(cls.lead_in) + '(.*)' + re.escape(cls.lead_out))
        content = re.sub('^' + pattern + '$', r'\1', shorthand)
        sections = re.split(re.escape(cls.separator), content)

        name, parameters = sections[0], sections[1:]
        if not parameters:
            parameters = ['']

        try:
            expression = cls.registry[name]
        except KeyError:
            s = 'Unregistered shorthand identifier "{}" in "{}".'
            raise exc.MarkupError(s.format(name, shorthand))

        try:
            # Replacements can be valid shorthand. Therefore, we recurse down.
            return cls.parse(expression.replacement).format(*parameters)
        except IndexError:
            s = 'Parameters {} insufficient for expansion of "{}" to "{}".'
            raise exc.MarkupError(s.format(sections, shorthand,
                                           expression.replacement))


class Shorthand():
    '''A code word for replacement of text with other text.'''

    def __init__(self, markupstring, replacement, authority=Authority):
        self.markupstring = markupstring
        self.replacement = replacement
        authority.register(self)
