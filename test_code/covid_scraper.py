#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2020 (C) AeroSys Engineering, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

************************************************************************************

Revision History:

  Jun 25, 2020, ksb, created
"""

import requests
from datetime import datetime




class CountryData:
  def __init__(self, country):
    link = 'https://www.worldometers.info/coronavirus/country/{}/'.format(country)
    
    # get the webpage data
    page = requests.get(link)
    
    # split the page into lines
    self.text_list = page.text.splitlines(False)
    
    # get the case data
    dates, data = self.get_data("Highcharts.chart(\'coronavirus-cases-linear\', {")
    self.case_data = dict(zip(dates, data))
    
    # get the death data
    dates, data = self.get_data("Highcharts.chart('coronavirus-deaths-linear', {")
    self.death_data = dict(zip(dates, data))
    
    # build the data list
    self.build_data_list()
    
    return
  
  def build_data_list(self):
    self.data = []
    for date in self.case_data:
      self.data.append('{},{},{}'.format(date, self.case_data[date], self.death_data[date]))
    return
  
  def len(self):
    return(len(self.data))
    
  def get_data(self, key):
    txt = self.parse_data(key, 'categories:')
    txts = txt[1:-1].split('","')
    dates = self.convert_dates(txts)
    
    txt = self.parse_data(key, 'data:')
    data = tuple(map(int, txt.split(',')))
    
    return dates, data
  
  def parse_data(self, key, flag):
    armed = False
    for line in self.text_list:
      if armed:
        if line.find(flag) >= 0:
          beg = line.find('[')
          end = line.find(']')
          return line[beg+1:end]
      elif line.find(key) >= 0:
        armed = True
    return None
  
  def convert_dates(self, date_list):
    dates = []
    for txt in date_list:
      dates.append(datetime.strptime(txt, '%b %d, %Y').strftime("%m/%d/%Y"))
    return dates
       
        

if __name__ == '__main__':
  # when this file is run directly, run this code
  us = CountryData('us')
  print("US completed. Lines: {}".format(us.len()))
  
  china = CountryData('china')
  print("China completed. Lines: {}".format(china.len()))
  
  rok = CountryData('south-korea')
  print("ROK completed. Lines: {}".format(rok.len()))
  
  italy = CountryData('italy')
  print("Italy completed. Lines: {}".format(italy.len()))

  # get the colorado data
  #https://data-cdphe.opendata.arcgis.com/datasets/cdphe-covid19-daily-state-statistics-1
  #https://data-cdphe.opendata.arcgis.com/datasets/cdphe-colorado-covid19-daily-state-statistics
  page = requests.get('https://opendata.arcgis.com/datasets/80193066bcb84a39893fbed995fc8ed0_0.csv')
  txt_list = page.text.splitlines(False)
  first = True
  co_data = []
  for line in txt_list:
    if first:
      # skip the header
      first = False
    else:
      data = line.split(',')
      if len(data[3]) > 0:
        date = data[2]
        cases = int(data[3])
        deaths = int(data[6])
        co_data.append("{},{},{}".format(date, cases, deaths))
  co_len = len(co_data)
  print("Colorado completed. Lines:", co_len)

  
  csv = open('c:\\Temp\\world_covid.csv', 'w')
  csv.write("china_dates,china_cases,china_deaths,rok_dates,rok_cases,rok_deaths,italy_dates,italy_cases,italy_deaths,us_dates,us_cases,us_deaths,co_dates,co_cases,co_deaths\n")
  ch_done = False 
  rok_done = False 
  it_done = False 
  us_done = False
  co_done = False
  
  i=0
  while not ch_done or not rok_done or not it_done or not us_done:
    if i < china.len():
      csv.write("{},".format(china.data[i]))
    else:
      csv.write(",,,")
      ch_done = True
  
    if i < rok.len():
      csv.write("{},".format(rok.data[i]))
    else:
      csv.write(",,,")
      rok_done = True
    
    if i < italy.len():
      csv.write("{},".format(italy.data[i]))
    else:
      csv.write(",,,")
      it_done = True
    
    if i < us.len():
      csv.write("{},".format(us.data[i]))
    else:
      csv.write(",,,")
      us_done = True
    
    if i < co_len:
      csv.write("{},".format(co_data[i]))
    else:
      csv.write(",,,")
      co_done = True
    
    csv.write("\n")
    i+=1
  
  csv.close()
    

  print("Done")
  
  
  
  
