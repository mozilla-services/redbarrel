# -*- coding: utf-8 -*-
"""
    Storage APIs

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from redbarrel.events._memory import MemoryPubSub, MemoryPushPull


_PUBSUB_BACKENDS = {'memory': MemoryPubSub}
_PUSHPULL_BACKENDS = {'memory': MemoryPushPull}


def get_pubsub(type_, *args, **kw):
    return _PUBSUB_BACKENDS[type_](*args, **kw)


def get_pushpull(type_, *args, **kw):
    return _PUBSUB_BACKENDS[type_](*args, **kw)
