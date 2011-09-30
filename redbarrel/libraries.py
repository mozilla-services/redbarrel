""" Libraries

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
from sandbox import Sandbox, SandboxConfig


_UNKNOWN = 0
_PYTHON = 1
_ROOT = os.path.join(os.path.dirname(__file__), 'libs')


class Library(object):
    """Can contain callables"""
    def __init__(self, path, name=None):
        self.path = path
        filename = os.path.split(path)[-1]
        if name is None:
            self.name = os.path.splitext(filename)[0]
        else:
            self.name = name

        ext = os.path.splitext(self.path)[-1]

        if ext == '.py':
            self.libtype = _PYTHON
        else:
            self.libtype = _UNKNOWN

        #self.config = SandboxConfig('stdout', 'code')
        config = SandboxConfig('code')
        self.sandbox = Sandbox(config)
        self._load()

    def update(self, content):
        self.path = content
        self._load()
        self.sync()

    def sync(self):
        path = os.path.join(_ROOT, self.name + '.py')
        with open(path, 'w') as f:
            f.write(self.code)

    def _load(self):
        # will scan and load the callables
        #if self.libtype == _PYTHON:
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.code = f.read()
        else:
            self.code = self.path

        self.namespace = {'__text': self.code}

        self.sandbox.execute('exec compile(__text, "<string>", "exec")',
                             locals=self.namespace)

    def call(self, function, *args, **kw):
        return self.sandbox.call(self.namespace[function], *args, **kw)

    def dir(self):
        keys = self.namespace.keys()
        keys.remove('__text')
        return keys

    def doc(self, name):
        return self.namespace[name].__doc__
