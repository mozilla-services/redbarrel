""" Demo for Redbarrel: an URL shortener
"""
from collections import defaultdict
import json
import os
import gevent
from random import randint
from urllib2 import HTTPError

from webob.exc import HTTPNotFound, HTTPSeeOther
from redbarrel.util import read_url

_SHORT = {}
_HITS = defaultdict(int)

_API_URL = 'http://localhost:8080/localise/%s'
_SERVER_IP = '127.0.0.1'


def shorten(globals, request):
    if 'url' in request.POST:
        # form
        url = request.POST['url']
        redirect = True
    else:
        # direct API call
        url = request.body
        # no redirect
        redirect = False

    next = len(_SHORT)
    if url not in _SHORT:
        _SHORT[next] = url

    shorten = 'http://%s/r/%d' % (request.host, next)

    if not redirect:
        return shorten
    else:
        location = '/shortened.html?url=%s&shorten=%s' \
                % (url, shorten)
        raise HTTPSeeOther(location=location)


def randip():
    'Return a random ip address'
    return "88." + ".".join(str(randint(1, 255)) for i in range(3))


def redirect(globals, request):
    """Redirects to the real URL"""
    path = request.path_info.split('/r/')
    if len(path) < 2 or int(path[-1]) not in _SHORT:
        raise HTTPNotFound()
    index = int(path[-1])
    location = _SHORT[index]
    _HITS[index] += 1

    ip = request.environ['REMOTE_ADDR']
    # We get rid of local address for test purposes
    while ip.split('.')[0] in ('10', '127', '172', '192'):
        ip = randip()

    # we should have used proxy
    try:
        json_infos = json.loads(read_url(_API_URL % ip))
    except HTTPError:
        json_infos = {}

    json_infos['url'] = _SHORT[index]
    request.environ['socketio'].server.broadcast(json.dumps(json_infos))

    raise HTTPSeeOther(location=location)


def stats(globals, request):
    """Returns the number of hits per redirect"""
    res = [(url, _HITS[index]) for index, url in _SHORT.items()]
    return json.dumps(dict(res))


def shortened_html(globals, request, url='', shorten=''):
    """HTML page with the shortened URL result"""
    tmpl = os.path.join(os.path.dirname(__file__), 'shortened.html')
    with open(tmpl) as f:
        tmpl = f.read()
    return tmpl % {'url': url, 'shorten': shorten}


def shorten_html(globals, request, url=''):
    """HTML page to create a shortened URL"""
    tmpl = os.path.join(os.path.dirname(__file__), 'shorten.html')
    with open(tmpl) as f:
        tmpl = f.read()
    return tmpl % url


def setup_socket(globals, request):
    """Set up the socket"""
    socketio = request.socketio

    while socketio.connected():

        gevent.sleep(0.5)


def get_ip_address():
    "Return the serveur IP to the template context"
    return _SERVER_IP


def convert_template(globs, request, template):
    template = template.replace('%(SERVER)s', get_ip_address())
    return template
