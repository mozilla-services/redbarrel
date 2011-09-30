# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import unittest
import os

from redbarrel.dsl import build_ast


_SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')


class TestParser(unittest.TestCase):

    def _rbrs(self):
        for path in os.listdir(_SAMPLES):
            if os.path.splitext(path)[-1] != '.rbr':
                continue

            yield os.path.join(_SAMPLES, path)

    def test_files(self):
        for fullpath in self._rbrs():
            with open(fullpath) as f:
                ast = build_ast(f.read())

            if ast is None:
                raise AssertionError(fullpath)

    def test_collapse(self):
        for fullpath in self._rbrs():
            with open(fullpath) as f:
                dsl = f.read()
                ast = build_ast(dsl)
            self.assertEquals(ast.collapse(), dsl)

    def test_several(self):
        path = os.path.join(_SAMPLES, 'service.rbr')
        with open(path) as f:
            ast = build_ast(f.read())

        wanted = {200: 'Success',
                503: 'Problems with looking up the user or sending the email',
                400: 'No email address on file for user',
                404: 'User not found'}

        response_status =  ast[0].right[4].right

        for status in response_status:
            code = status.value.left
            desc = status.value.right
            self.assertEquals(wanted[code], desc)

    def test_one_val_paren(self):
        path = os.path.join(_SAMPLES, 'html.rbr')
        with open(path) as f:
            ast = build_ast(f.read())

        response_headers = ast[0].right[4].right

        # we want a list of assignements
        self.assertTrue(isinstance(response_headers, list))

        # we have a single assignement
        content_type = response_headers[0]
        self.assertEqual(content_type.collapse(level=-1),
                         'set content-type "text/html"')
