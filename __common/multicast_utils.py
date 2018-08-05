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

class MulticastServerProcess(Process):
    def __init__(self, tx_array, MCAST_GRP, MCAST_PORT):
        # save our input
        self.tx_array = tx_array

        # configure our multicast server
        self.address = (MCAST_GRP, MCAST_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # run the base class init
        super(MulticastServerProcess, self).__init__()

        return

    def run(self):
        while True:
            # get our latest data from the array
            with self.tx_array.get_lock():
                data = self.tx_array[:]

            # convert our data from a list to a bytestring
            bs = list_to_bytestring(data)

            # now send the data
            try:
                self.sock.sendto(bs, self.address)
            except:
                print("MulticastServer: Error transmitting data")

            time.sleep(1.0)

class MulticastReceiverProcess(Process):
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
  
  # get our test imports
  import datetime
  import pytz
  import time
  
  # build an initial message
  now = datetime.datetime.now(pytz.UTC)
  timestr = now.strftime("%Y-%m-%d %H:%M:%S.%f").encode()
  sender = now.strftime("Sender %H%M%S").encode()
  sequence = 1
  
  # build an inital message
  fmt = '{:d}s {:d}s L'.format(len(sender), len(timestr))
  datastring = struct.Struct(fmt).pack(sender, timestr, sequence)
  datalist = bytestring_to_list(datastring)
  data_array = Array('B', datalist)
  
  # configure our muilticast group
  mcast_grp = '239.100.100.0'
  mcast_port = 5252
  
  # what do we want to test?
  test_server = False
  
  if test_server == True:
    # SERVER TEST CODE ####################################################
    # launch our multicast server
    server = MulticastServerProcess(data_array, mcast_grp, mcast_port)
    server.daemon = True
    server.start()

    # now build new messages forever
    while True:
        timestr = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
        sequence += 1

        print(sender, timestr, sequence)

        datastring = struct.Struct(fmt).pack(sender, timestr, sequence)
        data_list = bytestring_to_list(datastring)

        # share the data
        with data_array.get_lock():
            for i in range(len(data_list)):
                data_array[i] = data_list[i]

        # wait a bit to update
        time.sleep(1.0)

  
  else:
    # RECEIVER TEST CODE ##################################################
    # build a dictionary of received data
    rx_dict = {}
    rx_dict[sender] = (sequence, timestr)
  
    # start our receiver
    receiver = MulticastReceiverProcess(data_array, mcast_grp, mcast_port)
    receiver.daemon = True
    receiver.start()
    
    while True:
      # get the latest data
      with data_array.get_lock():
        data = data_array[:]
      
      # convert the data to a bytestring we can unpack
      bs = list_to_bytestring(data)
      sender, timestring, sequence = struct.Struct(fmt).unpack(bs)
      if sender in rx_dict.keys():
        if rx_dict[sender][0] != sequence:
          # new data
          if sequence > rx_dict[sender][0] + 1:
            print("Missed message from", sender.decode())
          rx_dict[sender] = (sequence, timestring)
          print(sender.decode(), timestring.decode(), sequence)
      else:
        # new sender
        rx_dict[sender] = (sequence, timestring)
        print(sender.decode(), timestring.decode(), sequence)
          
      
      # wait a bit
      time.sleep(.2)
      
      
  
