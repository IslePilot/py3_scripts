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

import cifp_processor

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
    
    print("Processing {} {} {}".format(self.dep.ident, fpr, self.arr.ident))
    
    # we have the input, now process the route
    return self.process_route()
  
  def process_route(self):
    route = []
    
    # add the depature airport
    route.append(Waypoint(self.dep.ident, self.dep.latitude, self.dep.longitude))
    
    # get the SID
    sid_route = self.get_sid_route()
    if sid_route == False:
      return False
    elif sid_route != None:
      for wp in sid_route:
        route.append(wp)

    # get the STAR (this will remove the STAR from our route, to clean up processing below
    star_route = self.get_star_route()
    
    # our route now only contains waypoints and airways add them to our route
    for i in range(len(self.route)):
      # we need to figure out whether this is a fix or an airway
      if self.cifp.usa.is_airway(self.route[i]):
        # get our airway points
        airway = self.cifp.usa.get_airway(route_id=self.route[i], initial_fix=route[-1].ident, final_fix=self.route[i+1], include_end_points=True)
        
        # add each point to our route
        for fix in airway:
          if route[-1].ident != fix[0]:
            route.append(Waypoint(fix[0], fix[1][0], fix[1][1]))
      
      else:
        # this is a waypoint
        if route[-1].ident != self.route[i]:
          # add our point
          if self.cifp.usa.vors.has_point(self.route[i]):
            point = self.cifp.usa.get_vor(self.route[i])
          elif self.cifp.usa.ndbs.has_point(self.route[i]):
            point = self.cifp.usa.get_ndb(self.route[i])
          elif self.cifp.usa.enroute_waypoints.has_point(self.route[i]):
            point = self.cifp.usa.get_waypoint(self.route[i])
          else:
            print("Item not a VOR, NDB, or Enroute Waypoint: {}".format(self.route[1]))
          
          # add our point
          route.append(Waypoint(point.ident, point.latlon[0], point.latlon[1]))
    
    # now add our STAR
    if star_route == False:
      return False
    elif star_route != None:
      for wp in star_route:
        route.append(wp)
    
    # add an approach
    
    # now finish up with the arrival airport
    route.append(Waypoint(self.arr.ident, self.arr.latitude, self.arr.longitude))
    
    # now show the whole route
    for wp in route:
      print("{}: ({:.6f}, {:.6f})".format(*wp))
      
    
    
    return True
  
  def get_sid_route(self):
    # build a list of sids
    sids = list(self.dep.sids.keys())
    
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
      sid = self.dep.sids[sid_name]
      print("SID Chosen: {}".format(sid_name))
    
    # clean up our route
    if sid_name in self.route:
      self.route.remove(sid_name)
      
    # choose the runway transition
    rw = False
    rw_transitions = list(sid.runway_transitions.keys())
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
    
    # choose the enroute transition
    enr = False
    enr_transitions = list(sid.enroute_transistions.keys())
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
    
        # clean up our route
        if enr_transition in self.route:
          self.route.remove(enr_transition)

    # build the sid routes
    routes = self.cifp.usa.build_procedure_tracks(self.dep.ident, sid_name, "SID")
    
    # build our requested route
    route = []
    # runway transition
    if rw:
      for wp in routes[rw_transition]:
        route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # common route
    if "     " in routes:
      for wp in routes["     "]:
        if route[-1].ident != wp.ident:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # entroute transition
    if enr:
      for wp in routes[enr_transition]:
        if route[-1].ident != wp.ident:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    return route
  
  def get_star_route(self):
    # build a list of stars
    stars = list(self.arr.stars.keys())
    
    # find out which STAR we are using
    for i in range(len(stars)):
      print("{:2d}: {}".format(i, stars[i]))
    # get the user input
    star_index = input("Enter STAR Number (X to exit, return for none): ")
    
    if star_index == "X":
      return False
    elif star_index == "":
      return True
    else:
      # get the STAR
      star_name = stars[int(star_index)]
      print("{}".format(star_name))
      star = self.arr.stars[star_name]
      print("SID Chosen: {}".format(star_name))
    
    # clean up our route
    if star_name in self.route:
      self.route.remove(star_name)
    
    # choose the enroute transition
    enr = False
    enr_transitions = list(star.enroute_transistions.keys())
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
    
        # clean up our route
        if enr_transition in self.route:
          self.route.remove(enr_transition)
    
    # choose the runway transition
    rw = False
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
        if route[-1].ident != wp.ident:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    # runway transition
    if rw:
      for wp in routes[rw_transition]:
        if route[-1].ident != wp.ident:
          route.append(Waypoint(wp.ident, wp.latlon[0], wp.latlon[1]))
    
    return route
    
if __name__ == '__main__':
  # when this file is run directly, run this code
  # get the basic info from the user
  print("Initializing Databse...stand by")
  rp = RouteProcessor(r"C:\Data\CIFP", "CIFP_200716")
  
  status = True
  while status:
    status = rp.enter_route()
  
  print("Terminating")
      
  

