# -*- coding: utf-8 -*-

import collections

def listlike(object_):
    '''True if object_ is an iterable container.'''
    if isinstance(object_, collections.Iterable) \
            and not isinstance(object_, str):
        return True
    return False
