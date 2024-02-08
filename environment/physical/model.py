import os

from modules.exceptions import Error
import tensorflow as tf
from tensorflow import keras
import numpy as np
from tensorflow.compat.v1.keras import backend as K
from keras.callbacks import TensorBoard

class ModelNotFound(Error):
    pass

class Model:
    model_path = "./model_store/"
    model = None

    def __init__(self, model_name, num_actions ):
        self.model_name = model_name
        self.model_path += self.model_name
        self.num_actions = num_actions

    def get_full_path(self):
        return "./model_store/" + self.model_name

    def init(self):
        model_path = self.get_full_path()

        if not os.path.exists( model_path ):
            raise ModelNotFound('model_not_found')

        self.model = keras.models.load_model(model_path, compile=False)

    def get_model(self):
        if self.model is not None:
            return self.model
        return None