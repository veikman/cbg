# -*- coding: utf-8 -*-
'''Generalized handling of data serialization languages.'''

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


###########
# IMPORTS #
###########


# Standard:
import json
import logging

# Third party:
try:
    # PyYAML.
    import yaml
except ImportError:
    yaml = None


#####################
# INTERFACE CLASSES #
#####################


class Serialization():
    '''An abstraction to handle multiple serialization formats agnostically.

    Packaged as a singleton-like expert for ease of extensions by users.

    '''

    registry = dict()

    def __init__(self, extensions, load_function, dumps_function):
        self.load = load_function
        self.dumps = dumps_function
        for extension in extensions:
            self.registry[extension.lower()] = self

    @classmethod
    def _get(self, extension):
        try:
            return self.registry[extension.lower()]
        except KeyError:
            s = ('Filename extension "{}" not a registered serialization '
                 'format, or not supported on local platform.')
            logging.error(s.format(extension))
            raise

    @classmethod
    def load(self, filepath):
        '''Open and read from named file. Return deserialized contents.'''

        file_ending = filepath.split('.')[-1].lower()
        specialist = self._get(file_ending)

        with open(filepath, encoding='utf-8') as filelike_object:
            return specialist.load(filelike_object)

    @classmethod
    def dumps(self, data, format='json'):
        '''Return a string.'''
        specialist = self._get(format)
        return specialist.dumps(data)


############
# EXAMPLES #
############


JSON = Serialization(('json',),
                     lambda f: json.load(f),
                     lambda f: json.dumps(f))

if yaml:
    YAML = Serialization(('yaml', 'yml'),
                         lambda f: yaml.load(f),
                         lambda f: yaml.dumps(f))
