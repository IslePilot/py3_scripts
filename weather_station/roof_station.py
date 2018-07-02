#!/usr/bin/python3

"""
Copyright (C) 2015 AeroSys Engineering, Inc.

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
  2015-02-01, ksb, added use of namedtuple
  2015-01-24, ksb, cleaned up comments 
  2015-01-24, ksb, removed 600 second averaging to increase speed
  2015-01-23, ksb, added wind vane
  2015-01-12, ksb, added pulse count
  2015-01-11, ksb, added csv capability
  2015-01-09, ksb, added pyranometer code
  2015-01-04, ksb, implemented 3, 120, and 600 second averaging
  2015-01-02, ksb, created
"""

import sys
sys.path.append("..")
import __common.mparray_transmitter as txrx
from multiprocessing import Array

import os
import math
import time
import datetime
import pytz
import signal
import threading
import configparser 

# look into these to make this better
#from collections import deque
from collections import namedtuple

import ada1733 as ada1733
import pyranometer as pyranometer
import vane as vane

import numpy as np

# define a version for this file
VERSION = "1.0.20180701a"

def signal_handler(signal, frame):
  print("You pressed Control-c.  Exiting.")
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# create a named tuple to return data cleanly
RoofData = namedtuple('RoofData', 'timestamp, direction, speed, gust, solar, cpu_t')

class Averager():
  def __init__(self, persist_seconds):
    """This is an averager object.  It will maintain a history
    of defined parameters and return averages when asked.  It will
    also persist the history as configured.

    persist_seconds: the number of seconds to persist the data"""

    # save the amount of time to persist
    self.persist_seconds = persist_seconds

    # initialize our history
    self.history = []

    return

  def add_values(self, timestamp, ws_4hz, wd_4hz, solar_insolation, cpu_t, gust_3second=-999.0):
    """Add new values to the history

    timestamp: datetime.datetime timestamp
    ws_4hz: wind speed measurement (in MPH) sampled at 4 Hz
    wd_4hz: wind direction measurement (degrees from True north) sampled at 4 Hz
    solar_insolation: measured solar insolation in W/m^2
    gust_3second: optional 3 second average of 4 Hz wind speeds--used for gust reporting"""

    # this is going to be called a lot, so do as little as possible
    # compute the vector components.  Remember direction is reported
    # as "from", so convert to "to"
    u = ws_4hz * math.sin(math.radians(wd_4hz+180.0))
    v = ws_4hz * math.cos(math.radians(wd_4hz+180.0))

    # save the data
    self.history.append((timestamp, (wd_4hz, ws_4hz, gust_3second, u, v, solar_insolation, cpu_t)))

    return

  def process_data(self, timenow):
    """Maintain the history and process the averages

    timenow: current time
    
    returns: namedtuple:
      m_dir: vector averaged direction (from u & v)
      v_spd: vector averaged speed (from u & v) in m/s
      s_spd: scalar averaged speed (from given speeds) in m/s
      ss_std: scalar speed standard deviation in m/s
      gust: maximum scalar wind speed in the averaging interval in m/s
      ti: turbulence intensity computed from scalar speeds
      solar: average solar insolation in W/m^2"""

    # first clean up the history
    self._clean_history(timenow) 
   
    # build our list of data
    data = [h[1] for h in self.history]

    # now compute the stats
    mean = np.mean(data, 0)
    maxs = np.max(data, 0)

    # pull out the interesting values
    # our order is 0:direction, 1:speed, 2:gust, 3:u, 4:v, 5:solar, 6:cpu_t
    scalar_speed = mean[1]
    insolation = mean[5]
    u = mean[3]
    v = mean[4]
    peak_gust = maxs[2]
    cpu_t = mean[6]

    # compute vector quantities
    vector_speed = math.sqrt(u**2.0 + v**2.0)
    # atan2 returns -180 to 180 so we will end up with 0 to 360
    mean_direction = (math.degrees(math.atan2(u, v))+180.0)%360.0

    return RoofData(self.history[-1][0].timestamp(), mean_direction, scalar_speed, peak_gust, insolation, cpu_t)

  def _clean_history(self, timenow):
    """This function removes stale data (that which is older than we
    need to persist) from the history

    timenow: current time"""
    # compute the start time for our history
    starttime = timenow - datetime.timedelta(seconds=self.persist_seconds) 

    self.history = [h for h in self.history if h[0] > starttime]

    return


class roof_station():
  def __init__(self, data_array):
    """The roof weather station class.  This collects data
    from the anemometer, wind vane, and  pyranometer and
    writes the data to the archive.

    data_path: path to data archive"""

    # save the shared memory
    self.data_array = data_array

    # get the current time so we know when we started
    timenow = datetime.datetime.now(pytz.UTC)

    # set our targets
    # our timing isn't exact, so set this limit a bit
    # sooner to get on the mark
    self.next_001 = timenow + datetime.timedelta(0, 0, 0, 875)

    # set a timer to go off every quarter second
    signal.setitimer(signal.ITIMER_REAL, 0.25, 0.25)
    signal.signal(signal.SIGALRM, self.timer_isr)

    # instance our hardware objects
    self.anemometer = ada1733.ADA1733()
    self.pyranometer = pyranometer.Pyranometer()
    self.vane = vane.Vane()

    # instance our processors
    self.process_003sec = Averager(3)
    self.process_120sec = Averager(120)

    # initialize the daily statistics
    self.pulse_count = 0
    self.reset_daily_stats()
    self.current_day = timenow.day

    self.data_acq = threading.Semaphore(1)

    return

  def reset_daily_stats(self):
    # initialize the daily statistics
    self.daily_windrun = 0.0
    self.max_gust = 0.0
    self.peak_solar = 0.0

  def run(self):
    """A do nothing routine to use so the thread won't exit"""
    while True:
      time.sleep(10)

  def timer_isr(self, signal, frame):
    """This is automatically run every 0.25 seconds by the signaller.  Perform
    high rate tasks in here and then call other routines for the low rate tasks.
    Called by the timer alarm."""

    if self.data_acq.acquire(False) == False:
      return

    # get our current time
    timenow = datetime.datetime.now(pytz.UTC)

    # get the CPU temp
    t_cpu_c = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
    t_cpu_f = t_cpu_c * 9.0/5.0 + 32.0

    # do these items every time we pass (4 Hz tasks)
    # anemometer
    ws_mph, windrun = self.anemometer.get_readings()
    # pyranometer
    volts, solar = self.pyranometer.get_readings()
    # wind vane
    volts, ws_dir = self.vane.get_readings()

    self.pulse_count += 1
    
    # 3 second data
    self.process_003sec.add_values(timenow, ws_mph, ws_dir, solar, t_cpu_f)

    # WMO peak gust comes from the maximum 3 second average wind in
    # the averaging interval.  Compute that here to add to the other
    # processing
    data_003 = self.process_003sec.process_data(timenow)

    # now save the data for the other intervals
    self.process_120sec.add_values(timenow, ws_mph, ws_dir, solar, t_cpu_f, data_003.speed)
    
    # if the day changed, reset stats
    if timenow.day != self.current_day:
        self.reset_daily_stats()
        self.current_day = timenow.day

    # maintain our daily stats
    self.daily_windrun += windrun
    if data_003.speed > self.max_gust:
      self.max_gust = data_003.speed
    if data_003.solar > self.peak_solar:
      self.peak_solar = data_003.solar

    # perform these tasks every second
    if timenow >= self.next_001:
      # reset our target
      self.next_001 = timenow + datetime.timedelta(0, 0, 0, 875)

      # compute our wind statistics
      data_120 = self.process_120sec.process_data(timenow)

      # print our data to the screen
      timestamp = timenow.strftime("%Y-%m-%d %H:%M:%S")
      
      # send our data to the shared memory
      with self.data_array.get_lock():
          self.data_array[0] = timenow.timestamp() # UNIX Timestamp
          self.data_array[1] = data_003.direction 
          self.data_array[2] = data_003.speed
          self.data_array[3] = data_120.gust
          self.data_array[4] = data_003.solar
          self.data_array[5] = data_003.cpu_t

      # sample output
      #     "2015-01-04 14:03:00:       Dir    Spd   Gust   Solar    CPU
      #     "                           deg    mph    mph   W/m^2   degF
      #     "                        123.56 123.56 123.56 1234.67 123.56
      print("{:s}:       Dir    Spd   Gust   Solar    CPU".format(timestamp))
      print("                           deg    mph    mph   W/m^2   degF")
      print("                        {:6.2f} {:6.2f} ---.-- {:7.2f} {:6.2f}".format(data_003.direction,
                                                                                     data_003.speed,
                                                                                     data_003.solar,
                                                                                     data_003.cpu_t))
      print("                        {:6.2f} {:6.2f} {:6.2f} {:7.2f} {:6.2f}".format(data_120.direction,
                                                                                     data_120.speed,
                                                                                     data_120.gust,
                                                                                     data_120.solar,
                                                                                     data_120.cpu_t))

      print("           Daily: Wind Run:{:.1f} Peak Gust:{:.1f} MaxSolar:{:.1f}".format(self.daily_windrun, 
                                                                                        self.max_gust,
                                                                                        self.peak_solar))
      print("     Pulse Count:{:d}".format(self.pulse_count))
      self.pulse_count = 0

    self.data_acq.release()

    return

if __name__ == '__main__':
  print("Copyright (C) 2018 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")
  print("Version:", VERSION)

  print("Press Control-c to exit.")

  print("Waiting for clock to stabilize.")
  time.sleep(15)

  # parse the config file
  config = configparser.ConfigParser()

  config.read('/home/pi/WeatherData/config.ini')

  hostname = config['ROOF_STATION']['host']
  port = int(config['ROOF_STATION']['port'])
  authkey = config['ROOF_STATION']['authkey'].encode()

  print(hostname, port, authkey)

  # creata a shared array of floats
  data_array = Array('d', 6)

  dataserver = txrx.MPArrayServer(hostname, port, authkey, data_array)
  dataserver.daemon = True
  dataserver.start()

  # instance our station
  roof = roof_station(data_array)

  # run until we are done
  roof.run()

