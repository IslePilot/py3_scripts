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

def circle(origin, radius_nm):
  """build a list of lat/lon coordinates defining points along a circle
  
  origin: tuple defining the center of the circle (lat, lon) in decimal degrees, +N, +E
  radius_nm: circle radius in nautical miles
  
  returns: list of waypoints(lat, lon) defining the arc (eg: [[lat1, lon1], [lat2, lon2]...]
  """
  # convert our center point to UTM
  center = utm.from_latlon(*origin)
  if origin[0] >= 0.0:
    northern_hemisphere = True
  else:
    northern_hemisphere = False
  
  # convert radius to meters
  radius = 1852.0 * radius_nm
  
  # figure out how many steps we need to take
  steps = 120
  stepsize = 3.0
  
  arclist = []
  for i in range(steps+1):
    theta = math.radians(float(i*stepsize))
    point = [radius*math.sin(theta)+center[0], radius*math.cos(theta)+center[1]]
    arclist.append(utm.to_latlon(point[0], point[1], center[2], northern=northern_hemisphere))

  return arclist
  
def arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise):
  """build a list of lat.lon coordinates defining points along an arc
  
  arc_begin: tuple defining the starting point (lat, lon) in decimal degrees,+N, +E
  arc_end: tuple defining the ending point (lat, lon) in decimal degrees,+N, +E
  arc_center: tuple defining the center point (lat, lon) in decimal degrees,+N, +E
  radius_nm: arc radius in nautical miles
  clockwise: bool defining arc direction
  """
  # convert our points
  begin = utm.from_latlon(*arc_begin)
  end = utm.from_latlon(*arc_end)
  center = utm.from_latlon(*arc_center)
  radius = 1852.0 * radius_nm
  
  utm_zone = center[2]
  utm_letter = center[3]
  
  # find the azimuth angles to the points
  bearing1 = get_azimuth(center, begin)
  bearing2 = get_azimuth(center, end)
  radius1 = get_distance(center, begin)
  radius2 = get_distance(center, end)
  
  if abs(radius-radius1) > 200 or abs(radius-radius2) > 200:
    print("Warning specified radius is more than 200 meters different than computed radius: begin:{:.2f} end:{:.2f}".format(radius-radius1, radius-radius2))

  
  # find the azimuth we need to sweep through
  if clockwise:
    if bearing2 >= bearing1:
      degrees_of_turn = bearing2 - bearing1
    else:
      degrees_of_turn = 360.0 + bearing2 - bearing1
  else: # CCW
    if bearing2 < bearing1:
      degrees_of_turn = bearing2 - bearing1  # notice negative number
    else:
      degrees_of_turn = (bearing2-360.0) - bearing1
  
  # figure out how many steps we need to take
  if abs(degrees_of_turn) < 6.0:
    steps = 2
  else:
    steps = int(abs(degrees_of_turn)/3.0)+1
  stepsize = degrees_of_turn / float(steps)
  
  arclist = []
  for i in range(steps+1):
    theta = math.radians(bearing1 + i*stepsize)
    point = [radius*math.sin(theta)+center[0], radius*math.cos(theta)+center[1]]
    arclist.append((utm.to_latlon(point[0], point[1], utm_zone, utm_letter, strict=False)))
    
  return arclist
      
def build_runway(arrival_end, departure_end, width_ft, bearing, declination):
  """
  """
  easting, northing, zone_number, zone_letter = utm.from_latlon(*arrival_end)
  op_easting, op_northing, _, _ = utm.from_latlon(*departure_end, zone_number, zone_letter)
  
  halfwidth = (0.3048 * width_ft)/2.0
  
  # correct for declination and utm rotation
  true_heading = bearing - declination
  true_heading -= get_utm_rotation(*arrival_end)
  
  # compute the angles to our points
  left = math.radians(true_heading-90.0)
  right = math.radians(true_heading+90.0)
  
  # compute the corners of the runway
  l_easting = easting + halfwidth * math.sin(left)
  l_northing = northing + halfwidth * math.cos(left)
  r_easting = easting + halfwidth * math.sin(right)
  r_northing = northing + halfwidth * math.cos(right)
  
  lo_easting = op_easting + halfwidth * math.sin(left)
  lo_northing = op_northing + halfwidth * math.cos(left)
  ro_easting = op_easting + halfwidth * math.sin(right)
  ro_northing = op_northing + halfwidth * math.cos(right)
  
  points = []
  points.append(utm.to_latlon(l_easting, l_northing, zone_number, zone_letter, strict=False))
  points.append(utm.to_latlon(lo_easting, lo_northing, zone_number, zone_letter, strict=False))
  points.append(utm.to_latlon(ro_easting, ro_northing, zone_number, zone_letter, strict=False))
  points.append(utm.to_latlon(r_easting, r_northing, zone_number, zone_letter, strict=False))
  points.append(utm.to_latlon(l_easting, l_northing, zone_number, zone_letter, strict=False))
  
  return points

def get_utm_rotation(lat, lon):
  # get the utm for the point
  p1_easting, p1_northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
  p1 = (p1_easting, p1_northing)
  
  # get the utm for a point 0.01 degrees north
  p2_easting, p2_northing, _, _ = utm.from_latlon(lat+0.01, lon, zone_number, zone_letter) # force zone to be the same
  p2 = (p2_easting, p2_northing)
  
  az= get_azimuth(p1, p2)
  if az > 180.0:
    az -= 360.0
  
  return az
  
  
def arcpoints(waypoint1, waypoint2, radius_nm, heading1_deg_mag, heading2_deg_mag, turn_direction, variation):
  """build a list of lat/lon coordinates defining points along an arc
  
  waypoint1: initial waypoint tuple (lat1, lon1), lat/lon in decimal degrees +N, +E
  waypoint2: end waypoint tuple (lat2, lon2), lat/lon in decimal degrees +N, +E
  radius_nm: circle radius in nautical miles
  heading1_deg_mag: initial magnetic heading at waypoint1
  heading2_deg_mag: final magnetic heading at waypoint2
  turn_direction: "R"ight, "L"eft
  variation: Degrees of variation (positive west)
  
  returns: list of waypoints(lat, lon) defining the arc (eg [[lat1, lon1], [lat2, lon2]...]
  """
  
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

def get_azimuth(pt1, pt2):
  deast = pt2[0] - pt1[0]
  dnorth = pt2[1] - pt1[1]
  return (math.degrees(math.atan2(deast, dnorth))+360.0)%360.0

def get_distance(pt1, pt2):
  deast = pt2[0] - pt1[0]
  dnorth = pt2[1] - pt1[1]
  return math.sqrt(deast**2 + dnorth**2)

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
  
  # test UTM rotation
  print(get_utm_rotation(40.06389444, -105.0441778))
  
  print(build_runway((39.901375, -105.101919), (39.915292, -105.128414), 100.0, 295.0, -9.0))
  
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
  
  
  
  
  
