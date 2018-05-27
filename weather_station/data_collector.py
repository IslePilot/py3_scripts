#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-25, ksb, created
"""

import sys
sys.path.append("..")

import threading
from queue import Queue
import time

# define a version for this file
VERSION = "1.0.2018-05-25a"

class DataCollector(threading.Thread):
  def __init__(self):
    
    # create our data lock
    data_lock = threading.Lock()
    
    # create our data queue
    data_queue = Queue()
    
    # make sure this dies when the caller dies
    self.daemon = True
    
    
    return

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
