import cv2
from modules.camera import Camera
from modules.logging import Logs
from modules.exceptions import Error

class SrcNotFound(Error):
    pass

class CamModule(Camera):
    src = None
    video = None

    def __init__(self, config={}):
        super().__init__('physical', config)

    def init(self):
        self.logs.set('initializing')
        if self.config['source'] is None:
            raise ValueError('Camera Source Not Defined')

        self.src = self.config['source']

        if not CamModule.src_exists_bool(self.src):
            raise ValueError('Camera source Invalid')

        self.cap_width = self.config['cap_width'] if 'cap_width' in self.config else 640
        self.cap_height = self.config['cap_height'] if 'cap_height' in self.config else 480
        self.cap_fps = self.config['cap_fps'] if 'cap_fps' in self.config else 25

        self.video = cv2.VideoCapture(self.src) # "./tracking_test.mov"
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self.cap_width)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cap_height)
        self.video.set(cv2.CAP_PROP_FPS, self.cap_fps)

    def get_frame(self):
        ret, image = self.video.read()
        return ret, image

    def save_frame(self, fname, frame ):
        cv2.imwrite(fname, frame )

    def close(self):
        if self.video:
            self.video.release()

    @staticmethod
    def src_exists_bool(src):
        srcExists = True
        try:
            CamModule.src_exists(src)
        except:
            srcExists = False
        finally:
            return srcExists

    @staticmethod
    def src_exists(src):
        try:
            cam = cv2.VideoCapture(src)
        except:
            raise SrcNotFound