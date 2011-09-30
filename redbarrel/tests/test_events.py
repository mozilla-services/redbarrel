# -*- coding: utf-8 -*-
"""
    Worker message broadcasting

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import unittest
from redbarrel.events import get_pubsub


class TestEvents(unittest.TestCase):

    def test_pubsub(self):

        def alice(data):
            data.append('alice')

        def bob(data):
            data.append('bob')

        ps = get_pubsub('memory')
        ps.subscribe('yo', alice)
        ps.subscribe('yo', bob)
        ps.subscribe('yo', bob)   # will be ignored
        stuff = []

        ps.notify('yo', stuff)
        self.assertEquals(stuff, ['alice', 'bob'])

        ps.unsubscribe('yo', alice)
        ps.notify('yo', stuff)
        self.assertEquals(stuff, ['alice', 'bob', 'bob'])
