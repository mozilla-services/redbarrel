# this is your app code
import time

# XXX see how to solve relative imports
from util import (generate_cid, json_response, CID_CHARS,
                  PrefixedCache, get_memcache_class)
from webob.exc import HTTPServiceUnavailable, HTTPBadRequest

__all__ = ['new_channel', 'get_channel',
           'put_channel', 'report']


# no cef for now
def log_cef(*args, **kw):
    pass

# memory cache for now
_mcache = get_memcache_class(True)([])
_cache = PrefixedCache(_mcache, 'keyex')

config = {}
_TTL = 600
_EMPTY = '{}'
cid_len = 4


def _delete_channel(channel_id):
    del _cache[channel_id]


def report(globs, request):
    """Reports a log and delete the channel if relevant"""
    client_id = request.headers.get('X-KeyExchange-Id')
    log = []
    header_log = request.headers.get('X-KeyExchange-Log')
    if header_log is not None:
        log.append(header_log)

    body_log = request.body[:2000].strip()
    if body_log != '':
        log.append(body_log)

    # logging only if the log is not empty
    if len(log) > 0:
        log = '\n'.join(log)
        log_cef('Report', 5, request.environ, config, msg=log)

    # removing the channel if present
    channel_id = request.headers.get('X-KeyExchange-Cid')
    if client_id is not None and channel_id is not None:
        content = _cache.get(channel_id)
        if content is not None:
            # the channel is still existing
            ttl, ids, data, etag = content

            # if the client_ids is in ids, we allow the deletion
            # of the channel
            if not _delete_channel(channel_id):
                log_cef('Could not delete the channel', 5,
                        request.environ, config,
                        msg=_cid2str(channel_id))

    return ''


def _get_new_cid(client_id):
    tries = 0
    ttl = time.time() + _TTL
    content = ttl, [client_id], _EMPTY, None

    while tries < 100:
        new_cid = generate_cid(cid_len)
        if _cache.get(new_cid) is not None:
            tries += 1
            continue   # already taken

        success = _cache.add(new_cid, content)  #, time=ttl)
        if success:
            break
        tries += 1

    if not success:
        raise HTTPServiceUnavailable()

    return new_cid


def _valid_client_id(client_id):
    return client_id is not None and len(client_id) == 256

def new_channel(globs, request):
    client_id = request.headers.get('X-KeyExchange-Id')

    #if not _valid_client_id(client_id):
    #    # The X-KeyExchange-Id is valid
    #    try:
    #        log = 'Invalid X-KeyExchange-Id'
    #        log_cef(log, 5, request.environ, config,
    #                msg=_cid2str(client_id))
    #    finally:
    #        raise HTTPBadRequest()
    cid = _get_new_cid(client_id)
    headers = [('X-KeyExchange-Channel', cid),
                ('Content-Type', 'application/json')]
    return json_response(cid, headerlist=headers)

def get_channel(globs, request):
    raise NotImplementedError()


def put_channel(globs, request):
    """Append data into channel."""
    raise NotImplementedError()