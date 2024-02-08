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
from virtual.envstate import EnvStates
from modules.actions import EnvActions
from modules.model import Model
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
seed = 42
gamma= 0.99
epsilon=1.0
epsilon_min=0.1
epsilon_max=1.0
epsilon_interval = (
    epsilon_max - epsilon_min
)
batch_size = 64 # size of batch for replay // 32
max_steps_per_episode=10000

# Number of frames to take random actions and observe outputs
epsilon_random_frames = 1000000.0 # 5000

# Number of frames for exploration
epsilon_greedy_frames = 1000000.0

# Max memory replay length
max_memory_length = 100000

# Train model after howmany actions
update_after_actions = 4

# When to update the target network
update_target_network = 10000

# -------

class QLearning:
    __model__ = 'QLearning_noisy'

    action_history = []
    state_history = []
    state_next_history = []
    rewards_history = []
    done_history = []
    episode_reward_history = []

    num_actions = 0
    running_reward = 0
    episode_count = 0
    frame_count = 0
    sess_fcount = 0

    modelData = None
    model = None
    model_target = None
    optimizer = None
    loss_function = None

    def __init__(self, options={} ):
        self.options = options

        now = datetime.now()
        self.model_datestamp = now.strftime("%Y_%m_%d_%H_%M_%S")

        self.TC = TensorBoard(log_dir='./tflogs/train_' + self.__model__ + "_" + self.model_datestamp + '/', histogram_freq=0, write_graph=True, write_images=True)

        self.avg_episode_reward = CSV("avg_episode_" + self.__model__ + "_" + self.model_datestamp )
        self.avg_critic_loss    = CSV("avg_critic_loss_" + self.__model__ + "_" + self.model_datestamp  )
        self.avg_policy_loss    = CSV("avg_policy_loss_" + self.__model__ + "_" + self.model_datestamp  )
        self.avg_expected_loss  = CSV("avg_expected_loss_" + self.__model__ + "_" + self.model_datestamp )
        self.episode_len_o_time = CSV("episode_len_o_time_" + self.__model__ + "_" + self.model_datestamp )
        self.avg_max_q_value_   = CSV("avg_max_q_value_" + self.__model__ + "_" + self.model_datestamp )

    def init(self):
        global input_shape, batch_size, gamma, \
            update_after_actions, max_steps_per_episode, \
            max_memory_length, epsilon, epsilon_random_frames, \
            epsilon_interval, epsilon_greedy_frames, epsilon_min, epsilon_max, update_target_network, \
            env_options

        # action chains
        self.envActions = EnvActions()
        num_actions = len(self.envActions.get_actions())
        print("actions=", self.envActions.get_actions())

        self.options['virtual']['rand_bg'] = 1 # randomized bg
        self.options['virtual']['add_noise'] = 1 # add noise
        self.envState = EnvStates( self.options['virtual'] )

        self.modelData = Model( num_actions, input_shape )
        self.model = self.modelData.get_model()
        self.model_target = self.modelData.get_model()
        self.optimizer = self.modelData.get_optimizer()
        self.loss_function = self.modelData.get_loss_function()

        # set tensorboard
        self.TC.set_model(self.model)

        last_high_score = 0

        # set intial state
        state = None
        episode_reward = 0
        is_new_session = False

        # reset environment
        state = self.envState.reset()
        done = False

        csv_episode_reward  = []
        csv_critic_loss     = []
        csv_policy_loss     = []
        csv_expected_loss   = []
        episode_len_o_time  = []
        csv_max_q_value     = []

        csv_episode_reward.append( ['episode', 'reward'] )
        csv_critic_loss.append( ['episode', 'critic_loss'] )
        csv_policy_loss.append( ['episode', 'policy_loss'] )
        csv_expected_loss.append( ['episode', 'expected_loss'] )
        episode_len_o_time.append( ['episode', 'len_o_time'] )
        csv_max_q_value.append( ['episode', 'max_q_val'] )

        # start capturing window
        while True:

            # initial episode reset
            state = self.envState.reset()
            state = np.array(state)
            done = False  # reset done status

            # previous episode scoe
            print("prev_episode_score=", episode_reward)

            episode_reward = 0
            for timestep in range(1, max_steps_per_episode):
                # total frame count
                self.frame_count += 1

                if self.frame_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
                    # generate a random action
                    action = np.random.choice(num_actions)
                else:
                    # predict using q-values :: replay
                    state_tensor = tf.convert_to_tensor(state, dtype=np.float)
                    state_tensor = tf.expand_dims(state_tensor, 0)
                    action_probs = self.model(state_tensor, training=False)
                    print("replay >> ", action_probs)
                    # get the best action
                    action = tf.argmax(action_probs[0]).numpy()

                # decay probability
                epsilon -= epsilon_interval / epsilon_greedy_frames
                epsilon = max(epsilon, epsilon_min)

                # apply the sampled action in the environment and get current state
                keystroke = self.envActions.get_action(action)
                state_next, reward, done, _ = self.envState.step( keystroke )
                state_next = np.array(state_next)

                # cv2.imwrite("data.png", state_next )

                # total reward
                episode_reward += reward

                self.action_history.append(action)
                self.state_history.append(state)
                self.state_next_history.append(state_next)
                self.done_history.append(done)
                self.rewards_history.append(reward)
                state = state_next  # set current state as next

                # episode len over time
                episode_len_o_time.append( [ self.episode_count, timestep ] )

                # update every forth frame and once batch is over 32
                if self.frame_count % update_after_actions == 0 and len(self.done_history) > batch_size:
                    # print('updating--->>')
                    # Get indices of samples for replay buffers
                    indices = np.random.choice(range(len(self.done_history)), size=batch_size)

                    # Using list comprehension to sample from replay buffer
                    state_sample = np.array([self.state_history[i] for i in indices], dtype=float)
                    state_next_sample = np.array([self.state_next_history[i] for i in indices], dtype=float)
                    rewards_sample = [self.rewards_history[i] for i in indices]
                    action_sample = [self.action_history[i] for i in indices]
                    done_sample = tf.convert_to_tensor(
                        [float(self.done_history[i]) for i in indices]
                    )

                    # Build the updated Q-values for the sampled future states
                    # Use the target model for stability
                    future_rewards = self.model_target.predict(state_next_sample)
                    # Q value = reward + discount factor * expected future reward
                    updated_q_values = rewards_sample + gamma * tf.reduce_max(
                        future_rewards, axis=1
                    )

                    # If final frame set the last value to -1
                    updated_q_values = updated_q_values * (1 - done_sample) - done_sample

                    # Create a mask so we only calculate loss on the updated Q-values
                    masks = tf.one_hot(action_sample, num_actions)

                    with tf.GradientTape() as tape:
                        # Train the model on the states and updated Q-values
                        q_values = self.model(state_sample)

                        # Apply the masks to the Q-values to get the Q-value for action taken
                        q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                        # Calculate loss between new Q-value and old Q-value
                        loss = self.loss_function(updated_q_values, q_action)
                        # print("loss=", loss)

                        logs = {'loss': loss, 'q_value': np.max(q_values), 'len_time': timestep, 'episode_reward': self.running_reward }
                        self.TC.on_epoch_end(self.episode_count, logs)

                        csv_expected_loss.append( [ self.episode_count, loss.numpy() ] )
                        csv_max_q_value.append( [ self.episode_count, np.max(q_values) ] )

                    # Backpropagation
                    grads = tape.gradient(loss, self.model.trainable_variables)
                    self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
                    if self.frame_count % update_target_network == 0:
                        # update target network with new weights
                        self.model_target.set_weights(self.model.get_weights())
                        template = "running reward: {:.2f}, frame count {}"
                        print(template.format(self.running_reward, self.frame_count))

                    self.sess_fcount += 1

                    if len(self.rewards_history) > max_memory_length:
                        del self.rewards_history[:1]
                        del self.state_history[:1]
                        del self.state_next_history[:1]
                        del self.action_history[:1]
                        del self.done_history[:1]

                    if done:
                        break

            # updating running reward check condition for solving
            self.episode_reward_history.append(episode_reward)
            if len(self.episode_reward_history) > 100:
                del self.episode_reward_history[:1]
            self.running_reward = np.mean(self.episode_reward_history)

            csv_episode_reward.append([self.episode_count, self.running_reward])
            print("reward=", self.running_reward, " episode=", self.episode_count)

            if self.frame_count % update_after_actions == 0:
                self.avg_episode_reward.set_data( csv_episode_reward )
                self.avg_expected_loss.set_data( csv_expected_loss )
                # self.avg_policy_loss.set_data( csv_policy_loss )
                # self.avg_critic_loss.set_data( csv_critic_loss )
                self.episode_len_o_time.set_data( episode_len_o_time )
                self.avg_max_q_value_.set_data( csv_max_q_value )

                csv_episode_reward = []
                csv_expected_loss = []
                csv_critic_loss = []
                csv_policy_loss = []
                episode_len_o_time = []
                csv_max_q_value = []

            self.episode_count += 1

            # exit conditions
            if self.running_reward > last_high_score:
                self.modelData.save('model_' + self.__model__ + '_' + self.model_datestamp, self.model)
                self.modelData.save('model_target_' + self.__model__ + '_' + self.model_datestamp, self.model_target)
                print(">> SAVE MODEL :: Solved at episode={}".format(self.episode_count))
                last_high_score = self.running_reward

            if last_high_score > 10000:
                break

    def close(self):
        if self.modelData != None:
            self.modelData.save('model_' + self.__model__ + '_' + self.model_datestamp, self.model)
            self.modelData.save('model_target_' + self.__model__ + '_' + self.model_datestamp, self.model_target)
        self.TC.on_train_end('_')
        pass

if __name__ == "__main__":
    qLearn = QLearning( sys_config )
    try:
        qLearn.init()
    except Exception as ex:
        print("Exception Occures:", ex )
    except KeyboardInterrupt:
        print("Keyboard Exception")
    finally:
        qLearn.close()
