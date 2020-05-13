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

  May 12, 2020, ksb, created
"""

import sys
sys.path.append("..")

    
class CIFPReader:
  def __init__(self):
    return
  
  @staticmethod
  def get_record_info(record):
    """determine the record classification information
    
    record: CIFP string
    
    returns: tuple containing:(Record Type,
                               Area Code,
                               Section Code,
                               Airport ICAO Identifier,
                               Subsection Code)"""
    record_type = record[0]
    area_code = record[1:4]
    section_code = record[4]
    airport_icao_id = record[6:10].rstrip()
    subsection_code = record[12]
    
    return (record_type, area_code, section_code, airport_icao_id, subsection_code)
  
  @staticmethod
  def parse_airport_primary_record(record):
    """parse an airport primary record (Section 4.1.7.1)
    
    record: CIFP string containing a PA record
    
    returns: tuple containing:(Airport ICAO Identifier,
                               Airport Reference Point Latitude,
                               Airport Reference Point Longitude,
                               Magnetic Variation (W positive),
                               Airport Elevation,
                               Airport Name)"""
    # SUSAP KDENK2ADEN     0     160YHN39514200W104402340E008005434         1800018000C    MNAR    DENVER INTL                   599261208
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    icao_code = record[6:10].rstrip()
    lat = CIFPReader.parse_lat(record[32:41])
    lon = CIFPReader.parse_lon(record[41:51])
    var = CIFPReader.parse_variation(record[51:56])
    el = float(record[56:61])
    name = record[93:123].rstrip()
    
    return (icao_code, lat, lon, var, el, name)
  
  @staticmethod
  def parse_lat(lat):
    # 5.36
    # N39514200
    # 012345678
    hem = lat[0]
    deg = float(lat[1:3])
    mn = float(lat[3:5])
    sec = float(lat[5:])/100.0
    latitude = deg + mn/60.0 + sec/3600.0
    if hem == "S":
      latitude = -latitude
    return latitude
  
  @staticmethod
  def parse_lon(lon):
    # 5.37
    # W104402340
    # 0123456789
    hem = lon[0]
    deg = float(lon[1:4])
    mn = float(lon[4:6])
    sec = float(lon[6:])/100.0
    longitude = deg + mn/60.0 + sec/3600.0
    if hem == "W":
      longitude = -longitude
    return longitude
  
  @staticmethod
  def parse_variation(var):
    # 5.39
    # E0080
    # 01234
    hem = var[0]
    variation = float(var[1:])/10.0
    if hem == "E":
      variation = -variation
    return variation


# define a version for this file
VERSION = "1.0"

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  with open(r"C:\Data\CIFP\CIFP_200521\FAACIFP18", "r") as f:
    for line in f:
      info = CIFPReader.get_record_info(line)
      
      if info[3] == "KDEN":
        print(info)
      
        if info[2] == 'P' and info[4] == 'A':
          airport = CIFPReader.parse_airport_primary_record(line)
          print(airport)
        
      
    
  
