#!/usr/bin/env python3
from ctypes import resize
import numpy as np
from physical.camera import CamModule
from config.config import sys_config

if __name__ == "__main__":
    camera = CamModule(sys_config['camera'])
    try:
        camera.init()
        while True:
            ret, image = camera.get_frame()
            #print(np.shape(image))
            #camera.save_frame('test1.png', image)
            resized = camera.get_resized(image)
            #camera.save_frame('final1.png', resized)
            down_samp = camera.set_downsample( resized, sys_config['camera']['cr_height'], sys_config['camera']['cr_height'] )
            #camera.save_frame('down1.png', down_samp)
            print(np.shape(down_samp))
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        print(ex)
    finally:
        camera.close()