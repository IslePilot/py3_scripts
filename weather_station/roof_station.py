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

import os
import math
import time
import datetime
import pytz
import signal
import threading

# look into these to make this better
#from collections import deque
from collections import namedtuple

import ada1733 as ada1733
import pyranometer as pyranometer
import vane as vane

import numpy as np

# define a version for this file
VERSION = "1.0.20150802a"

def signal_handler(signal, frame):
  print("You pressed Control-c.  Exiting.")
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# create a named tuple to return data cleanly
RoofData = namedtuple('RoofData', 'm_dir, v_spd, s_spd, ss_std, gust, ti, solar')
class Averager(object):
  def __init__(self, persist_seconds):
    """This is an averager object.  It will maintain a history
    of defined parameters and return averages when asked.  It will
    also persist the history as configured.

    persist_seconds: the number of seconds to persist the data"""

    # save the amount of time to persist
    self.persist_seconds = persist_seconds

    # start a list of history
    self.timestamps = []
    self.history = []

    return

  def add_values(self, timestamp, ws_4hz, wd_4hz, solar_insolation, gust_3second=-999.0):
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
    self.timestamps.append(timestamp)
    self.history.append([ws_4hz, wd_4hz, solar_insolation, gust_3second, u, v])
    	
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
   
    # KSB return...may need to mask bad values (-999)

    # now compute the stats
    mean = np.mean(a=self.history, axis=0)
    std = np.std(a=self.history, axis=0)
    maxs = np.argmax(a=self.history, axis=0)  # these are indices, not values

    # pull out the interesting values
    scalar_speed = mean[0]
    insolation = mean[2]
    u = mean[4]
    v = mean[5]
    ws_std = std[0]
    peak_gust = self.history[maxs[3]][3]

    # compute vector quantities
    vector_speed = math.sqrt(u**2.0 + v**2.0)
    # atan2 returns -180 to 180 so we will end up with 0 to 360
    mean_direction = math.degrees(math.atan2(u, v))+180.0

    # turbulence intensity is the standard deviation of the horizontal wind speed
    # divided by the mean wind speed.  The min speed the anemometer can measure
    # is 0.3 m/s, which is 0.671 mph.  Don't compute TI if the average is less than
    # that.
    if scalar_speed >= 0.671:
      ti = ws_std / scalar_speed
    else:
      ti = -999.0

    return RoofData._make([mean_direction, vector_speed, scalar_speed, ws_std, peak_gust, ti, insolation])

  def _clean_history(self, timenow):
    """This function removes stale data (that which is older than we
    need to persist) from the history

    timenow: current time"""

    # compute the start time for our history
    starttime = timenow - datetime.timedelta(seconds=self.persist_seconds) 

    # find the indices to delete
    count = 0
    for ts in self.timestamps:
      if ts <= starttime:
        count += 1
      else:
        # the timestamp is now greater, so we are done
        break

    # now delete our range
    if count > 0:
      del self.timestamps[0:count]
      del self.history[0:count]
    return


class roof_station(object):
  def __init__(self, data_path):
    """The roof weather station class.  This collects data
    from the anemometer, wind vane, and  pyranometer and
    writes the data to the archive.

    data_path: path to data archive"""
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
    #self.process_600sec = Averager(600)

    # initialize the daily statistics
    self.last_date = timenow.date()
    self.daily_windrun = 0.0
    self.max_gust = 0.0
    self.peak_solar = 0.0
    self.pulse_count = 0

    self.data_acq = threading.Semaphore(1)

    # open a file
    self.csv = None
    self.data_path = data_path
    self.new_file(timenow)

    return

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

    # do these items every time we pass (4 Hz tasks)
    # anemometer
    ws_mph, windrun = self.anemometer.get_readings()
    # pyranometer
    volts, solar = self.pyranometer.get_readings()
    # wind vane
    volts, ws_dir = self.vane.get_readings()

    self.pulse_count += 1
    
    # 3 second data
    self.process_003sec.add_values(timenow, ws_mph, ws_dir, solar)

    # WMO peak gust comes from the maximum 3 second average wind in
    # the averaging interval.  Compute that here to add to the other
    # processing
    data_003 = self.process_003sec.process_data(timenow)

    # now save the data for the other intervals
    self.process_120sec.add_values(timenow, ws_mph, ws_dir, solar, data_003.s_spd)
    #self.process_600sec.add_values(timenow, ws_mph, ws_dir, solar, data_003.s_spd)
    
    # maintain our daily stats
    self.daily_windrun += windrun
    if data_003.s_spd > self.max_gust:
      self.max_gust = data_003.s_spd
    if data_003.solar > self.peak_solar:
      self.peak_solar = data_003.solar

    # perform these tasks every second
    if timenow >= self.next_001:
      # reset our target
      self.next_001 = timenow + datetime.timedelta(0, 0, 0, 875)

      # if our date changed, open a new file
      if timenow.date() != self.last_date or self.need_new_files == True:
        # close the current file and reopen a new one
        self.new_file(timenow)
      
        # save this date for next time
        self.last_date = timenow.date()

      # compute our wind statistics
      data_120 = self.process_120sec.process_data(timenow)
      #data_600 = self.process_600sec.process_data(timenow)

      # print our data to the screen
      timestamp = timenow.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
      
      # sample output
      #     "2015-01-04 14:03:00:    Dir   Vspd   Sspd  SpStd    Gust      Ti Insolation
      #     "                        deg    mph    mph    mph     mph      -- W/m^2
      #     "         XXX Second: XXX.xx YYY.yy ZZZ.zz AAA.aa -BBB.ba CCC.ccc DDDD.d
      #os.system('cls' if os.name == 'nt' else 'clear')
      print("{:s}:    Dir   Vspd   Sspd  SpStd    Gust      Ti Insolation".format(timestamp))
      print("                        deg    mph    mph    mph     mph      -- W/m^2")
      print("           3 Second: {:06.2f} {:6.2f} {:6.2f} {:6.2f} {:7.2f} {:7.3f} {:6.1f}".format(data_003.m_dir,
                                                                                                   data_003.v_spd,
                                                                                                   data_003.s_spd,
                                                                                                   data_003.ss_std,
                                                                                                   data_003.gust,
                                                                                                   data_003.ti,
                                                                                                   data_003.solar))

      print("           2 Minute: {:06.2f} {:6.2f} {:6.2f} {:6.2f} {:7.2f} {:7.3f} {:6.1f}".format(data_120.m_dir,
                                                                                                   data_120.v_spd,
                                                                                                   data_120.s_spd,
                                                                                                   data_120.ss_std,
                                                                                                   data_120.gust,
                                                                                                   data_120.ti,
                                                                                                   data_120.solar))

      #print("          10 Minute: {:06.2f} {:6.2f} {:6.2f} {:6.2f} {:7.2f} {:7.3f} {:6.1f}".format(data_600.m_dir,
      #                                                                                             data_600.v_spd,
      #                                                                                             data_600.s_spd,
      #                                                                                             data_600.ss_std,
      #                                                                                             data_600.gust,
      #                                                                                             data_600.ti,
      #                                                                                             data_600.solar))

      print("           Daily: Wind Run:{:.1f} Peak Gust:{:.1f} MaxSolar:{:.1f}".format(self.daily_windrun, 
                                                                                        self.max_gust,
                                                                                        self.peak_solar))
      print("     Pulse Count:{:d}".format(self.pulse_count))
      self.pulse_count = 0

      # get the CPU temp
      t_cpu_c = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
      t_cpu_f = t_cpu_c * 9.0/5.0 + 32.0
      print("CPU Temp:{:.2f}".format(t_cpu_f))

      # add the wind file
      try:
        with open("%s/currentwind.csv"%self.data_path, "w") as windfile:
          windfile.write("%6.2f,%.2f,%.2f\n"%(data_003.m_dir, data_003.v_spd, data_003.gust))
          self.need_new_file  = False

        # add the data to the CSV file
        self.csv.write("{:s},".format(timestamp))
        self.csv.write("{:06.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.3f},{:.1f},".format(data_003.m_dir,
                                                                                  data_003.v_spd,
                                                                                  data_003.s_spd,
                                                                                  data_003.ss_std,
                                                                                  data_003.gust,
                                                                                  data_003.ti,
                                                                                  data_003.solar))
        self.csv.write("{:06.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.3f},{:.1f}\n".format(data_120.m_dir,
                                                                                  data_120.v_spd,
                                                                                  data_120.s_spd,
                                                                                  data_120.ss_std,
                                                                                  data_120.gust,
                                                                                  data_120.ti,
                                                                                  data_120.solar))
        #self.csv.write("{:06.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.3f},{:.1f}\n".format(data_600.m_dir,
        #                                                                            data_600.v_spd,
        #                                                                            data_600.s_spd,
        #                                                                            data_600.ss_std,
        #                                                                            data_600.gust,
        #                                                                            data_600.ti,
        #                                                                            data_600.solar))
      except:
          print("unable to write to windfile....will retry next time")
          self.need_new_files = True



    self.data_acq.release()

    return

  def new_file(self, timenow):
    """Opens a new data archive CSV file and adds a header.  
    Also closes old file if it exists.

    timenow: datetime current time"""
    # close the current file
    if self.csv:
      self.csv.close()

    # build the filename of the new file
    filename = self.data_path + timenow.strftime("/%Y%m%d_%H%M%S_roof.csv")

    # open the new file
    # only buffer 1 line
    bufsize = 1
    try: 
      self.csv = open(filename, "w", bufsize)

      # add the header
      self.csv.write("Timestamps indicate end of averaging period\n")
      self.csv.write("Software Version {:s}\n".format(VERSION))
  
      self.csv.write("Yesterday's Stats (only filled in when running past midnight)\n")
      self.csv.write("Total Windrun (miles),Maximum Gust (mph),Peak Solar Insolation (W/m^2)\n")
      self.csv.write("{:.1f},{:.1f},{:.1f}\n".format(self.daily_windrun, self.max_gust, self.peak_solar))
  
      self.csv.write("Time (UTC),")
  
      self.csv.write("Wind Direction [3 sec] (True),")
      self.csv.write("Vector Wind Speed [3 sec] (mph),")
      self.csv.write("Scalar Wind Speed [3 sec] (mph),")
      self.csv.write("Wind Speed Standard Deviation [3 sec] (mph),")
      self.csv.write("Gust [3 sec] (mph),")
      self.csv.write("TI [3 sec],")
      self.csv.write("Solar Insolation [3 sec] (W/m^2),")
  
      self.csv.write("Wind Direction [120 sec] (True),")
      self.csv.write("Vector Wind Speed [120 sec] (mph),")
      self.csv.write("Scalar Wind Speed [120 sec] (mph),")
      self.csv.write("Wind Speed Standard Deviation [120 sec] (mph),")
      self.csv.write("Gust [120 sec] (mph),")
      self.csv.write("TI [120 sec],")
      self.csv.write("Solar Insolation [120 sec] (W/m^2)\n")
   
      # if using this code, change the \n above to a ,
      #self.csv.write("Wind Direction [600 sec] (True),")
      #self.csv.write("Vector Wind Speed [600 sec] (mph),")
      #self.csv.write("Scalar Wind Speed [600 sec] (mph),")
      #self.csv.write("Wind Speed Standard Deviation [600 sec] (mph),")
      #self.csv.write("Gust [600 sec] (mph),")
      #self.csv.write("TI [600 sec],")
      #self.csv.write("Solar Insolation [600 sec] (W/m^2)\n")
      self.need_new_files = False
    except:
      print("Unable to open new file.  Will retry")
      self.need_new_files = True
  
    # reset the daily statistics
    self.daily_windrun = 0.0
    self.max_gust = 0.0
    self.peak_solar = 0.0

    return


def main():
  print("Copyright (C) 2015 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")

  print("Press Control-c to exit.")

  print("Waiting for clock to stabilize.")
  time.sleep(15)

  # instance our station
  roof = roof_station('/mnt/keith-pc/wx_data/roof_station')

  # run until we are done
  roof.run()

# only run main if this is called directly
if __name__ == '__main__':
  main()

