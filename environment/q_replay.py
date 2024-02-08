#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tensorflow as tf
from tensorflow import keras
import numpy as np
from tensorflow.compat.v1.keras import backend as K
from keras.callbacks import TensorBoard

from config.config import sys_config, input_shape
from modules.actions import EnvActions

# q learning config
from virtual.envstate import EnvStates

# --

print("NUM GPUS AVAILABLE:", len(tf.config.list_physical_devices('GPU')))
tf.config.list_physical_devices('GPU')

from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
config = tf.compat.v1.ConfigProto( device_count = {'GPU': 1 , 'CPU': 56} )
sess = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(sess)

class Replay:
    def __init__(self, model_name, options={}):
        self.options  = options
        self.model_name = model_name

    def load_model(self):
        return keras.models.load_model( "./model_store/" + self.model_name, compile=False )

    def init(self):
        global input_shape

        # check if the model exists
        self.model = self.load_model()

        # initialize actions
        self.envActions = EnvActions()
        num_actions = len( self.envActions.get_actions() )
        print("actions=", self.envActions.get_actions())

        self.options['virtual']['rand_bg'] = 1 # bg randomization
        self.envState = EnvStates( self.options['virtual'] )

        # intial episode reset
        state = self.envState.reset()

        while True:
            state = tf.convert_to_tensor( state, dtype=np.float )
            state = tf.expand_dims( state, 0 )

            # predict the action probs and estimate future value
            action_probs = self.model( state )
            # get the best action
            action = tf.argmax(action_probs[0]).numpy()

            # apply the sampled action in the environment
            keystroke = self.envActions.get_action(action)
            print(keystroke)

            state, reward, done, _ = self.envState.step( keystroke )

    def close(self):
        pass

if __name__ == "__main__":
    model_name = 'model_target_QLearning_2022_01_26_00_45_20'
    #model_name = 'model_target_QLearning_2022_01_25_03_51_20'
    replay = Replay( model_name, sys_config )
    try:
        replay.init()
    except Exception as ex:
        print("Exception Occures:", ex)
    except KeyboardInterrupt:
        print("Keyboard Exception")
    finally:
        replay.close()
