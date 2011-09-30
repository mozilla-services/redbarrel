# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import unittest
import os

from redbarrel.dsl.parser import build_ast


_SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')


class TestParser(unittest.TestCase):

    def test_files(self):
        # test some files
        for path in os.listdir(_SAMPLES):
            if os.path.splitext(path)[-1] != '.rbr':
                continue

            fullpath = os.path.join(_SAMPLES, path)
            ast = build_ast(fullpath)
            if ast is None:
                raise AssertionError(fullpath)

    def test_several(self):
        path = os.path.join(_SAMPLES, 'service.rbr')
        ast = build_ast(path)

        wanted = {200: 'Success',
                503: 'Problems with looking up the user or sending the email',
                400: 'No email address on file for user',
                404: 'User not found'}

        response_status = ast[0][2][4]
        self.assertEqual(len(response_status[2]), 4)
        for desc in response_status[2]:
            code = desc[1][1]
            desc = desc[1][2]
            self.assertEquals(wanted[code], desc)

    def test_one_val_paren(self):
        path = os.path.join(_SAMPLES, 'html.rbr')
        ast = build_ast(path)

        response_headers = ast[0][2][4][2]

        # we want a list of assignements
        self.assertTrue(isinstance(response_headers, list))

        # we have a single assignement
        content_type = response_headers[0]
        self.assertEqual(content_type,
                     ('val', ('assign', 'content-type', ('val', 'text/html'))))
