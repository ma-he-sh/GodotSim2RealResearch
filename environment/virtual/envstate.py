import json
from PIL import Image
import numpy as np
from io import BytesIO
import cv2
import base64
import subprocess
from skimage.util import random_noise
from time import sleep
from websocket import create_connection
from virtual.camera import CamModule

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

class NetworkSocket:
    def __init__(self, port ):
        self.socket = "ws://localhost:" + port
        self.ws = create_connection( self.socket )
        print(self.socket)

    def send(self, message={}):
        self.ws.send(json.dumps(message))

    def get(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()

class EnvStates:
    observation=None
    reward=0.0
    done=False
    info={}

    process=None
    socketConn=None

    def __init__(self, options={}):
        self.options=options

        # connect shell
        with open("./tmp/stdout.txt", "wb") as out, open("./tmp/stderr.text", "wb") as err:
            self.process = subprocess.Popen([self.options['exec_path'],
                                             "--path", self.options['exec_env'],
                                             "--port=" + str(self.options['env1_port']),
                                             "--color="+str(self.options['rand_bg'])],
                                            stdout=out,
                                            stderr=err)
        sleep(2)
        self.socketConn = NetworkSocket( str(self.options['env1_port']) )
        self.camera = CamModule( self.options )

    def add_noise(self, image ):
        image = random_noise( image, mode='s&p', amount=0.3 )
        image = np.array( 255*image, dtype='uint8' )
        return image

    def _get_observation(self, image=None):
        if self.options['add_noise'] == 1:
            # add random noise to image
            image = self.add_noise( image )
            # cv2.imwrite("noisy.png", image)

        image = self.camera.get_resized(image)
        raw_img = image.copy()

        track_img, ball_pos, cart_ball_pos = self.camera.get_ball_pos(image)
        aligned, center_pos = self.camera.get_overlay_aligner(image)
        observation = self.camera.set_downsample(raw_img, self.options['cr_height'], self.options['cr_height'])
        # self.camera.save_frame("aligned.png", aligned)
        within_center, within_outer = self.camera.get_score(ball_pos, center_pos)
        # print(within_center, within_outer)

        return ball_pos, cart_ball_pos, observation, track_img, within_center, within_outer

    def seed(self, seed=None):
            pass

    def step(self, action):

        self.socketConn.send({"cmd":"state", "keycode": action })
        result = self.socketConn.get()

        parser = Parser( result )
        data = parser.get_data()

        yaw = float(data['result']['yaw'])
        pitch = float(data['result']['pitch'])
        roll = float(data['result']['roll'])

        ball_pos_x = float(data['result']['ball_pos']['x'])
        ball_pos_y = float(data['result']['ball_pos']['y'])

        ball_vel_x = float(data['result']['ball_velocity']['x'])
        ball_vel_y = float(data['result']['ball_velocity']['y'])

        in_center = bool(data['result']['in_center'])
        in_outer = bool(data['result']['in_outer'])
        dist_to_center = float(data['result']['dist_to_center'])

        info = data['result']['prev_data']

        img = parser.get_image(data['result']['img'])
        _, _, observation, _, _, _ = self._get_observation(img)
        # print(ball_pos, within_center, within_outer)

        # if the ball is not within the ranges
        done = bool(not in_center and not in_outer)

        if in_center:
            reward = 1.0
        elif in_outer:
            reward = 0.5
        else:
            reward = 0.0

        ## TODO reward function and done status :: image resizing
        ## TODO get ball pos, and assign reward

        return observation, reward, done, info

    def reset(self):
        #print("reset--")
        self.socketConn.send({"cmd":"reset", "keycode": None})
        result = self.socketConn.get()

        parser = Parser( result )
        data = parser.get_data()

        # yaw = float(data['result']['yaw'])
        # pitch = float(data['result']['pitch'])
        # roll = float(data['result']['roll'])
        #
        # ball_pos_x = float(data['result']['ball_pos']['x'])
        # ball_pos_y = float(data['result']['ball_pos']['y'])
        #
        # ball_vel_x = float(data['result']['ball_velocity']['x'])
        # ball_vel_y = float(data['result']['ball_velocity']['y'])
        #
        # in_center = bool(data['result']['in_center'])
        # in_outer = bool(data['result']['in_outer'])
        # dist_to_center = float(data['result']['dist_to_center'])

        img = parser.get_image(data['result']['img'])
        _, _, observation, _, _, _ = self._get_observation(img)
        return observation

    def render(self):
        pass

    def close(self):
        self.process.kill()
        self.socketConn.close()