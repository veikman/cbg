# -*- coding: utf-8 -*-
'''All exceptions in the package.'''

class SpecificationError(Exception):
    '''A human error in the design of a YAML specification for a deck.'''
    pass

class PageFull(Exception):
    pass

class PrintableAreaTooSmall(Exception):
    pass
