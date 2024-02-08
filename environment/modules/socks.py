from websocket import create_connection
import json

class NetworkSocket:
    params = {}
    params['version'] = '__1.0.0__'

    def __init__(self):
        self.ws = create_connection( "ws://localhost:9000" )

    def send(self, message={}):
        self.ws.send(json.dumps(message))

    def get(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()