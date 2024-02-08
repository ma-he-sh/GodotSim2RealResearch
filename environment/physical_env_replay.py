#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt
import logging

from physical.stewart import Stewart
from config.config import sys_config

def main( argv ):
    model  = ''
    logfile= ''

    try:
        opts, args = getopt.getopt( argv, "hm:l", ["model=", "log="])
    except getopt.GetoptError:
        print( 'physical_env_replay.py -m <model> -l <log>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'physical_env_replay.py -m <model> -l <log>' )
            sys.exit()
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-l", "--log" ):
            logfile = arg

    return model, logfile

if __name__ == '__main__':
    model, logfile = main( sys.argv[1:])

    if not model or not logfile:
        sys.exit()

    stewart = Stewart( model, sys_config )

    try:
        stewart.initialize()
        stewart.loop()
    except Exception as ex:
        print( ex )
    except KeyboardInterrupt:
        print( 'terminate' )
    finally:
        stewart.kill()
