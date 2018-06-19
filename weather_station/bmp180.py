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
    2017-09-17: ksb, style formating to move towards PEP8 compliance
    2015-07-24: ksb, moved density altitude computation out of class for accuracy
    2015-07-24: ksb, added calibration factor for SLP computation
    2014-12-31: ksb, created
"""
# define a version for this file
VERSION = "1.0.20170917a"

import Adafruit_BMP.BMP085 as BMP085
import time
import datetime


# define the module methods
def compute_density_altitude(p_inhg, t_f):
  """Compute the density altitude.
  
  This is not a class method as the temperature used should be
  the best temperature available.  Since the BMP180 isn't weather
  proof, it likely won't be in a FARS and will probably be too
  warm.
  
  p_inhg: static pressure in inches of mercury
  t_f: temperature in Farenheit
  
  returns: density altitude in feet"""
  # use NWS approximation for density altitude
  return 145442.16 * (1 - (17.326*p_inhg/(459.67+t_f))**0.235)

class BMP180():

  def __init__(self, sensor_elevation_ft):
    """Instance the bmp085 sensor reader.  The BMP085 and BMP180 have identical interfaces.
    
    sensor_elevation_ft:  The elevation above mean sea-level of the sensor"""
    
    # instance the sensor class
    # we aren't too concerned with power or speed so use ultra high res mode
    self.sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
    
    # compute our standard atmosphere temperature
    self.sensor_elevation_ft = sensor_elevation_ft
    self.isa_temp_c = 15.0 - 2.0 * sensor_elevation_ft/1000.0
    
    return
    
  def get_readings(self):
    """Get the readings from the sensor and compute other derived values.
    
    returns a tuple (t_f, t_c, p_inhg, slp_inhg, pa_ft, da_ft)
      t_f: temperature in Farenheit
      t_c: temperature in Celsius
      p_inHg: static pressure in inches of mercury
      slp_inHg: sea-level pressure in inches of mercury
      pa_ft: pressure altitude in feet"""
    
    # read the sensor to get the basic readings
    t_c = self.sensor.read_temperature()	# get the temperature in deg C
    p_pa = self.sensor.read_pressure()		# get the pressure in pascals
    pa_m = self.sensor.read_altitude()		# get the pressure altitude in meters
    
    # compute the derived values and conversions
    t_f = self.c_to_f(t_c)
    
    p_inhg = self.pa_to_inhg(p_pa)
    slp_inhg = self.compute_sealevel_pressure(p_inhg)
    
    pa_ft = self.m_to_ft(pa_m)
    
    return t_f, t_c, p_inhg, slp_inhg, pa_ft
  
  def c_to_f(self, t_c):
    """Convert Celsius to Farenheit.
    
    t_c: temperature in celsius
    
    returns: temperature in farenheit"""
    return t_c * 9.0/5.0 + 32.0
  
  def pa_to_inhg(self, p_pa):
    """Convert pressure in pascals to inches of mercury.
    
    p_pa: pressure in pascals
    
    returns: pressure in inches of mercury"""
    return p_pa * 0.000295299830714
  
  def m_to_ft(self, m):
    """Convert distance in meters to US feet.
    
    m: distance in meters
    
    returns: distance in US feet"""
    return m / 0.3048
  
  def compute_sealevel_pressure(self, p_inhg):
    """Compute the sea level pressure based on the measured pressure and
    the station elevation (self.sensor_elevation_ft).
    
    p_inhg:  current static pressure in inches of mercury
    
    returns computed sea-level pressure in inches of mercury"""
    # define some constants
    p0 = 29.92126	# inHg
    T0 = 288.15		# kelvin
    L = -0.00198	# deg K/ft
    H0 = 0.0		# feet above sea level
    R = 89494.6		#
    g0 = 32.17405	# ft/s^2
    M = 28.9644		# g/mol
    
    calibration = 0.05
    
    exponent = (g0*M)/(R*L)
    paren = T0 / (T0+L*(self.sensor_elevation_ft-H0))
    pressure = p0 * paren**exponent
    
    delta_p = p0 - pressure
    
    return delta_p + p_inhg + calibration


if __name__ == '__main__':
  # instance our sensor object
  bmp180 = BMP180(sensor_elevation_ft = 5089.0)
  
  # read the values every second
  while True:
    # get the readings
    t_f, t_c, p_inhg, slp_inhg, pa_ft = bmp180.get_readings()
    da_ft = compute_density_altitude(p_inhg, t_f)
    
    # get a timestamp
    timenow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # show the user what we got
    print("{:s}: T(F):{:.2f} T(C):{:.2f} P(inHg):{:.2f} SLP(inHg):{:.2f} PA(ft):{:.1f} DA:{:.1f}".format(timenow,
                                                                                                            t_f,
                                                                                                            t_c,
                                                                                                            p_inhg,
                                                                                                            slp_inhg,
                                                                                                            pa_ft,
                                                                                                            da_ft))
    
    # rest a bit
    time.sleep(1.0)

  return


