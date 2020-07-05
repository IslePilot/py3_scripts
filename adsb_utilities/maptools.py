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
import simplekml

def circle(origin, radius_nm):
  """build a list of lat/lon coordinates defining points along a circle
  
  origin: tuple defining the center of the circle (lat, lon) in decimal degrees, +N, +E
  radius_nm: circle radius in nautical miles
  
  returns: list of waypoints(lat, lon) defining the arc (eg: [[lat1, lon1], [lat2, lon2]...]
  """
  # convert our center cifp_point to UTM
  center = utm.from_latlon(*origin)
  if origin[0] >= 0.0:
    northern_hemisphere = True
  else:
    northern_hemisphere = False
  
  # convert radius to meters
  radius = 1852.0 * radius_nm
  
  # figure out how many steps we need to take
  steps = 120
  stepsize = 6.0
  
  arclist = []
  for i in range(steps+1):
    theta = math.radians(float(i*stepsize))
    point = [radius*math.sin(theta)+center[0], radius*math.cos(theta)+center[1]]
    arclist.append(utm.to_latlon(point[0], point[1], center[2], northern=northern_hemisphere))

  return arclist
  
def arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise, name):
  """build a list of lat.lon coordinates defining points along an arc
  
  arc_begin: tuple defining the starting cifp_point (lat, lon) in decimal degrees,+N, +E
  arc_end: tuple defining the ending cifp_point (lat, lon) in decimal degrees,+N, +E
  arc_center: tuple defining the center cifp_point (lat, lon) in decimal degrees,+N, +E
  radius_nm: arc radius in nautical miles
  clockwise: bool defining arc direction
  """
  # convert our points
  center = utm.from_latlon(*arc_center)
  utm_zone = center[2]
  utm_letter = center[3]
  
  # use the zone from the center and force the points to be the same
  begin = utm.from_latlon(*arc_begin, utm_zone, utm_letter)
  end = utm.from_latlon(*arc_end, utm_zone, utm_letter)
  
  radius = 1852.0 * radius_nm
  
  # find the azimuth angles to the points
  bearing1 = get_azimuth(center, begin)
  bearing2 = get_azimuth(center, end)
  radius1 = get_distance(center, begin)
  radius2 = get_distance(center, end)
  
  if abs(radius-radius1) > 250 or abs(radius-radius2) > 250:
    print("Warning specified radius is more than 250 meters different than computed radius: begin:{:.2f} end:{:.2f}: {}".format(radius-radius1, radius-radius2, name))

  
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
  if abs(degrees_of_turn) < 12.0:
    steps = 2
  else:
    steps = int(abs(degrees_of_turn)/6.0)+1
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

def build_hold(hold_fix, inbound_course, turn_direction, leg_distance_nm, declination, tas_knots):
  # convert the hold_fix to UTM
  fix_utm = utm.from_latlon(*hold_fix)
  
  # find the true bearing from the fix
  true_inbound = get_true_hdg(inbound_course, declination, hold_fix)
  bearing = (true_inbound+180.0)%360.0
  
  if turn_direction == "R":
    cross_bearing = (bearing-90.0+360)%360.0
    clockwise = True
  else:
    cross_bearing = (bearing+90.0)%360.0
    clockwise = False
  
  # find the turn radius
  radius_m = std_rate_radius_m(tas_knots)
  radius_nm = radius_m/1852.0
  
  # leg distance
  leg_distance_m = leg_distance_nm * 1852.0
  
  # start building our shape
  # working backwards
  pt_a = (fix_utm[0], fix_utm[1])
  pt_b = (fix_utm[0]+leg_distance_m*math.sin(math.radians(bearing)), fix_utm[1]+leg_distance_m*math.cos(math.radians(bearing)))
  pt_c = (pt_b[0]+2.0*radius_m*math.sin(math.radians(cross_bearing)), pt_b[1]+2.0*radius_m*math.cos(math.radians(cross_bearing)))
  pt_d = (pt_a[0]+2.0*radius_m*math.sin(math.radians(cross_bearing)), pt_a[1]+2.0*radius_m*math.cos(math.radians(cross_bearing)))
  
  ctr_ad = (pt_a[0]+radius_m*math.sin(math.radians(cross_bearing)), pt_a[1]+radius_m*math.cos(math.radians(cross_bearing)))
  ctr_bc = (pt_b[0]+radius_m*math.sin(math.radians(cross_bearing)), pt_b[1]+radius_m*math.cos(math.radians(cross_bearing)))
  
  # convert our points to lat lon
  utm_a = utm.to_latlon(*pt_a, fix_utm[2], fix_utm[3], strict=False)
  utm_b = utm.to_latlon(*pt_b, fix_utm[2], fix_utm[3], strict=False)
  utm_c = utm.to_latlon(*pt_c, fix_utm[2], fix_utm[3], strict=False)
  utm_d = utm.to_latlon(*pt_d, fix_utm[2], fix_utm[3], strict=False)
  utm_ad = utm.to_latlon(*ctr_ad, fix_utm[2], fix_utm[3], strict=False)
  utm_bc = utm.to_latlon(*ctr_bc, fix_utm[2], fix_utm[3], strict=False)
  
  # build the turns
  turn_ad = arc_path(utm_a, utm_d, utm_ad, radius_nm, clockwise, "holding outbound turn")
  turn_cb = arc_path(utm_c, utm_b, utm_bc, radius_nm, clockwise, "holding inbound turn")
  
  # we have all of our points, build our shape
  shape = []
  # add the outbound turn
  for point in turn_ad:
    shape.append(point)
  # add the inbound turn
  for point in turn_cb:
    shape.append(point)
  # add the leg back to the holding fix
  shape.append(hold_fix)
  
  return shape

def build_procedure_turn(fix, course, outbound_course, turn_direction, declination, max_distance):
  # convert our fix to UTM
  fix_easting, fix_northing, zone_number, zone_letter = utm.from_latlon(*fix)
  
  # code for a standard pattern at 210 knots TAS (no wind) to remain within 10 nm (we will verify later)
  v_knots = 210 # knots
  v_mps = v_knots*1852.0/3600.0
  radius_m = v_mps*60.0 / math.pi
  radius_nm = radius_m/1852.0
  p0_p1_time = 84 # seconds
  p2_p3_time = 53 # seconds
  
  # get our distances
  p0_p1_dist = p0_p1_time*v_mps
  p2_p3_dist = p2_p3_time*v_mps  
  ctr1_ctr3_dist = 2.0*radius_m/math.cos(math.radians(45.0))
  
  # compute the headings we need
  p0_p1 = get_true_hdg(course, declination, fix)
  p2_p3 = get_true_hdg(outbound_course, declination, fix)
  
  # compute the construction headings
  if turn_direction == "R":
    p1_ctr1 = (p0_p1-90.0+360.0)%360.0
    ctr1_p1 = (p1_ctr1+180.0)%360.0
    ctr1_p2 = (ctr1_p1-45.0+360.0)%360.0
    p3_ctr2 = ctr1_p2
    ctr3_p5 = ctr1_p2
    ctr3_p6 = ctr1_p1
    turn1_clockwise = False
    turn2_clockwise = True
    turn3_clockwise = True
  else:
    p1_ctr1 = (p0_p1+90.0)%360.0
    ctr1_p1 = (p1_ctr1+180.0)%360.0
    ctr1_p2 = (ctr1_p1+45.0)%360.0
    p3_ctr2 = ctr1_p2
    ctr3_p5 = ctr1_p2
    ctr3_p6 = ctr1_p1
    turn1_clockwise = True
    turn2_clockwise = False
    turn3_clockwise = False
  
  # build our points
  p0 = (fix_easting, fix_northing)
  p1 = (p0[0]+p0_p1_dist*math.sin(math.radians(p0_p1)), p0[1]+p0_p1_dist*math.cos(math.radians(p0_p1)))
  ctr1 = (p1[0]+radius_m*math.sin(math.radians(p1_ctr1)), p1[1]+radius_m*math.cos(math.radians(p1_ctr1)))
  p2 = (ctr1[0]+radius_m*math.sin(math.radians(ctr1_p2)), ctr1[1]+radius_m*math.cos(math.radians(ctr1_p2)))
  p3 = (p2[0]+p2_p3_dist*math.sin(math.radians(p2_p3)), p2[1]+p2_p3_dist*math.cos(math.radians(p2_p3)))
  ctr2 = (p3[0]+radius_m*math.sin(math.radians(p3_ctr2)), p3[1]+radius_m*math.cos(math.radians(p3_ctr2)))
  p4 = (p3[0]+2.0*radius_m*math.sin(math.radians(p3_ctr2)), p3[1]+2.0*radius_m*math.cos(math.radians(p3_ctr2)))
  ctr3 = (ctr1[0]+ctr1_ctr3_dist*math.sin(math.radians(p0_p1)), ctr1[1]+ctr1_ctr3_dist*math.cos(math.radians(p0_p1)))
  p5 = (ctr3[0]+radius_m*math.sin(math.radians(ctr3_p5)), ctr3[1]+radius_m*math.cos(math.radians(ctr3_p5)))
  p6 =(ctr3[0]+radius_m*math.sin(math.radians(ctr3_p6)), ctr3[1]+radius_m*math.cos(math.radians(ctr3_p6)))
  
  # convert to lat/lon for the arc_path call
  p0_ll = utm.to_latlon(*p0, zone_number, zone_letter, strict=False)
  p1_ll = utm.to_latlon(*p1, zone_number, zone_letter, strict=False)
  p2_ll = utm.to_latlon(*p2, zone_number, zone_letter, strict=False)
  ctr1_ll = utm.to_latlon(*ctr1, zone_number, zone_letter, strict=False)
  
  p3_ll = utm.to_latlon(*p3, zone_number, zone_letter, strict=False)
  p4_ll = utm.to_latlon(*p4, zone_number, zone_letter, strict=False)
  ctr2_ll = utm.to_latlon(*ctr2, zone_number, zone_letter, strict=False)
  
  p5_ll = utm.to_latlon(*p5, zone_number, zone_letter, strict=False)
  p6_ll = utm.to_latlon(*p6, zone_number, zone_letter, strict=False)
  ctr3_ll = utm.to_latlon(*ctr3, zone_number, zone_letter, strict=False)
  
  # start building our shape
  shape = []
  
  # start at the fix (p0) and head to p1
  shape.append(p0_ll)
  shape.append(p1_ll)
  
  # turn 45 degrees from p1 to p2
  t1 = arc_path(p1_ll, p2_ll, ctr1_ll, radius_nm, turn1_clockwise, "Procedure Turn 1")
  for p_ll in t1:
    shape.append(p_ll)
  
  # turn 180 from p3 to p4
  t2 = arc_path(p3_ll, p4_ll, ctr2_ll, radius_nm, turn2_clockwise, "Procedure Turn 2")
  for p_ll in t2:
    shape.append(p_ll)
  
  # turn 45 degrees from p5 to p6
  t3 = arc_path(p5_ll, p6_ll, ctr3_ll, radius_nm, turn3_clockwise, "Procedrue Turn 3")
  for p_ll in t3:
    shape.append(p_ll)
  
  # head back to the fix
  shape.append(p1_ll)
  
  return shape

def find_intersection(point, point_bearing, fix, fix_bearing, declination):
  # convert our locations to UTM
  f = utm.from_latlon(*fix)
  p = utm.from_latlon(*point, f[2], f[3])
  
  # find our true headings
  azp = get_true_hdg(point_bearing, declination, point)
  azf = get_true_hdg(fix_bearing, declination, fix)
  
  # to keep things a bit simpler, do all the trig here
  cp = math.cos(math.radians(azp))
  sp = math.sin(math.radians(azp))
  cf = math.cos(math.radians(azf))
  sf = math.sin(math.radians(azf))
  
  # break out our points
  xp = p[0]
  yp = p[1]
  xf = f[0]
  yf = f[1]
  
  # we have two unknowns, the distance from the fix and the distance from the point.
  # xi = xp+dp*sp, yi = yp+dp*cp
  # xi = xf+df*sf, yi = yf+df*cf
  # set the xi equations equal to each other and solve for dp
  # xp+dp*sp = xf+df*sf
  # dp = (xf+df*sf-xp)/sp
  #
  # set the yi equations equal to each other, substitute dp and solve for df
  # yp+cp*dp = yf+cf*df
  # yp+cp*(xf+df*sf-xp)/sp = yf+cf*df
  # yp + cp*xf/sp + (cp*sf/sp)*df - cp*xp/sp = yf+cf*df
  # (cp*sf/sp)*df - cf*df = yf - yp - cp*xf/sp + cp*xp/sp
  # (cp*sf/sp - cf)*df = yf - yp - cp*xf/sp + cp*xp/sp
  # df = (yf - yp - cp*xf/sp + cp*xp/sp) / (cp*sf/sp - cf)
  df = (yf - yp - cp*xf/sp + cp*xp/sp) / (cp*sf/sp - cf)
  dp = (xf+df*sf-xp)/sp
  
  xi = xp+dp*sp
  yi = yp+dp*cp
  
  return utm.to_latlon(xi, yi, f[2], f[3], strict=False)

def turn_to_heading(point1, current_heading, final_heading, declination, clockwise, tas_knots):
  # convert the points to utm
  pt1_utm = utm.from_latlon(*point1)
  
  # find the turn radius
  radius_m = std_rate_radius_m(tas_knots)
  radius_nm = radius_m/1852.0
  
  # find the true course
  true_heading = get_true_hdg(current_heading, declination, point1)
  true_course = get_true_hdg(final_heading, declination, point1)
  
  # find the center of our circle and then the azimuth and distance from the center to the fix
  if clockwise:
    bearing = (true_heading+90.0)%360.0
    final_bearing = (true_course-90.0+360.0)%360.0
  else:
    bearing = (true_heading-90.0+360.0)%360.0
    final_bearing = (true_course+90.0)%360.0
  
  ctr = (pt1_utm[0]+radius_m*math.sin(math.radians(bearing)), pt1_utm[1]+radius_m*math.cos(math.radians(bearing)))
  point2 = (ctr[0]+radius_m*math.sin(math.radians(final_bearing)), ctr[1]+radius_m*math.cos(math.radians(final_bearing)))
  ctr_ll = utm.to_latlon(*ctr, pt1_utm[2], pt1_utm[3], strict=False)
  point2_ll = utm.to_latlon(*point2, pt1_utm[2], pt1_utm[3], strict=False)
  
  return arc_path(point1, point2_ll, ctr_ll, radius_nm, clockwise, "Turn to Heading")

def forward(origin, magnetic_course, distance_nm, declination=0.0):
  # convert to UTM
  utm_origin = utm.from_latlon(*origin)
  
  # get our true bearing
  bearing = (magnetic_course - declination + 360.0)%360.0
  
  # convert our distance to meters
  distance_m = distance_nm * 1852.0
  
  # find our new point
  utm_new = (utm_origin[0]+distance_m*math.sin(math.radians(bearing)), utm_origin[1]+distance_m*math.cos(math.radians(bearing)))
  
  return utm.to_latlon(*utm_new, utm_origin[2], utm_origin[3], strict=False)

def get_mag_heading(origin, dest, declination):
  d_utm = utm.from_latlon(*dest)
  o_utm = utm.from_latlon(*origin, d_utm[2], d_utm[3])
  
  # get the heading from origin to destination
  true_heading = get_azimuth(o_utm, d_utm) - get_utm_rotation(*origin)
  
  return true_heading + declination

def get_utm_rotation(lat, lon):
  # get the utm for the cifp_point
  p1_easting, p1_northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
  p1 = (p1_easting, p1_northing)
  
  # get the utm for a cifp_point 0.01 degrees north
  p2_easting, p2_northing, _, _ = utm.from_latlon(lat+0.01, lon, zone_number, zone_letter) # force zone to be the same
  p2 = (p2_easting, p2_northing)
  
  az= get_azimuth(p1, p2)
  if az > 180.0:
    az -= 360.0
  
  return az
def get_true_hdg(mag, dec, point):
  # True Heading = Magnetic Heading - Declination - UTM
  return (mag - dec + get_utm_rotation(*point)+360.0)%360.0
def get_mag_hdg(true, dec, point):
  # Mag Heading = True Heading + Declination + UTM
  return (true + dec - get_utm_rotation(*point)+360.0)%360.0
  
def build_tangent_to_fix(pt1, heading, fix, tas_knots, clockwise):
  """used to build a path from a current point to to a fix when cleared direct to the fix
  
  pt1: current point (lat, lon)
  heading: current heading
  fix: fix to fly to (lat, lon)
  tas_knots: tas in knots
  clockwise: bool defining if turn is CW (right) or not"""
  
  # convert the points to utm
  fix_utm = utm.from_latlon(*fix)
  pt1_utm = utm.from_latlon(*pt1, fix_utm[2], fix_utm[3])
  
  
  # find the turn radius
  radius_m = std_rate_radius_m(tas_knots)
  radius_nm = radius_m/1852.0
  
  # find the center of our circle and then the azimuth and distance from the center to the fix
  if clockwise:
    bearing = (heading+90.0)%360.0
  else:
    bearing = (heading-90.0+360.0)%360.0
  ctr = (pt1_utm[0]+radius_m*math.sin(math.radians(bearing)), pt1_utm[1]+radius_m*math.cos(math.radians(bearing)))
  ctr_ll = utm.to_latlon(*ctr, fix_utm[2], fix_utm[3], strict=False)
  dist = get_distance(ctr, fix_utm)
  az = get_azimuth(ctr, fix_utm)
  
  # a line tangent to a circle is perpendicular to its radius at the intersection of the line and the circle,
  # so we have a right triangle.  There are two triangles actually and we need to figure out which one is right
  # each triangle has a hypotenuse of dist (the distance from the fix to the center), and a leg of radius r, so
  # find the angle from the ctr-fix line and the radials
  ctr_ang = math.degrees(math.acos(radius_m/dist))
  
  # the radials to the tangent points are at the ctr-fix azimuth plus and minus the ctr_ang
  az1 = (az-ctr_ang+360.0)%360.0
  az2 = (az+ctr_ang)%360.0
  
  # find our new points
  tan1 = (ctr[0]+radius_m*math.sin(math.radians(az1)), ctr[1]+radius_m*math.cos(math.radians(az1)))
  tan2 = (ctr[0]+radius_m*math.sin(math.radians(az2)), ctr[1]+radius_m*math.cos(math.radians(az2)))
  
  # find the heading to the fix from each of our points
  heading1 = get_azimuth(tan1, fix_utm)
  heading2 = get_azimuth(tan2, fix_utm)
  
  # if one of these headings is really close to our current heading, just go straight to the point
  if abs(heading-heading1) < 0.5 or abs(heading-heading1) > 359.5 or abs(heading-heading2) < 0.5 or abs(heading-heading2) > 359.5:
    return (pt1, fix)
  
  # at each tangent point, we can get the heading based on the direction of turn, the one that matches the heading
  # to our fix is the right point.  One point will be 180 degrees out of phase, the other will be our solution.
  # analyze one to see if it is the solution...if not, use the other.
  if clockwise:
    tan2_diff = abs((az2+90.0)%360.0 - heading2)
  else:# counterclockwise
    tan2_diff = abs((az2-90.0+360.0)%360.0 - heading2)
  
  # the right answer will be around 0 or around 360, the wrong answer will be around 180
  if 90.0 < tan2_diff and tan2_diff < 270.0:
    p2 = utm.to_latlon(*tan1, fix_utm[2], fix_utm[3], strict=False)
  else:
    p2 = utm.to_latlon(*tan2, fix_utm[2], fix_utm[3], strict=False)

  # all done, construct our curve
  
  return arc_path(pt1, p2, ctr_ll, radius_nm, clockwise, "tangent_to_fix") 

def std_rate_radius_m(tas_knots):
  """compute the radius of a standard rate turn at a given TAS
  
  tas_knots: true airspeed in knots
  
  returns radius in meters"""
  # a standard rate turn is at 3 deg/sec, or a 1-minute to complete 180 degrees of turn
  turn_time_sec = 60.0  # seconds
  
  # compute the distance flown in the turn time (half circle)
  #    meters          nm/hr        hr/sec          sec         m/nm
  distance_flown_m = tas_knots * (1.0/3600.0) * turn_time_sec * 1852.0
  
  # a half circle traces out half a circumference (2*pi*r/2) and is the same as the distance flown above
  return distance_flown_m / math.pi
  
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
  
  # we know the distance from each cifp_point to the midpoint (halfd), and we know our radius,
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
  steps = int(degrees_of_turn/6.0)+1
  stepsize = degrees_of_turn / float(steps)
  
  arclist = []
  for i in range(steps+1):
    theta = math.radians(bearing1 + i*stepsize)
    point = [radius*math.sin(theta)+midpoint[0], radius*math.cos(theta)+midpoint[1]]
    arclist.append(utm.to_latlon(point[0], point[1], wp1[2], northern=northern_hemisphere))

  return arclist

def get_azimuth(pt1, pt2):
  """returns the azimuth in the UTM coordinate frame"""
  deast = pt2[0] - pt1[0]
  dnorth = pt2[1] - pt1[1]
  return (math.degrees(math.atan2(deast, dnorth))+360.0)%360.0

def get_distance(pt1, pt2):
  deast = pt2[0] - pt1[0]
  dnorth = pt2[1] - pt1[1]
  return math.sqrt(deast**2 + dnorth**2)

def get_dist_ll(pt1, pt2):
  pt1_utm = utm.from_latlon(*pt1)
  pt2_utm = utm.from_latlon(*pt2, pt1_utm[2], pt1_utm[3])
  return get_distance(pt1_utm[:2], pt2_utm[:2])

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
  # CFFNB
  cffnb = dms2deg("N", 39, 58, 52.83, "W", 104, 46, 43.59)
  
  arclist1 = arc_path(cepee, aagee, cffnb, 2.750, True, "arc1")
  #arclist1 = arcpoints(cepee, aagee, 2.750, 352.5, 82.5, "R", -8.0)
  
  # JABRO
  jabro = dms2deg("N", 40, 1, 37.13, "W", 104, 45, 14.79)
  # JETSN
  jetsn = dms2deg("N", 39, 58, 50.83, "W", 104, 41, 42.36)
  #CFPQD
  cfpqd =dms2deg("N", 39, 58, 52.24, "W", 104, 45, 16.70)
  
  arclist2 = arc_path(jabro, jetsn, cfpqd, 2.750, True, "arc2")
  #arclist2 = arcpoints(jabro, jetsn, 2.750, 82.5, 172.5, "R", -8.0)
  
  # build the shape
  shape1 = []
  for point in arclist1:
    shape1.append(point)
  for point in arclist2:
    shape1.append(point)
  
  # build a hold at SHAATZ
  shatz = dms2deg("N", 40, 5, 58.57, "W", 104, 58, 30.10)
  leg_distance_nm = 1.0 * 210.0/60.0
  holdshape = build_hold(shatz, 203.0, "R", leg_distance_nm, -11.0, 210.0)
  
  # build a simple kml file to test
  kml = simplekml.Kml()
  kml.document.name = "Maptools Test"
  
  # get shape1 coords in kml format
  coords1 = []
  for point in shape1:
    coords1.append((point[1], point[0]))
  
  # add the line
  line1 = kml.newlinestring(name="KDEN H16RZ",
                            coords = coords1,
                            altitudemode=simplekml.AltitudeMode.clamptoground)
  line1.style.linestyle.width = 4
  line1.style.linestyle.color = simplekml.Color.blue
  
  # get shape2 coords in kml format
  coords2 = []
  for point in holdshape:
    coords2.append((point[1], point[0]))
  
  # add the line
  line1 = kml.newlinestring(name="Hold at SHATZ",
                            coords = coords2,
                            altitudemode=simplekml.AltitudeMode.clamptoground)
  line1.style.linestyle.width = 4
  line1.style.linestyle.color = simplekml.Color.blue
  
  kml.save("C:\\Temp\\maptools.kml")
  

  print("Done.")
  
  
  
  
  
