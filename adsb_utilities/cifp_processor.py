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
import __common.maptools as maptools

from collections import namedtuple
    
class CIFPReader:
  UC_DATA = namedtuple('UC_Data', 'airspace_type, airspace_center, airspace_classification,'\
                       ' multiple_code, sequence_number,'\
                       ' continuation_record_number, boundary_via, latitude, longitude,'\
                       ' arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing')
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
    
    if section_code == 'U':
      airport_icao_id = record[9:14].rstrip()
      subsection_code = record[5]
    elif section_code == 'P':
      airport_icao_id = record[6:10].rstrip()
      subsection_code = record[12]
    else:
      airport_icao_id = ''
      subsection_code = ''
    
    return (record_type, area_code, section_code, airport_icao_id, subsection_code)
  
  @staticmethod
  def parse_controlled_airspace(record):
    """parse a controlled airport record (UC)
    
    Types: A: Class C
           R: TRSA
           T: Class B
           Z: Class D
    
    Boundary Via: A: Arc by edge
                  C: Full circle
                  G: Great circle
                  H: Rhumb line
                  L: CCW Arc
                  R: CW Arc"""
    # SUSAUCK2ZKBJC PAD  A00100     CE                   N39543200W1050702000050       GND  A07999MDENVER                        473321703
    # SUSAUCK2ZKBKF PAD  A00100     R N39393650W104402500N39420630W10445071000441245   GND  A07499MAURORA                        473331703
    # SUSAUCK2ZKBKF PAD  A00200     G N39460130W104474270                                                                        473341703
    # SUSAUCK2ZKBKF PAD  A00300     G N39455530W104472450                                                                        473351703
    # SUSAUCK2ZKBKF PAD  A00400     G N39453560W104462610                                                                        473361703
    # SUSAUCK2ZKBKF PAD  A00500     G N39452270W104454850                                                                        473371703
    # SUSAUCK2ZKBKF PAD  A00600     G N39451240W104451840                                                                        473381703
    # SUSAUCK2ZKBKF PAD  A00700     G N39450370W104450200                                                                        473391703
    # SUSAUCK2ZKBKF PAD  A00800     G N39450000W104445630                                                                        473401703
    # SUSAUCK2ZKBKF PAD  A00900     G N39445390W104444630                                                                        473411703
    # SUSAUCK2ZKBKF PAD  A01000     G N39443000W104440480                                                                        473421703
    # SUSAUCK2ZKBKF PAD  A01100     GEN39442600W104435020                                                                        473431703
    # SUSAUCK2ZKBKF PAD  B01200     G N39442600W104435020                              GND  A06499MAURORA                        473441703
    # SUSAUCK2ZKBKF PAD  B01300     G N39442380W104434230                                                                        473451703
    # SUSAUCK2ZKBKF PAD  B01400     G N39442450W104425950                                                                        473461703
    # SUSAUCK2ZKBKF PAD  B01500     G N39442430W104414800                                                                        473471703
    # SUSAUCK2ZKBKF PAD  B01600     G N39442410W104402340                                                                        473481703
    # SUSAUCK2ZKBKF PAD  B01700     R N39442390W104401490N39420630W10445071000440586                                             473491703
    # SUSAUCK2ZKBKF PAD  B01800     GEN39393650W104402500                                                                        473501703
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    airspace_type = record[8]
    airspace_center = record[9:14].rstrip()
    airspace_classification = record[16]
    multiple_code = record[19]
    sequence_number = int(record[20:24])
    continuation_record_number = CIFPReader.parse_int(record[24])
    boundary_via = record[30:32]
    latitude = CIFPReader.parse_lat(record[32:41])
    longitude = CIFPReader.parse_lon(record[41:51])
    arc_origin_latitude = CIFPReader.parse_lat(record[51:60])
    arc_origin_longitude = CIFPReader.parse_lon(record[60:70])
    arc_distance = CIFPReader.parse_float(record[70:74], 10.0)
    arc_bearing = CIFPReader.parse_float(record[74:78], 10.0)

    return CIFPReader.UC_DATA(airspace_type, airspace_center, airspace_classification, multiple_code, 
                              sequence_number, continuation_record_number, boundary_via, latitude, longitude, 
                              arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing)
  
  @staticmethod
  def parse_vhf_navaid(record):
    """
    """
    # SUSAD        BJC   K2011540VDHW N39544695W105082035    N39544695W105082035E0110057372     NARJEFFCO                        228681605
    # SUSAD KACKK6 IACK  K6010910 ITW                    IACKN41144628W070043228W0160000120     NARNANTUCKET MEMORIAL            238471807
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    
    return
  
  
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
  def parse_float(fstr, divisor=1.0):
    # if fstr is empty we are done
    if fstr.strip() == "":
      return None
    return float(fstr)/divisor
  
  @staticmethod
  def parse_int(istr):
    # if istr is empty we are done
    if istr.strip() == "":
      return None
    return int(istr)
  
  @staticmethod
  def parse_lat(lat):
    # if lat is an empty string (just whitespace), we are done
    if lat.strip() == "":
      return None
    
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
    # if lon is an empty string (just whitespace), we are done
    if lon.strip() == "":
      return None
    
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
        if info[2] == 'P' and info[4] == 'A':
          airport = CIFPReader.parse_airport_primary_record(line)
          print(airport)
      
      if info[3] == "KBKF":
        if info[2] == 'U' and info[4] == 'C':
          uc_data = CIFPReader.parse_controlled_airspace(line)
          print(uc_data)
      
      if info[3] == "KBJC":
        if info[2] == 'U' and info[4] == 'C':
          uc_data = CIFPReader.parse_controlled_airspace(line)
          print(uc_data)
          points = maptools.circle((uc_data.arc_origin_latitude, uc_data.arc_origin_longitude), uc_data.arc_distance)
          outfile = open("c:\\temp\\{}_Class{}.out".format(uc_data.airspace_center, uc_data.airspace_classification), "w")
          outfile.write("{{{}_Class_{}}}\n".format(uc_data.airspace_center, uc_data.airspace_classification))
          outfile.write("$TYPE=6\n")
          
          for point in points:
            outfile.write("{:.6f}+{:.6f}\n".format(point[0], point[1]))
          outfile.write("-1\n")
          outfile.close()
        
        
      
    
  
