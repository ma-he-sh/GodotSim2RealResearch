#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, time, logging
from datetime import datetime
import os
import numpy as np

import tensorflow as tf
from tensorflow.compat.v1.keras import backend as K
from keras.callbacks import TensorBoard

from config.config import sys_config, input_shape
from virtual.envstate_pos import EnvStates
from modules.actions import EnvActions
from modules.model_actor_position_data import ActorModel as Model
from modules.datacsv import CSV

print("NUM GPUS AVAILABLE:", len(tf.config.list_physical_devices('GPU')))
tf.config.list_physical_devices('GPU')

from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
config = tf.compat.v1.ConfigProto( device_count = {'GPU': 1 , 'CPU': 56} )
sess = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(sess)

# -------

import cv2

# Configuration
input_shape=4
update_after_actions = 4

class ActorCritic:
    __model__ = 'ActorCritic_pos_data'

    gamma = 0.99
    max_steps_per_episode = 10000
    action_probs_history = []
    critic_value_history = []
    rewards_history = []
    running_reward = 0
    episode_count = 0
    curr_session = None

    pre_reward = 0

    modelData = None
    model = None
    optimizer = None
    loss_function = None

    def __init__(self, options={}):
        self.options = options

        now = datetime.now()
        self.model_datestamp = now.strftime("%Y_%m_%d_%H_%M_%S")

        self.TC = TensorBoard(log_dir='./tflogs/train_' + self.__model__ + "_" + self.model_datestamp + '/', histogram_freq=0, write_graph=True, write_images=True)

        self.avg_episode_reward = CSV("avg_episode_" + self.__model__ + "_" + self.model_datestamp)
        self.avg_critic_loss = CSV("avg_critic_loss_" + self.__model__ + "_" + self.model_datestamp)
        self.avg_actor_loss  = CSV("avg_actor_loss_" + self.__model__ + "_" + self.model_datestamp )
        self.avg_policy_loss = CSV("avg_policy_loss_" + self.__model__ + "_" + self.model_datestamp)
        self.avg_expected_loss = CSV("avg_expected_loss_" + self.__model__ + "_" + self.model_datestamp)
        self.episode_len_o_time = CSV("episode_len_o_time_" + self.__model__ + "_" + self.model_datestamp)

    def init(self):
        global input_shape, update_after_actions

        # action chains
        self.envActions = EnvActions()
        num_actions = len(self.envActions.get_actions())
        print("actions=", self.envActions.get_actions())

        self.options['virtual']['rand_bg'] = 0 # no bg randomization
        self.envState = EnvStates( self.options['virtual'] )

        # define model
        self.modelData = Model( num_actions, input_shape )
        self.model = self.modelData.get_model()
        self.optimizer = self.modelData.get_optimizer()
        self.huber_loss= self.modelData.get_loss_function()
        self.eps = np.finfo(np.float32).eps.item()

        # set model on tensorboard
        self.TC.set_model(self.model)
        self.pre_reward = 0

        # reset initial state
        state = self.envState.reset()

        csv_episode_reward = []
        csv_critic_loss = []
        csv_actor_loss  = []
        csv_policy_loss = []
        csv_expected_loss = []
        episode_len_o_time = []

        csv_episode_reward.append(['episode', 'reward'])
        csv_critic_loss.append(['episode', 'critic_loss'])
        csv_actor_loss.append( ['episode', 'actor_loss'] )
        csv_policy_loss.append(['episode', 'policy_loss'])
        csv_expected_loss.append(['episode', 'expected_loss'])
        episode_len_o_time.append(['episode', 'len_o_time'])

        while True:  # run until solve

            # initial episode reset
            state = self.envState.reset()
            episode_reward = 0

            with tf.GradientTape() as tape:
                for timestep in range(1, self.max_steps_per_episode):
                    # predict action prob and estimated future reward
                    state = tf.convert_to_tensor(state)
                    state = tf.expand_dims(state, 0)

                    # predict action prob and estimates and estimate future rewards
                    action_probs, critic_value = self.model(state)
                    self.critic_value_history.append(critic_value[0, 0])

                    # Sample action from action probability distribution
                    action = np.random.choice(num_actions, p=np.squeeze(action_probs))
                    # print("probs=", action_probs)
                    self.action_probs_history.append(tf.math.log(action_probs[0, action]))

                    # apply the sampled action in the environment
                    keystroke = self.envActions.get_action(action)
                    # print(keystroke)
                    state, reward, done, _ = self.envState.step(keystroke)
                    self.rewards_history.append(reward)
                    episode_reward += reward

                    # episode len over time
                    episode_len_o_time.append( [self.episode_count, timestep] )

                    if done:
                        print("done>>", timestep)
                        break

                print('-----')

                csv_episode_reward.append( [ self.episode_count, episode_reward ] )

                # Update running reward to check condition for solving
                self.running_reward = 0.05 * episode_reward + (1 - 0.05) * self.running_reward

                # Cal expected value from reward
                returns = []
                discounted_sum = 0
                for r in self.rewards_history[::-1]:
                    discounted_sum = r + self.gamma * discounted_sum
                    returns.insert(0, discounted_sum)

                # Normalize
                returns = np.array(returns)
                returns = (returns - np.mean(returns)) / (np.std(returns) + self.eps)
                returns = returns.tolist()

                # Calculating loss values to update our network
                history = zip(self.action_probs_history, self.critic_value_history, returns)
                actor_losses = []
                critic_losses = []
                for log_prob, value, ret in history:
                    diff = ret - value
                    actor_losses.append(-log_prob * diff)  # actor loss

                    # update critic for a between estimate of future rewards
                    critic_losses.append(
                        self.huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
                    )

                # Backpropagation
                loss_value = sum(actor_losses) + sum(critic_losses)
                grads = tape.gradient(loss_value, self.model.trainable_variables)
                self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

                self.TC.on_epoch_end( self.episode_count, {
                    'loss': loss_value,
                    'actor_loss': sum(actor_losses),
                    'critic_loss': sum(critic_losses),
                    'len_time': timestep,
                    'episode_reward': self.running_reward
                } )

                csv_expected_loss.append( [ self.episode_count, loss_value ] )
                csv_critic_loss.append( [self.episode_count, sum(critic_losses)] )
                csv_actor_loss.append( [ self.episode_count, sum(actor_losses) ] )

                # Clear the loss and reward history
                self.action_probs_history.clear()
                self.critic_value_history.clear()
                self.rewards_history.clear()

            # log details
            self.episode_count += 1
            if self.episode_count % 10 == 0:
                template = "running reward: {:.2f} at episode {}"
                print(template.format(self.running_reward, self.episode_count))

            csv_episode_reward.append( [self.episode_count, self.running_reward] )
            print("reward=", self.running_reward, " episode=", self.episode_count)

            if self.episode_count % update_after_actions == 0:
                self.avg_episode_reward.set_data(csv_episode_reward) #
                self.avg_expected_loss.set_data(csv_expected_loss) #
                self.avg_policy_loss.set_data( csv_policy_loss )
                self.avg_critic_loss.set_data( csv_critic_loss ) #
                self.avg_actor_loss.set_data( csv_actor_loss ) #
                self.episode_len_o_time.set_data(episode_len_o_time) #

                csv_episode_reward = []
                csv_expected_loss = []
                csv_critic_loss = []
                csv_actor_loss = []
                csv_policy_loss = []
                episode_len_o_time = []

            if self.running_reward > self.pre_reward:
                self.modelData.save('model_actor_' + self.__model__ + '_' + self.model_datestamp, self.model)
                print("MODEL SAVED")
                self.pre_reward = self.running_reward

            if self.running_reward > 10000:  # Condition to consider the task solved
                print("Solved at episode {}!".format(self.episode_count))
                break

    def close(self):
        if self.modelData != None:
            self.modelData.save('model_actor_' + self.__model__ + '_' + self.model_datestamp, self.model)
            print("MODEL SAVED")
        self.TC.on_train_end('_')

if __name__ == "__main__":
    actorCritic = ActorCritic( sys_config )
    try:
        actorCritic.init()
    except Exception as ex:
        print("Exception Occures:", ex )
    except KeyboardInterrupt:
        print("Keyboard Exception")
    finally:
        actorCritic.close()