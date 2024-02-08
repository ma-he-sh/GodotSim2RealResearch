#!/usr/bin/env python
from websocket import create_connection
import json
import base64
import numpy as np
import cv2
from time import sleep
import subprocess
import os

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

class Parser:
    def __init__(self, data=None):
        self.data = data
        if data is not None:
            self.data = json.loads(data.decode("utf-8"))

    def get_data(self):
        return self.data

    def get_image(self, raw_data):
        base64data = base64.b64decode(raw_data)
        nparr = np.fromstring(base64data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image

if __name__ == "__main__":

    exec_path = "./exports/version_1/linux/Envsrc.x86_64"
    exec_env  = "./exports/version_1/linux/Envsrc.pck"

    process = None
    socketConn = None

    try:
        # connect shell
        with open("./tmp/stdout.txt", "wb") as out, open("./tmp/stderr.text", "wb") as err:
            process = subprocess.Popen([ exec_path, "--path", os.path.abspath(exec_env), "--port", "9200" ], stdout=out, stderr=err)
            sleep(2)

        socketConn = NetworkSocket()
        result = socketConn.send({"cmd":"reset", "action":"reset", "keycode": ""})
        socketConn.get()

        while True:
            sleep(1)

            p=process.poll()
            print(p)

            if socketConn is None:
                socketConn = NetworkSocket()

            socketConn.send({"cmd": "state", "action":"left", "keycode": "Right"})
            result = socketConn.get()
            #print(result)

            if result is not None:
                parser = Parser(result)
                resp = parser.get_data()

                if resp['error'] <= 0:
                    print("Error")
                    continue

                if resp['result']['img'] is not None:
                    imgdata = parser.get_image(resp['result']['img'])
                    #print(imgdata)
                    cv2.imwrite("/tmp/data1.png", imgdata)
                    print(np.shape(imgdata))

            #socketConn.send({"cmd": "reset", "action": "left", "keycode": "Right"})
    except KeyboardInterrupt:
        pass
    finally:
        if socketConn:
            socketConn.close()
        if process:
            process.kill()