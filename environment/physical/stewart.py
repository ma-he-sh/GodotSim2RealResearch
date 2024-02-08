from ctypes import resize
import numpy as np

from modules.logging import Logs
from physical.camera import CamModule
from physical.gimbalpos import GimbalPos
from physical.model import Model
#from physical.serialconn import SerialConn
from modules.actions import EnvActions
from physical.envstate_pos import EnvStatePhysical

import cv2

class Stewart:
    input_shape = 4
    log_name = 'StewartPlatform.log'
    ready = False
    resetted = False

    def __init__(self, model_name, config={}):
        self.model_name = model_name
        self.logs   = Logs(self.log_name)
        self.camera = CamModule(config['camera'])
        self.gimbalpos = GimbalPos(config['physical'])
        #self.serial = SerialConn( config['serial'] )
        self.envState = EnvStatePhysical()

        self.envActions = EnvActions()
        num_actions = len( self.envActions.get_actions() )
        self.model = Model(self.model_name, num_actions )

    def initialize(self):
        # initialize camera
        self.camera.init()

        # initialize serial
        #self.serial.init()

        # load model
        self.model.init()

        self.ready = True

    def loop(self):
        while self.ready:
            ret, image = self.camera.get_frame()
            resized = self.camera.get_resized( image )
            cv2.imwrite( 'resize.png', resized )

            image, pos, cart_pos = self.camera.get_ball_pos(resized)
            cv2.imwrite("overlay.png", image)
            print(pos)
            print(cart_pos)

            if not self.resetted:
                # get the initial camera image
                print('resetted')
                print( np.shape(resized) )
                self.envState.step(resized)
                continue
            else:
                print('run action')

    def kill(self):
        self.ready = False