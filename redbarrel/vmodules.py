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

""" Sanboxed execution of Python and JS modules.
"""
import os
from sandbox import Sandbox, SandboxConfig


_UNKNOWN = 0
_PYTHON = 'py'
_JS = 'js'
_ROOT = os.path.join(os.path.dirname(__file__), 'libs')
_ALLOWED_MODULES = (('json', []),
                    ('time', []),
                    ('re', []),
                    ('StringIO', ['StringIO']),
                    ('cssmin', []))


class VirtualModule(object):
    """Can contain callables"""
    def __init__(self, name, content, type=_PYTHON):
        """
        - name: the module name (with no extension).
        - content: Python or JS code
        - type: 'js', 'py'  (XXX might be removed)
        """
        self.libtype = type
        self.name = name
        self.content = content
        self.namespace = {}

        if type == 'js':
            raise NotImplementedError()

        config = SandboxConfig('code')
        for module, elements in _ALLOWED_MODULES:
            config.allowModule(module, *elements)
        self.sandbox = Sandbox(config)
        self._load()

    def update(self, content):
        self.content = content
        self._load()
        self.sync()

    def sync(self):
        path = os.path.join(_ROOT, self.name + '.py')
        with open(path, 'w') as f:
            f.write(self.content)

    def _load(self):
        # XXX will scan and load the callables
        #if self.libtype == _PYTHON:
        #self.namespace = {'__text': self.content}
        #self.sandbox.execute('exec compile(__text, "<string>", "exec")',
        #                     locals=self.namespace)
        exec compile(self.content, self.name, 'exec') in self.namespace

    def call(self, function, *args, **kw):
        #return self.sandbox.call(self.namespace[function], *args, **kw)
        return self.namespace[function](*args, **kw)

    def dir(self):
        keys = self.namespace.keys()
        #keys.remove('__text')
        return keys

    def doc(self, name):
        return self.namespace[name].__doc__
