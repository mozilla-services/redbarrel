import json
import socket
import fcntl
import struct
import thread
import gevent

from redbarrel.storage import RedBarrelStorage, REDIS, MEM

try:
    import redis        # NOQA
    storage = REDIS
except ImportError:
    storage = MEM


# XXX see if we want this to be in the DSL
storage = RedBarrelStorage.get(storage)
_BUFFER = storage.get_list('chat')
_D = json.dumps
_INTERFACE = 'eth0'


def add(msg):
    _BUFFER.append(msg)
    if len(_BUFFER) > 10:
        del _BUFFER[0]


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15]))[20:24])
    except IOError:
        return '0.0.0.0'


def convert_template(globs, request, template):
    template = template.replace('%(SERVER)s', get_ip_address(_INTERFACE))
    return template


def chat(globs, request):
    """A Chat room using web sockets"""
    socketio = request.environ['socketio']
    if socketio.session is None:
        print "Thread %s - NO SESSION" % thread.get_ident()
        return
    sid = socketio.session.session_id

    def announce(message):
        socketio.broadcast(_D({'announcement': message}))

    if socketio.on_connect():
        announce(sid + ' connected')
        socketio.send(_D({'buffer': list(_BUFFER)}))

    while True:
        message = socketio.recv()
        if len(message) == 1:
            message = {'message': [sid, message[0]]}
            add(message)
            socketio.broadcast(_D(message))
        else:
            if not socketio.connected():
                announce(sid + ' disconnected')

        gevent.sleep(0.1)
