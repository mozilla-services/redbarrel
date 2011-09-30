# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import unittest
from redbarrel.dsl.hook import WebHook


class TestWebHook(unittest.TestCase):

    def test_describe(self):

        params = {'url': '/',
                  'use': 'do.something',
                  'response-headers':
                    (['', ('description', 'here')],)}
        hook = WebHook(params)
        self.assertEqual(hook.describe('response-headers'), '<p>here</p>')
