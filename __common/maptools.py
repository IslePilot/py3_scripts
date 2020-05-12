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

  May 11, 2020, ksb, created
"""

import sys
sys.path.append("..")

import utm
import math

def arcpoints(waypoint1, waypoint2, radius_nm, heading1_deg_mag, heading2_deg_mag, turn_direction, variation):
  """build a list of lat/lon coordinates defining points along an arc
  
  waypoint1: initial waypoint tuple (lat1, lon1), lat/lon in decimal degrees +N, +E
  waypoint2: end waypoint tuple (lat2, lon2), lat/lon in decimal degrees +N, +E
  radius_nm: circle radius in nautical miles
  heading1_deg_mag: initial magnetic heading at waypoint1
  heading2_deg_mag: final magnetic heading at waypoint2
  turn_direction: "R"ight, "L"eft
  variation: Degrees of variation (positive west)
  
  returns: list of waypoints(lat, lon) defining the arc (eg [[lat1, lon1], [lat2, lon2]...]"""
  
  # convert our waypoints to UTM
  wp1 = utm.from_latlon(*waypoint1)
  wp2 = utm.from_latlon(*waypoint2)
  if waypoint1[0] >= 0.0:
    northern_hemisphere = True
  else:
    northern_hemisphere = False
  
  # if the UTM zones are different we can't really proceed
  if wp1[2] != wp2[2]:
    print("maptools.arcpoints: Error, UTM zones for waypoint1 and waypoint2 are different.  Unable to proceed")
    return []
  
  # convert our headings to true
  h1_true = (heading1_deg_mag - variation + 360.0)%360.0
  h2_true = (heading2_deg_mag - variation + 360.0)%360.0
  
  # find the distance between our points
  deast = wp2[0] - wp1[0]
  dnorth = wp2[1] - wp1[1]
  distance = math.sqrt(deast**2 + dnorth**2)
  halfd = distance/2.0
  
  # convert the radius to meters
  radius = 1852*radius_nm
  
  # find the midpoint
  mideast = (wp2[0] + wp1[0])/2.0
  midnorth = (wp2[1] + wp1[1])/2.0
  
  # we know the distance from each point to the midpoint (halfd), and we know our radius,
  # find the distance along the bisector from the midpoint to the arc centerpoints
  bslen = math.sqrt(radius**2 - halfd**2)
  
  # the bisector has the opposite slope of the line from waypoint1 to waypoint2
  rise = -deast
  run = dnorth
  angle = math.atan2(rise, run)
  dx = bslen*math.cos(angle)
  dy = bslen*math.sin(angle)
  
  # we have everything we need to define our two points, only one of which is correct
  point1 = (mideast+dx, midnorth+dy)
  point2 = (mideast-dx, midnorth-dy)
  
  # compute the bearing from each midpoint to our waypoints
  p1_wp1 = (wp1[0]-point1[0], wp1[1]-point1[1])
  p1_wp2 = (wp2[0]-point1[0], wp2[1]-point1[1])
  p2_wp1 = (wp1[0]-point2[0], wp1[1]-point2[1])
  p2_wp2 = (wp2[0]-point2[0], wp2[1]-point2[1])
  
  # compute the bearings to the first points
  bearing_p1_wp1 = (math.degrees(math.atan2(p1_wp1[0], p1_wp1[1]))+360.0)%360.0
  bearing_p1_wp2 = (math.degrees(math.atan2(p1_wp2[0], p1_wp2[1]))+360.0)%360.0
  bearing_p2_wp1 = (math.degrees(math.atan2(p2_wp1[0], p2_wp1[1]))+360.0)%360.0
  bearing_p2_wp2 = (math.degrees(math.atan2(p2_wp2[0], p2_wp2[1]))+360.0)%360.0

  
  # convert the bearings (from the center to the initial waypoint) to a heading
  if turn_direction == "R":
    heading1 = (bearing_p1_wp1 + 90.0 + 360.0)%360.0
    heading2 = (bearing_p2_wp1 + 90.0 + 360.0)%360.0
  else:
    heading1 = (bearing_p1_wp1 - 90.0 + 360.0)%360.0
    heading2 = (bearing_p2_wp1 - 90.0 + 360.0)%360.0
  
  # now find which heading is closer to our expectation
  err1 = math.fabs(h1_true - heading1)
  err2 = math.fabs(h2_true - heading2)
  
  if err1 <= err2:
    midpoint = point1
    bearing1 = bearing_p1_wp1
    bearing2 = bearing_p1_wp2
  else:
    midpoint = point2
    bearing1 = bearing_p2_wp1
    bearing2 = bearing_p2_wp2
  
  # compute the degrees of turn we need to cover
  if turn_direction == "R":
    if bearing2 >= bearing1:
      degrees_of_turn = bearing2 - bearing1
    else:
      degrees_of_turn = 360.0 + bearing2 - bearing1
  else: # left turn
    if bearing2 < bearing1:
      degrees_of_turn = bearing2 - bearing1
    else:
      degrees_of_turn = 360.0 - bearing2 + bearing1
  
  # figure out how many steps we need to take
  steps = int(degrees_of_turn/3.0)+1
  stepsize = degrees_of_turn / float(steps)
  
  arclist = []
  for i in range(steps+1):
    theta = math.radians(bearing1 + i*stepsize)
    point = [radius*math.sin(theta)+midpoint[0], radius*math.cos(theta)+midpoint[1]]
    arclist.append(utm.to_latlon(point[0], point[1], wp1[2], northern=northern_hemisphere))

  return arclist

def dms2deg(lathem, latdeg, latmin, latsec, lonhem, londeg, lonmin, lonsec):
  """convert latitude and longitude to decimal degrees with the appropriate sign (+N -S, +E, -W)
  lathem: "N | n | S | s" North or South Hemisphere for latitude
  latdeg: latitude degrees
  latmin: latitude minutes
  latsec: latitude seconds
  lonhem: "E | e | W | w" East or West Hemsisphere for longitude
  londeg: longitude degrees
  lonmin: longitude minutes
  lonsec: longitude seconds
  
  returns: tuple with (lat, lon) in decimal degrees with the appropriate sign"""
  # latitude
  lat = float(latdeg) + float(latmin)/60.0 + float(latsec)/3600.0
  if lathem == "S" or lathem == "s":
    lat = -lat
  
  lon = float(londeg) + float(lonmin)/60.0 + float(lonsec)/3600.0
  if lonhem == "W" or lonhem == "w":
    lon = -lon
    
  return (lat, lon)

# define a version for this file
VERSION = "1.0"

if __name__ == '__main__':
  # when this file is run directly, run this code
  
  # Test Code
  # CEPEE
  cepee = dms2deg("N", 39, 58, 54.34, "W", 104, 50, 17.93)
  # AAGEE
  aagee = dms2deg("N", 40, 1, 37.71, "W", 104, 46, 41.74)
  
  arclist1 = arcpoints(cepee, aagee, 2.750, 352.5, 82.5, "R", -8.0)
  
  # JABRO
  jabro = dms2deg("N", 40, 1, 37.13, "W", 104, 45, 14.79)
  
  # JETSN
  jetsn = dms2deg("N", 39, 58, 50.83, "W", 104, 41, 42.36)
  
  arclist2 = arcpoints(jabro, jetsn, 2.750, 82.5, 172.5, "R", -8.0)
  
  outfile = open("c:\\temp\\test1.csv", "w")
  outfile.write("latitude,longitude\n")
  
  for point in arclist1:
    outfile.write("{:.6f},{:.6f}\n".format(point[0], point[1]))
  
  for point in arclist2:
    outfile.write("{:.6f},{:.6f}\n".format(point[0], point[1]))
  
  outfile.close()
  print("Done.")
  
  
  
  
  
