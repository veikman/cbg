# -*- coding: utf-8 -*-

import re
import logging


class Shorthand():
    '''A replacement of text in raw specifications with richer text.'''
    ## TODO: Expand/subclass/extend at SVG stage to use pictures.

    substring_lead_in = '_'
    substring_lead_out = substring_lead_in
    substring_separator = ':'

    def __init__(self, markupstring, replacement):
        self.markupstring = markupstring
        self.replacement = replacement

    def _find_substring(self, name):
        name = 'substring_' + name  # Avoid recursion.
        if hasattr(self, name):
            ret = getattr(self, name)
        elif hasattr(self.__class__, name):
            ret = getattr(self.__class__, name)
        elif hasattr(super(), name):
            ret = getattr(super(), name)
        else:
            raise ValueError('No such token substring: {}.'.format(name))
        assert type(ret) == str
        return ret

    @property
    def lead_in(self):
        return self._find_substring('lead_in')

    @property
    def lead_out(self):
        return self._find_substring('lead_out')

    @property
    def separator(self):
        return self._find_substring('separator')

    def apply_to(self, text):
        '''Point of entry.'''
        return self.conclude(text, self.regular_expression(text))

    def regular_expression(self, text):
        '''Look for a match in duck-typed rule text object.'''
        template = '{0}{1}(|{2}|{2}[^{3}]*){3}'
        pattern = template.format(self.lead_in, self.markupstring,
                                  self.separator, self.lead_out)
        try:
            modified = re.sub(pattern, self.substitute, text.string)
        except AttributeError:
            s = 'Markup duck-typing failure with {}.'
            logging.critical(s.format(repr(text)))
            raise
        except TypeError:
            s = 'Regex type failure with {}: {}.'
            logging.critical(s.format(repr(text.string), str(text.string)))
            raise
        return modified

    def substitute(self, match):
        '''Replace shorthand expression. Called by re.sub().'''
        parameters = self.find_parameters(match)
        if parameters:
            return self.insert_parameters(self.replacement, parameters)
        return self.replacement

    def find_parameters(self, match):
        argblock = match.groups()[-1].lstrip(self.separator)
        if argblock is None:
            ## Implies error in regex construction.
            s = 'No match for possible group of arguments to token "{}".'
            raise ValueError(s.format(self.markupstring))
        if argblock == '':
            return []
        else:
            ## Convert to tuple so that the old-style string formatting
            ## syntax can understand it.
            return tuple(argblock.split(self.separator))

    def insert_parameters(self, template, parameters):
        if len(template) == 1 and len(parameters) == 1:
            ## Assume we are dealing with a symbol that can take an amount
            ## as a prefix, but does not have to.
            return str(parameters[0]) + template
        try:
            return template % parameters
        except TypeError:
            ## The wrong amount of anchor points, presumably.
            s = 'Failed to place token parameters "{}" in "{}".'
            logging.critical(s.format(parameters, self.replacement))
            raise

    def conclude(self, original, outcome):
        if original.string == outcome:
            ## No match.
            return False
        else:
            original.string = outcome
            return True

    def __str__(self):
        '''The expected string, with delimiters but without parameters.'''
        return self.lead_in + self.markupstring + self.lead_out


class Interpolator(Shorthand):
    '''Special markup that triggers examination of a larger context.'''

    def apply_to(self, text):
        '''Point of entry.'''
        try:
            field = text.parent
        except AttributeError:
            self._error()
            s = 'Expected to operate on paragraph with parent field, found {}.'
            logging.critical(s.format(repr(text)))
            raise

        try:
            card = field.parent
        except AttributeError:
            self._error()
            s = 'Expected to operate on field with parent card, found {}.'
            logging.critical(s.format(repr(field)))
            raise

        return self.conclude(text, self.interpolate(card, field, text))

    def _error(self):
        logging.error('Unable to interpolate from shorthand.')

    def interpolate(self, card, field, text):
        raise NotImplementedError
