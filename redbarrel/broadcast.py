# -*- coding: utf-8 -*-
"""
    Worker message broadcasting

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import gevent
from gevent_zeromq import zmq
from gevent import spawn


class Broadcaster(object):
    def __init__(self, publish_port=5000, pull_port=5001):
        context = zmq.Context()
        self.publish = context.socket(zmq.PUB)
        self.pull = context.socket(zmq.PULL)
        self.publish_port = publish_port
        self.pull_port = pull_port

    def start(self):
        self.pull.bind("tcp://127.0.0.1:%d" % self.pull_port)
        self.publish.bind("tcp://127.0.0.1:%d" % self.publish_port)
        spawn(self._pull)
        gevent.sleep(0.1)

    def stop(self, timeout=None):
        self.publish.close()
        self.pull.close()

    def _pull(self):
        while not self.pull.closed:
            msg = self.pull.recv()
            filter, msg = msg.split(' ', 1)
            self.broadcast(filter, msg)

    def broadcast(self, filter, msg):
        self.publish.send("%s %s" % (filter, msg))


class Client(object):

    def __init__(self, receive_port, push_port, callback):
        context = zmq.Context()
        self.receive_port = receive_port
        self.push_port = push_port
        self.callback = callback
        self.subscribe = context.socket(zmq.SUB)
        self.subscribe.setsockopt(zmq.SUBSCRIBE, "")
        self.push = context.socket(zmq.PUSH)

    def start(self):
        self.subscribe.connect("tcp://127.0.0.1:%d" % self.receive_port)
        self.push.connect("tcp://127.0.0.1:%d" % self.push_port)
        spawn(self._subscribe)
        gevent.sleep(0.1)

    def stop(self, timeout=None):
        self.subscribe.close()
        self.push.close()

    def _subscribe(self):
        while not self.subscribe.closed:
            msg = self.subscribe.recv()
            self.callback(msg)

    def broadcast(self, filter, msg):
        self.push.send("%s %s" % (filter, msg))
