# -*- coding: utf-8 -*-
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Sync Server
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   See AUTHORS.txt
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****
import unittest
import os
from redbarrel.dsl import build_ast


_SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')


class TestParser(unittest.TestCase):

    def test_files(self):
        # test some files
        for path in os.listdir(_SAMPLES):
            if os.path.splitext(path)[-1] != '.rbr':
                continue

            fullpath = os.path.join(_SAMPLES, path)
            with open(fullpath) as f:
                ast = build_ast(f)

            if ast is None:
                raise AssertionError(fullpath)

    def test_several(self):
        with open(os.path.join(_SAMPLES, 'service.rbr')) as f:
            ast = build_ast(f)

        wanted = {200: 'Success',
               503: 'Problems with looking up the user or sending the email',
               400: 'No email address on file for user',
               404: 'User not found'}

        statuses = [status.value for status in ast[0].right[4].right]
        self.assertEqual(len(statuses), 4)

        for status in statuses:
            code = status.left
            desc = status.right
            self.assertEquals(wanted[code], desc)

    def test_one_val_paren(self):
        with open(os.path.join(_SAMPLES, 'html.rbr')) as f:
            ast = build_ast(f)

        # let's check that we have a single set in the ast
        res = ast[0].right[4].right[0].value
        res = res.collapse()
        self.assertEqual(res, 'set content-type "text/html"')
