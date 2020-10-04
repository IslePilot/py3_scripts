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
import bisect

def get_cases(text_list):
  key = 'Highcharts.chart(\'coronavirus-cases-linear\', {'
  return get_data(text_list, key)
def get_deaths(text_list):
  key = 'Highcharts.chart(\'coronavirus-deaths-linear\', {'
  return get_data(text_list, key)
def get_data(text_list, key):
  flag = 'data:'
  armed = False
  for line in text_list:
    if armed:
      if line.find(flag) >= 0:
        beg = line.find('[')
        end = line.find(']')
        return tuple(map(int, line[beg+1:end].split(',')))
    elif line.find(key) >= 0:
      armed = True
  return None
       
        

if __name__ == '__main__':
  # when this file is run directly, run this code
  page = requests.get('https://www.worldometers.info/coronavirus/country/us/')
  txt_list = page.text.splitlines(False)
  us_cases = get_cases(txt_list)
  index = bisect.bisect_left(us_cases, 500)
  us_cases = us_cases[index:]
  us_deaths = get_deaths(txt_list)[index:]
  us_len = len(us_cases)
  print("US completed.  Lines:", us_len)
  
  page = requests.get('https://www.worldometers.info/coronavirus/country/china/')
  txt_list = page.text.splitlines(False)
  china_cases = get_cases(txt_list)
  index = bisect.bisect_left(china_cases, 500)
  china_cases = china_cases[index:]
  china_deaths = get_deaths(txt_list)[index:]
  china_len = len(china_cases)
  print("China completed. Lines:", china_len)

  page = requests.get('https://www.worldometers.info/coronavirus/country/south-korea/')
  txt_list = page.text.splitlines(False)
  rok_cases = get_cases(txt_list)
  index = bisect.bisect_left(rok_cases, 500)
  rok_cases = rok_cases[index:]
  rok_deaths = get_deaths(txt_list)[index:]
  rok_len = len(rok_cases)
  print("ROK completed. Lines:", rok_len)
  
  page = requests.get('https://www.worldometers.info/coronavirus/country/italy/')
  txt_list = page.text.splitlines(False)
  italy_cases = get_cases(txt_list)
  index = bisect.bisect_left(italy_cases, 500)
  italy_cases = italy_cases[index:]
  italy_deaths = get_deaths(txt_list)[index:]
  italy_len = len(italy_cases)
  print("Italy completed. Lines:", italy_len)

  # get the colorado data
  #page = requests.get('https://opendata.arcgis.com/datasets/6811473e86fe4e2cb6af10d54c15ecee_0.csv')
  page = requests.get('https://opendata.arcgis.com/datasets/bd4ee19bc7fc4288a20db8d5a7bd2be2_0.csv')
  txt_list = page.text.splitlines(False)
  first = True
  co_cases = []
  co_deaths = []
  for line in txt_list:
    if first:
      # skip the header
      first = False
    else:
      data = line.split(',')
      if len(data[3]) > 0:
        cases = int(data[3])
        deaths = int(data[6])
        if cases > 500:
          co_cases.append(cases)
          co_deaths.append(deaths)
  co_len = len(co_cases)
  print("Colorado completed. Lines:", co_len)

  
  csv = open('c:\\Temp\\world_covid.csv', 'w')
  csv.write("china_cases,china_deaths,rok_cases,rok_deaths,italy_cases,italy_deaths,us_cases,us_deaths,co_cases,co_deaths\n")
  ch_done = False 
  rok_done = False 
  it_done = False 
  us_done = False
  co_done = False
  
  i=0
  while not ch_done or not rok_done or not it_done or not us_done:
    if i < china_len:
      csv.write("{},{},".format(china_cases[i], china_deaths[i]))
    else:
      csv.write(",,")
      ch_done = True
  
    if i < rok_len:
      csv.write("{},{},".format(rok_cases[i], rok_deaths[i]))
    else:
      csv.write(",,")
      rok_done = True
    
    if i < italy_len:
      csv.write("{},{},".format(italy_cases[i], italy_deaths[i]))
    else:
      csv.write(",,")
      it_done = True
    
    if i < us_len:
      csv.write("{},{},".format(us_cases[i], us_deaths[i]))
    else:
      csv.write(",,")
      us_done = True
    
    if i < co_len:
      csv.write("{},{},".format(co_cases[i], co_deaths[i]))
    else:
      csv.write(",,")
      co_done = True
    
    csv.write("\n")
    i+=1
  
  csv.close()
    
    
      
      
    
    
  
    
  
  print("Done")
  
  
  
  
