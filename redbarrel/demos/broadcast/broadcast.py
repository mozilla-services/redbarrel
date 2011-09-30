import json
import socket
import fcntl
import struct
import thread
import gevent


_BUFFER = []
_D = json.dumps
_INTERFACE = 'eth0'


def add(msg):
    _BUFFER.append(msg)
    if len(_BUFFER) > 30:
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


def broadcast(globs, request):
    """Broadcasts everytime someone new joins"""
    socketio = request.socketio
    if socketio.session is None:
        print "Thread %s - NO SESSION" % thread.get_ident()
        return

    sid = socketio.session.session_id

    def broadcast(message):
        socketio.broadcast(_D({'message': message}))

    if socketio.on_connect():
        broadcast(sid + ' connected')

    while socketio.connected():
        socketio.broadcast(_D({'message': 'I am alive %s' % sid}))
        gevent.sleep(2.)

    broadcast(sid + ' disconnected')
