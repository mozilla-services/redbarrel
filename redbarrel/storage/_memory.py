# -*- coding: utf-8 -*-
"""
    Memory queue

    :copyright: Copyright 2011 by the RedBarrel team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from gevent.queue import Queue
from redbarrel.storage import RedBarrelStorage



class NamedList(list):
    def __init__(self, name, data=None):
        if data is None:
            data = []
        list.__init__(self, data)
        self.name = name


class MemoryQueueList(dict):

    def get_queue_ids(self, server='localhost'):
        return self.keys()

    def queue_exists(self, queue_id, server='localhost'):
        return queue_id in self

    def add_queue(self, qid, server='localhost'):
        return MemoryQueue(self, qid, server)

    def remove(self, qid):
        del self[qid]

class MemoryQueue(Queue):
    def __init__(self, queue_list, session_id, server='localhost'):
        Queue.__init__(self)
        self.id_name = session_id
        self.ql = queue_list
        self.ql[session_id] = self

    def delete(self):
        self.put_nowait(None)
        if self.id_name not in self.ql:
            return
        self.ql.remove(self.id_name)


class MemoryCounter(object):
    def __init__(self, name, server='localhost'):
        self.name = name
        self.value = 0

    def incr(self):
        self.value += 1
        return self.value

    def get(self):
        return self.value

    def delete(self):
        pass


class MemoryStorage(RedBarrelStorage):
    counter = MemoryCounter
    queue = MemoryQueue
    queuelist = MemoryQueueList
    list = NamedList

