#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-22, ksb, created
"""

import sys
sys.path.append("..")
import __common.filetools as filetools

import datetime

from collections import OrderedDict

import time

# define a version for this file
VERSION = "1.0.20180522a"

class WxDataCollector():
  BAD_INT = -999
  BAD_FLOAT = -999.99
  
  SKY_CLR = 0 # for SKC (human generated) and CLR meaning no clouds
  SKY_FEW = 1 # 1/8 to 1/4 coverage
  SKY_SCT = 2 # 3/8 to 1/2 coverage
  SKY_BKN = 3 # 5/8 to 7/8 coverage
  SKY_OVC = 4 # total coverage
  
  WX_DZ = 5 # Drizzle
  WX_RA = 6 # Rain
  WX_FZRA = 7 # Freezing Rain
  WX_SH = 8 # Showers
  WX_BR = 9 # Mist
  WX_FC = 10 # Funnel Cloud, Tornado, or Waterspout
  WX_FG = 11 # Fog
  WX_FU = 12 # Smoke
  WX_GR = 13 # Hail
  WX_HZ = 14 # Haze
  WX_IC = 15 # Ice Crystals
  WX_SA = 16 # Sand
  WX_SG = 17 # Snow Grains
  WX_SN = 18 # Snow
  WX_SNSH = 19 # Snow Showers
  WX_LTG = 20 # Lightning
  WX_TS = 21 # Thunderstorm  
  
  def __init__(self, wx_data_directory, metar_site):
    # save the input
    self.path = wx_data_directory
    self.metar_site = metar_site
    
    # ensure our data path exists
    filetools.mkdir("{:s}/VWSInput".format(self.path))
    
    # build the data format
    self.data = OrderedDict() # native units
    self.build_data_format()
    
    # instance the data collectors
    
    # start the main loop
    self.main_loop()
    
    return
  
  def build_data_format(self):
    self.data['version'] = [1.01, "{:.2f},", "Version"]
    
    # from timestamp
    self.data['year'] = [WxDataCollector.BAD_INT, "{:d},", "Year"]
    self.data['month'] = [WxDataCollector.BAD_INT, "{:d},", "Month"]
    self.data['day'] = [WxDataCollector.BAD_INT, "{:d},", "Day"]
    self.data['hour'] = [WxDataCollector.BAD_INT, "{:d},", "Hour"]
    self.data['minute'] = [WxDataCollector.BAD_INT, "{:d},", "Minute"]
    self.data['second'] = [WxDataCollector.BAD_INT, "{:d},", "Second"]
    
    # from anemometer and vane
    self.data['wind_speed_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Speed (mph)"]
    self.data['wind_gust_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Gust (mph)"]
    self.data['wind_direction_deg'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Direction (true deg)"]
    
    # from sensors
    self.data['inside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Humidity (%)"]
    self.data['outside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outside Humidity (%)"]
    self.data['inside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Temperature (deg F)"]
    self.data['outside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outiside Temperature (deg F)"]
    self.data['barometer_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Sea Level Pressure (in Hg)"]
    
    # from rain gauge
    self.data['total_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Total Rain (in)"]
    self.data['daily_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Daily Rain (in)"]
    self.data['hourly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Hourly Rain (in)"]
    
    # from METAR
    self.data['sky_condition'] = [WxDataCollector.BAD_INT, "{:d},", "Sky Condition"]
    
    # from system
    self.data['channel1_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temperature (deg F)"]
    self.data['channel1_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Humidity (%)"]
    self.data['channel2_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Temperature (deg F)"]
    self.data['channel2_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Humidity (%)"]
    self.data['channel3_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Temperature (deg F)"]
    self.data['channel3_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Humidity (%)"]
    
    # not used
    self.data['evapotransporation'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Evapotranspiration (in)"]
    self.data['uv_index'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "UV Index"]
    
    # from pyranometer
    self.data['solar_radiation'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Solar Radiation (W/m**2)"]
    
    # computed
    self.data['wind_chill_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Chill (deg F)"]
    self.data['indoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Heat Index (deg F)"]
    self.data['outdoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Heat Index (deg F)"]
    self.data['dew_point_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Dew Point (deg F)"]
    
    # rates from data
    self.data['rain_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Rain Rate (in/hr)"]
    self.data['outdoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Temp Rate (deg F/hr)"]
    self.data['indoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Temp Rate (deg F/hr)"]
    self.data['barometer_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Barometer Rate"]
    self.data['channel1_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temp Rate (deg F/hr)"]
    self.data['channel2_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Temp Rate (deg F/hr)"]
    self.data['channel3_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Temp Rate (deg F/hr)"]
    
    # from rain gauge
    self.data['monthly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Monthly Rain (in)"]
    self.data['yearly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f}\n", "Yearly Rain (in)"]
    
    return
  
  def main_loop(self):
    """This is the main loop...collect data, publish it, wait, and repeat"""
    # main loop...don't ever exit
    while True:
      # collect data
      # get the time...the local clock is set with NTP regularly
      self._get_time()
      
      # get the latest metar data from the closest location
      
      
      # publish the data to our data file
      self.write_data_files()
      
      # show the user what we have
      print("Time: {:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(self.data['year'][0],
                                                                     self.data['month'][0],
                                                                     self.data['day'][0],
                                                                     self.data['hour'][0],
                                                                     self.data['minute'][0],
                                                                     self.data['second'][0]))
      
      # wait a bit for the next loop
      time.sleep(3.0)
      
    return
  
  def write_data_files(self):
    """write the current data to a file, and when complete move the file to the proper input location"""
    # build our strings
    header_string = ""
    data_string = ""
    for value in self.data.values():
      header_string += value[2] + ","
      data_string += value[1].format(value[0])
    # remove the extra comma and replace with a newline
    header_string = header_string[:-1]
    header_string += "\n"
    
    # show what we built
    #print(header_string)
    #print(data_string)
    
    # open a temp file
    with open("{:s}\\VWSInput\\temp_data.csv".format(self.path), "w") as temp_file:
      #temp_file.write(header_string)
      temp_file.write(data_string)
    
    # move to the input file
    filetools.mv("{:s}\\VWSInput\\temp_data.csv".format(self.path), "{:s}\\VWSInput\\data.csv".format(self.path))
    
    return
  
  def _get_time(self):
    """Get the time from the local clock.  This clock should be set via NTP"""
    # get the current time in UTC
    timenow = datetime.datetime.utcnow()
    
    # save the data to our data
    self.data['year'][0] = timenow.year
    self.data['month'][0] = timenow.month
    self.data['day'][0] = timenow.day
    self.data['hour'][0] = timenow.hour
    self.data['minute'][0] = timenow.minute
    self.data['second'][0] = timenow.second
    
    return
    
    
    
        
if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  wx_data_directory = r"C:\WX"
  metar_site = 'KEIK'
  
  while True:
    # this should never return
    wx_data_collector = WxDataCollector(wx_data_directory, metar_site)
    
    # if we get here, give it a few seconds and restart
    time.sleep(10.0)
  
  
    
    
