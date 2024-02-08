from typing import overload
import numpy as np
import cv2

class EnvStatePhysical:
    observation = None
    reward = 0.0
    done = False
    info = {}

    def __init__(self, options={}):
        self.options = options

    def _get_observation(self, image=None ):
        raw_image = image.copy()

    def step(self, image):
        cv2.imwrite('img.png', image )

        ball_pos_x, ball_pos_y, in_center, in_outer = .0, .0, 0, 0

        observation = (ball_pos_x, ball_pos_y, int(in_center), int(in_outer))

        reward = 0.0
        done = False
        info = {}

        return np.array( observation, dtype=np.float32 ), reward, done, info

    def reset(self, image):
        ball_pos_x, ball_pos_y, in_center, in_outer = .0, .0, 0, 0
        observation = (ball_pos_x, ball_pos_y, int(in_center), int(in_outer))

        return np.array(observation, dtype=np.float32)

class EnvState:
    observation = None
    reward = 0.0
    done = False
    info = {}

    def __init__(self, options={}):
        self.options = options

    def seed(self, seed=None):
        pass

    def step(self, action):
        ball_pos_x, ball_pos_y, in_center, in_outer = .0, .0, 0, 0

        observation = (ball_pos_x, ball_pos_y, int(in_center), int(in_outer))
        info = {}

        done = bool(not in_center and not in_outer)

        if in_center:
            reward = 1.0
        elif in_outer:
            reward = 0.5
        else:
            reward = 0.0

        return np.array( observation, dtype=np.float32 ), reward, done, info

    def reset(self, image ):
        ball_pos_x, ball_pos_y, in_center, in_outer = .0, .0, 0, 0
        observation = (ball_pos_x, ball_pos_y, int(in_center), int(in_outer))

        return np.array(observation, dtype=np.float32)
    
    def render(self):
        pass

    def close(self):
        pass