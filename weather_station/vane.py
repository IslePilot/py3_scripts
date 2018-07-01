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
  2015-01=23, ksb, corrected calibration for actual device
  2015-01-09, ksb, created
"""

import sys
sys.path.append("..")

import time
import datetime
import pytz
import signal

#from __hardware.Adafruit_ADS1x15 import ADS1x15
from Adafruit_ADS1x15 import ADS1x15

# define a version for this file
VERSION = "1.0.20150109a"

def signal_handler(signal, frame):
  """This exits cleanly after receiving a control-c"""
  print("You pressed Control-c.  Exiting.")
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class Vane(object):
  # address selections
  ADDR_GND = 0x48
  ADDR_VDD = 0x49
  ADDR_SDA = 0x4a
  ADDR_SCL = 0x4b

  ADS1015 = 0x00	# 12-bit ADC
  ADS1115 = 0x01	# 16-bit ADC

  def __init__(self):
    """Initialize the ADS1115 object."""
    #self.adc = ADS1x15(address=Vane.ADDR_VDD, ic=Vane.ADS1115)
    self.adc = ADS1x15.ADS1115(address=0x49)

    self.last_v = None

    return

  def get_readings(self):
    """Read the anemometer.  This code reads 1 sample at 250 Hz in the
    expectation that a user downstream will be calling this every 0.25 
    seconds and averaging appropriately."""

    # get a timestamp and a reading
    timenow = datetime.datetime.now(pytz.UTC)
    #volts = self.adc.readADCDifferential(chP=2, chN=3, pga=6144, sps=250)/1000.0
    # differential
    # 0: 0 & 1
    # 1: 0 & 3
    # 2: 1 & 3
    # 3: 2 & 3

    # channel
    # 0: 0 & GND
    # 1: 1 & GND
    # 2: 2 & GND
    # 3: 3 & GND

    # gain
    # 0: FS=+/-6.144
    # 1: FS=+/-4.096
    # 2: FS=+/-2.048
    # 4: FS=+/-1.024
    # 8: FS=+/-0.512
    # 16: FS=+/-0.256
    #volts = self.adc.read_adc_difference(3, gain=0, data_rate=250)/10000.0
    #digitized = self.adc.read_adc(3, gain=0, data_rate=250)
    while True:
        try:
            digitized = self.adc.read_adc_difference(3, gain=0, data_rate=250)
            break
        except:
            print("vane.get_readings(): unable to read ADC")
            time.sleep(0.1)
    
    # convert to volts
    volts = digitized * 6.144/32767

    # get the converted values
    degrees = self.volts_to_degrees(volts)

    return volts, degrees

  def volts_to_degrees(self, volts):
    """Convert from voltage to meters per second.

    volts: voltage from ADA1733 anemometer

    returns: voltage converted to meters per second"""

    # calibrations
    min_v = 0.24469
    max_v = 4.82415
    slope = 360.0/(max_v-min_v)
    b = -(slope*min_v)
    deg = slope*volts+b
    if deg < 0.05: deg = 0.0
    if deg > 359.95: deg = 0.0

    # calibration
    deg -= 249.5 # 339.5=90.0
    deg %= 360.0

    return deg


def main():
  print("Copyright (C) 2015 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")

  print("Press Control-c to exit.")

  # instance the anemometer class
  vane = Vane()

  # read the values and loop
  max_volts = 0.0
  min_volts = 5.0
  while True:
    # get the readings
    volts, degrees = vane.get_readings()

    # track the max and min
    if volts < min_volts: min_volts = volts
    if volts > max_volts: max_volts = volts

    # get a timestamp
    timenow = datetime.datetime.now(pytz.UTC)

    # show the user what we got
    data = ": Volts:{:.5f}  Degrees:{:05.1f}, max:{:.5f} min:{:.5f}".format(volts, degrees, max_volts, min_volts)
    print(timenow.strftime("%Y-%m-%d %H:%M:%S.%f %Z"), data)

    time.sleep(0.25)

# only run main if this is called directly
if __name__ == '__main__':
  main()

