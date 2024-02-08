import math

import cv2
import numpy as np
from abc import ABC, abstractmethod
from modules.logging import Logs
from config.config import *
from shapely.geometry import Polygon, Point

class Camera(ABC):
    radius_limit  = 120
    radius_center = 50
    radius_outer = 100
    color_red     = (0, 0, 255)
    color_blue    = (255, 0, 0)
    color_green   = (0, 255, 0)

    def __init__(self, log_name, config={}):
        self.config = config
        self.log_name = log_name
        self.logs = Logs(self.log_name + ".log")

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def save_frame(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def get_input_shape(self, frame ):
        return np.shape(frame)

    def set_downsample(self,  frame, width, height ):
        ds_dims = ( width, height )
        return cv2.resize( frame, ds_dims, interpolation=cv2.INTER_AREA )

    def get_resized(self, frame):
        w = self.config['cap_height']
        h = self.config['cap_height']
        x = ( self.config['cap_width'] / 2 ) - w / 2
        y = ( self.config['cap_height'] / 2 ) - h / 2
        # print(w, h, x, y)
        return frame[int(y):int(y+h), int(x):int(x+w)]
    
    def get_gray_scaled(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def get_overlay_aligner(self, frame):
        center_x = int( np.shape(frame)[1] / 2 )
        center_y = int( np.shape(frame)[0] / 2 )

        center_pos = ( center_x, center_y )

        cv2.circle( frame, center_pos, self.radius_center, self.color_red, 2 )
        cv2.circle( frame, center_pos, self.radius_outer, self.color_blue, 2 )
        cv2.circle( frame, center_pos, self.radius_limit, self.color_green, 2 )

        return frame, center_pos

    def _get_cartesian_cood(self, center, obj_pos ):
        cen_x, cen_y = center
        obj_x, obj_y = obj_pos

        distance = math.sqrt( ( cen_x - obj_x )**2 + ( cen_y - obj_y )**2 )
        y_diff = ( cen_y - obj_y )
        x_diff = ( cen_x - obj_x )

        if y_diff == 0 and x_diff == 0:
            return (0, 0)

        tan_theta= y_diff / x_diff
        angle    = math.degrees( math.atan( tan_theta ) )

        opposite = math.sin( angle ) * distance
        adjacent = math.cos( angle ) * distance

        cart_ball_pos = ( adjacent, opposite ) # define based on center (0, 0)
        return cart_ball_pos

    def get_ball_pos(self, frame):
        """
        determine the ball position
        return X,Y pos
        """
        pos = (0, 0) # left, bottom corner
        cart_pos = (0,0) # center
    
        image = frame
        if image is None:
            return image, pos

        imageDims = np.shape(frame)
        width = imageDims[0]
        height= imageDims[1]

        # real center of the image
        center_pos = ( int(width/2), int(height/2) ) # mapped to (0,0)

        gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.blur(gray, (3, 3))
        # cv2.imwrite("blur.png", gray_blurred)
        detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 1, maxRadius = 40)
        if detected_circles is not None:
            detected_circles = np.uint16(np.around(detected_circles))
            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]

                pos = (a, b)
                cart_pos=self._get_cartesian_cood( center_pos, pos )

                # border outline
                cv2.circle( image, center=(a, b), radius=r, color=(0, 255, 0), thickness=-1)

                # center circle
                cv2.circle( image, center=(a, b), radius=1, color=(0, 0, 255), thickness=1)

        return image, pos, cart_pos

    def get_score(self, ball_pos, center_pos):
        ballPos = Point( ball_pos[0], ball_pos[1] )

        p = Point( center_pos[0], center_pos[1] )
        circle_center = p.buffer(self.radius_center)
        circle_outer  = p.buffer(self.radius_outer)

        within_center = ballPos.intersects(circle_center)
        within_outer  = ballPos.intersects(circle_outer)

        # print(within_outer, within_center)

        return within_center, within_outer