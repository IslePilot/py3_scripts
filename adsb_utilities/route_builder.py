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

  Jul 4, 2020, ksb, created
"""

import sys
sys.path.append("..")
import __common.filetools as ft

import cifp_processor
import kml_output

import simplekml

from collections import namedtuple
Waypoint = namedtuple('Waypoint', 'ident, latitude, longitude')

class RouteProcessor:
  def __init__(self, path, version ):
    # load the database
    print("Loading CIFP Version {} database".format(version))
    self.cifp = cifp_processor.CIFPReader(path, version)
    return
    
  def enter_route(self):
    # get the input data:
    print("Enter data as requested, enter 'X' to exit")
    
    # get the departure airport
    dep = None
    while dep == None:
      dep = input("Enter Departure Airport (KDEN): ")
      if dep == 'X':
        return False
      elif dep == "":
        dep = "KDEN"
      
      # get the departure airport
      if dep in self.cifp.usa.airports:
        self.dep = self.cifp.usa.airports[dep]
      else:
        print("Departure Airport {} not found...try again".format(dep))
        dep = None
    
    arr = None
    while arr == None:
      arr = input("Enter Arrival Airport (KEWR): ")
      if arr == 'X':
        return False
      elif arr == "":
        arr = "KEWR"
      
      # get the arrival airport
      if arr in self.cifp.usa.airports:
        self.arr = self.cifp.usa.airports[arr]
      else:
        print("Arrival Airport {} not found...try again".format(arr))
        arr = None
    
    fpr = input("Enter Flight Plan Route (EEONS7 WYNDM HCT J60 LNK DSM EVOTE NELLS KEEHO J584 SLT FQM3): ")
    if fpr == 'X':
      return False
    elif fpr == "":
      fpr = "EEONS7 WYNDM HCT J60 LNK DSM EVOTE NELLS KEEHO J584 SLT FQM3"
    
    self.route = fpr.split(" ")
    
    route = "{}.".format(self.dep.ident)
    for item in self.route:
      route += "{}.".format(item)
    route += "{}".format(self.arr.ident)
    
    print("Processing {}".format(route))
    
    # we have the input, now process the route
    return self.process_route()
  
  def process_route(self):
    route = []
    
    # add the depature airport
    route.append(Waypoint(self.dep.ident, self.dep.latitude, self.dep.longitude))
    
    # get the SID
    sid_route = self.get_sid_route(self.route[0], self.route[1])
    if sid_route == False:
      return False
    elif sid_route != None:
      for wp in sid_route:
        route.append(wp)

    # get the STAR (this will remove the STAR from our route, to clean up processing below
    if len(self.route) > 1:
      star_route = self.get_star_route(self.route[-2], self.route[-1])
    elif len(self.route) > 0:
      star_route = self.get_star_route(None, self.route[-1])
    else:
      star_route = self.get_star_route(None, None)
    
    # our route now only contains waypoints and airways add them to our route
    for i in range(len(self.route)):
      # we need to figure out whether this is a fix or an airway
      if self.cifp.usa.is_airway(self.route[i]):
        # get our airway points
        airway = self.cifp.usa.get_airway(route_id=self.route[i], initial_fix=route[-1].ident, final_fix=self.route[i+1], include_end_points=True)
        
        # add each point to our route
        for fix in airway:
          if route[-1].ident != fix[0] or route[-1].ident == None:
            route.append(Waypoint(fix[0], fix[1][0], fix[1][1]))
      
      else:
        # this is a waypoint
        if route[-1].ident != self.route[i] or route[-1].ident == None:
          fix = self.route[i].rstrip()
          
          # add our point
          if self.cifp.usa.vors.has_point(fix):
            point = self.cifp.usa.get_vor(fix)
          elif self.cifp.usa.ndbs.has_point(fix):
            point = self.cifp.usa.get_ndb(fix)
          elif self.cifp.usa.enroute_waypoints.has_point(fix):
            point = self.cifp.usa.get_waypoint(fix)
          else:
            print("Item not a VOR, NDB, or Enroute Waypoint: {}".format(fix))
            continue
          
          # add our point
          route.append(Waypoint(point.ident, point.latlon[0], point.latlon[1]))
    
    # now add our STAR
    if star_route == False:
      return False
    elif star_route != None:
      for wp in star_route:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(wp)
    
    # add an approach
    # find the last real previous fix (it could be a no-name manual termination point)
    appr_route = self.get_appr_route(route[-1].ident)
    
    if appr_route == False:
      return False
    
    # it is possible the first point in our appr route is one we recently "passed."  If so, find it and remove that
    # point and the ones after that
    if appr_route[0].ident == route[-1].ident:
      route.pop(-1) # remove the first point in the approach
    elif appr_route[0].ident == route[-2].ident:
      route.pop(-1) # remove the manual termination
      route.pop(-1) # remove the first point in the approach
    
    # now add the approach
    if appr_route != None:
      for wp in appr_route:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(wp)   
    
    # now finish up with the arrival airport
    route.append(Waypoint(self.arr.ident, self.arr.latitude, self.arr.longitude))
    
    # now show the whole route
    i=1
    for wp in route:
      print("{} {}: ({:.6f}, {:.6f})".format(i, *wp))
      i+=1
    
    return route
  
  def get_sid_route(self, sid_name, enr_transition):
    # the enr_transition needs to be 5 characters
    if enr_transition != None:
      while len(enr_transition) < 5:
        enr_transition += " "
    
    # build a list of sids
    sids = list(self.dep.sids.keys())
    
    # if the sid_name is in the list, use that, otherwise query the user
    if sid_name not in sids:
      # find out which SID we are using
      for i in range(len(sids)):
        print("{:2d}: {}".format(i, sids[i]))
      # get the user input
      sid_index = input("Enter SID Number (X to exit, return for none): ")
      
      if sid_index == "X":
        return False
      elif sid_index == "":
        return None
      else:
        # get the SID
        sid_name = sids[int(sid_index)]
    
    # set our SID
    sid = self.dep.sids[sid_name]
    
    # clean up our route
    if sid_name in self.route:
      self.route.remove(sid_name)
    
    # choose the runway transition
    rw = False
    rw_transition = ""
    rw_transitions = list(sid.runway_transitions.keys())
    if len(rw_transitions) > 0:
      for i in range(len(rw_transitions)):
        print("{:2d}: {}".format(i, rw_transitions[i]))
      rw_transition_index = input("Enter Departure Runway Number (X to exit, return for none): ")
    
      if rw_transition_index == "X":
        return False
      elif rw_transition_index == "":
        rw_transition = None
      else:
        rw_transition = rw_transitions[int(rw_transition_index)]
        rw = True
    
    # choose the enroute transition
    enr = False
    enr_transitions = list(sid.enroute_transistions.keys())
    
    if enr_transition not in enr_transitions:
      if len(enr_transitions) > 0:
        for i in range(len(enr_transitions)):
          print("{:2d}: {}".format(i, enr_transitions[i]))
        enr_transition_index = input("Enter Enroute Transition Number (X to exit, return for none): ")
        
        if enr_transition_index == "X":
          return False
        elif enr_transition_index == "":
          enr_transition = ""
        else:
          enr_transition = enr_transitions[int(enr_transition_index)]
          enr = True
      else:
        enr_transition = ""
    else:
      enr = True
    
      # clean up our route
      if enr_transition in self.route:
        self.route.remove(enr_transition)
    
    # show the user our SID
    print("Full SID: {} {} {}".format(rw_transition, sid_name, enr_transition))
    
    # build the sid routes
    routes = self.cifp.usa.build_procedure_tracks(self.dep.ident, sid_name, "SID")
    
    # build our requested route
    route = []
    # runway transition
    if rw:
      for wp in routes[rw_transition]:
        route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # common route
    common = "     "
    if "ALL  " in routes:
      common = "ALL  "
      
    if common in routes:
      for wp in routes[common]:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # entroute transition
    if enr:
      for wp in routes[enr_transition]:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    return route
  
  def get_star_route(self, enr_transition, star_name):
    # the enr_transition needs to be 5 characters
    if enr_transition != None:
      while len(enr_transition) < 5:
        enr_transition += " "
    
    # build a list of stars
    stars = list(self.arr.stars.keys())
    
    # if the star_name isn't in the list, query the user
    if star_name not in stars:
      # find out which STAR we are using
      for i in range(len(stars)):
        print("{:2d}: {}".format(i, stars[i]))
      # get the user input
      star_index = input("Enter STAR Number (X to exit, return for none): ")
      
      if star_index == "X":
        return False
      elif star_index == "":
        return None
      else:
        # get the STAR
        star_name = stars[int(star_index)]
        
    star = self.arr.stars[star_name]
    
    # clean up our route
    if star_name in self.route:
      self.route.remove(star_name)
    
    # choose the enroute transition
    enr = False
    enr_transitions = list(star.enroute_transistions.keys())
    
    if enr_transition not in enr_transitions:
      if len(enr_transitions) > 0:
        for i in range(len(enr_transitions)):
          print("{:2d}: {}".format(i, enr_transitions[i]))
        enr_transition_index = input("Enter Enroute Transition Number (X to exit, return for none): ")
        
        if enr_transition_index == "X":
          return False
        elif enr_transition_index == "":
          enr_transition = None
        else:
          enr_transition = enr_transitions[int(enr_transition_index)]
          enr = True
    else:
      enr = True
      
      # clean up our route
      if enr_transition in self.route:
        self.route.remove(enr_transition)
    
    # choose the runway transition
    rw = False
    rw_transition = ""
    rw_transitions = list(star.runway_transitions.keys())
    if len(rw_transitions) > 0:
      for i in range(len(rw_transitions)):
        print("{:2d}: {}".format(i, rw_transitions[i]))
      rw_transition_index = input("Enter Runway Transition Number (X to exit, return for none): ")
    
      if rw_transition_index == "X":
        return False
      elif rw_transition_index == "":
        rw_transition = None
      else:
        rw_transition = rw_transitions[int(rw_transition_index)]
        rw = True

    # show the user our SID
    print("Full STAR: {} {} {}".format(enr_transition, star_name, rw_transition))
    
    # build the star routes
    routes = self.cifp.usa.build_procedure_tracks(self.arr.ident, star_name, "STAR")
    
    # build our requested route
    route = []
    
    # entroute transition
    if enr:
      for wp in routes[enr_transition]:
        route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # common route
    common = "     "
    if "ALL  " in routes:
      common = "ALL  "
      
    if common in routes:
      for wp in routes[common]:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # runway transition
    if rw:
      for wp in routes[rw_transition]:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    return route
  
  def get_appr_route(self, ap_transition):
    # the enr_transition needs to be 5 characters
    if ap_transition != None:
      while len(ap_transition) < 5:
        ap_transition += " "
    
    # build a list of approaches
    apprs = list(self.arr.approaches.keys())
    
    # query the user which approach 
    for i in range(len(apprs)):
      print("{:2d}: {}".format(i, apprs[i]))
    # get the user input
    appr_index = input("Enter the Approach Number (X to exit, return for none):")
    
    if appr_index == 'X':
      return False
    if appr_index == '':
      return None
    else:
      # get the approach
      appr_name = apprs[int(appr_index)]
    
    appr = self.arr.approaches[appr_name]
    print("Approach: {}".format(appr_name))
      
    # choose the transition
    apt = False
    ap_transitions = list(appr.approach_transition.keys())
    
    if ap_transition not in ap_transitions:
      if len(ap_transitions) > 0:
        for i in range(len(ap_transitions)):
          print("{:2d}: {}".format(i, ap_transitions[i]))
        ap_transition_index = input("Enter Approach Transition Number (X to exit, return for none): ")
      
        if ap_transition_index == "X":
          return False
        elif ap_transition_index == "":
          ap_transition = None
        else:
          ap_transition = ap_transitions[int(ap_transition_index)]
          apt = True
    else:
      apt = True
      
      # clean up our route
      if ap_transition in self.route:
        self.route.remove(ap_transition)
      
    print("Approach Transition via {}".format(ap_transition))

    # build the appr routes
    routes = self.cifp.usa.build_procedure_tracks(self.arr.ident, appr_name, "APPROACH")
    
    # build our requested route
    route = []
    # runway transition
    if apt:
      for wp in routes[ap_transition]:
        route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # common route
    common = "     "
    if "ALL  " in routes:
      common = "ALL  "
      
    if common in routes:
      for wp in routes[common]:
        if route[-1].ident != wp.ident or route[-1].ident == None:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    return route

if __name__ == '__main__':
  # when this file is run directly, run this code
  # get the basic info from the user
  print("Initializing Database...stand by")
  rp = RouteProcessor(r"C:\Data\CIFP", "CIFP_221201")
  
  ft.mkdir(r"C:\Data\CIFP\CIFP_221201\routes")
  kml = kml_output.KMLOutput("Routes", r"C:\Data\CIFP\CIFP_221201\routes\routes.kml")
  
  route = True
  while route != False:
    route = rp.enter_route()
    
    if route != False:
      route_name = "{}-{}".format(route[0].ident, route[-1].ident)
      
      # build a text file for AVARE
      txt = open(r"C:\Data\CIFP\CIFP_221201\routes\{}.txt".format(route_name), "w")
      for wp in route:
        
        if wp.ident != None and wp.ident[:2] != "RW":
          txt.write("{} ".format(wp.ident))
        else:
          txt.write("{:.4f}&{:.4f} ".format(wp.latitude, wp.longitude))
      txt.write("\n")
      txt.close()
      
      # build a kml file for Google Earth
      folder = kml.create_folder("{}".format(route_name))
      
      # now add the waypoints...don't add the first or last as they are just the airport
      track = []
      for wp in route[1:-1]:
        # get this ready for the kml file as long as we are looping
        track.append((wp.latitude, wp.longitude))
        
        if wp.ident != None:
          kml.add_point(folder, wp.ident, (wp.latitude, wp.longitude), "")
        else:
          kml.add_point(folder, "", (wp.latitude, wp.longitude), "")
      
      # add the track
      kml.add_line(folder, "Flight Route", track, simplekml.Color.red)
      
      kml.savefile()
      
  
  print("Terminating")
      
  

