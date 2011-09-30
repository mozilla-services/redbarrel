# -*- coding: utf-8 -*-
"""
    Redis queue

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import redis
from json import dumps, loads

from redbarrel import logger
from redbarrel.storage import RedBarrelStorage


class RedisQueueList(dict):
    def get_queue_ids(server='localhost'):
        r = redis.Redis(server)
        return r.smembers('redbarrelqueues')


    def queue_exists(queue_id, server='localhost'):
        r = redis.Redis(server)
        logger.debug("checking if %s exists in redis" % queue_id)
        return r.sismember('redbarrelqueues', queue_id)

    def add_queue(self, qid, server='localhost'):
        return RedisQueue(self, qid, server)



class RedisQueue(object):
    def __init__(self, session_id, server='localhost'):
        self.redis = redis.Redis(server)
        self.id_name = session_id
        logger.debug("register %s in the list of queues" % session_id)
        self.redis.sadd('redbarrelqueues', session_id)

    def put_nowait(self, element):
        if element is None:
            # XXXX now ?
            self.delete()
        id_name = self.id_name
        self.redis.lpush(id_name, element)

    def get(self, block=True, timeout=None):
        # blocking pop
        id_name = self.id_name
        if block:
            rpop = self.redis.brpop
        else:
            rpop = self.redis.rpop

        popped_element = rpop(id_name, timeout=timeout)
        return popped_element[1]

    def qsize(self):
        return self.redis.llen(self.id_name)

    def delete(self):
        logger.debug('removing %s from redis' % self.id_name)
        self.redis.srem('redbarrelqueues', self.id_name)
        self.redis.delete(self.id_name)


class RedisCounter(object):
    def __init__(self, name, server='localhost'):
        self.redis = redis.Redis(server)
        self.name = name

    def incr(self):
        return self.redis.incr(self.name)

    def get(self):
        value = self.redis.get(self.name)
        if value is None:
            return 0
        return int(value)

    def delete(self):
        return self.redis.delete(self.name)


class RedisList(object):

    def __init__(self, name, server='localhost'):
        self.redis = redis.Redis(server)
        self.name = name
        self._iter = 0

    def __iter__(self):
        return self

    def __len__(self):
        return self.redis.llen(self.name)

    def next(self):
        if self._iter >= len(self):
            self._iter = 0
            raise StopIteration()
        try:
            return loads(self.redis.lindex(self.name, self._iter))
        finally:
            self._iter += 1

    def append(self, item):
        self.redis.rpush(self.name, dumps(item))

    def extend(self, other):
        for item in other:
            self.append(dumps(item))

    def insert(self, index, item):
        raise NotImplementedError()

    def remove(self, item):
        self.redis.lrem(self.name, item)

    def pop(self, position=None):
        if position is not None:
            raise NotImplementedError()
        return loads(self.redis.rpop(self.name))

    def __delitem__(self, index):
        if index not in (0, -1, len(self) - 1):
            raise NotImplementedError()

        if index == 0:
            self.redis.lpop(self.name)
        else:
            self.redis.rpop(self.name)

    def index(self, item):
        raise NotImplementedError()

    def count(self, item):
        raise NotImplementedError()


class RedisStorage(RedBarrelStorage):
    counter = RedisCounter
    queue = RedisQueue
    queuelist = RedisQueueList
    list = RedisList

