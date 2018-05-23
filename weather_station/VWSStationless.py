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

from collections import OrderedDict

# define a version for this file
VERSION = "1.0.20180522a"

class StationlessCSV():
  BAD_INT = -999
  BAD_FLOAT = -999.9
  
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
  
  def __init__(self):
    self.data = OrderedDict() # native units
    self.data2 = OrderedDict()  # user units
    
    return
  
  def build_data_dict(self):
    self.data['version'] = 1.0
    
    # from timestamp
    self.data['year'] = StationlessCSV.BAD_INT
    self.data['month'] = StationlessCSV.BAD_INT
    self.data['day'] = StationlessCSV.BAD_INT
    self.data['hour'] = StationlessCSV.BAD_INT
    self.data['minute'] = StationlessCSV.BAD_INT
    self.data['second'] = StationlessCSV.BAD_INT
    
    # from anemometer and vane
    self.data['wind_speed_mph'] = StationlessCSV.BAD_FLOAT
    self.data['wind_gust_mph'] = StationlessCSV.BAD_FLOAT
    self.data['wind_direction_deg'] = StationlessCSV.BAD_FLOAT
    
    # from sensors
    self.data['inside_humidity_pct'] = StationlessCSV.BAD_FLOAT
    self.data['outside_humidity_pct'] = StationlessCSV.BAD_FLOAT
    self.data['inside_temp_degF'] = StationlessCSV.BAD_FLOAT
    self.data['outside_temp_degF'] = StationlessCSV.BAD_FLOAT
    self.data['barometer_in'] = StationlessCSV.BAD_FLOAT
    
    # from rain gauge
    self.data['total_rain_in'] = StationlessCSV.BAD_FLOAT
    self.data['daily_rain_in'] = StationlessCSV.BAD_FLOAT
    self.data['hourly_rain_in'] = StationlessCSV.BAD_FLOAT
    
    # from METAR
    self.data['sky_condition'] = StationlessCSV.BAD_INT
    
    # from system
    self.data['channel1_temp_degF'] = StationlessCSV.BAD_FLOAT
    self.data['channel1_humidity_pct'] = StationlessCSV.BAD_FLOAT
    self.data['channel2_temp_degF'] = StationlessCSV.BAD_FLOAT
    self.data['channel2_humidity_pct'] = StationlessCSV.BAD_FLOAT
    self.data['channel3_temp_degF'] = StationlessCSV.BAD_FLOAT
    self.data['channel3_humidity_pct'] = StationlessCSV.BAD_FLOAT
    
    # not used
    self.data['evapotransporation'] = StationlessCSV.BAD_FLOAT
    self.data['uv_index'] = StationlessCSV.BAD_FLOAT
    
    # from pyranometer
    self.data['solar_radiation'] = StationlessCSV.BAD_FLOAT
    
    # computed
    self.data['wind_chill_degF'] = StationlessCSV.BAD_FLOAT
    self.data['indoor_heat_index_degF'] = StationlessCSV.BAD_FLOAT
    self.data['outdoor_heat_index_degF'] = StationlessCSV.BAD_FLOAT
    self.data['dew_point_degF'] = StationlessCSV.BAD_FLOAT
    
    # rates from data
    self.data['rain_rate_in_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['outdoor_temp_rate_degF_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['indoor_temp_rate_degF_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['barometer_rate_in_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['channel1_temp_rate_degF_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['channel2_temp_rate_degF_per_hour'] = StationlessCSV.BAD_FLOAT
    self.data['channel3_temp_rate_degF_per_hour'] = StationlessCSV.BAD_FLOAT
    
    # from rain gauge
    self.data['monthly_rain_in'] = StationlessCSV.BAD_FLOAT
    self.data['yearly_rain_in'] = StationlessCSV.BAD_FLOAT
    
    return
    
    
    
        
if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
    
    
