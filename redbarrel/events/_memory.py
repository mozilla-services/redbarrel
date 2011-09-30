# -*- coding: utf-8 -*-
"""
    Storage APIs

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from collections import defaultdict
from gevent.queue import Queue


class MemoryPubSub(object):
    def __init__(self):
        self._events = defaultdict(list)

    def subscribe(self, event, func):
        if func not in self._events[event]:
            self._events[event].append(func)

    def notify(self, event, *args, **kw):
        for func in self._events[event]:
            func(*args, **kw)

    def unsubscribe(self, event, func):
        if func in self._events[event]:
            self._events[event].remove(func)


class MemoryPushPull(Queue):
    pass
