from curses import baudrate
import serial
import json
import time
from modules.exceptions import Error

class SerialFailedToConnect(Error):
    pass

class SerialConn:
    serialConn = False

    def __init__(self, config={}):
        self.port = config['SERIAL_PORT']  if 'SERIAL_PORT' in config else ''
        self.baudrate = config['SERIAL_BAUDRATE'] if 'SERIAL_BAUDRATE' in config else 115200
        self.timeout = config['SERIAL_TIMEOUT'] if 'SERIAL_TIMEOUT' in config else .1

    def init(self):
        try:
            self.conn = serial.Serial( port=self.port, baudrate=self.baudrate, timeout=self.timeout )
            self.serialConn = True
        except:
            raise SerialFailedToConnect('Serial connection failed')

    def dictionary_to_json(self, dict):
        jsobObj = json.dumps(dict)
        return jsobObj.encode('utf-8')

    def send(self, data={}):
        if not self.serialConn: return False

        payload = self.dictionary_to_json(data)
        self.conn.write(payload)
        time.sleep(0.05)
        resp = self.conn.readline()
        try:
            return resp.decode('utf-8')
        except:
            return None