#!/usr/bin/python3

"""
Copyright 2023 (C) AeroSys Engineering, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Revision History:
  2023-12-26, ksb, created
"""

import sys
sys.path.append("..")
import __common.mparray_transmitter as txrx

import time
import datetime
import pytz
import signal

import socket
import json

import configparser
from multiprocessing import Array

import weather_computations as wxcomp

# define a version for this file
VERSION = "1.0.20231227a"

class WeatherTempest():
  def __init__(self, station_elevation_ft):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('', 50222))
    
    self.z_ft = station_elevation_ft
    
    self.timestamp = None
    self.wind_speed_3sec_mph = 0.0
    self.wind_direction_3sec_deg = 0.0
    self.wind_lull_1min_mph = 0.0
    self.wind_speed_1min_mph = 0.0
    self.wind_gust_1min_mph = 0.0
    self.wind_direction_1min_deg = 0.0
    self.press_inhg = 0.0
    self.slp_inhg = 0.0
    self.pa_ft = 0.0
    self.da_ft = 0.0
    self.temp_f = 0.0
    self.rh_pct = 0.0
    self.solar_illuminance_lux = 0.0
    self.uv_index = 0.0
    self.solar_irradiance_wpm2 = 0.0
    self.last_minute_rain_in = 0.0
    self.lightning_distance_miles = 0
    self.lightning_count = 0
    self.battery_v = 0
    
    self.new_rain = False
    
    return 
  
  def get_new_rain(self):
    if self.new_rain == True:
      print(">>>>>>>>>>> New Rain Detected: {} inches <<<<<<<<<<<".format(self.last_minute_rain_in))
      self.new_rain = False 
      return self.last_minute_rain_in
    else:
      return 0.0
    
  def get_data(self):
    # get the next packet available
    m = self.sock.recvfrom(1024)
    
    # get the transmitter info
    #ip, port = m[1]
    #print("Packet Received from {}:{}".format(ip, port))
    
    # parse the data
    wx_dict = json.loads(m[0])
  
    if wx_dict['type'] == 'rapid_wind':
      rapid_wind_obs_list = wx_dict['ob']
      self.timestamp = datetime.datetime.fromtimestamp(rapid_wind_obs_list[0])
      self.wind_speed_3sec_mph = rapid_wind_obs_list[1]*2.236936292 # from m/s to mph
      self.wind_direction_3sec_deg = rapid_wind_obs_list[2]
      if False:
        print("Rapid Wind Observation")
        print("----------------------")
        print("     Time: {}".format(self.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        print("    Speed: {:.1f} mph".format(self.wind_speed_3sec_mph))
        print("      Dir: {} deg".format(self.wind_direction_3sec_deg))
        
    elif wx_dict['type'] == 'obs_st':
      # parse the data and fix units
      obs_list = wx_dict['obs'][0]
      self.timestamp = datetime.datetime.fromtimestamp(obs_list[0])
      self.wind_lull_1min_mph = obs_list[1]*2.236936292 # from m/s to mph
      self.wind_speed_1min_mph = obs_list[2]*2.236936292 # from m/s to mph
      self.wind_gust_1min_mph = obs_list[3]*2.236936292 # from m/s to mph
      self.wind_direction_1min_deg = obs_list[4]
      self.temp_f = wxcomp.temp_c_to_f(obs_list[7])
      obs_wind_interval = obs_list[5]
      self.press_inhg = obs_list[6]/33.8639 # from mbar to inHg
      self.slp_inhg = wxcomp.compute_slp_from_station(self.press_inhg, self.z_ft, obs_list[7])-0.02 # Calibration Factor
      self.pa_ft = wxcomp.compute_pressure_altitude(self.slp_inhg, self.z_ft)
      self.da_ft = wxcomp.compute_density_altitude(self.press_inhg, self.temp_f)
      self.rh_pct = obs_list[8]
      self.solar_illuminance_lux = obs_list[9]
      self.uv_index = obs_list[10]
      self.solar_irradiance_wpm2 = obs_list[11]
      self.last_minute_rain_in = obs_list[12]/25.4
      obs_rain_type = obs_list[13]
      self.lightning_distance_miles = obs_list[14]/1.609344
      self.lightning_count = obs_list[15]
      self.battery_v = obs_list[16]
      obs_rep_interval = obs_list[17]
      if False:
        print("Weather Observation")
        print("-------------------")
        print("           Time: {}".format(self.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        print("      Wind Lull: {} mph".format(self.wind_lull_1min_mph))
        print("     Wind Speed: {:.1f} mph".format(self.wind_speed_1min_mph))
        print("      Wind Gust: {:.1f} mph".format(self.wind_gust_1min_mph))
        print("       Wind Dir: {} deg".format(self.wind_direction_1min_deg))
        print("       Wind Int: {} seconds".format(obs_wind_interval))
        print("       Pressure: {} inHg".format(self.press_inhg))
        print("    Temperature: {} F".format(self.temp_f))
        print("       Humidity: {}%".format(self.rh_pct))
        print("    Illuminance: {} Lux".format(self.solar_illuminance_lux))
        print("             UV: {} Index".format(self.uv_index))
        print("Solar Radiaiton: {} W/m2".format(self.solar_irradiance_wpm2))
        print("  Last Min Rain: {} in".format(self.last_minute_rain_in))
        print("      Rain Type: {}".format(obs_rain_type))
        print("Strike Distance: {} sm".format(self.lightning_distance_miles))
        print("   Strike Count: {}".format(self.lightning_count))
        print("        Battery: {} V".format(self.battery_v))
        print("Report Interval: {} minutes".format(obs_rep_interval))
      
      if self.last_minute_rain_in > 0.001:
        self.new_rain = True 
      
  #=============================================================================
  #   elif wx_dict['type'] == 'hub_status':
  #     pass
  #     hub_fw = wx_dict['firmware_revision']
  #     hub_uptime = wx_dict['uptime']
  #     hub_rssi = wx_dict['rssi']
  #     hub_time = datetime.datetime.fromtimestamp(wx_dict['timestamp'])
  #     hub_seq = wx_dict['seq']
  #     if False:
  #       print("Hub Status")
  #       print("----------")
  #       print("    Time: {}".format(hub_time.strftime("%Y-%m-%d %H:%M:%S")))
  #       print("  Uptime: {} seconds".format(hub_uptime))
  #       print("      FW: {}".format(hub_fw))
  #       print("    RSSI: {}".format(hub_rssi))
  #       print("     Seq: {}".format(hub_seq))
  # 
  #   elif wx_dict['type'] == 'device_status':
  #     pass
  #     dev_time = datetime.datetime.fromtimestamp(wx_dict['timestamp'])
  #     dev_uptime = wx_dict['uptime']
  #     dev_voltage = wx_dict['voltage']
  #     dev_fw = wx_dict['firmware_revision']
  #     dev_rssi = wx_dict['rssi']
  #     dev_hrssi = wx_dict['hub_rssi']
  #     dev_status = wx_dict['sensor_status'] & 0b111111111
  #     if False:
  #       print(wx_dict)
  #       print("Device Status")
  #       print("-------------")
  #       print("    Time: {}".format(dev_time.strftime("%Y-%m-%d %H:%M:%S")))
  #       print("  Uptime: {}".format(dev_uptime))
  #       print("      FW: {}".format(dev_fw))
  #       print(" Voltage: {} V".format(dev_voltage))
  #       print("    RSSI: {}".format(dev_rssi))
  #       print("Hub RSSI: {}".format(dev_hrssi))
  #       if(dev_status == 0):
  #         print("  Status: OKAY")
  #       else:
  #         print("  Status: FAIL: {:b}".format(dev_status))
  #     
  #   elif wx_dict['type'] == 'evt_precip':
  #     rain_start_time = datetime.datetime.fromtimestamp(wx_dict['evt'][0])
  #     if False:
  #       print("Rain Event Start: {}".format(rain_start_time.strftime("%Y-%m-%d %H:%M:%S")))
  #       
  #   elif wx_dict['type'] == 'evt_strike':
  #     lightning_evt = wx_dict['evt']
  #     lightning_time = datetime.datetime.fromtimestamp(lightning_evt[0])
  #     lightning_distance = lightning_evt[1]
  #     lightning_energy = lightning_evt[2]
  #     if False:
  #       print("Lightning Strike")
  #       print("----------------")
  #       print("      Time: {}".format(lightning_time.strftime("%Y-%m-%d %H:%M:%S")))
  #       print("  Distance: {} km".format(lightning_distance))
  #       print("    Energy: {}".format(lightning_energy))
  #   
  #   else:
  #     print(wx_dict)
  #=============================================================================


def signal_handler(__signal, __frame):
  """Called by the signal handler when Control C is pressed"""
  print("TempestReader.py:  You pressed Ctrl-c.  Exiting.")
  # set the flag to terminate the rain gauge monitoring thread, and wait for it to close
  time.sleep(1.0)
  
  # exit cleanly
  sys.exit(0)


# trap Control C presses and call the signal handler
signal.signal(signal.SIGINT, signal_handler)


def new_rain_file(new_rain):
  """build a new rain file"""
  # buld our filename
  timenow = datetime.datetime.now()
  # this is a local time!
  current_year = timenow.year
  rain_file = "C:\\WX\\RainData\\{:d}_RainTotal.txt".format(current_year)

  try:
    with open(rain_file, "w") as rf:
      rf.write("AUTOGENERATED FILE...DO NOT EDIT\n")
      rf.write("Time (Local),Yearly Rain (in),Monthly Rain (in),Daily Rain (in)\n")
  except IOError as err:
      print("Unable to build new rain file: {:s}".format(err))
      return

  # add a starting line of data
  save_new_rain_total(new_rain, new_rain, new_rain, new_rain)
  
  return 


def get_rain_total():
  # get our annual total rain
  # buld our filename
  timenow = datetime.datetime.now()
  # this is a local time
  current_year = timenow.year
  rain_file = "C:\\WX\\RainData\\{:d}_RainTotal.txt".format(timenow.year)
  total_rain_in = 0.0
  monthly_rain_in = 0.0
  daily_rain_in = 0.0
  
  # open the rain file if it exists
  try:
    with open(rain_file, "r") as rf:
      contents = rf.read()

    # we need the last line with actual data
    lines = contents.split('\n')
    line = [l for l in lines if len(l) >= 20][-1]
    print(line)

    # parse the line to get the rain
    rain_data = line.split(',')
    print("Rain Totals: Last Update:{:s} Year Total:{:s}, Month Total:{:s}, Day Total:{:s}".format(*rain_data))
    
    # find out when the last data was added
    # if we call this between UTC midnight and local midnight we will be off for the day potentially
    last_time = datetime.datetime.strptime(rain_data[0], '%Y-%m-%d %H:%M:%S.%f')
    
    if timenow.year == last_time.year and \
       timenow.month == last_time.month and \
       timenow.day == last_time.day:
      daily_rain_in = float(rain_data[-1])
    else:
      daily_rain_in = 0.0
    
    if timenow.year == last_time.year and \
       timenow.month == last_time.month:
      monthly_rain_in = float(rain_data[-2])
    else:
      monthly_rain_in = 0.0
    
    total_rain_in = float(rain_data[-3])
    
  except IOError as err:
    print("Unable to open rain file: {}".format(err))

    # if the file did not exist, build it
    if err.errno == 2:
      new_rain_file(0.0)

    # default to zero
    total_rain_in = 0.0
    daily_rain_in = 0.0

  return current_year, total_rain_in, monthly_rain_in, daily_rain_in


def save_new_rain_total(total_rain_in, new_rain_in, daily_rain_in, monthly_rain_in):
  """This adds new rain to the total file...only call when adding new rain"""
  # buld our filename
  timenow = datetime.datetime.now()
  rain_file = "C:\\WX\\RainData\\{:d}_RainTotal.txt".format(timenow.year)

  # build our new value
  data_string = "{:s},{:.2f},{:.2f},{:.2f}\n".format(timenow.strftime("%Y-%m-%d %H:%M:%S.%f"), total_rain_in, monthly_rain_in, daily_rain_in)
  print("Adding to rain file: {:s}".format(data_string))
  
  # append the string to the file
  try:
    with open(rain_file, "a") as rf:
      rf.write(data_string)
  except IOError as err:
    print("Unable to write to rain file: {:s}".format(err))

    # if the file doesn't exist, the year may have rolled over
    if err.errno == 2:
      # build a new file
      new_rain_file(new_rain_in)

  return
  

# only run main if this is called directly
if __name__ == '__main__':
  # add the GPL license output
  print("Copyright (C) 2023 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")
  print("Version: ", VERSION)

  # parse the config file
  config = configparser.ConfigParser()
  config.read('C:\\py3_scripts\\weather_station\\config.ini')

  hostname = config['WEATHER_TEMPEST']['host']
  port = int(config['WEATHER_TEMPEST']['port'])
  authkey = config['WEATHER_TEMPEST']['authkey'].encode()
  z_ft = float(config['WEATHER_TEMPEST']['station_elevation_ft'])

  print(hostname, port, authkey, z_ft)

  # initialize our daily rain
  rain_today = 0.0
  monthly_rain = 0.0
  today = datetime.datetime.now()  # use local time
  
  # create our time base (UNIX time)
  epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)

  # create a shared array of doubles
  data = Array('d', 20)

  dataserver = txrx.MPArrayServer(hostname, port, authkey, data)
  dataserver.daemon = True  # run until this process dies
  dataserver.start()

  # start here
  tempest = WeatherTempest(z_ft)
    
  current_year, total_rain_in, monthly_rain_in, daily_rain_in, = get_rain_total()
  if daily_rain_in > 0:
    rain_today = daily_rain_in
  if monthly_rain_in > 0:
    monthly_rain = monthly_rain_in
  annual_rain = total_rain_in

  # main loop
  while True:
    # get a timestamp
    timenow = datetime.datetime.now(pytz.UTC)
    local_timenow = datetime.datetime.now()
    str_time = timenow.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    
    # if the day changed, we need to reset rain
    if today.day != local_timenow.day:
      # the day changed
      rain_today = 0.0
      
      # if the month changed, we need to reset the monthly total
      if today.month != local_timenow.month:
        monthly_rain = 0.0
      
      # if the year changed, we need to reset the annual total
      if today.year != local_timenow.year:
        annual_rain = 0.0
      
      today = local_timenow
    
    # read the data
    tempest.get_data()
    
    # get the rain (if any)
    interval_rain_in = tempest.get_new_rain()

    annual_rain += interval_rain_in
    rain_today += interval_rain_in
    monthly_rain += interval_rain_in
  
    # we need to watch the year for our rain data
    if current_year != local_timenow.year:
      # open a new rain file
      new_rain_file(interval_rain_in)
      current_year = local_timenow.year
      annual_rain = interval_rain_in
      rain_today = interval_rain_in
      monthly_rain = interval_rain_in
    else:
      # if we got some rain, add it to the file
      if interval_rain_in > 0.0:
        save_new_rain_total(annual_rain, interval_rain_in, rain_today, monthly_rain)

    # update our array
    with data.get_lock():
        data[0] = (timenow - epoch).total_seconds()  # UNIX Timestamp
        data[1] = tempest.wind_speed_3sec_mph
        data[2] = tempest.wind_direction_3sec_deg
        data[3] = tempest.wind_lull_1min_mph
        data[4] = tempest.wind_speed_1min_mph
        data[5] = tempest.wind_gust_1min_mph
        data[6] = tempest.wind_direction_1min_deg
        data[7] = tempest.press_inhg
        data[8] = tempest.slp_inhg
        data[9] = tempest.pa_ft
        data[10] = tempest.da_ft
        data[11] = tempest.temp_f
        data[12] = tempest.rh_pct
        data[13] = tempest.solar_illuminance_lux
        data[14] = tempest.uv_index
        data[15] = tempest.solar_irradiance_wpm2
        data[16] = tempest.last_minute_rain_in
        data[17] = tempest.lightning_distance_miles
        data[18] = tempest.lightning_count
        data[19] = tempest.battery_v

    # show the user what we got
    print("=============================================================")
    print("{:s}:".format(str_time))
    print(" 3 second wind: {:3.0f}°@{:4.1f} mph".format(tempest.wind_direction_3sec_deg, tempest.wind_speed_3sec_mph))
    print(" 1 minute wind: {:3.0f}°@{:4.1f} mph Gusts {:4.1f} mph (Min: {:4.1f} mph)".format(tempest.wind_direction_1min_deg, 
                                                                             tempest.wind_speed_1min_mph, 
                                                                             tempest.wind_gust_1min_mph,
                                                                             tempest.wind_lull_1min_mph))
    print("Temperature:{:.2f} °F Humidity:{:.1f}% ".format(tempest.temp_f, tempest.rh_pct))
    print("Pressure:{:.2f} inHg Sea-Level Pressure:{:.2f} inHg".format(tempest.press_inhg, tempest.slp_inhg))
    print("Pressure Altitude:{:.1f} ft Density Altitude:{:.1f} ft".format(tempest.pa_ft, tempest.da_ft))
    print("Illuminance:{:.2f} lux UV Index:{:.2f} Radiation:{:.1f} W/m^2".format(tempest.solar_illuminance_lux,
                                                                                 tempest.uv_index,
                                                                                 tempest.solar_irradiance_wpm2))
    print("New Rain:{:.2f} Daily Rain:{:.2f} Montly Rain:{:.2f} Total Rain:{:.2f}".format(interval_rain_in, rain_today, monthly_rain, total_rain_in))
    print("Lightning Distance: {} miles Lightning Count: {}".format(tempest.lightning_distance_miles, tempest.lightning_count))
    print("Battery Voltage:{:.3f}".format(tempest.battery_v))

