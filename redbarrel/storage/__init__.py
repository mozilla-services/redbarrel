# -*- coding: utf-8 -*-
"""
    Storage APIs

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import abc
from redbarrel.pluginreg import PluginRegistry

REDIS = 'redbarrel.storage._redis.RedisStorage'
MEM = 'redbarrel.storage._memory.MemoryStorage'


class RedBarrelStorage(PluginRegistry):

    counter = None
    queue = None
    queuelist = None
    list = None

    def get_counter(self, *args, **kwargs):
        return self.counter(*args, **kwargs)

    def get_queue(self, *args, **kwargs):
        return self.queue(*args, **kwargs)

    def get_queuelist(self, *args, **kwargs):
        return self.queuelist(*args, **kwargs)

    def get_list(self, *args, **kwargs):
        return self.list(*args, **kwargs)


class RedBarrelList(PluginRegistry):
    pass


class RedBarrelQueueList(PluginRegistry):
    @abc.abstractmethod
    def get_queue_ids(self, server='localhost'):
        pass

    @abc.abstractmethod
    def queue_exists(self, queue_id, server='localhost'):
        pass

    # + list methods


class RedBarrelQueue(PluginRegistry):
    @abc.abstractmethod
    def delete(self):
        pass

    # + queue methods


class RedBarrelCounter(PluginRegistry):
    @abc.abstractmethod
    def incr(self):
        pass

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass
