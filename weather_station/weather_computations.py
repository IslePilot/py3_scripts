#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-27, ksb, created
"""

import sys
sys.path.append("..")

import math

# define a version for this file
VERSION = "1.0.2018-05-27a"

def temp_c_to_f(temp_c):
  return temp_c * 9.0/5.0 + 32.0

def temp_f_to_c(temp_f):
  return (temp_f - 32.0)*5.0/9.0

def speed_kt_to_mph(speed_kt):
  return speed_kt * 6076.12 / 5280.0

def speed_mph_to_kt(speed_mph):
  return speed_mph * 5280.0 / 6076.12

def calc_vapor_saturation_pressure_hPa(temp_c):
  """from https://www.vaisala.com/sites/default/files/documents/Humidity_Conversion_Formulas_B210973EN-F.pdf"""
  # constants
  Tc = 647.096  # critical temperature, K
  Pc = 220640.0 # critical pressure, hPa
  C1 = -7.85951783
  C2 = 1.84408259
  C3 = -11.7866497
  C4 = 22.6807411
  C5 = -15.9618719
  C6 = 1.80122502
  
  Tn = 273.16 # triple point temperature, K
  Pn = 6.11657  # vapor pressure at triple point temperature, hPa
  A0 = -13.928169
  A1 = 34.707823
  
  
  # get the temp in Kelvin
  temp_k = temp_c+273.15
  
  # computation is different based on temperature
  if temp_c >= 0.0:
    v = 1.0 - (temp_k/Tc)
    return Pc * math.exp((Tc*(C1*v + C2*v**1.5 + C3*v**3 + C4*v**3.5 + C5*v**4 + C6*v**7.5))/temp_k)
  
  else:
    theta = temp_k / Tn
    return Pn * math.exp(A0*(1-theta**-1.5) + A1*(1-theta**-1.25))
  
def calc_dewpoint_c(temp_c, rh_pct):
  """Compute the dewpoint in deg C
  
  Computation info from https://www.vaisala.com/sites/default/files/documents/Humidity_Conversion_Formulas_B210973EN-F.pdf, Chapter 3
  
  temp_c: current temperature in deg C
  rh_pct: current relative humidity in percent
  
  returns: dewpoint in deg C"""
  # build our constants
  if -20.0 <= temp_c and temp_c <= 50.0:
    A = 6.116441
    m = 7.591386 
    Tn = 240.7263
  elif 50.0 < temp_c and temp_c <= 100.0:
    A = 6.004918
    m = 7.337936 
    Tn = 229.3975
  elif -70.0 <= temp_c and temp_c < -20.0:
    A = 6.114742
    m = 9.778707  
    Tn = 273.1466
  else:
    print("dewpoint_c: Temperature range not supported.")
  
  # get the vapor pressure
  Pws = calc_vapor_saturation_pressure_hPa(temp_c)
  Pw = Pws*rh_pct/100.0
  
  return Tn/(m/math.log10(Pw/A)-1) 
  
  return

def calc_rh_pct(temp_c, dewpoint_c):
  return 100.0 * calc_vapor_saturation_pressure_hPa(dewpoint_c)/calc_vapor_saturation_pressure_hPa(temp_c)

def compute_wind_chill(temp_f, wind_speed_mph):
  return 35.74 + (0.6215*temp_f) - (35.75*wind_speed_mph**0.16) + (0.4275*temp_f*wind_speed_mph**0.16)

def compute_heat_index(temp_f, rh_pct):
  """from http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml"""
  heat_index = -42.379 \
               + 2.04901523*temp_f \
               + 10.14333127*rh_pct \
               - 0.22475541*temp_f*rh_pct \
               - 0.00683783*temp_f**2 \
               - 0.05481717*rh_pct**2 \
               + 0.00122874*rh_pct*temp_f**2 \
               + 0.00085282*temp_f*rh_pct**2 \
               - 0.00000199*(temp_f**2)*rh_pct**2
  
  if rh_pct < 13.0 and 80.0 < temp_f and temp_f < 112.0:
    heat_index -= ((13.0-rh_pct)/4.0)*math.sqrt((17.0-abs(temp_f-95.0))/17.0)
  
  if rh_pct > 85.0 and 80.0 < temp_f and temp_f < 87.0:
    heat_index += ((rh_pct-85.0)/10.0) * ((87.0-temp_f)/5.0)
  
  if heat_index < 80.0:
    heat_index =  0.5 * (temp_f + 61.0 + [(temp_f-68.0)*1.2] + (rh_pct*0.094))
  
  return heat_index  
  
  return 
if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # test 1
  temp_f = 92.3
  rh_pct = 9.0
  dp_f = 25.3
  
  dp_calc_c = calc_dewpoint_c(temp_f_to_c(temp_f), rh_pct)
  print(temp_c_to_f(dp_calc_c))
  
  rh_calc = calc_rh_pct(temp_f_to_c(temp_f), dp_calc_c)
  print(rh_calc)

