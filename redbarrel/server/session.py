# -*- coding: utf-8 -*-
"""
    Socket IO session

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from socketio.server import Session

from redbarrel import logger
from redbarrel.storage import RedBarrelStorage, MEM, REDIS


def _(*args):
    return ':'.join(args)


class RedBarrelSessionManager(dict):

    def __init__(self, storage_type=MEM):
        self.st = RedBarrelStorage.get(storage_type)
        self.ql = self.st.get_queuelist()

    def get_session_ids(self):
        sessions = []
        for id_ in self.ql.get_queue_ids():
            if ':' in id_:
                prefix, session_id = id_.split(':')
            else:
                session_id = id_
            if session_id not in sessions:
                sessions.append(session_id)
        return sessions

    def session_exists(self, session_id):
        return self.ql.queue_exists('client' + session_id)

    def add_session(self, server):
        session = RedBarrelSession(server, self.ql, self.st.counter)
        self.ql.add_queue(session.session_id)
        self[session.session_id] = session
        return session


class RedBarrelSession(Session):

    def __init__(self, server, queue_list, counter_cls):
        self.server = server
        Session.__init__(self)
        self.clientq = queue_list.add_queue(self._key('client'))
        self.serverq = queue_list.add_queue(self._key('server'))
        self._heartbeat = counter_cls(self._key('heart'))
        self._hits = counter_cls(self._key('hits'))

    def _key(self, *args):
        return _(*args + (self.session_id,))

    def incr_hits(self):
        logger.debug('hit %s incremented' % self._hits.name)
        self._hits.incr()

    def heartbeat(self):
        logger.debug('heartbeat %s incremented' % self._heartbeat.name)
        return self._heartbeat.incr()

    def valid_heartbeat(self, counter):
        self.clear_disconnect_timeout()
        return self._heartbeat.get() == counter

    def is_new(self):
        return self._hits.get() == 0

    def kill(self):
        self.serverq.delete()
        self.clientq.delete()
        self._heartbeat.delete()
        self._hits.delete()

    def put_server_msg(self, msg):
        self.clear_disconnect_timeout()
        self.serverq.put_nowait(msg)

    def put_client_msg(self, msg):
        self.clear_disconnect_timeout()
        self.clientq.put_nowait(msg)

    def get_client_msg(self, **kwargs):
        return self.clientq.get(**kwargs)

    def get_server_msg(self, **kwargs):
        return self.serverq.get(**kwargs)
