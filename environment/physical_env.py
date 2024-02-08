#!/usr/bin/env python3

from time import sleep
from config import *
from physical.gimbal import Gimbal
from config.config import sys_config
import sys, getopt

gimbal=None
def arg_handler(argv):
    model_name=None
    log_file=None

    global gimbal

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("handle.py -i <model> -o <logname>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("handle.py -i <model> -o <logname>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            model_name=arg
        elif opt in ("-o", "--ofile"):
            log_file=arg

    if model_name and log_file:
        print(f"mode={model_name} log_file={log_file}" % [model_name, log_file])
        gimbal=Gimbal(model_name, sys_config)
    
    raise ValueError("handle.py -i <model> -o <logname>")

if __name__=='__main__':
    try:
        arg_handler(sys.argv[1::])
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        print(ex)
    finally:
        if gimbal is not None:
            gimbal.close()