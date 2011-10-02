# -*- coding: utf-8 -*-
"""
    Contains all runnners used by use:

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import urlparse
import sys

from redbarrel.util import response
from wsgiproxy.exactproxy import proxy_exact_request

_RUNNERS = {}


def get_runner_names():
    return _RUNNERS.keys()


def register_runner(name):
    def _register(function):
        _RUNNERS[name] = function

        def __register(*args, **kw):
            return function(*args, **kw)
        return __register

    return _register


@register_runner('file')
def rfile(name, root, url):
    name = os.path.abspath(os.path.join(root, name))
    if not os.path.exists(name):
        raise IOError(name)

    def __file(*args, **kw):
        return response(name)

    return __file


@register_runner('directory')
def rdirectory(name, root, url):
    path = os.path.join(root, name)

    if not os.path.exists(path):
        raise IOError(path)

    def __directory(globs, request, **kw):
        match = request.match
        if match is None:
            raise IOError(path)
        name = match.get('name')
        if name is None or name.startswith('.'):
            raise IOError(path)

        filename = os.path.join(path, name)
        return response(filename)

    return __directory


@register_runner('proxy')
def rproxy(name, root, url):
    parsed = urlparse.urlsplit(url)
    if ':' in parsed.netloc:
        location, port = parsed.netloc.split(':')
    else:
        location = parsed.netloc
        if parsed.scheme == 'https':
            port = '443'
        else:
            port = '80'

    def __proxy(globals, request, **params):
        path_info = request.path_info
        if path_info.startswith(url):
            path_info = '/' + path_info[len(url):]
        request.environ['PATH_INFO'] = path_info
        request.path_info = path_info
        request.environ['SERVER_NAME'] = location
        request.environ['SERVER_PORT'] = port
        return request.get_response(proxy_exact_request)
    return __proxy


def _save_env(func):
    def __save_env(*args, **kw):
        old_sys = sys.path[:]
        try:
            return func(*args, **kw)
        finally:
            sys.path[:] = old_sys
    return __save_env


@register_runner('python')
@_save_env
def rpython(name, root, url):
    sys.path.insert(0, root)
    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]
    last_error = None
    last_error_module_path = None
    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError, ext:
            last_error = ext
            args = []
            if (root is not None and
                not '/'.join(module_name).startswith(root)):
                args.append(root)
            args += module_name
            last_error_module_path = '%s.py' % os.path.join(*args)
            if cursor == 0:
                raise
            cursor -= 1
            module_name = parts[:cursor]
            ret = ''
        else:
            last_error = None
            last_error_module_path = None

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError as exc:
            if last_error is not None \
                    and os.path.isfile(last_error_module_path):
                raise last_error
            raise ImportError(exc)

    return ret


def resolve_runner(name, root=None, url=None):
    if ':' in name:
        prefixed = name.split(':', 1)
        if prefixed[0] not in _RUNNERS:
            raise NotImplementedError(name)
        prefix, nname = prefixed
        name = nname
    else:
        prefix = 'python'   # default

    return _RUNNERS[prefix](name, root, url)
