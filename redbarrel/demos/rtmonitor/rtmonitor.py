import json
import time
import threading
import signal
import sys
import gevent
import socket
import fcntl
import struct


_KB = 1024
_INTERFACE = 'eth0'


class SysInfo(threading.Thread):

    def __init__(self, target, interval=2):
        threading.Thread.__init__(self)
        self.target = target
        self.running = False
        self.interval = interval

    def _meminfo(self):
        with open('/proc/meminfo') as f:
            lines = f.readlines()

        def _get_kb(line):
            return int(line.split()[1]) / _KB

        mem = dict()
        mem['total'] = _get_kb(lines[0])
        mem['free'] = _get_kb(lines[1])
        mem['buffers'] = _get_kb(lines[2])
        mem['cached'] = _get_kb(lines[3])
        return mem

    def _get_times(self):
        with open('/proc/stat') as f:
            return [int(val) for val in f.readline().split()[2:6]]

    def _cpu(self):
        current = self._get_times()
        time.sleep(self.interval)
        delta = [(y - x) for y, x in zip(current, self._get_times())]
        usage = delta[-1] * 100. / sum(delta)
        return '%.2f' % usage

    def join(self):
        self.running = False
        threading.Thread.join(self)

    def run(self):
        self.running = True
        while self.running:
            self.target['memory'] = self._meminfo()
            self.target['cpu'] = self._cpu()
            time.sleep(0.1)


# will run in the background and update _VALUES
_VALUES = {}
_info = SysInfo(_VALUES, interval=.2)
_info.start()
_funcs = []


def _sigterm(sig, fr):
    try:
        _info.join()
    except RuntimeError:
        pass
    print 'end'
    sys.exit(1)


def _runonce(func):
    if func not in _funcs:
        _funcs.append(func)

    def __once(*args, **kw):
        if not func in _funcs:
            return
        try:
            func(*args, **kw)
        finally:
            _funcs.remove(func)
    return __once


def add_sig(sig, func):
    signal.signal(sig, _runonce(_sigterm))


#add_sig(signal.SIGTERM, _sigterm)
#add_sig(signal.SIGINT, _sigterm)

def get_sys_info():
    return _VALUES


def main(globals, request):
    """Sends back the current info"""
    socketio = request.environ['socketio']
    while socketio.connected():
        socketio.send(json.dumps(get_sys_info()))
        gevent.sleep(.5)


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
