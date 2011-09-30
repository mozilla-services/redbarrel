# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import unittest

from redbarrel.dsl.hook import WebHook
from redbarrel.dsl import build_ast


_RBR = """\
path foo (
    url /foo,
    use python:foo.bar,
    response-headers (
        description "here"
    ),
);
"""


class TestWebHook(unittest.TestCase):

    def test_describe(self):
        ast = build_ast(_RBR)
        resp_headers = ast[0].right[2].right
        params = {'url': '/',
                  'use': 'do.something',
                  'response-headers': resp_headers}

        hook = WebHook(params)
        self.assertEqual(hook.describe('response-headers'), '<p>here</p>')
