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

def pressure_mbar_to_inhg(pressure_mbar):
  return pressure_mbar / 33.863886666667

def pressure_inhg_to_mbar(pressure_inhg):
  return pressure_inhg * 33.863886666667

def pressure_pascals_to_inhg(pressure_pascals):
  return pressure_pascals*0.000295299830714

def distance_m_to_ft(distance_m):
  return distance_m/0.3048

def distance_ft_to_m(distance_f):
  return distance_f*0.3048

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
  
  #Tn = 273.16 # triple cifp_point temperature, K
  #Pn = 6.11657  # vapor pressure at triple cifp_point temperature, hPa
  #A0 = -13.928169
  #A1 = 34.707823
  
  
  # get the temp in Kelvin
  temp_k = temp_c+273.15
  
  # computation is different based on temperature
  if temp_c >= 0.0:
    v = 1.0 - (temp_k/Tc)
    return Pc * math.exp((Tc*(C1*v + C2*v**1.5 + C3*v**3 + C4*v**3.5 + C5*v**4 + C6*v**7.5))/temp_k)
  
  else:
    #theta = temp_k / Tn
    #return Pn * math.exp(A0*(1-theta**-1.5) + A1*(1-theta**-1.25))
    
    # valid for temp -70 to 0C
    a = 6.114742
    m = 9.778707
    Tn = 273.1466
    
    mt = m*temp_c
    tptn = temp_c+Tn 
    div = mt/tptn
    pws = a*10**div
    return pws
  
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
  rh = 100.0 * calc_vapor_saturation_pressure_hPa(dewpoint_c)/calc_vapor_saturation_pressure_hPa(temp_c)
  return rh
  #dp = (17.625*dewpoint_c)/(243.04+dewpoint_c)
  #t = (17.625*temp_c)/(243.04+temp_c)
  #return 100.0 * math.exp(dp)/math.exp(t)

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
    heat_index =  0.5 * (temp_f + 61.0 + ((temp_f-68.0)*1.2) + (rh_pct*0.094))
  
  return heat_index  
  
  return 

def compute_slp_from_station(station_pressure_inhg, elevation_ft, temp_c):
  p = pressure_inhg_to_mbar(station_pressure_inhg)
  h = 0.3048*elevation_ft
  c = (1.0 - (0.0065*h)/(temp_c+273.15+0.0065*h))**-5.257
  p0 = p*c
  return pressure_mbar_to_inhg(p0)

def compute_station_from_slp(slp_in_hg, elevation_ft, temp_c):
  p0 = pressure_inhg_to_mbar(slp_in_hg)
  h = 0.3048*elevation_ft
  c = (1.0 - (0.0065*h)/(temp_c+273.15+0.0065*h))**-5.257
  p = p0/c
  return pressure_mbar_to_inhg(p)

def compute_station_from_altimeter(altimeter_inhg, elevation_ft):
  return (altimeter_inhg**0.1903-(1.313e-5*elevation_ft))**5.255

def compute_altimeter_from_station(station_inhg, elevation_ft):
  pb = 29.92126 # inHg
  tb = 288.15 # kelvin
  lb = -0.00198 # degK/ft
  hb = 0  # feet
  r = 89494.6
  g0 = 32.17405 # ft/s**2
  m = 28.9644 # g/mol
  
  exp = (g0*m)/(r*lb)
  paren = tb/(tb+lb*(elevation_ft-hb))
  
  press = pb*paren**exp
  delta = pb-press
  return delta+station_inhg
  
def compute_density_altitude(pressure_inhg, temp_f):
  return 145442.16 * (1-(17.326*pressure_inhg/(459.67+temp_f))**0.235)

def compute_pressure_altitude(slp_inhg, elevation_ft):
  return (29.92-slp_inhg)*1000+elevation_ft

if __name__ == '__main__':
  
  # using home station inside
  print(compute_altimeter_from_station(24.85, 5106.7)) # 29.975 KEIK=30.02
  print(compute_slp_from_station(24.85, 5106.7, temp_f_to_c(71.06))) # 29.672

  print(compute_station_from_altimeter(30.008858, 5106.7))  # 22.53
  print(pressure_mbar_to_inhg(1005.4)) # 29.69
  print(compute_station_from_slp(29.69, 75106.7, 21.1))  # 22.74
  
  
  
  print()


  
  
  


