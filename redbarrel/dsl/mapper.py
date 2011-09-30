"""
    Mapper that loads the AST and produces the routing

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import sys
import traceback

from routes import Mapper
from webob.exc import HTTPNotFound, HTTPServiceUnavailable
from webob import Response

from redbarrel import logger
from redbarrel.dsl.hook import WebHook
from redbarrel.dsl.runners import resolve_runner


class BackendError(Exception):
    pass


class WebMapper(object):
    """
    Loads the AST, link routes and run the post- and pre-conditions
    """
    def __init__(self, dsl):
        sys.path.insert(0, os.getcwd())  # why ?
        self.mapper = Mapper()
        self.globs = dsl.globs
        self.types = dsl.types
        self.context = dsl.context
        self._hooks = {}
        self.options = {}
        self.root = dsl.root
        self.root_path = dsl.root_path

    def add(self, name, args):
        if name in self._hooks:
            raise NameError('%r already defined.' % name)

        params = {}
        for arg in args:
            if arg.type == 'assign':
                left = arg.left
                right = arg.right
                if isinstance(left, basestring):    # XXX meh
                    params[left] = right
                else:
                    name_ = left.value
                    if isinstance(right, list):
                        params[name_] = arg.right
                    else:
                        params[name_] = arg.right.value
            else:
                raise NotImplementedError(arg)

        use = params.get('use', 'redbarrel.util.dummy')

        if 'url' in params:
            url = params.get('url', '/')
            if self.root_path:
                if url != '/':
                    url = self.root_path + url
                else:
                    url = self.root_path

            try:
                function = resolve_runner(use, self.root, url)
            except ImportError:
                # let's try in the context
                # # XXX ugly, need isolation
                function = None

                for lib in self.context.libraries:
                    for callable in lib.dir():
                        name_ = '%s.%s' % (lib.name, callable)
                        if name_ == use:
                            function = lib.namespace[callable]
                            break

                if function is None:
                    logger.info(" => Error on %r" % name)
                    raise

            params['func'] = function

            conditions = {}
            oldname = name
            params['name'] = name


            if 'method' in params:
                conditions['method'] = [str(method)
                            for method in params['method']]
                self.mapper.connect(None, url, action=name,
                                    conditions=conditions)

            self._hooks[name] = WebHook(params, self.types)
            logger.info(" => %r hooked for %r" % (oldname, url))

        else:
            logger.info(" => %r incomplete, ignoring" % name)

    def set_options(self, options):
        for option in options:
            if option.type == 'assign':
                left = option.left
                right = option.right

                if isinstance(left, basestring):    # XXX meh
                    self.options[left] = right
                else:
                    self.options[left.value] = right.value
            else:
                raise NotImplementedError(option)

    def __call__(self, request):
        # finding a match
        match = self.mapper.routematch(environ=request.environ)
        if match is None:
            return HTTPNotFound()
        match, __ = match
        hook = self._hooks.get(match['action'])

        if hook is None:
            raise HTTPNotFound('Unknown URL %r' % request.path_info)

        hook.preconditions(request, self.globs)

        function = hook['func']

        # the GET mapping is filled on GET and DELETE requests
        if request.method in ('GET', 'DELETE'):
            params = dict(request.GET)
        else:
            params = {}

        request.match = match

        try:
            result = function(self.globs, request, **params)
        except BackendError:
            err = traceback.format_exc()
            logger.error(err)
            raise HTTPServiceUnavailable(retry_after=self.retry_after)

        if isinstance(result, basestring):
            response = getattr(request, 'response', None)
            if response is None:
                response = Response(result)
            elif isinstance(result, str):
                response.body = result
            else:
                # if it's not str it's unicode, which really shouldn't happen
                response.body = result.encode('utf-8')
        else:
            # result is already a Response
            response = result

        hook.postconditions(response, request, self.globs)
        return response
