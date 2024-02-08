import logging
from config.config import *


class Logs:
    def __init__(self, filename):
        self.filename = filename
        self.filepath = LOGGING_PATH + "/" + self.filename + ".log"
        file_handler = logging.FileHandler(self.filepath)
        self.logger = logging.getLogger()
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

    def set(self, msg='', func=''):
        msg += func + ":" + msg
        self.logger.warning(msg)