# -*- coding: utf-8 -*-
"""
    Contains the pistil worker

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import socket

from pistil.tcp.sync_worker import TcpSyncWorker

from gevent.pywsgi import WSGIServer
from gevent.pool import Pool
import gevent

from socketio.policyserver import FlashPolicyServer
try:
    from redbarrel.broadcast import Client, Broadcaster
    ZMQ_SUPPORTED = True
except ImportError:
    Broadcaster = Client = None     # NOQA
    ZMQ_SUPPORTED = False

from redbarrel.server.servers import RedBarrelSocketIOServer
from redbarrel.server.handlers import RedBarrelSocketIOHandler
from redbarrel import logger


class RedBarrelWSGIWorker(TcpSyncWorker):

    def on_init(self, conf):
        super(RedBarrelWSGIWorker, self).on_init(conf)
        self.conf = conf
        self.worker_connections = conf.get('worker_connections')

    def on_init_process(self):
        if 'sock' not in self.conf:
            return
        super(RedBarrelWSGIWorker, self).on_init_process()

    def _on_socket_error(self, err):
        raise err

    def run(self):
        if 'sock' in self.conf:
            self.socket.setblocking(1)

            # loading the wsgi app    / XXX in which worker ?
            from redbarrel.wsgiapp import WebApp
            self.application = WebApp(self.conf['path'],
                                      worker=self)

        # creating and starting the server
        server = self._get_server()
        try:
            server.start()
            running = True
        except socket.error, err:
            self._on_socket_error(err)
            running = False

        self._after_start()
        try:
            while self.alive:
                self.notify()
                if self.ppid != os.getppid():
                    logger.debug("Parent changed, shutting down: %s", self)
                    break
                gevent.sleep(1.0)
        except KeyboardInterrupt:
            pass

        # try to stop the connections
        try:
            self.notify()
            if running:
                server.stop(timeout=self.timeout)
                self._after_stop()
        except Exception, err:
            logger.error(str(err))

    if hasattr(gevent.core, 'dns_shutdown'):

        def init_process(self):
            # gevent 0.13 and older doesn't reinitialize
            # dns for us after forking
            # here's the workaround
            gevent.core.dns_shutdown(fail_requests=1)
            gevent.core.dns_init()
            super(RedBarrelWSGIWorker, self).init_process()

    def _get_server(self):
        pool = Pool(self.worker_connections)
        return WSGIServer(self.socket, application=self.application,
                          spawn=pool)  # , worker=self)

    def _after_start(self):
        pass

    def _after_stop(self):
        pass


class RedBarrelSocketIOWorker(RedBarrelWSGIWorker):
    """SocketIO Worker.

       Has a broadcaster + a SocketIO server
    """
    def on_init(self, conf):
        super(RedBarrelSocketIOWorker, self).on_init(conf)
        self.receive_port = conf.get('receive_port', 5000)
        self.push_port = conf.get('push_port', 5001)
        self.broadcaster = None

    def callback(self, msg):
        # TO IMPLEMENT XXX
        pass

    def broadcast(self, filter, msg):
        if self.broadcaster is None:
            return   # XXX warning ?
        self.broadcaster.broadcast("%s %s" % (filter, msg))

    def _get_server(self):
        pool = Pool(self.worker_connections)
        return RedBarrelSocketIOServer(self.socket,
                                       application=self.application,
                                       spawn=pool, worker=self,
                                       handler_class=RedBarrelSocketIOHandler,
                                       resource="socket.io",
                                       memory=True)

    def _after_start(self):
        if ZMQ_SUPPORTED:
            self.broadcaster = Client(self.receive_port, self.push_port,
                                      self.callback)

            self.broadcaster.start()

    def _after_stop(self):
        if ZMQ_SUPPORTED:
            self.broadcaster.stop()


class FlashPolicyWorker(RedBarrelWSGIWorker):
    def _get_server(self):
        return FlashPolicyServer()

    def _on_socket_error(self, err):
        logger.warning('Flash Policy Server not running (%s)' % str(err))


class BroadcasterWorker(RedBarrelWSGIWorker):
    def on_init(self, conf):
        super(BroadcasterWorker, self).on_init(conf)
        self.receive_port = conf.get('receive_port', 5000)
        self.push_port = conf.get('push_port', 5001)
        self.bc = Broadcaster(self.receive_port, self.push_port)

    def _get_server(self):
        return Broadcaster(self.receive_port, self.push_port)


WORKERS = {'flash': FlashPolicyWorker,
           'broadcast': BroadcasterWorker,
           'socketio': RedBarrelSocketIOWorker,
           'wsgi': RedBarrelWSGIWorker}
