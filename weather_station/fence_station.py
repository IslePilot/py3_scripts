#!/usr/bin/python3

"""
Copyright 2018 (C) AeroSys Engineering, Inc.

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
  2018-05-31, ksb, added shared memory array and array server code
  2015-07-24, ksb, output cleanup
  2015-07-24, ksb, corrected temperature input into density altitude computation
  2015-07-24, ksb, changed data retrieval to once per 5 seconds
  2015-07-24, ksb, added raingauge support
  2014-12-31, ksb, created
"""

import sys
sys.path.append("..")
import __common.mparray_transmitter as txrx

import time
import datetime
import pytz
import signal

import am2315 as am
import bmp180 as bmp
import rainwise111 as rain

import configparser
from multiprocessing import Array

# define a version for this file
VERSION = "1.0.20180531a"

def signal_handler(signal, frame):
  """Called by the signal handler when Control C is pressed"""
  print("Fence_Station.py:  You pressed Ctrl-c.  Exiting.")
  # set the flag to terminate the rain gauge monitoring thread, and wait for it to close
  rain.RAINWISE_TERMINATE_REQUEST = True
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
  rain_file = "/home/pi/WeatherData/{:d}_RainTotal.txt".format(current_year)

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
  rain_file = "/home/pi/WeatherData/{:d}_RainTotal.txt".format(timenow.year)
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
  rain_file = "/home/pi/WeatherData/{:d}_RainTotal.txt".format(timenow.year)

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
  print("Copyright (C) 2018 AeroSys Engineering, Inc.")
  print("This program comes with ABSOLUTELY NO WARRANTY;")
  print("This is free software, and you are welcome to redistribute it")
  print("under certain conditions.  See GNU Public License.")
  print("")
  print("Version: ", VERSION)

  # parse the config file
  config = configparser.ConfigParser()
  config.read('/home/pi/WeatherData/config.ini')

  hostname = config['FENCE_STATION']['host']
  port = int(config['FENCE_STATION']['port'])
  authkey = config['FENCE_STATION']['authkey'].encode()

  print(hostname, port, authkey)

  # initialize our daily rain
  rain_today = 0.0
  monthly_rain = 0.0
  today = datetime.datetime.now() # use local time
  
  # create our time base (UNIX time)
  epoch = datetime.datetime(1970,1,1, tzinfo=pytz.UTC)

  # create a shared array of doubles
  data = Array('d', 13)

  dataserver = txrx.MPArrayServer(hostname, port, authkey, data)
  dataserver.daemon = True  # run until this process dies
  dataserver.start()

  # start here
  am2315 = am.AM2315()
  bmp180 = bmp.BMP180(sensor_elevation_ft = 5094.0)
  rain111 = rain.Rainwise111()
  current_year, total_rain_in, monthly_rain_in, daily_rain_in,  = get_rain_total()
  if daily_rain_in > 0:
    rain_today = daily_rain_in
  if monthly_rain_in > 0:
    monthly_rain = monthly_rain_in
  annual_rain = total_rain_in

  # the first two readings of the AM2315 might be junk, read and skip
  t_f, t_c, rh = am2315.get_readings()
  time.sleep(1)
  t_f, t_c, rh = am2315.get_readings()
  time.sleep(1)

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
    # Read the AM2315
    t2315_f, t2315_c, rh2315 = am2315.get_readings()
    
    # Read the BMP180
    t180_f, t180_c, p180_inhg, slp180_inhg, pa180_ft = bmp180.get_readings()

    # Read the Rain Gauge
    interval_rain_in = rain111.get_readings()
    annual_rain += interval_rain_in
    rain_today += interval_rain_in
    monthly_rain += interval_rain_in

    # compute the density altitude
    da_ft = bmp.compute_density_altitude(p180_inhg, t2315_f)

    # get the CPU temp
    t_cpu_c = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
    t_cpu_f = t_cpu_c * 9.0/5.0 + 32.0
    
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
        data[0] = (timenow-epoch).total_seconds()  # UNIX Timestamp
        data[1] = t2315_f               # Outside Temperature (deg F)
        data[2] = rh2315                # Relative Humidty (%)
        data[3] = t180_f                # BMP180 Board Temp (deg F)
        data[4] = p180_inhg             # Pressure (inHg)
        data[5] = slp180_inhg           # Sea Level Pressure (inHg)
        data[6] = pa180_ft              # Pressure Altitdue (ft)
        data[7] = da_ft                 # Density Altitude (ft)
        data[8] = interval_rain_in      # Rain in the last read interval (in)
        data[9] = annual_rain           # total rain this year (in)
        data[10] = rain_today           # today's rain (in)
        data[11] = monthly_rain         # monthly rain (in)
        data[12]= t_cpu_f               # CPU Temp (deg F)

    # show the user what we got
    print("=============================================================")
    print("{:s}:".format(str_time))
    print("Temperature(F):{:.2f} Humidity(%):{:.1f} ".format(t2315_f, rh2315))
    print("Pressure(inHg):{:.2f} Sea-Level Pressure(inHg):{:.2f}".format(p180_inhg, slp180_inhg))
    print("Pressure Altitude:{:.1f} Density Altitude:{:.1f}".format(pa180_ft, da_ft))
    print("New Rain:{:.2f} Daily Rain:{:.2f} Montly Rain:{:.2f} Total Rain:{:.2f}".format(interval_rain_in, rain_today, monthly_rain, total_rain_in))
    print("CPU Temp:{:.2f} Board Temp:{:.2f}".format(t_cpu_f, t180_f))

    time.sleep(5)


