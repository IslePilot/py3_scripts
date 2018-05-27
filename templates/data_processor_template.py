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
import __common.mparray_transmitter as txrx

import datetime
import time

from multiprocessing import Process
from multiprocessing import Array


# define a version for this file
VERSION = "1.0.2018-05-25a"

class DataCollector(Process):
  BAD_TIME_ARRAY = list(datetime.datetime(2000,1,1).timetuple())[:7]
  
  def __init__(self, mp_array):
    """Instance a sample data collector.  This sample simply reads the local clock.
    
    mp_array: shared data multiprocessing.Array object"""
    # save our input
    self.mp_array = mp_array  # this is shared memory, so use locks when operating on it
    
    # run the base class constructor
    super().__init__()
    return
  
  def run(self):
    """Main Receiver Loop.  Oveloaded multiprocessing.Process.run()"""
    while True:
      # get the latest time and turn it into a list
      data = datetime.datetime.utcnow()
      print("    DataCollector: {:s}".format(data.strftime("%Y-%m-%d %H:%M:%S.%f")))
      datalist = list(data.timetuple())[:6]
      datalist.append(data.microsecond)
      
      # now share the data
      with self.mp_array.get_lock():
        for i in range(len(datalist)):
          self.mp_array[i]=datalist[i]

      time.sleep(0.1)

    return

class DataUser(Process):
  def __init__(self, mp_array):
    # save our input
    self.mp_array = mp_array  # this is shared memory, so use locks when operating on it
    
    # run the base class constructor
    super().__init__()
    return
  
  def run(self):
    while True:
      # show the user what we got
      with self.mp_array.get_lock():
        data = datetime.datetime(*self.mp_array[:])
      
      print(" DataUser running: {:s}".format(data.strftime("%Y-%m-%d %H:%M:%S.%f")))

      time.sleep(1.0)
    return
    
if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # regardless of mode, define a few basics
  # create our shared memory object
  timearray = Array('i', DataCollector.BAD_TIME_ARRAY)  # initialize with sample bad time
  hostname = 'keith-pc'
  port = 6969
  authkey = b'DataCollector Test'
  read_delay = 0.1  # delay between network reads
    
  # DATA GATHERER/SERVER MODE
  if False:
    # instance our collector object  (Data Gatherer)
    timecollector = DataCollector(timearray)
    timecollector.daemon = True     # run this process on its own until this process dies
    timecollector.start()
    
    # instance the data server object (Data Server)
    dataserver = txrx.MPArrayServer(hostname, port, authkey, timearray)
    dataserver.daemon = True  # run this process on its own until this process dies
    dataserver.start()
    
  # DATA RECEIVER/PROCESSOR MODE
  else:
    datareceiver = txrx.MPArrayReceiver(hostname, port, authkey, read_delay, timearray)
    datareceiver.daemon = True  # run this process on its own until this process dies
    datareceiver.start()
    
    # instance the data processor
    datauser = DataUser(timearray)
    datauser.daemon = True  # run this process on its own until this process dies
    datauser.start()
  
  # regardless of type, we want to monitor what is in our shared object
  while True:
    # show the user what we got
    with timearray.get_lock():
      arraytime = datetime.datetime(*timearray[:])
      
    print("Main Thread Array: {:s}".format(arraytime.strftime("%Y-%m-%d %H:%M:%S.%f")))
    
    # wait a bit
    time.sleep(1.0)
    
    
  
  
  
