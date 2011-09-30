# -*- coding: utf-8 -*-
"""
    Contains custom pistil arbiters

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from pistil.tcp.arbiter import TcpArbiter
from redbarrel.server.workers import RedBarrelWSGIWorker
from redbarrel.server.workers import RedBarrelSocketIOWorker


class RedBarrelArbiter(TcpArbiter):
    def on_init(self, conf):
        TcpArbiter.on_init(self, conf)
        return RedBarrelWSGIWorker, 30, "worker", conf, "rb"


class RedBarrelSocketIOArbiter(TcpArbiter):
    def on_init(self, conf):
        TcpArbiter.on_init(self, conf)
        return RedBarrelSocketIOWorker, 9999, "worker", conf, "socketio"


ARBITERS = {'http': RedBarrelArbiter,
            'socketio': RedBarrelSocketIOArbiter}
