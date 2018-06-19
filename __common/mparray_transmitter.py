#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-26, ksb, created
"""

import sys
sys.path.append("..")

from multiprocessing import Process
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from multiprocessing import AuthenticationError

import time

# define a version for this file
VERSION = "1.0.2018-05-26a"

class MPArrayServer(Process):
  def __init__(self, hostname, port, password, mp_array):
    """Create a multiprocessing.Process object to serve multiprocessing.Array data.
    
    hostname: hostname of this machine
    port: socket to use for server connections
    password: "password" required to connect to this server
    mp_array: multiprocessing.Array shared data type to transmit"""
    # save our input
    self.hostname = hostname
    self.port = port
    self.password = password
    self.mp_array = mp_array
    
    # run the base class constructor
    super().__init__()
    return
  
  def run(self):
    """Main Receiver Loop.  Oveloaded multiprocessing.Process.run()"""
    # build our address tuple
    address = (self.hostname, self.port)
    
    # create a server socket
    with Listener(address, authkey = self.password) as listener:
      while True:
        # wait for a connection here
        #print("MPArrayServer: Waiting for connection...")
        try:
          with listener.accept() as conn:
            #print("MPArrayServer: Connection accepted from", listener.last_accepted)
            # send our data
            with self.mp_array.get_lock():
              conn.send(self.mp_array[:]) # Note: not data length aware-fully generic
              print("MPArrayServer: connection accepted from {}".format(listener.last_accepted))
            # this is all are sending, disconnect and go back to waiting for another connection
        except AuthenticationError:
          print("MPArrayServer: Unauthorized Access Attempted!")
    
    return
    
class MPArrayReceiver(Process):
  def __init__(self, hostname, port, password, read_delay, mp_array):
    """Create a multiprocessing.Process object to receive data into a multiprocessing.Array.
    
    hostname: hostname of this machine
    port: socket to use for server connections
    password: "password" required to connect to this server
    read_delay: time in seconds between connections to the server to retrieve data
    mp_array: multiprocessing.Array shared data type to transmit"""
    # save our input
    self.hostname = hostname
    self.port = port
    self.password = password
    self.read_delay = read_delay
    self.mp_array = mp_array
    
    # run the base class constructor
    super().__init__()
    return
  
  def run(self):
    """Main Receiver Loop.  Oveloaded multiprocessing.Process.run()"""
    # build our address tuple
    address = (self.hostname, self.port)
  
    while True:
      try:
        with Client(address, authkey=self.password) as conn:
          data = conn.recv()
          # save the data
          with self.mp_array.get_lock():
            for i in range(len(data)):
              self.mp_array[i]=data[i]
          
          time.sleep(self.read_delay)
      except AuthenticationError:
        print("MPArrayReceiver: Authentication Error!  Exiting.")
        return
      except:
        # wait a bit and try again
        print("MPArrayReceiver: No server to connect to...trying again soon")
        print(sys.exc_info()[0])
        time.sleep(5.0) # no rush to try again
    
    return

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
