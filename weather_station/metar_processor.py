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

from multiprocessing import Process
from multiprocessing import Array

import urllib
import bs4 as bs


# define a version for this file
VERSION = "1.0.2018-05-26a"

class MetarCollector(Process):
  URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString="
  
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
      
      # now share the data
      with self.mp_array.get_lock():
        for i in range(len(data_tuple)):
          self.mp_array[i]=float(data_tuple[i])
      
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
    # raw_text: KBID 271456Z AUTO 06015G22KT 1 1/4SM -RA BR OVC002 12/12 A3010 RMK AO2 RAB24 SLP195 P0001 6//// T01220122 TSNO
    # visibility_statute_mi: 1.25
    # altim_in_hg: 30.100393

    
    # get the latest METAR and make soup
    soup = bs.BeautifulSoup(urllib.request.urlopen(self.url).read(), 'lxml')
        
    # get the items we need
    # show the user we read something
    raw_text = soup.find('raw_text').text
    print("MetarCollector: METAR Read:", raw_text)
    
    # get the data timestamp
    time_string = soup.find('observation_time').text
    obs_time = datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ") # 2018-05-27T19:17:00Z
    #print("Metar Time:", obs_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # get the temp, dewpoint, and relative humidity
    temp_c = float(soup.find('temp_c').text)
    dewpoint_c = float(soup.find('dewpoint_c').text)
    rh_pct = wx.calc_rh_pct(temp_c, dewpoint_c)
    #print("Temp:{:.1f} Dewpoint:{:.1f} Relative Humidity:{:.1f}".format(temp_c, dewpoint_c, rh_pct))
    
    # get the wind information
    wind_dir_deg = float(soup.find('wind_dir_degrees').text)
    wind_speed_kt = float(soup.find('wind_speed_kt').text)
    gust = soup.find('wind_gust_kt')
    if gust:
      wind_gust_kt = float(gust.text)
    else:
      wind_gust_kt = wind_speed_kt
    #print("Wind: {:.1f} at {:.1f} gusting {:.1f}".format(wind_dir_deg, wind_speed_kt, wind_gust_kt))
    
    # combine wx_string and sky condition into a single condition for VWS
    wx_str = soup.find('wx_string')
    if wx_str:
      # find the first 2 letter item
      condition = wx_str.text.split(" ")[0]
    else:
      # if no significant weather exists, use the sky cover
      condition = soup.find('sky_condition')['sky_cover']
    #print("Combined VWS Weather Condtion:", condition)
    
    # find the condition code
    code = vws.WxDataCollector.get_weather_condition_code(condition)
    
    # get other data of interest that we probably can't use with VWS
    visibility_statute_mi = float(soup.find('visibility_statute_mi').text)
    altim_in_hg = float(soup.find('altim_in_hg').text)
    
    #print("VWS Code:", code)
    
    return obs_time.timestamp(), temp_c, dewpoint_c, rh_pct, wind_dir_deg, wind_speed_kt, wind_gust_kt, code, visibility_statute_mi, altim_in_hg


if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # regardless of mode, define a few basics
  # create our shared memory object
  timearray = Array('f', 10)
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

