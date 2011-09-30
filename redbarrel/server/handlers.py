from socketio.handler import SocketIOHandler


class RedBarrelSocketIOHandler(SocketIOHandler):
    def handle_one_response(self):
        self.environ['socketio'].server = self.server
        super(RedBarrelSocketIOHandler, self).handle_one_response()
