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
import configparser

from collections import OrderedDict
from collections import namedtuple

from multiprocessing import Array

# define a version for this file
VERSION = "1.0.20180701a"

class WxDataCollector():
  BAD_INT = 0
  BAD_FLOAT = 0
  
  metar_list = ["timestamp"]
  metar_list.append("temp_c")
  metar_list.append("dewpoint_c")
  metar_list.append("rh_pct")
  metar_list.append("wind_dir_deg")
  metar_list.append("wind_speed_kt")
  metar_list.append("wind_gust_kt")
  metar_list.append("code")
  metar_list.append("altim_in_hg")
  METAR_DATA = namedtuple("METAR_DATA", metar_list)
  
  fence_list = ["timestamp"]
  fence_list.append("temp_f")
  fence_list.append("rh_pct")
  fence_list.append("sensor_temp_f")
  fence_list.append("press_inhg")
  fence_list.append("slp_inhg")
  fence_list.append("pa_ft")
  fence_list.append("da_ft")
  fence_list.append("int_rain_in")
  fence_list.append("total_rain_in")
  fence_list.append("daily_rain_in")
  fence_list.append("monthly_rain_in")
  fence_list.append("cpu_temp_f")
  FENCE_DATA = namedtuple("FENCE_DATA", fence_list)
  
  roof_list = ["timestamp"]
  roof_list.append("wind_direction")
  roof_list.append("wind_speed_mph")
  roof_list.append("wind_gust_mph")
  roof_list.append("solar_insolation")
  roof_list.append("cpu_temp_f")
  ROOF_DATA = namedtuple("ROOF_DATA", roof_list)
  
  def __init__(self, config_file):
    # parse the config file
    self.config = configparser.ConfigParser()
    self.config.read(config_file)
  
    # read the SYSTEM configuration items
    self.path = self.config['SYSTEM']['wx_data_directory']
    self.timezone = pytz.timezone(self.config['SYSTEM']['timezone'])
    
    # initialize 
    self.wind_speed_mph = None
    
    # ensure our output data path exists
    filetools.mkdir("{:s}/VWSInput".format(self.path))
    
    # build our shared memory datasets
    self.metar_array = Array('d', len(self.metar_list))
    self.fencestation_array = Array('d', len(self.fence_list))
    self.roofstation_array = Array('d', len(self.roof_list))
    
    # instance the data collectors
    self.gather_metar_data(self.config['METAR'])
    self.gather_fencestation_data(self.config['FENCE_STATION'])
    self.gather_roofstation_data(self.config['ROOF_STATION'])
    
    # build the data format
    self.data = OrderedDict() # native units
    self.build_data_format()
    
    # start the main loop
    self.main_loop()
    
    return
  
  def gather_metar_data(self, config):
    # read the config
    station_id = config['metar_site']
    
    # initialize the METAR variables
    self.last_metar = None
    
    # create and run the metar collector
    self.metar_collector = metar.MetarCollector(self.metar_array, station_id)
    self.metar_collector.daemon = True  # run this process until this process dies
    self.metar_collector.start()
    
    return
  
  def gather_fencestation_data(self, config):
    # read the config
    hostname = config['host']
    port = int(config['port'])
    password = config['authkey'].encode()
    read_delay = float(config['update_interval_sec'])
    
    # initialize the fence station variables
    self.last_fence_data = []
    
    # create and run the fence station collector
    self.fencestation_collector = txrx.MPArrayReceiver(hostname, port, password, read_delay, self.fencestation_array)
    self.fencestation_collector.daemon = True  # run this process on its own until this process dies
    self.fencestation_collector.start()
    
    return
  
  def gather_roofstation_data(self, config):
    # read the config
    hostname = config['host']
    port = int(config['port'])
    password = config['authkey'].encode()
    read_delay = float(config['update_interval_sec'])
    
    # initialize the fence station variables
    self.last_roof_data = []
    
    # create and run the fence station collector
    self.roofstation_collector = txrx.MPArrayReceiver(hostname, port, password, read_delay, self.roofstation_array)
    self.roofstation_collector.daemon = True  # run this process on its own until this process dies
    self.roofstation_collector.start()
    
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
    self.data['wind_speed_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Speed (mph)"]  # Roof Station
    self.data['wind_gust_mph'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Gust (mph)"]  # Roof Station
    self.data['wind_direction_deg'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Direction (true deg)"]  # Roof Station
    
    # from sensors
    self.data['inside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Humidity (%)"]
    self.data['outside_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outside Humidity (%)"]  # Fence Station
    self.data['inside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Inside Temperature (deg F)"]
    self.data['outside_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outside Temperature (deg F)"]  # Fence Station
    self.data['barometer_in'] = [29.92, "{:.2f},", "Sea Level Pressure (in Hg)"]  # Fence Station
    
    # from rain gauge
    self.data['total_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Total Rain (in)"]
    self.data['daily_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Daily Rain (in)"]
    self.data['hourly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Hourly Rain (in)"]  # Fence Station
    
    # from METAR
    self.data['sky_condition'] = [WxDataCollector.BAD_INT, "{:d},", "Sky Condition"] # METAR
    
    # from other various sources
    self.data['channel1_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temperature (deg F)"] # METAR
    self.data['channel1_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Humidity (%)"] # METAR
    self.data['channel2_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Temperature (deg F)"] # Roof Station CPU
    self.data['channel2_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Humidity (%)"]
    self.data['channel3_temp_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Temperature (deg F)"] # Fence Station CPU
    self.data['channel3_humidity_pct'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Humidity (%)"]
    
    # not used
    self.data['evapotransporation'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Evapotranspiration (in)"]
    self.data['uv_index'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "UV Index"]
    
    # from pyranometer
    self.data['solar_radiation'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Solar Radiation (W/m**2)"] # Roof Station
    
    # computed
    self.data['wind_chill_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Wind Chill (deg F)"]  # Fence Station and Roof Station
    self.data['indoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Heat Index (deg F)"]
    self.data['outdoor_heat_index_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Heat Index (deg F)"]  # Fence Station
    self.data['dew_point_degF'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Dew Point (deg F)"]  # METAR for now # Fence Station
    
    # rates from data
    self.data['rain_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Rain Rate (in/hr)"]  # Fence Station
    self.data['outdoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Outdoor Temp Rate (deg F/hr)"] # Fence Station
    self.data['indoor_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Indoor Temp Rate (deg F/hr)"]
    self.data['barometer_rate_in_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Barometer Rate"]  # Fence Station
    self.data['channel1_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch1 Temp Rate (deg F/hr)"]  # METAR
    self.data['channel2_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch2 Temp Rate (deg F/hr)"] # Roof Station
    self.data['channel3_temp_rate_degF_per_hour'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Ch3 Temp Rate (deg F/hr)"] # Fence Station
    
    # from rain gauge
    self.data['monthly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Monthly Rain (in)"]
    self.data['yearly_rain_in'] = [WxDataCollector.BAD_FLOAT, "{:.2f},", "Yearly Rain (in)"]
    
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
      
      # get the latest fence station data
      self._get_fence_station()
      
      # get the lastest roof station data
      self._get_roof_station()
            
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
      if value[0] != None:
        data_string += value[1].format(value[0])
      else:
        data_string += ","
    # remove the extra comma and replace with a newline
    header_string = header_string[:-1]
    header_string += "\n"
    data_string = data_string[:-1]
    data_string += "\n"
    
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
    now_utc = datetime.datetime.now(pytz.UTC)
    
    # convert to our local timezone
    timenow = now_utc.astimezone(self.timezone)
    
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
      temp = self.metar_array[:]
    
    # create a named tuple
    metar_data = self.METAR_DATA(*temp)
    
    # if the timestamp is zero, we have no data, so just return for now
    if round(metar_data.timestamp) == 0:
      return
    
    # if the timestamp didn't change, nothing changed, so we are done
    if self.last_metar != None and metar_data.timestamp == self.last_metar.timestamp:
      return
    
    # get some things in better units
    temp_f = wx.temp_c_to_f(metar_data.temp_c)
    #===========================================================================
    # dewpoint_f = wx.temp_c_to_f(metar_data.dewpoint_c)
    # wind_speed_mph = wx.speed_kt_to_mph(metar_data.wind_speed_kt)
    # gust_speed_mph = wx.speed_kt_to_mph(metar_data.wind_gust_kt)
    #===========================================================================
    
    # values we always want to get from the METAR data
    self.data['channel1_temp_degF'][0] = temp_f
    self.data['channel1_humidity_pct'][0] = metar_data.rh_pct
    self.data['sky_condition'][0] = round(metar_data.code)
    if self.last_metar != None and round(self.last_metar.timestamp) != 0:
      d_temp_f = temp_f - wx.temp_c_to_f(self.last_metar.temp_c)
      d_time_sec = metar_data.timestamp - self.last_metar.timestamp
      d_time_hr = d_time_sec/3600.0
      self.data['channel1_temp_rate_degF_per_hour'][0] = d_temp_f/d_time_hr
    else:
      self.data['channel1_temp_rate_degF_per_hour'][0] = 0.0
    
    # these values will be replaced with our sensors when available
    # self.data['wind_speed_mph'][0] = wind_speed_mph
    # self.data['wind_gust_mph'][0] = gust_speed_mph
    # self.data['wind_direction_deg'][0] = metar_data.wind_dir_deg
    
    # self.data['outdoor_heat_index_degF'][0] = wx.compute_heat_index(temp_f, metar_data.rh_pct)
    # self.data['dew_point_degF'][0] = dewpoint_f
    
    # self.data['outside_temp_degF'][0] = temp_f
    # self.data['outside_humidity_pct'][0] = metar_data.rh_pct
    
    # self.data['wind_chill_degF'][0] = wx.compute_wind_chill(temp_f, wind_speed_mph)
    
    # for now, compute the baro rate from the METAR data...it will be hard from our data because
    # the update rate is high
    #===========================================================================
    # if self.last_metar != None and round(self.last_metar.timestamp) != 0:
    #   d_press = metar_data.altim_in_hg - self.last_metar.altim_in_hg
    #   d_time_sec = metar_data.timestamp - self.last_metar.timestamp
    #   d_time_hr = d_time_sec/3600.0
    #   self.data['barometer_rate_in_per_hour'][0] = d_press/d_time_hr
    # else:
    #   self.data['barometer_rate_in_per_hour'][0] = 0.0
    #===========================================================================
    
    # save the data we need for the next update
    self.last_metar = metar_data
    
    return
  
  def _get_fence_station(self):
    # get the latest fencestation data
    with self.fencestation_array.get_lock():
      temp = self.fencestation_array[:]
    
    # build the named tuple
    fence_data = self.FENCE_DATA(*temp)
    
    # only proceed if we have real data
    if round(fence_data.timestamp) == 0:
      return
    
    # if the timestamp didn't change, nothing changed, so we are done
    if len(self.last_fence_data) != 0 and fence_data.timestamp == self.last_fence_data[-1].timestamp:
      return
    
    # now update our values
    self.data['outside_temp_degF'][0] = fence_data.temp_f
    self.data['outside_humidity_pct'][0] = fence_data.rh_pct
    self.data['outdoor_heat_index_degF'][0] = wx.compute_heat_index(fence_data.temp_f, fence_data.rh_pct)
    
    self.data['barometer_in'][0] = fence_data.press_inhg
    
    temp_c = wx.temp_f_to_c(fence_data.temp_f)
    dewpoint_c = wx.calc_dewpoint_c(temp_c, fence_data.rh_pct)
    self.data['dew_point_degF'][0] = wx.temp_c_to_f(dewpoint_c)
    
    self.data['channel3_temp_degF'][0] = fence_data.cpu_temp_f
    
    # compute the wind chill if we can
    if self.wind_speed_mph != None:
      self.data['wind_chill_degF'][0] = wx.compute_wind_chill(fence_data.temp_f, self.wind_speed_mph)
    
    datatime = datetime.datetime.fromtimestamp(fence_data.timestamp, tz=pytz.UTC)
    print("==========================================================================")
    print("Fence Station: {:s}".format(datatime.strftime("%Y-%m-%d %H:%M:%S.%f %Z")))
    print("Fence Station: Temperature (F):{:.2f} Humidity:{:.1f}".format(fence_data.temp_f, fence_data.rh_pct))
    print("Fence Station: Pressure (inHg):{:.2f} Sea-Level Pressure:{:.2f}".format(fence_data.press_inhg, fence_data.slp_inhg))
    print("Fence Station: Pressure Altitude:{:.1f} Density Altitude:{:.1f}".format(fence_data.pa_ft, fence_data.da_ft))
    print("Fence Station: New Rain:{:.2f} Total Rain:{:.2f}".format(fence_data.int_rain_in, fence_data.total_rain_in))
    print("Fence Station: CPU Temp:{:.2f} Sensor Temp:{:.2f}".format(fence_data.cpu_temp_f, fence_data.sensor_temp_f))
    
    # save this for next time
    self.last_fence_data.append(fence_data)
    
    # keep the last 60 minutes of data in memory
    self.last_fence_data = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 3600.0]
    
    # compute the length of our history
    history_sec = self.last_fence_data[-1].timestamp - self.last_fence_data[0].timestamp
    
    # only proceed if we have ~1 minutes or more of data
    if history_sec < 60.0:
      return
    
    # we have enough history data, compute our multiplier
    multiplier = 3600.0 / history_sec
    
    # build lists containing a specified amount of time
    sec060 = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 60.0]
    sec150 = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 150.0]
    sec300 = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 300.0]
    sec600 = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 600.0]
    sec900 = [d for d in self.last_fence_data if fence_data.timestamp-d.timestamp < 900.0]

    # get the temperature change rate
    temp900 = sec900[-1].temp_f - sec900[0].temp_f
    self.data['outdoor_temp_rate_degF_per_hour'][0] = temp900 * 4
    print("Fence Station: Outdoor Temperature Rate (degF/hr):{:.2f}".format(temp900*4))
    
    # find the amount of rain in each time period
    rain060 = sec060[-1].total_rain_in - sec060[0].total_rain_in
    rain150 = sec150[-1].total_rain_in - sec150[0].total_rain_in
    rain300 = sec300[-1].total_rain_in - sec300[0].total_rain_in
    rain600 = sec600[-1].total_rain_in - sec600[0].total_rain_in
    rain900 = sec900[-1].total_rain_in - sec900[0].total_rain_in
    rain_hr = self.last_fence_data[-1].total_rain_in - self.last_fence_data[0].total_rain_in
    
    if rain060 >= 0.02:
      rate = rain060 * 60
    elif rain150 >= 0.02:
      rate = rain150 * 24
    elif rain300 >= 0.02:
      rate = rain300 * 12
    elif rain600 >= 0.02:
      rate = rain600 * 6
    elif rain900 >= 0.02:
      rate = rain900 * 4
    else:
      rate = rain_hr * multiplier
    # set our hourly rain rate
    self.data['rain_rate_in_per_hour'][0] = rate
    print("Fence Station: Rain Rate (in/hr):{:.2f}".format(rate))
    
    # set the amount of hourly rain
    self.data['hourly_rain_in'][0] = rain_hr
    print("Fence Station: Rain in the last hour:{:.2f}".format(rain_hr))
    
    self.data['total_rain_in'][0] = self.last_fence_data[-1].total_rain_in # -self.last_fence_data[-2].total_rain_in # works
    self.data['daily_rain_in'][0] = self.last_fence_data[-1].daily_rain_in
    self.data['monthly_rain_in'][0] = self.last_fence_data[-1].monthly_rain_in
    self.data['yearly_rain_in'][0] = self.last_fence_data[-1].total_rain_in
    
    self.data['barometer_rate_in_per_hour'][0] = (sec900[-1].slp_inhg - sec900[0].slp_inhg)*4.0
    
    return
  
  def _get_roof_station(self):
    # get the latest fencestation data
    with self.roofstation_array.get_lock():
      temp = self.roofstation_array[:]
    
    # build the named tuple
    roof_data = self.ROOF_DATA(*temp)
    
    # only proceed if we have real data
    if round(roof_data.timestamp) == 0:
      return
    
    # if the timestamp didn't change, nothing changed, so we are done
    if len(self.last_roof_data) != 0 and roof_data.timestamp == self.last_roof_data[-1].timestamp:
      return
    
    # now update our values
    self.data['wind_direction_deg'][0] = roof_data.wind_direction
    self.data['wind_speed_mph'][0] = roof_data.wind_speed_mph
    self.data['wind_gust_mph'][0] = roof_data.wind_gust_mph
    self.data['solar_radiation'][0] = roof_data.solar_insolation
    self.data['channel2_temp_degF'][0] = roof_data.cpu_temp_f
    
    # save this for wind chill computations
    self.wind_speed_mph = roof_data.wind_speed_mph
    
    datatime = datetime.datetime.fromtimestamp(roof_data.timestamp, tz=pytz.UTC)
    print("==========================================================================")
    print("Roof Station: {:s}".format(datatime.strftime("%Y-%m-%d %H:%M:%S.%f %Z")))
    print("Roof Station: Direction:{:.2f} Speed:{:.2f} Gust:{:.2f}".format(roof_data.wind_direction, roof_data.wind_speed_mph, roof_data.wind_gust_mph))
    print("Roof Station: Solar Radiation:{:.2f}".format(roof_data.solar_insolation))
    print("Roof Station: CPU Temp:{:.2f}".format(roof_data.cpu_temp_f))
    
    # save this for next time
    self.last_roof_data.append(roof_data)
    
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
  
  config_file = "config.ini"
  
  while True:
    # this should never return
    wx_data_collector = WxDataCollector(config_file)
    
    # if we get here, give it a few seconds and restart
    time.sleep(10.0)
  
  
    
    
