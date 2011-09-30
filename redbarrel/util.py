# -*- coding: utf-8 -*-
"""
    Contains various helpers.

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import sys
import argparse
import mimetypes
import urllib2
import logging
from ConfigParser import ConfigParser

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator
from webob.response import Response

from redbarrel import logger


def check_syntax(args=None):
    parser = argparse.ArgumentParser(
        description='Checks the syntax of a RBR file.')
    parser.add_argument('path', type=str, help='Path of the RBR file')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args(args=args)
    from redbarrel.dsl import build_ast
    with open(args.path) as f:
        res = build_ast(f.read(), args.verbose)

    if res is None:
        print("Syntax Error.")
        sys.exit(1)
    else:
        print("Syntax OK.")
        sys.exit(0)


def _set_logger(debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level)


def run_server(args=None):

    parser = argparse.ArgumentParser(
        description='Runs a RBR file.')

    # how to make this optional ??
    parser.add_argument('path', type=str, help='Path of the RBR file',
                        nargs='*')

    parser.add_argument('--port', type=int, default=8000,
                        help='Port to run the server')
    parser.add_argument('--workers', type=str, default='http:1',
                        help='Workers and/or arbiters')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Debug mode')
    parser.add_argument('--config', type=str, default=None,
                        help='Configuration file')

    args = parser.parse_args(args=args)
    if args.path is None:
        args.path = []

    def _workers(_workers):
        workers = []
        for worker in _workers.split(','):
            if ':' in worker:
                worker, number = worker.split(':')
                number = int(number)
            else:
                number = 1
            workers.append((worker, number))
        return workers

    args.workers = _workers(args.workers)

    if args.config is not None:
        # loading the config file and overriding options
        config = ConfigParser()
        config.read(args.config)
        options = dict([(key, value.strip()) for key, value
                        in config.items('rbr')])

        if 'port' in options:
            args.port = int(options['port'])

        if 'workers' in options:
            args.workers = _workers(options['workers'])

        if 'debug' in options:
            args.debug = int(options['debug'])

        if 'rbr-file' in options:
            args.path = options['rbr-file']

    _set_logger(args.debug)
    _run_server(args)


def _run_server(args):
    logger.info("Serving on port %d..." % args.port)

    # loading the rbr to get the workers/arbiters
    from redbarrel.dsl import build_ast
    from redbarrel.dsl.runners import resolve_runner

    workers = {}
    arbiters = {}

    for path in args.path:
        with open(path) as f:
            ast = build_ast(f.read())

        for definition in ast:
            type_ = definition.type
            if type_ not in ('worker', 'arbiter'):
                continue

            name = definition[1]
            logger.info('Loading %s %r' % (type_, name))
            runner = resolve_runner(definition[2])
            if type_ == 'worker':
                workers[name] = runner
            else:
                arbiters[name] = runner

    # default arbiters and workers
    from redbarrel.server.arbiters import ARBITERS
    arbiters.update(ARBITERS)

    from redbarrel.server.workers import WORKERS
    workers.update(WORKERS)

    # now loading the workers and arbiters, given a config
    specs = []
    from pistil.arbiter import Arbiter

    conf = {"address": ("127.0.0.1", args.port),
            "debug": True,
            "memory": True,
            #"num_workers": args.workers,
            "path": args.path}

    for name, num in args.workers:
        # is it an arbiter or a worker ?
        if name in arbiters:
            klass = arbiters[name]
            type_ = 'supervisor'
        elif name in workers:
            klass = workers[name]
            type_ = 'worker'
        else:
            raise ValueError(name)

        timeout = 90000  # XXX to be defined
        specs.append((klass, timeout, type_, {}, name))
        # XXX conf ?
        #

    arbiter = Arbiter(conf, specs)
    arbiter.run()

    return
    if args.workers == 1:
        from redbarrel.wsgiapp import WebApp
        from redbarrel.server import RedBarrelSocketIOServer
        app = WebApp(args.path)
        server = RedBarrelSocketIOServer(('', args.port), app,
                                          resource='socket.io',
                                          policy_server=True, memory=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        try:
            import redis   # NOQA
        except ImportError:
            logger.error('You need to install the Redis python client in '
                         'order to support several workers')
            sys.exit(0)

        from redbarrel.server import RedBarrelArbiter
        from redbarrel.server import ZMQ_SUPPORTED

        if not ZMQ_SUPPORTED:
            logger.warning('0MQ not supported, broacasts will fail.')
            logger.warning('If you want 0MQ, install pyzmq.')

        from redbarrel.server import BroadcasterWorker
        from redbarrel.server import FlashPolicyWorker

        from pistil.arbiter import Arbiter

        conf = {"address": ("127.0.0.1", args.port),
                "debug": True,
                "num_workers": args.workers,
                "path": args.path,
                "receive_port": 5000,
                "push_port": 5001}

        specs = [(RedBarrelArbiter, 999999, "supervisor", {}, "tcp_pool"),
                 (FlashPolicyWorker, 30, "worker", {}, "flash")]

        if ZMQ_SUPPORTED:
            specs.append((BroadcasterWorker, 30, "worker", {}, "0mq"))

        arbiter = Arbiter(conf, specs)
        arbiter.run()


class HTMLFragmentTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

    def astext(self):
        return ''.join(self.body)


class _FragmentWriter(Writer):
    translator_class = HTMLFragmentTranslator

    def apply_template(self):
        subs = self.interpolation_dict()
        return subs['body']


def reST2HTML(data):
    return core.publish_string(data, writer=_FragmentWriter())


def response(path):
    """Returns the file content in a response
    with a guessed mimetype
    """
    mimetype = mimetypes.guess_type(path)[0]
    with open(path) as f:
        content = f.read()
    return Response(content, content_type=mimetype)


def translate(rules, part=''):
    """Translates rules in a human readable format."""
    from redbarrel.dsl.runners import resolve_runner

    def _ds(func):
        doc = resolve_runner(func).__doc__
        if doc is None:
            return func
        return '%r (%s)' % (func, doc)

    def _translate(rule, part=''):
        if rule.type == 'val':
            rule = rule.value
        if rule.type == 'description':
            return None
        return str(rule)

    res = []
    if isinstance(rules, tuple):
        tran = _translate(rules, part)
        if tran is not None:
            res.append(tran)
    else:
        for rule in rules:
            tran = _translate(rule, part)
            if tran is not None:
                res.append(tran)

    return res


def dummy(globs, request, **params):
    res = Response(str(request))
    res.headers['Content-Type'] = 'text/plain'
    return res


def read_url(url):
    """
    Return the content of an url
    """
    response = urllib2.urlopen(url)
    return response.read()
