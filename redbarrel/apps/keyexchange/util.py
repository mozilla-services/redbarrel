""" Various helpers.
"""
import json
import string
import os
import random

from webob import Response


CID_CHARS = '23456789abcdefghijkmnpqrstuvwxyz'


def randchar(chars=string.digits + string.letters):
    try:
        pos = int(float(ord(os.urandom(1))) * 256. / 255.)
        return chars[pos % len(chars)]
    except NotImplementedError:
        return random.choice(chars)


def json_response(data, dump=True, **kw):
    """Returns Response containing a json string"""
    if dump:
        data = json.dumps(data)
    return Response(data, content_type='application/json', **kw)


def generate_cid(size=4):
    """Returns a random channel id."""
    return ''.join([randchar(CID_CHARS) for i in range(size)])


class MemoryClient(dict):
    """Fallback if a memcache client is not installed.
    """
    def __init__(self, servers):
        pass

    def set(self, key, value, time=0):
        self[key] = value
        return True

    cas = set

    def add(self, key, value, time=0):
        if key in self:
            return False
        self[key] = value
        return True

    def replace(self, key, value, time=0):
        if key not in self:
            return False
        self[key] = value
        return True

    def delete(self, key):
        if not key in self:
            return True  # that's how memcache libs do...
        del self[key]
        return True

    def incr(self, key):
        val = self[key]
        self[key] = str(int(val) + 1)


class PrefixedCache(object):
    def __init__(self, cache, prefix=''):
        self.cache = cache
        self.prefix = ''

    def incr(self, key):
        return self.cache.incr(self.prefix + key)

    def get(self, key):
        return self.cache.get(self.prefix + key)

    def set(self, key, value, **kw):
        return self.cache.set(self.prefix + key, value, **kw)

    def delete(self, key):
        return self.cache.delete(self.prefix + key)

    def add(self, key, value, **kw):
        return self.cache.add(self.prefix + key, value, **kw)


def get_memcache_class(memory=False):
    """Returns the memcache class."""
    if memory:
        return MemoryClient
    import memcache
    return memcache.Client
