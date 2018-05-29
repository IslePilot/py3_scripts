#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-26, ksb, created
"""

import weather_computations as wx
import VWSStationless as vws

import datetime
import time
import pytz

from multiprocessing import Process
from multiprocessing import Array

import urllib
import bs4 as bs

from collections import namedtuple

# define a version for this file
VERSION = "1.0.2018-05-26a"

class MetarCollector(Process):
  BAD_FLOAT = -99999.999
  
  URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString="
  
  # create our METAR named tuple
  field_names = ['raw_text']
  field_names.append('station_id')  # four character alpha numeric
  field_names.append('observation_time')  # timezone aware datetime object
  field_names.append('latitude')
  field_names.append('longitude')
  field_names.append('temp_c')
  field_names.append('dewpoint_c')
  field_names.append('wind_dir_degrees')  # 0 degrees indicates variable
  field_names.append('wind_speed_kt')
  field_names.append('wind_gust_kt')
  field_names.append('visibility_statute_mi')
  field_names.append('altim_in_hg')
  field_names.append('sea_level_pressure_mb')
  field_names.append('wx_string')
  field_names.append('sky_cover_1')
  field_names.append('cloud_base_ft_agl_1')
  field_names.append('sky_cover_2')
  field_names.append('cloud_base_ft_agl_2')
  field_names.append('sky_cover_3')
  field_names.append('cloud_base_ft_agl_3')
  field_names.append('sky_cover_4')
  field_names.append('cloud_base_ft_agl_4')
  field_names.append('flight_category')
  field_names.append('three_hr_pressure_tendency_mb')
  field_names.append('maxT_c')  # max temp in past 6 hours
  field_names.append('minT_c')  # min temp in past 6 hours
  field_names.append('maxT24hr_c')  # max temp in past 24 hours
  field_names.append('minT24hr_c')  # min temp in past 24 hours
  field_names.append('precip_in') # precip since last METAR
  field_names.append('pcp3hr_in') # precip in past 3 hours
  field_names.append('pcp6hr_in') # precip in past 6 hours
  field_names.append('pcp24hr_in') # precip in past 24 hours
  field_names.append('snow_in') # snow depth on ground
  field_names.append('vert_vis_ft') # vertical visibility
  field_names.append('metar_type')
  field_names.append('elevation_m')
  METAR = namedtuple('METAR', field_names)
  
  def __init__(self, mp_array, station_id, countdown = False):
    """Instance a sample data collector.  This sample simply reads the local clock.
    
    mp_array: shared data multiprocessing.Array object"""
    # save our input
    self.mp_array = mp_array  # this is shared memory, so use locks when operating on it
    self.countdown = countdown
    
    # build our URL
    self.url = "{:s}{:s}".format(self.URL, station_id)
    
    # run the base class constructor
    super().__init__()
    return
  
  def run(self):
    """Main Receiver Loop.  Oveloaded multiprocessing.Process.run()"""
    while True:
      # get a timestamp
      timenow = datetime.datetime.utcnow()
      print(timenow.strftime("Getting METAR Data at %Y-%m-%d %H:%M:%S.%f:"))
      # get the latest METAR and parse it
      data_tuple = self.get_latest_metar()
      
      # compute a few items
      # if we don't have a gust, use the normal wind
      if data_tuple.wind_gust_kt:
        gust = float(data_tuple.wind_gust_kt)
      else:
        gust = float(data_tuple.wind_speed_kt)
      
      # determine the most significant weather
      if data_tuple.wx_string != None:
        code = vws.WxDataCollector.get_weather_condition_code(data_tuple.wx_string.split(' ')[0])
      else:
        code = vws.WxDataCollector.get_weather_condition_code(data_tuple.sky_cover_1)
      
      # now share the data
      with self.mp_array.get_lock():
        # save the data needed for VWS:
        self.mp_array[0] = data_tuple.observation_time.timestamp()
        self.mp_array[1] = data_tuple.temp_c
        self.mp_array[2] = data_tuple.dewpoint_c
        self.mp_array[3] = wx.calc_rh_pct(data_tuple.temp_c, data_tuple.dewpoint_c)
        self.mp_array[4] = float(data_tuple.wind_dir_degrees)
        self.mp_array[5] = float(data_tuple.wind_speed_kt)
        self.mp_array[6] = gust
        self.mp_array[7] = code
        self.mp_array[8] = data_tuple.altim_in_hg
      
      # countdown to the next update
      if self.countdown:
        delay = 300
        while delay > 0:
          print("Time until next update: {:d} seconds".format(delay), end='\r', flush=True)
          time.sleep(1)
          delay -= 1
      else:
        time.sleep(300)

    return
  
  def get_latest_metar(self):
    """Get the latest METAR data.
    
    returns a Metar Named Tuple"""
    # get our web data
    sauce = None
    while sauce == None:
      try:
        with urllib.request.urlopen(self.url, timeout=15) as response:
          sauce = response.read()
      except urllib.error.URLError as err:
        print("MetarCollector.get_latest_metar: URLError")
        print(err)
        time.sleep(15)
      except:
        print("MetarCollector.get_latest_metar: Timeout")
        time.sleep(15)
    
    # now make soup with our sauce
    soup = bs.BeautifulSoup(sauce, 'lxml')
    
    # get the items we need
    data = []
    data.append(self.search_soup(soup, 'raw_text', 'string', show=True))
    data.append(self.search_soup(soup, 'station_id', 'string', show=False))
    data.append(self.search_soup(soup, 'observation_time', 'utc', show=False))
    data.append(self.search_soup(soup, 'latitude', 'float', show=False))
    data.append(self.search_soup(soup, 'longitude', 'float', show=False))
    data.append(self.search_soup(soup, 'temp_c', 'float', show=False))
    data.append(self.search_soup(soup, 'dewpoint_c', 'float', show=False))
    data.append(self.search_soup(soup, 'wind_dir_degrees', 'int', show=False))
    data.append(self.search_soup(soup, 'wind_speed_kt', 'int', show=False))
    data.append(self.search_soup(soup, 'wind_gust_kt', 'int', show=False))
    data.append(self.search_soup(soup, 'visibility_statute_mi', 'float', show=False))
    data.append(self.search_soup(soup, 'altim_in_hg', 'float', show=False))
    data.append(self.search_soup(soup, 'sea_level_pressure_mb', 'float', show=False))
    data.append(self.search_soup(soup, 'wx_string', 'string', show=False))
    data += self.search_soup(soup, 'sky_condition', 'attrib', show=False)
    data.append(self.search_soup(soup, 'flight_category', 'string', show=False))
    data.append(self.search_soup(soup, 'three_hr_pressure_tendency_mb', 'float', show=False))
    data.append(self.search_soup(soup, 'maxT_c', 'float', show=False))
    data.append(self.search_soup(soup, 'minT_c', 'float', show=False))
    data.append(self.search_soup(soup, 'maxT24hr_c', 'float', show=False))
    data.append(self.search_soup(soup, 'minT24hr_c', 'float', show=False))
    data.append(self.search_soup(soup, 'precip_in', 'float', show=False))
    data.append(self.search_soup(soup, 'pcp3hr_in', 'float', show=False))
    data.append(self.search_soup(soup, 'pcp6hr_in', 'float', show=False))
    data.append(self.search_soup(soup, 'pcp24hr_in', 'float', show=False))
    data.append(self.search_soup(soup, 'snow_in', 'float', show=False))
    data.append(self.search_soup(soup, 'vert_vis_ft', 'int', show=False))
    data.append(self.search_soup(soup, 'metar_type', 'string', show=False))
    data.append(self.search_soup(soup, 'elevation_m', 'float', show=False))
    
    # return our named tuple
    return MetarCollector.METAR(*data)
  
  def search_soup(self, soup, tag, fmt, show=False):
    # get our item(s)
    if fmt == 'attrib':
      items = soup.find_all(tag)
    else:
      # look for our item
      item = soup.find(tag)
      
      # if we didn't find anything, then we are done, otherwise get the data
      if item == None:
        if show:
          print("{:s}:".format(tag), "None")
        return None
      else:
        text = item.text
    
    # now process the data based on our format
    if fmt == 'string':
      if show:
        print("{:s}:".format(tag), text)
      return text
    
    elif fmt == 'utc':
      # this is a time string, parse it into an aware datetime, example: 2018-05-27T19:17:00Z
      obs_time = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
      if show:
        print("{:s}:".format(tag), obs_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
      return obs_time
    
    elif fmt == 'float':
      val = float(text)
      if show:
        print("{:s}:".format(tag), val)
      return val
    
    elif fmt == 'int':
      val = int(text)
      if show:
        print("{:s}:".format(tag), val)
      return val
    
    elif fmt == 'attrib':
      data = []
      for item in items:
        data.append(item['sky_cover'])
        if data[-1] != 'CLR' and data[-1] != 'SKC' and data[-1] != 'CAVOK':
          data.append(float(item['cloud_base_ft_agl']))
        else:
          data.append(None)
      # pad the rest of data with None
      for i in range(len(items), 4):
        i=i # noop to get rid of unused variable warning
        data.append(None) # missing sky cover
        data.append(None) # missing cloud base
      
      if show:
        print("{:s} 1:".format(tag), data[0], data[1])
        print("{:s} 2:".format(tag), data[2], data[3])
        print("{:s} 3:".format(tag), data[4], data[5])
        print("{:s} 4:".format(tag), data[6], data[7])

      return data
    
    else:
      print('MetarCollector.search_soup: Unknown format Requested')

    return None

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # regardless of mode, define a few basics
  # create our shared memory object
  timearray = Array('f', 9)
  read_delay = 15.0  # delay between network reads
  metar_station = 'KEIK'
    
  # DATA GATHERER/SERVER MODE
  # instance our collector object  (Data Gatherer)
  timecollector = MetarCollector(timearray, metar_station, countdown = True)
  timecollector.daemon = True     # run this process on its own until this process dies
  timecollector.start()
  
  # regardless of type, we want to monitor what is in our shared object
  while True:
    # show the user what we got
    with timearray.get_lock():
      data_tuple = timearray[:]
    
    print("Test Loop read:", data_tuple)
    
    # wait a bit
    time.sleep(read_delay)

