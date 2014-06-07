# -*- coding: utf-8 -*-
'''All exceptions in the package.'''


class SpecificationError(Exception):
    '''A human error in the design of a YAML specification for a deck.'''
    pass


class PageFull(Exception):
    '''Not an error. Footprint cannot be fitted into current page layout.'''
    pass


class PrintableAreaTooSmall(Exception):
    '''Footprint too large for page type. Layout impossible.'''
    pass
