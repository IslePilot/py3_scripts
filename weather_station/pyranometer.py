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


class Pyranometer(object):
  # address selections
  ADDR_GND = 0x48
  ADDR_VDD = 0x49
  ADDR_SDA = 0x4a
  ADDR_SCL = 0x4b

  ADS1015 = 0x00	# 12-bit ADC
  ADS1115 = 0x01	# 16-bit ADC

  def __init__(self):
    """Initialize the ADS1115 object."""
    #self.adc = ADS1x15(address=Pyranometer.ADDR_GND, ic=Pyranometer.ADS1115)
    self.adc = ADS1x15.ADS1115(address=0x48)
    return

  def get_readings(self):
    """Read the pyranometer.  This code reads 1 sample at 250 Hz in the
    expectation that a user downstream will be calling this every 0.25 
    seconds and averaging appropriately."""

    # get a timestamp and a reading
    timenow = datetime.datetime.now(pytz.UTC)
    # set the gain for a maximum of 1.024 V
    # the peak insolation in Colorado is likely around 1000 W/m^2.  If we use
    # a voltage range that goes +/-0.256, we are good up to about 1229 W/m^2.
    while True:
        try:
            digitized = self.adc.read_adc_difference(0, gain=16,data_rate=250)
            break
        except:
            print("Pyranometer.get_readings(): unable to read ADC.")
            time.sleep(0.1)

    # convert to volts
    volts = digitized * 0.256/32767

    # don't let it go negative
    if volts < 0.0:
        volts = 0.0

    # get the converted values
    flux = self.volts_to_flux(volts)

    return volts, flux

  def volts_to_flux(self, volts):
    """Convert from voltage to meters per second.

    volts: voltage from the pyranometer

    returns: voltage converted to meters per second"""

    # this calibration value is the one found in a calibration by the original
    # pyranometer designer.  This needs to be verified once installed and compared
    # to local measurements if you can find any.  Try NREL?
    # http://midcdmz.nrel.gov/srrl_bms/display/
    # http://midcdmz.nrel.gov/srrl_bms <-- 20 nm from home
    # calibrated on 20170906 data, 0.963 factor found (4622.4)
    return volts * 4800.0 * 0.963


def main():
  print("Copyright (C) 2015 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")

  print("Press Control-c to exit.")

  # instance the anemometer class
  pyranometer = Pyranometer()

  # read the values and loop
  while True:
    # get the readings
    volts, flux = pyranometer.get_readings()

    # get a timestamp
    timenow = datetime.datetime.now(pytz.UTC)

    # show the user what we got
    data = ": Volts:{:.5f}  Solar Insolation (W/m^2):{:.1f}".format(volts, flux)
    print(timenow.strftime("Y-%m-%d %H:%M:%S.%f %Z"), data)

    # wait a bit
    time.sleep(0.25) 

# only run main if this is called directly
if __name__ == '__main__':
  main()

