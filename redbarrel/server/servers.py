# -*- coding: utf-8 -*-
"""
    Contains custom redbarrel servers

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import sys
from thread import get_ident

from socketio.server import SocketIOServer
from socketio.protocol import SocketIOProtocol
from socketio.policyserver import FlashPolicyServer

try:
    from redbarrel.broadcast import Client, Broadcaster
    ZMQ_SUPPORTED = True
except ImportError:
    Broadcaster = Client = None     # NOQA
    ZMQ_SUPPORTED = False


from redbarrel import logger
from redbarrel.server.session import RedBarrelSessionManager, MEM, REDIS
from redbarrel.server.handlers import RedBarrelSocketIOHandler

# workaround on osx, disable kqueue
if sys.platform == "darwin":
    os.environ['EVENT_NOKQUEUE'] = "1"


class RedBarrelSocketIOProtocol(SocketIOProtocol):

    def send(self, message, destination=None):
        SocketIOProtocol.send(self, message, destination)
        # XXX this is were we want to broadcast to other servers if destination
        # is located somewhere else
        # via ZMQ
        if destination is not None:
            logger.debug('sending socketio to %s' % destination)

    def broadcast(self, message, exceptions=None):
        SocketIOProtocol.broadcast(self, message, exceptions)
        # XXX this is were we want to broadcast to other servers
        # via ZMQ
        # XXX TODO : be able to pass exceptions (which should be augmented with
        # all local sesssion ids)
        logger.debug('broadcasting socketio')

    def recv(self):
        logger.debug('Wait for incoming messages')

        msg = self.session.get_server_msg()

        logger.debug(str(self.session))
        if msg is None:
            return []
        else:
            logger.debug('Received %s' % msg)

            return msg


class RedBarrelSocketIOServer(SocketIOServer):
    def __init__(self, *args, **kwargs):

        self.resource = kwargs.pop('resource')
        if kwargs.pop('policy_server', False):
            self.policy_server = FlashPolicyServer()
        else:
            self.policy_server = None
        self.worker = kwargs.pop('worker', None)
        kwargs['handler_class'] = RedBarrelSocketIOHandler
        if kwargs.pop('memory', True):
            self.sessions = RedBarrelSessionManager(MEM)
        else:
            self.sessions = RedBarrelSessionManager(REDIS)
        super(SocketIOServer, self).__init__(*args, **kwargs)

    def handle(self, socket, address):
        handler = self.handler_class(socket, address, self)
        self.set_environ({'socketio': RedBarrelSocketIOProtocol(handler)})
        handler.handle()

    def broadcast(self, message, exceptions=None):
        """
        Send messages to all connected clients
        """
        if exceptions is None:
            exceptions = []

        for session_id, session in self.sessions.iteritems():
            if session_id not in exceptions:
                session.put_client_msg(message)

    def get_session(self, session_id=''):
        """Return an existing or new client Session."""
        logger.debug("LOOKING FOR SESSION %s" % session_id)
        exists = self.sessions.session_exists(session_id)
        if exists:
            logger.debug('session exists')
        else:
            logger.debug('session does not exist')
            logger.debug('existing sessions are %s' \
                    % self.sessions.get_session_ids())

        session = self.sessions.get(session_id)

        if session is None:
            logger.debug("session doesn't exist locally")
            session = self.sessions.add_session(self)
            logger.debug("Thread %s - created session %s" % (get_ident(),
                                                      str(session)))
            if exists:
                session.incr_hits()
        else:
            logger.debug("Thread %s - reusing same session %s" % (get_ident(),
                                                           str(session)))
            session.incr_hits()

        return session
