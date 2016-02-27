# -*- coding: utf-8 -*-
'''Unit tests for CBG.'''


import unittest

import cbg


class LayoutField(unittest.TestCase):

    class TagDependentField(cbg.content.text.TextField):
        '''A field that, if found in specs, will react to tags elsewhere.'''
        key = 'tdf'

        def in_spec(self):
            for tag in self.tags:
                self.specification = 2 * self.specification
            super().in_spec()

    def test_direct_access_to_tags(self):
        class DirectContainerCard(cbg.content.card.Card):
            plan = (cbg.content.tag.BaseTagField,
                    self.TagDependentField)

        c = DirectContainerCard({'tdf': 'x'})
        self.assertEqual(list(map(str, c)), ['', 'x'])

        c = DirectContainerCard({'tags': ['A'], 'tdf': 'x'})
        self.assertEqual(list(map(str, c)), ['A', 'xx'])

        c = DirectContainerCard({'tags': ['A', 'B'], 'tdf': 'x'})
        self.assertEqual(list(map(str, c)), ['A, B', 'xxxx'])

    def test_indirect_access_to_tags(self):
        class ContainerField(cbg.content.field.Layout):
            plan = (cbg.content.tag.BaseTagField,
                    self.TagDependentField)

        class IndirectContainerCard(cbg.content.card.Card):
            plan = (ContainerField,)

        c = IndirectContainerCard({'tdf': 'y'})
        self.assertEqual(list(map(str, c[0])), ['', 'y'])

        c = IndirectContainerCard({'tags': ['1'], 'tdf': 'y'})
        self.assertEqual(list(map(str, c[0])), ['1', 'yy'])

        c = IndirectContainerCard({'tags': ['1', '2'], 'tdf': 'y'})
        self.assertEqual(list(map(str, c[0])), ['1, 2', 'yyyy'])
