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
import __common.mparray_transmitter as txrx

import weather_computations as wx
import metar_processor as metar

import datetime
import pytz
import time

from collections import OrderedDict

from multiprocessing import Array

# define a version for this file
VERSION = "1.0.20180522a"

class WxDataCollector():
  BAD_INT = 0
  BAD_FLOAT = 0
  
  def __init__(self, wx_data_directory, metar_site, elevation_ft):
    # save the input
    self.path = wx_data_directory
    
    # ensure our data path exists
    filetools.mkdir("{:s}/VWSInput".format(self.path))
    
    # build our shared memory datasets
    self.metar_array = Array('f', 9)
    
    # instance the data collectors
    self.gather_metar_data(station_id = metar_site)
    
    # build the data format
    self.data = OrderedDict() # native units
    self.build_data_format()
    
    # initialize some data
    self.elevation_ft = elevation_ft
    self.last_metar_timestamp = None
    self.last_metar_temp_deg_f = None
    self.last_metar_altim_in_hg = None
    
    # start the main loop
    self.main_loop()
    
    return
  
  def gather_metar_data(self, station_id):
    # create the metar collector
    self.metar_collector = metar.MetarCollector(self.metar_array, station_id)
    self.metar_collector.daemon = True  # run this process until this process dies
    self.metar_collector.start()
    
    return
  
  def build_data_format(self):
    self.data['version'] = [1.01, "{:.2f},", "Version"]
    
    # from timestamp
    self.data['year'] = [WxDataCollector.BAD_INT, "{:d},", "Year"]  # local clock
    self.data['month'] = [WxDataCollector.BAD_INT, "{:d},", "Month"]  # local clock
    self.data['day'] = [WxDataCollector.BAD_INT, "{:d},", "Day"]  # local clock
    self.data['hour'] = [WxDataCollector.BAD_INT, "{:d},", "Hour"]  # local clock
    self.data['minute'] = [WxDataCollector.BAD_INT, "{:d},", "Minute"]  # local clock
    self.data['second'] = [WxDataCollector.BAD_INT, "{:d},", "Second"]  # local clock
    
    # from anemometer and vane
    self.data['wind_speed_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Speed (mph)"]  # METAR for now
    self.data['wind_gust_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Gust (mph)"]  # METAR for now
    self.data['wind_direction_deg'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Direction (true deg)"]  # METAR for now
    
    # from sensors
    self.data['inside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Humidity (%)"]
    self.data['outside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outside Humidity (%)"]  # METAR for now
    self.data['inside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Temperature (deg F)"]
    self.data['outside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outiside Temperature (deg F)"]  # METAR for now
    self.data['barometer_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Sea Level Pressure (in Hg)"]  # METAR for now
    
    # from rain gauge
    self.data['total_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Total Rain (in)"]
    self.data['daily_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Daily Rain (in)"]
    self.data['hourly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Hourly Rain (in)"]
    
    # from METAR
    self.data['sky_condition'] = [WxDataCollector.BAD_INT, "{:d},", "Sky Condition"] # METAR
    
    # from other various sources
    self.data['channel1_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temperature (deg F)"] # METAR
    self.data['channel1_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Humidity (%)"] # METAR
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
    self.data['wind_chill_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Chill (deg F)"]  # METAR for now
    self.data['indoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Heat Index (deg F)"]
    self.data['outdoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Heat Index (deg F)"]  # METAR for now
    self.data['dew_point_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Dew Point (deg F)"]  # METAR for now
    
    # rates from data
    self.data['rain_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Rain Rate (in/hr)"]
    self.data['outdoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Temp Rate (deg F/hr)"]
    self.data['indoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Temp Rate (deg F/hr)"]
    self.data['barometer_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Barometer Rate"]  # METAR for now
    self.data['channel1_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temp Rate (deg F/hr)"]  # METAR
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
      self._get_metar()
            
      # publish the data to our data file
      self.write_data_files()
      
      # show the user we are running
      print("{:s}".format(datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f")), end="\r", flush=True)
      
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
    # get the current time in UTC (make sure we are timezone aware)
    timenow = datetime.datetime.now(pytz.UTC)
    
    # save the data to our data
    self.data['year'][0] = timenow.year
    self.data['month'][0] = timenow.month
    self.data['day'][0] = timenow.day
    self.data['hour'][0] = timenow.hour
    self.data['minute'][0] = timenow.minute
    self.data['second'][0] = timenow.second
    
    return
  
  def _get_metar(self):
    # get the current metar data
    with self.metar_array.get_lock():
      timestamp, temp_c, dewpoint_c, rh_pct, wind_dir_deg, wind_speed_kt, wind_gust_kt, code, altim_in_hg = self.metar_array[:]
    
    # if the timestamp is zero, we have no data, so just return for now
    if round(timestamp) == 0:
      return
    
    # if the timestamp didn't change, nothing changed, so we are done
    if self.last_metar_timestamp != None and timestamp == self.last_metar_timestamp:
      return
    
    print("New METAR Data:", timestamp, temp_c, dewpoint_c, rh_pct, wind_dir_deg, wind_speed_kt, wind_gust_kt, code, altim_in_hg)
    
    # get some things in better units
    temp_f = wx.temp_c_to_f(temp_c)
    dewpoint_f = wx.temp_c_to_f(dewpoint_c)
    wind_speed_mph = wx.speed_kt_to_mph(wind_speed_kt)
    gust_speed_mph = wx.speed_kt_to_mph(wind_gust_kt)
    
    # values we always want to get from the METAR data
    self.data['channel1_temp_degF'][0] = temp_f
    self.data['channel1_humidity_pct'][0] = rh_pct
    self.data['sky_condition'][0] = round(code)
    if self.last_metar_timestamp != None and round(self.last_metar_timestamp) != 0:
      d_temp_f = temp_f - self.last_metar_temp_deg_f
      d_time_sec = timestamp - self.last_metar_timestamp
      d_time_hr = d_time_sec/3600.0
      self.data['channel1_temp_rate_degF_per_hour'][0] = d_temp_f/d_time_hr
    else:
      self.data['channel1_temp_rate_degF_per_hour'][0] = 0.0
    
    # these values will be replaced with our sensors when available
    self.data['wind_speed_mph'][0] = wind_speed_mph
    self.data['wind_gust_mph'][0] = gust_speed_mph
    self.data['wind_direction_deg'][0] = wind_dir_deg
        
    self.data['barometer_in'][0] = wx.compute_station_from_altimeter(altim_in_hg, self.elevation_ft)
    self.data['outdoor_heat_index_degF'][0] = wx.compute_heat_index(temp_f, rh_pct)
    self.data['dew_point_degF'][0] = dewpoint_f
    
    self.data['outside_temp_degF'][0] = temp_f
    self.data['outside_humidity_pct'][0] = rh_pct
    
    self.data['wind_chill_degF'][0] = wx.compute_wind_chill(temp_f, wind_speed_mph)
    if self.last_metar_timestamp != None and round(self.last_metar_timestamp) != 0:
      d_press = altim_in_hg - self.last_metar_altim_in_hg
      d_time_sec = timestamp - self.last_metar_timestamp
      d_time_hr = d_time_sec/3600.0
      self.data['barometer_rate_in_per_hour'][0] = d_press/d_time_hr
    else:
      self.data['barometer_rate_in_per_hour'][0] = 0.0
      
    
    # save the data we need for the next update
    self.last_metar_timestamp = timestamp
    self.last_metar_temp_deg_f = temp_f
    self.last_metar_altim_in_hg = altim_in_hg
    
    return
  
  @staticmethod
  def get_weather_condition_code(text):
    # Not all sky covers are available, so use some logic
    if text == 'SKC' or text == 'CLR' or text == 'CAVOK':
      return 0  # SKY_CLR = 0 # for SKC (human generated) and CLR meaning no clouds
    
    if text == 'FEW':
      return 1 # SKY_FEW = 1 # 1/8 to 1/4 coverage
    
    if text == 'SCT':
      return 2 # SKY_SCT = 2 # 3/8 to 1/2 coverage
    
    if text == 'BKN':
      return 3 # SKY_BKN = 3 # 5/8 to 7/8 coverage
   
    if text == 'OVC' or text == 'OVX':
      return 4 # SKY_OVC = 4 # total coverage
    
    # Weather codes from: https://aviationweather.gov/static/adds/docs/metars/wxSymbols_anno2.pdf
    if text == '-DZ' or text == 'DZ' or text == '+DZ':
      return 5 # WX_DZ = 5 # Drizzle
    
    if text == '-RA' or text == 'RA' or text == '+RA':
      return 6 # WX_RA = 6 # Rain
    
    if text == '-FZRA' or text == 'FZRA' or text == '+FZRA' or \
       text == '-FZDZ' or text == 'FZDZ' or text == '+FZDZ':
      return 7 # WX_FZRA = 7 # Freezing Rain
    
    if text == '-SH' or text == 'SH' or text == '+SH' or \
       text == '-SHRA' or text == 'SHRA' or text == '+SHRA' or text == 'VCSH':
      return 8 # WX_SH = 8 # Showers
    
    if text == 'BR' or text == 'BLPY':  # Mist, Spray
      return 9 # WX_BR = 9 # Mist
    
    if text == 'FC' or text == '+FC':
      return 10 # WX_FC = 10 # Funnel Cloud, Tornado, or Waterspout
    
    if text == 'FG' or text == 'MIFG' or text == 'VCFG' or text == 'BCFG' or text == 'PRFG' or 'FZFG':
      return 11 # WX_FG = 11 # Fog
    
    if text == 'FU' or text == 'VA':  # Smoke, Volcanic Ash
      return 12 # WX_FU = 12 # Smoke
    
    if text == 'GR' or text == 'SHRG' or text == '+GR' or text == '+SHGR' or \
       text == 'PL' or text == 'PL' or text == 'SHPL' or text == 'SHPE' or \
       text == '-GS' or text == '-SHGS' or text == 'GS' or text == 'SHGS' or \
       text == '+GS' or text == '+SHGS' or text == '-GR' or text == '-SHGR':
      return 13 # WX_GR = 13 # Hail
    
    if text == 'HZ':
      return 14 # WX_HZ = 14 # Haze
    
    if text == 'IC':
      return 15 # WX_IC = 15 # Ice Crystals
    
    if text == 'SA' or text == 'BLSA' or text == 'VCBLSA' or \
       text == 'DU' or text == 'BLDU' or text == 'VCBLDU' or \
       text == 'PO' or text == 'VCPO' or text == 'VCSS' or text == 'VCDS' or \
       text == 'SS' or text == 'DRSA' or text == 'DS' or text == 'DRDU' or \
       text == '+SS' or text == '+DS':
      return 16 # WX_SA = 16 # Sand
    
    if text == 'SG':
      return 17 # WX_SG = 17 # Snow Grains
    
    if text == '-SN' or text == 'SN' or text == '+SN' or \
       text == 'BLSN' or text == 'VCBLSN' or text == 'DRSN':
      return 18 # WX_SN = 18 # Snow
    
    if text == '-SHSN' or text == 'SHSN' or text == '+SHSN':
      return 19 # WX_SNSH = 19 # Snow Showers
    
    #WX_LTG = 20 # Lightning -- No distinct code...lightning would imply a TS by definition
    
    if text == 'TS' or text == 'VCTS' or \
       text == 'TSRA' or text == 'TSSN' or text == 'TSPL' or text == 'TSGR' or \
       text == 'TSGS' or text == '+TSRA' or text == '+TSSN' or text == '+TSPL' or \
       text == '+TSGS' or text == '+TSGR' or text == 'VIRGA' or text == 'SQ':
      return 21 # WX_TS = 21 # Thunderstorm  
    
    print("WxDataCollector.get_weather_condition_code(): Unknown weather code:", text)
    
    return None


if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  wx_data_directory = r"C:\WX"
  metar_site = 'KEIK'
  pressure_sensor_elevation_ft = 5094.0
  
  while True:
    # this should never return
    wx_data_collector = WxDataCollector(wx_data_directory, metar_site, pressure_sensor_elevation_ft)
    
    # if we get here, give it a few seconds and restart
    time.sleep(10.0)
  
  
    
    
