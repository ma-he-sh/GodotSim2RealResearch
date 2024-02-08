import cv2
from modules.camera import Camera
from modules.logging import Logs
from modules.exceptions import Error

class CamModule(Camera):
    def __init__(self, config={}):
        super().__init__('virtual', config )

    def init(self):
        pass

    def get_frame(self):
        pass

    def save_frame(self, fname, frame ):
        cv2.imwrite(fname, frame)

    def close(self):
        pass

