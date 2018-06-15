#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

Jun 14, 2018, ksb, created
"""

import sys
sys.path.append("..")

import struct
import socket

from multiprocessing import Process, Array

# define a version for this file
VERSION = "1.0.2018-06-14a"

def bytestring_to_list(bs):
  return struct.Struct('{:d}B'.format(len(bs))).unpack(bs)

def list_to_bytestring(l):
  return struct.Struct('{:d}B'.format(len(l))).pack(*l)


class MulticastReceiver(Process):
  def __init__(self, rx_array, MCAST_GRP, MCAST_PORT):
    # save the inputs
    self.rx_array = rx_array
    
    # configure the socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                                      # to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # run the base constructor
    super().__init__()
    
    return
  
  def run(self):
    while True:
      # wait here for a message
      bs = self.sock.recv(1024)
      
      # now convert our bytestring to a list
      l = bytestring_to_list(bs)
      
      # now share the data
      with self.rx_array.get_lock():
        for i in range(len(l)):
          self.rx_array[i] = l[i]
    
    return
  
  


if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # build our defaults
  import datetime
  import pytz
  import time
  
  # build an initial message
  timestr = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f").encode()
  sequence = 0
  fmt = '{:d}s L'.format(len(timestr))
  bs = struct.Struct(fmt).pack(timestr, sequence)
  l = bytestring_to_list(bs)
  rx_array = Array('B', l)
  
  # start our receiver
  mcast_grp = '239.100.100.0'
  mcast_port = 5252
  receiver = MulticastReceiver(rx_array, mcast_grp, mcast_port)
  receiver.daemon = True
  receiver.start()
  
  while True:
    # get the latest data
    with rx_array.get_lock():
      data = rx_array[:]
    
    # convert the data to a bytestring we can unpack
    bs = list_to_bytestring(data)
    timestring, sequence = struct.Struct(fmt).unpack(bs)
    print(timestring.decode(), sequence)
    
    # wait a bit
    time.sleep(1.0)
  
