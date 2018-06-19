#!/usr/bin/env python3

"""
Copyright 2018 (C) AeroSys Engineering, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Revision History:
  2015-07-24, ksb, created

NOTE:
  This requires the pigpio library created by Joan.

  Get this via git:
         git clone https://github.com/joan2937/pigpio

         Documentation at http://abyz.co.uk/rpi/pigpio

         Ensure pigpiod is running prior to starting this code
         add /usr/local/bin/pigpiod to /etc/rc.local to run automatically
"""

import sys
sys.path.append("..")

from threading import Thread
import signal

import pigpio
import time
import datetime

# define a version for this file
VERSION = "1.0.20150724a"

RAINWISE_TERMINATE_REQUEST = False

class Rainwise111():
  INCHES_PER_TIP = 0.01
  GPIO_PIN = 4

  def __init__(self):
    """Instance the Rainwise 111 rain gauge""" 

    # connect to the local pi
    self.pi = pigpio.pi()

    # add the call back for the interrupts
    self.callback = self.pi.callback(Rainwise111.GPIO_PIN, pigpio.FALLING_EDGE, self.rain_cb)

    # initialize the monitor
    self.processing_tip = False
    self.reset_tip = False
    self.interval_rain_in = 0.0

    # create a monitoring thread
    self.exit_thread = False
    self.thread = Thread(target = self.monitor_thread, args=())
    self.thread.start()

    return

  def rain_cb(self, gpio, level, tick):
    """Interrupt Service Routine Callback."""
    if self.processing_tip is False:
      self.processing_tip = True

  def monitor_thread(self):
    """This is run automatically every quarter second.  
    Capture any tips and add to total. We don't expect tips faster than once every few seconds"""
    global RAINWISE_TERMINATE_REQUEST
    while RAINWISE_TERMINATE_REQUEST is False:
      # should we reset the tip monitoring
      if self.reset_tip:
        self.processing_tip = False
        self.reset_tip = False

      # if a tip has occured the flag will be true
      if self.processing_tip:
        # count the tip
        self.interval_rain_in = self.interval_rain_in + self.INCHES_PER_TIP

        # reenable tip monitoring on the next pass through
        self.reset_tip = True

      # wait a bit
      time.sleep(0.25)

  def signal_handler(self):
    """Set the flag to exit the thread"""
    self.exit_thread = True

  def get_readings(self):
    """Get the current rainfall, add to total, and reset counter"""

    # get the amount of rain that fell since the last reading and reset
    interval_rain = self.interval_rain_in
    self.interval_rain_in = 0.0

    return interval_rain


if __name__ == '__main__':
  # setup a signal handler for this code
  def rainwise_signal_handler(signal, frame):
    global RAINWISE_TERMINATE_REQUEST
    print("Rainwise111.py: You pressed Ctrl-c.  Exiting.")
    RAINWISE_TERMINATE_REQUEST = True
    time.sleep(1.0)
    sys.exit(0)
    
  signal.signal(signal.SIGINT, rainwise_signal_handler)
  
  # instance our sensor object
  rain111 = Rainwise111()
  total_rain_in = 0.0

  # read the values every second
  while True:
    # get the readings
    interval_rain_in = rain111.get_readings()
    total_rain_in = total_rain_in + interval_rain_in

    # get a timestamp
    timenow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # show the user what we got
    print("{:s}: Interval Rain(in):{:.2f} Total Rain(in):{:.2f}".format(timenow, interval_rain_in, total_rain_in))

    # rest a bit
    time.sleep(1.0)

  return




