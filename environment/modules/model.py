import os
from keras import backend as K

# define mode
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
# K.set_session(tf.compat.v1.Session(config=config))

class Model:
    def __init__(self, num_actions, shape=None):
        self.shape = shape
        self.num_actions = num_actions

    def model(self):
        # Network defined by the Deepmind paper
        inputs = layers.Input(shape=self.shape)

        # Convolutions on the frames on the screen
        layer1 = layers.Conv2D(32, 8, strides=4, activation="relu")(inputs)
        layer2 = layers.Conv2D(64, 4, strides=2, activation="relu")(layer1)
        layer3 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer2)

        layer4 = layers.Flatten()(layer3)

        layer5 = layers.Dense(512, activation="relu")(layer4)
        action = layers.Dense(self.num_actions, activation="linear")(layer5)

        return keras.Model(inputs=inputs, outputs=action)

    def get_model(self):
        return self.model()

    def get_optimizer(self):
        return tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

    def get_loss_function(self):
        return keras.losses.Huber()

    def summary(self):
        model = self.model()
        model.summary()

    def save(self, _name, _model):
        _model.save("./model_store/" + _name)