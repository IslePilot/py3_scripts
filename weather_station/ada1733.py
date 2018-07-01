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
  2015-01-02, ksb, created
"""

import sys
sys.path.append("..")

import time
import datetime
import signal
import pytz

#from __hardware.Adafruit_ADS1x15 import ADS1x15
from Adafruit_ADS1x15 import ADS1x15

# define a version for this file
VERSION = "1.0.20180701a"

def signal_handler(signal, frame):
  """This exits cleanly after receiving a control-c"""
  print("You pressed Control-c.  Exiting.")
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class ADA1733(object):
  # address selections
  ADDR_GND = 0x48
  ADDR_VDD = 0x49
  ADDR_SDA = 0x4a
  ADDR_SCL = 0x4b

  #ADS1015 = 0x00	# 12-bit ADC
  #ADS1115 = 0x01	# 16-bit ADC

  def __init__(self):
    """Initialize the ADA1733 (anemometer) object."""
    #self.adc = ADS1x15(address=ADA1733.ADDR_GND, ic=ADA1733.ADS1115)
    self.adc = ADS1x15.ADS1115(address=0x48)
    self.lasttime = datetime.datetime.now(pytz.UTC)
    self.min_v = 5.0
    self.max_v = 0.0
    return

  def get_readings(self):
    """Read the anemometer.  This code reads 1 sample at 250 Hz in the
    expectation that a user downstream will be calling this every 0.25 
    seconds and averaging appropriately.

    returns a tuple (ws_mph, wr_miles)
      ws_mph: wind speed in miles per hour
      wr_miles: wind run in miles"""

    # get a timestamp and a reading
    timenow = datetime.datetime.now(pytz.UTC)
    # 0 = 0-1, 1=0-3, 2=1-3, 3=2-3
    # Gains: 2/3=6.144, 1=4.096, 2=2.048, 4=1.02, 8=0.512, 16=0.256
    while True:
        try:
            digitized = self.adc.read_adc_difference(3, gain=2,data_rate=250)
            break
        except:
            print("ADA1733.get_readings(): unable to read ADC")
            time.sleep(0.1)

    volts = digitized * 62.5*10.0**-6.0

    # get the converted values
    ws_mph = self.volts_to_mph(volts)

    # find the wind run
    wr_miles = self.wind_run(timenow - self.lasttime, ws_mph)

    # save this time for the next pass
    self.lasttime = timenow

    return ws_mph, wr_miles

  def volts_to_mph(self, volts):
    """Convert from voltage to meters per second.

    volts: voltage from ADA1733 anemometer

    returns: voltage converted to meters per second"""
    # output voltage is 0.4 to 2.0
    # which scales from 0 to 32.4 m/s
    # a 0 second average of the zero speed value was 0.3988 on 1/2/2015
    #rise = 32.4
    #run = 2.0 - 0.3988
    m = 32.4/(2.0-0.3988)   # 20.2348
    b = 32.4 - (m*2.0) # -8.0696

    if volts < 0.4:
      # don't return negative values ever
      return 0.0
    else:
      return (m*volts+b)*(3600.0/(0.3048*5280))

  def wind_run(self, delta_t, ws_mph):
    """Computes the wind run for the given time period.

    delta_t: datetime.timedelta object

    ws_mph: wind speed in miles per hour

    returns: wind run in US statute miles"""
    # compute the wind run in miles
    return delta_t.total_seconds() * ws_mph / 3600.0

def main():
  print("Copyright (C) 2015 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")

  print("Press Control-c to exit.")

  # instance the anemometer class
  ada1733 = ADA1733()

  # initialize total wind_run
  total_windrun = 0.0

  # read the values and loop
  while True:
    # get the readings
    ws_mph, windrun = ada1733.get_readings()

    # add the windrun to our total
    total_windrun += windrun

    # get a timestamp
    timenow = datetime.datetime.now(pytz.UTC)

    # show the user what we got
    data = ": Wind Speed (mph):{:.1f} Wind Run (miles):{:.3f}".format(ws_mph, total_windrun)
    print(timenow.strftime("%Y-%m-%d %H:%M:%S.%f %Z"), data)

    # wait a bit
    time.sleep(0.25) 

# only run main if this is called directly
if __name__ == '__main__':
  main()

