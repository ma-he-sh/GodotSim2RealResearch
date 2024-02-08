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

class ActorModel:
    num_hidden=128

    def __init__(self, num_actions, shape ):
        self.shape = shape
        self.num_actions = num_actions

    def model(self):
        inputs = layers.Input(shape=(self.shape,))
        common = layers.Dense(self.num_hidden, activation='relu')(inputs)
        action = layers.Dense(self.num_actions, activation='softmax')(common)
        critic = layers.Dense(1)(common)

        return keras.Model(inputs=inputs, outputs=[action, critic])

    def get_model(self):
        return self.model()

    def get_optimizer(self):
        return tf.keras.optimizers.Adam(learning_rate=0.01, clipnorm=1.0)

    def get_loss_function(self):
        return keras.losses.Huber()

    def summary(self):
        model = self.model()
        model.summary()

    def save(self, _name, _model):
        _model.save("./model_store/" + _name)