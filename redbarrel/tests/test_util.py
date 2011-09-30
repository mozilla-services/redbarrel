# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import tempfile
import os

import unittest
from redbarrel.util import reST2HTML, run_server
from redbarrel import util


_CFG = """
[rbr]
port = 9090
workers = 3
debug = 1
rbr-file = /there
"""


class TestUtil(unittest.TestCase):

    def test_rst(self):
        self.assertEqual(reST2HTML('here'), '<p>here</p>')

    def test_run_server(self):
        fd, tmpfile = tempfile.mkstemp()
        os.close(fd)
        with open(tmpfile, 'w') as f:
            f.write(_CFG)

        def _run(args):
            self.assertEqual(args.port, 9090)
            self.assertEqual(args.workers, [('3', 1)])
            self.assertTrue(args.debug)
            self.assertEqual(args.path, '/there')

        args = ['', '--config', tmpfile]
        old = util._run_server
        util._run_server = _run
        try:
            run_server(args)
        finally:
            os.remove(tmpfile)
            util._run_server = old
