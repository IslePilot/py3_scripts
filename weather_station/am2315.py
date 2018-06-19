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
    2017-09-17: ksb, style editing to move towards PEP8 compliance
    2014-12-29: ksb, created

NOTE:
This requires the pigpio library created by Joan.

Get this via git:
    git clone https://github.com/joan2937/pigpio

Documentation at http://abyz.co.uk/rpi/pigpio

Ensure pigpiod is running prior to starting this code
add /usr/local/bin/pigpiod to /etc/rc.local to run automatically
"""

import pigpio
import time
import datetime

# define a version for this file
VERSION = "1.0.20170917a"

class AM2315():
  """A Python class to read the AOSONG 2315 sensor."""
  
  def __init__(self):
    """Initialize the AOSONG AM2315 reader.
    Note you must have the pigpiod running (sudo pigpiod)"""
    # connect to the local pi
    self.pi = pigpio.pi()
    
    # Use bus 1 for the B+ model
    # set the device address we are working with (0x5c)
    self.handle = self.pi.i2c_open(1, 0x5c, 0)
    
    return
    
  def get_readings(self):
    """This is the main routine to call.  This will get the 
    readings from the sensor and return engineering units.
    
    NOTE:  the readings returned seem to be one or two cycles
    old, so you may want to ignore the first two readings as 
    they may be inaccurate.
    
    returns a tuple (temp_f, temp_c, rh)
      temp_f: temperature in Farenheit
      temp_c: temperature in Celsius
      rh:  relative humidity"""
    # wake up the sensor
    self._wake_sensor()
    
    # read the raw data
    rh_msb, rh_lsb, t_msb, t_lsb = self._read_raw()
    
    # convert the humidity to engineering units
    rh = self._calculate_humidity(rh_msb, rh_lsb)
    
    # convert the temperature to engineering units (C and F)
    temp_c, temp_f = self._calculate_temperature(t_msb, t_lsb)
    
    return temp_f, temp_c, rh
  
  def _wake_sensor(self):
    """Wake up the sensor from dormancy--sleeps after 3 seconds
    to improve humidity readings."""
    # Wake up the sensor...this dies because the sensor doesn't
    # return an ack.  Ignore the issue and plunder along happily
    # 0x03 = Read Command
    # 0x00 = Read starting at byte 0
    # 0x04 = Read 4 bytes
    try:
      self.pi.i2c_write_device(self.handle, [0x03, 0x00, 0x04])
    except:
      pass
    time.sleep(0.1)
    return
  
  def _read_raw(self):
    """Read the raw data values from the sensor.
    
    returns a tuple (rh_msb, rh_lsb, t_msb, t_lsb)
      rh_msb: relative humidity most significant byte
      rh_lsb: relative humidity least significant byte
      t_msb:  temperature most significant byte
      t_lsb:  temperature least significant byte"""
    # request the data, wait, and read the data
    # 0x03 = Read Command
    # 0x00 = Read starting at byte 0
    # 0x04 = Read 4 bytes
    self.pi.i2c_write_device(self.handle, [0x03, 0x00, 0x04])
    time.sleep(0.1)
    
    # even though 4 bytes were requested, 8 are returned, only get the data
    # byte 0: function code
    # byte 1: number of bytes returned
    # byte 2: RH MSB
    # byte 3: RH_LSB
    # byte 4: TEMP_MSB
    # byte 5: TEMP_LSB
    # byte 6: CRC_LSB    # this could be checked, not straightforward, docs very poor
    # byte 7: CRC_MSB
    data = self.pi.i2c_read_device(self.handle, 8)[1]
    
    return data[2], data[3], data[4], data[5]
  
  def _calculate_humidity(self, msb, lsb):
    """convert the msb and lsb to relative humidity (%)
    
    msb: relative humidity most significant byte
    lsb: relative humidity least significant byte"""
    return (msb*256.0 + float(lsb)) / 10.0
  
  def _calculate_temperature(self, msb, lsb):
    """convert the msb and lsb to temperature (C and F)
    
    msb: relative humidity most significant byte
    lsb: relative humidity least significant byte
    
    returns a tuple (t_c, t_f)
      t_c: temperature in Celsius
      t_f: temperature in Farenheit"""
    # the bit 15 of the msb is a positive/negative flag, mask it off
    t_c = ((msb&0x7f)*256.0 + float(lsb)) / 10.0
    
    # if bit 15 of the msb is 1, then the value is negative
    if msb & 0x80:
      t_c = -t_c
    
    # convert to farenheit
    t_f = 9.0*t_c/5.0 + 32.0
    
    return t_c, t_f
  
if __name__ == '__main__':
  # add the GPL license output
  print("am2315.py Copyright (C) 2018 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")
  
  # start here
  am2315 = AM2315()
  
  # the first two readings might be junk, read and skip
  am2315.get_readings()
  time.sleep(1)
  am2315.get_readings()
  time.sleep(1)
  
  # read the values every 5 seconds
  while True:
    temp_f, temp_c, rh = am2315.get_readings()
    
    timenow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
     
    print("{:s}:  T(F): {:.2f}   T(C): {:.1f}   RH: {:.1f}".format(timenow, temp_f, temp_c, rh))
    
    # the AOSONG docs don't indicate how often you can read the device, but
    # they do indicate that the sensor goes to sleep to improve humidity values after
    # 3 seconds from waking up.  This indicates we might not want to read more often
    # than every 5 to 10 seconds to maximize accuracy.
    time.sleep(5)


