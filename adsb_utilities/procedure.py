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

  May 25, 2020, ksb, created
"""

import cifp_functions as cf
import maptools as maptools
import cifp_point as cp

class Procedure:
  # Supported Procedures
  PROCEDURE_STAR = 1
  PROCEDURE_SID = 2
  PROCEDURE_APPROACH = 3
  
  # SID Route Types (PD, HD)
  D_TYPE_ENGINE_OUT_SID = '0'
  D_TYPE_SID_RUNWAY_TRANSITION = '1'
  D_TYPE_SID_COMMON_ROUTE = '2'
  D_TYPE_SID_ENROUTE_TRANSITION = '3'
  D_TYPE_RNAV_SID_RUNWAY_TRANSITION = '4'
  D_TYPE_RNAV_SID_COMMON_ROUTE = '5'
  D_TYPE_RNAV_SID_ENROUTE_TRANSITION = '6'
  D_TYPE_FMS_SID_RUNWAY_TRANSITION = 'F'
  D_TYPE_FMS_SID_COMMON_ROUTE = 'M'
  D_TYPE_FMS_SID_ENROUTE_TRANSITION = 'S'
  D_TYPE_VECTOR_SID_RUNWAY_TRANSITION = 'T'
  D_TYPE_VECTOR_SID_ENROUTE_TRANSITION = 'V'

  D_RUNWAY_TRANSITIONS = D_TYPE_SID_RUNWAY_TRANSITION + \
                         D_TYPE_RNAV_SID_RUNWAY_TRANSITION + \
                         D_TYPE_FMS_SID_RUNWAY_TRANSITION + \
                         D_TYPE_VECTOR_SID_RUNWAY_TRANSITION
  D_COMMON_ROUTES = D_TYPE_SID_COMMON_ROUTE + \
                    D_TYPE_RNAV_SID_COMMON_ROUTE + \
                    D_TYPE_FMS_SID_COMMON_ROUTE
  D_ENROUTE_TRANISTIONS = D_TYPE_SID_ENROUTE_TRANSITION + \
                          D_TYPE_RNAV_SID_ENROUTE_TRANSITION + \
                          D_TYPE_FMS_SID_ENROUTE_TRANSITION + \
                          D_TYPE_VECTOR_SID_ENROUTE_TRANSITION

  # STAR Route Types (PE, HE)
  E_TYPE_STAR_ENROUTE_TRANSITION = '1'
  E_TYPE_STAR_COMMON_ROUTE = '2'
  E_TYPE_STAR_RUNWAY_TRANSITION = '3'
  E_TYPE_RNAV_STAR_ENROUTE_TRANSITION = '4'
  E_TYPE_RNAV_STAR_COMMON_ROUTE = '5'
  E_TYPE_RNAV_STAR_RUNWAY_TRANSITION = '6'
  E_TYPE_PROFILE_DESCENT_ENROUTE_TRANSITION = '7'
  E_TYPE_PROFILE_DESCENT_COMMON_ROUTE = '8'
  E_TYPE_PROFILE_DESCENT_RUNWAY_TRANSITION = '9'
  E_TYPE_FMS_STAR_ENROUTE_TRANSITION = 'F'
  E_TYPE_FMS_STAR_COMMON_ROUTE = 'M'
  E_TYPE_FMS_STAR_ENROUTE_TRANSITION = 'S'

  E_ENROUTE_TRANSITIONS = E_TYPE_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_RNAV_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_PROFILE_DESCENT_ENROUTE_TRANSITION + \
                          E_TYPE_FMS_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_FMS_STAR_ENROUTE_TRANSITION
  E_COMMON_ROUTES = E_TYPE_STAR_COMMON_ROUTE + \
                    E_TYPE_RNAV_STAR_COMMON_ROUTE + \
                    E_TYPE_PROFILE_DESCENT_COMMON_ROUTE + \
                    E_TYPE_FMS_STAR_COMMON_ROUTE
  E_RUNWAY_TRANSITIONS = E_TYPE_STAR_RUNWAY_TRANSITION + \
                         E_TYPE_RNAV_STAR_RUNWAY_TRANSITION + \
                         E_TYPE_PROFILE_DESCENT_RUNWAY_TRANSITION

  # Approach Route Types (PF, HF)
  F_TYPE_APPROACH_TRANSITION = 'A'
  F_TYPE_LOCALIZER_BACKCOURSE_APPROACH = 'B'
  F_TYPE_VORDME_APPROACH = 'D'
  F_TYPE_FMS_APPROACH = 'F'
  F_TYPE_IGS_APPROACH = 'G'
  F_TYPE_RNP_APPROACH = 'H'
  F_TYPE_ILS_APPROACH = 'I'
  F_TYPE_GLS_APPROACH = 'J'
  F_TYPE_LOC_APPROACH = 'L'
  F_TYPE_MLS_APPROACH = 'M'
  F_TYPE_NDB_APPROACH = 'N'
  F_TYPE_GPS_APPROACH = 'P'
  F_TYPE_NDBDME_APPROACH = 'Q'
  F_TYPE_RNAV_APPROACH = 'R'
  F_TYPE_VORTAC_APPROACH = 'S'
  F_TYPE_TACAN_APPROACH = 'T'
  F_TYPE_SDF_APPROACH = 'U'
  F_TYPE_VOR_APPROACH = 'V'
  F_TYPE_MLSA_APPROACH = 'W'
  F_TYPE_LDA_APPROACH = 'X'
  F_TYPE_MLSBC_APPROACH = 'Y'
  F_TYPE_MISSED_APPROACH = 'Z'

  F_APPROACH_TRANSITIONS = F_TYPE_APPROACH_TRANSITION
  F_APPROACHES = F_TYPE_LOCALIZER_BACKCOURSE_APPROACH + \
                 F_TYPE_VORDME_APPROACH + \
                 F_TYPE_FMS_APPROACH + \
                 F_TYPE_IGS_APPROACH + \
                 F_TYPE_RNP_APPROACH + \
                 F_TYPE_ILS_APPROACH + \
                 F_TYPE_GLS_APPROACH + \
                 F_TYPE_LOC_APPROACH + \
                 F_TYPE_MLS_APPROACH + \
                 F_TYPE_NDB_APPROACH + \
                 F_TYPE_GPS_APPROACH + \
                 F_TYPE_NDBDME_APPROACH + \
                 F_TYPE_RNAV_APPROACH + \
                 F_TYPE_VORTAC_APPROACH + \
                 F_TYPE_TACAN_APPROACH + \
                 F_TYPE_SDF_APPROACH + \
                 F_TYPE_VOR_APPROACH + \
                 F_TYPE_MLSA_APPROACH + \
                 F_TYPE_LDA_APPROACH + \
                 F_TYPE_MLSBC_APPROACH + \
                 F_TYPE_MISSED_APPROACH

  APP_5_SPEED_KTS = 210.0 # knots (3.5 nm/min)
  APP_5_RATE_OF_CLIMB_FPNM = 500.0  # note feet/nm
  
  def __init__(self):
    # these dictionaries each contain a list of ProcedureRecords in order, the key is the transition name
    # SIDS/STARS
    self.runway_transitions = {}  
    
    self.enroute_transistions = {}
    
    # Approaches
    self.approach_transition = {}
    
    # All Procedures
    self.common_route = {} 
    
    return
  
  def add_procedure_record(self, pr):
    # we need to add this procedure data to the appropriate procedure dictionary
    if pr.subsection_code == "D":
      self.procedure_type = self.PROCEDURE_SID
      # SID
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.D_RUNWAY_TRANSITIONS:
        if pr.transition_identifier not in self.runway_transitions:
          self.runway_transitions[pr.transition_identifier] = []
        self.runway_transitions[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.D_COMMON_ROUTES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.D_ENROUTE_TRANISTIONS:
        if pr.transition_identifier not in self.enroute_transistions:
          self.enroute_transistions[pr.transition_identifier] = []
        self.enroute_transistions[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled SID route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))
    
    elif pr.subsection_code == "E":
      self.procedure_type = self.PROCEDURE_STAR
      # STAR
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.E_RUNWAY_TRANSITIONS:
        if pr.transition_identifier not in self.runway_transitions:
          self.runway_transitions[pr.transition_identifier] = []
        self.runway_transitions[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.E_COMMON_ROUTES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.E_ENROUTE_TRANSITIONS:
        if pr.transition_identifier not in self.enroute_transistions:
          self.enroute_transistions[pr.transition_identifier] = []
        self.enroute_transistions[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled STAR route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))
    
    elif pr.subsection_code == "F":
      self.procedure_type = self.PROCEDURE_APPROACH
      # IAP
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.F_APPROACH_TRANSITIONS:
        if pr.transition_identifier not in self.approach_transition:
          self.approach_transition[pr.transition_identifier] = []
        self.approach_transition[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.F_APPROACHES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled IAP route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))

    return
  
  def get_data(self, fix_id, fix_section):
    if fix_section == "D ": # VHF Navaid
      return self.d.get_data(fix_id)
    elif fix_section == "DB": # NDB
      return self.db.get_data(fix_id)
    elif fix_section == "EA": # Enroute Waypoint
      return self.ea.get_data(fix_id)
    elif fix_section == "PN": # Terminal NDB
      return self.pn.get_data(fix_id)
    elif fix_section == "PC": # Terminal Waypoint
      return self.pc.get_data(fix_id)
    elif fix_section == "PG": # Runway
      return self.pg.get_data(fix_id)
    elif fix_section == "PI": # ILS
      return self.pi.get_data(fix_id)
    elif fix_section == "PA": # Airport Reference
      return self.pa.get_data
    else:
      print("Procedure.get_fix: Unhandled fix:{} Section:{}".format(fix_id, fix_section))
    return None
  
  
  def get_fix(self, fix_id, fix_section):
    if fix_section == "D ": # VHF Navaid
      return self.d.get_point(fix_id)
    elif fix_section == "DB": # NDB
      return self.db.get_point(fix_id)
    elif fix_section == "EA": # Enroute Waypoint
      return self.ea.get_point(fix_id)
    elif fix_section == "PN": # Terminal NDB
      return self.pn.get_point(fix_id)
    elif fix_section == "PC": # Terminal Waypoint
      return self.pc.get_point(fix_id)
    elif fix_section == "PG": # Runway
      return self.pg.get_point(fix_id)
    elif fix_section == "PI": # ILS
      return self.pi.get_point(fix_id)
    elif fix_section == "PA": # Airport Reference
      return [(self.pa.latitude, self.pa.longitude), 
              self.pa.declination, 
              self.pa.ident, 
              self.pa.name, 
              self.pa.elevation_ft]
    else:
      print("Procedure.get_fix: Unhandled fix:{} Section:{}".format(fix_id, fix_section))
    return None
  
  def build_procedure_shape(self, d, db, ea, pn, pc, pg, pi, pa, elevation_ft):
    # save access to the fix databases
    self.d = d
    self.db = db
    self.ea = ea
    self.pn = pn
    self.pc = pc
    self.pg = pg
    self.pi = pi
    self.pa = pa
    self.elevation_ft = elevation_ft
    
    # build each section of the procedure on its own
    procedure = {}
    for key, route in self.process_route(self.runway_transitions).items():
      print("     "+key)
      procedure[key] = route
    for key, route in self.process_route(self.enroute_transistions).items():
      print("     "+key)
      procedure[key] = route
    for key, route in self.process_route(self.common_route).items():
      print("     "+key)
      procedure[key] = route
    for key, route in self.process_route(self.approach_transition).items():
      print("     "+key)
      procedure[key] = route
      
    return procedure
  
  def process_route(self, procedure_records):
    # this is one set of procedure_records for a single procedure (i.e. a set defining a transition)
    routes = {}
    
    # if this is an instrument approach, we want to start at an appropriate fix
    if self.procedure_type == self.PROCEDURE_APPROACH:
      armed = False
    else:
      armed = True
    
    intercept_heading = None
    intercept_heading_count = 0
    
    for key, prs in procedure_records.items():
      routes[key] = []
      for pr in prs:
        # get some easier accessors
        pt = pr.path_and_termination
        ft = pr.waypoint_description[3]
        
        # if we haven't found a start point, is this one?
        if armed == False:
          #        IAF        Int Fix       IAF-H        IAF-C         FAF          FAF-C
          if ft == "A" or ft == "B" or ft == "C" or ft == "D" or ft == "F" or ft == "I":
            armed = True
          else:
            continue
        
        if pt == "IF":
          # Initial Fix - simply add the fix to our route
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            fix[4] = pr.altitude1
          routes[key].append(fix)
          
        elif pt == "TF":
          # Track to Fix: Point A to Point B via great circle track - simply add the fix to our route
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            fix[4] = pr.altitude1
          routes[key].append(fix)
          
        elif pt == "CF":
          # Course to Fix: Course to a Fix
          # first get the fix
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            fix[4] = pr.altitude1
          declination = fix[1]
          
          # if we have an intercept angle, use that to find where to intercept
          if intercept_heading != None and len(routes[key]) > 0:
            # use the previous point as the starting point
            point = routes[key][-1]
            
            # find the intercept point
            intercept_ll = maptools.find_intersection(point[0], intercept_heading, fix[0], pr.magnetic_course, declination)

          else:
            # find the intercept point using the distance and bearing from the station
            # if we have a recommended navaid, use that declination
            if pr.recommended_nav != "":
              nav = self.get_fix(pr.recommended_nav, pr.nav_section)
              declination = nav[1]
              
            intercept_ll = maptools.forward(origin=fix[0],
                                            magnetic_course=(pr.magnetic_course+180.0)%360.0, 
                                            distance_nm=pr.distance,
                                            declination=declination)
          # build our new point out
          intercept = [intercept_ll, fix[1], None, "CF Intercept Point", pr.altitude1]
          
          # only add this point if there isn't already a point that is close...maybe we already added something
          if len(routes[key]) > 0:
            prev = routes[key][-1]
            dist = maptools.get_dist_ll(prev[0], intercept_ll)
            if dist > 500.0: # what if this is wrong?...might you ever have two fixes less than 1500' apart?...not likely, 4 seconds apart
              routes[key].append(intercept)
          else:
            routes[key].append(intercept)
          
          # now add the fix
          routes[key].append(fix)
          
        elif pt == "DF":
          # get our fix info
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            fix[4] = pr.altitude1
            
          if len(routes[key]) > 2:
            # Direct to Fix: standard rate turn to great circle direct
            pt0 = routes[key][-2] # if this doesn't exist we have no way to know the current heading
            pt1 = routes[key][-1]
            
            if pr.turn_direction == "R":
              clockwise = True
            else:
              clockwise = False
  
            shape = maptools.build_tangent_to_fix(pt0[0], pt1[0], fix[0], self.APP_5_SPEED_KTS, clockwise)
            
            # append the points
            for pt in shape:
              routes[key].append([pt, fix[1], None, "DF turn", pr.altitude1])
              
          # now append the fix
          routes[key].append(fix)
          
        elif pt == "FA":
          # Fix to an Altitude: Fix A to an altitude via a course
          # Course to an altitude
          if len(routes[key]) > 0:
            # get the previous point as the start of our climb
            prev = routes[key][-1]
            
            # figure how far we go in the climb
            if pr.altitude1 < prev[4]:
              # we are already above our altitude, skip this point
              continue
            
            # compute how far it will take to climb
            dz = pr.altitude1 - prev[4]
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # build our new point
            new_point = maptools.forward(origin=prev[0], magnetic_course=pr.magnetic_course, distance_nm=dist, declination=prev[1])
            routes[key].append([new_point, prev[1], "{}".format(pr.altitude1), "Course to Altitude Point, Position Estimated", pr.altitude1])
          else:
            # presume we are coming off a runway
            rw = self.get_departure_end(pr.transition_identifier) # (lat, lon, el_ft, new_ident, declination)
            
            # add this point to the list:
            routes[key].append([(rw[0], rw[1]), rw[4], rw[3], "{} Departure end".format(pr.transition_identifier)])
            
            # now figure how far we have to go in the climb
            dz = pr.altitude1 - rw[2]
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # # build our new point
            new_point = maptools.forward(origin=(rw[0], rw[1]), magnetic_course=pr.magnetic_course, distance_nm=dist, declination=rw[4])
            routes[key].append([new_point, rw[4], "{}".format(pr.altitude1), "Heading to Altitude Point, Position Estimated", pr.altitude1])
          
        elif pt == "FC":
          # Fix to a Course: Track a course from a fix for a distance
          # add the fix
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            fix[4] = pr.altitude1
          routes[key].append(fix)
          
        elif pt == "FD":
          # Fix to a DME distance: track a course from a fix to a distance from a DME
          print("Procedure.process_route: FD path and termination not supported")
        
        elif pt == "FM":
          # Fix to Manual Termination: track a course from a fix until notified by ATC
          # add a point 1 nm out
          point = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            point[4] = pr.altitude1
          man_fix = maptools.forward(origin=point[0], magnetic_course=pr.magnetic_course, distance_nm=1.0, declination=point[1])
          routes[key].append([man_fix, point[1], None, "FM Manual Termination", point[4]])
          
        elif pt == "CA":
          # Course to an altitude
          if len(routes[key]) > 0:
            # get the previous point as the start of our climb
            prev = routes[key][-1]
            
            # figure how far we go in the climb
            if pr.altitude1 < prev[4]:
              # we are already above our altitude, skip this point
              continue
            
            # compute how far it will take to climb
            dz = pr.altitude1 - self.elevation_ft
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # build our new point
            new_point = maptools.forward(origin=prev[0], magnetic_course=pr.magnetic_course, distance_nm=dist, declination=prev[1])
            routes[key].append([new_point, prev[1], "{}".format(pr.altitude1), "Course to Altitude Point, Position Estimated", pr.altitude1])
          else:
            # presume we are coming off a runway
            rw = self.get_departure_end(pr.transition_identifier) # (lat, lon, el_ft, new_ident, declination)
            
            # add this point to the list:
            routes[key].append([(rw[0], rw[1]), rw[4], rw[3], "{} Departure end".format(pr.transition_identifier)])
            
            # now figure how far we have to go in the climb
            dz = pr.altitude1 - rw[2]
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # # build our new point
            new_point = maptools.forward(origin=(rw[0], rw[1]), magnetic_course=pr.magnetic_course, distance_nm=dist, declination=rw[4])
            routes[key].append([new_point, rw[4], "{}".format(pr.altitude1), "Heading to Altitude Point, Position Estimated", pr.altitude1])
            
        elif pt == "CD":
          # Course to a DME Distance: track a course to a distance from a DME
          # get the previous point
          prev = routes[key][-1]
          
          # get the nav info
          nav = self.get_fix(pr.recommended_nav, pr.nav_section)
          
          # get the heading from the prev to the nav
          heading_to_nav = maptools.get_mag_heading(prev[0], nav[0], nav[1])
          
          dhdg = abs(heading_to_nav - pr.magnetic_course)
          
          if 90.0 <= dhdg and dhdg <= 270.0:
            # the heading to the nav and the course we are flying are opposite, we are heading away
            outbound_course = pr.magnetic_course
          else:
            # we are heading towards the station
            outbound_course = (pr.magnetic_course+180.0)%360.0
          
          point = maptools.forward(nav[0], outbound_course, pr.distance, nav[1])
          
          # add the point
          routes[key].append([point, nav[1], "{}".format(pr.altitude1), "Course to Distance", pr.altitude1])
          
        elif pt == "CI":
          # Course to an intercept: track a course to intercept the next leg
          if len(routes[key]) >= 2:
            # get the last point as the starting point
            p0 = routes[key][-2]
            p1 = routes[key][-1]
            
            if pr.turn_direction == "R":
              clockwise = True
            else:
              clockwise = False
            
            # get the nav we are intercepting
            nav = self.get_fix(pr.recommended_nav, pr.nav_section)
            nav_point = self.get_data(pr.recommended_nav, pr.nav_section)
            
            # are we dealing with a localizer?
            if cp.CIFPPoint.POINT_LOCALIZER_ONLY <= nav_point.style and nav_point.style <= cp.CIFPPoint.POINT_SDF:
              intercept_course = (nav_point.bearing+180.0)%360.0
            else:
              intercept_course = pr.theta
            
            turn_shape = maptools.turn_to_heading(p0[0], p1[0], pr.magnetic_course, nav[1], clockwise, self.APP_5_SPEED_KTS)
            
            # save the last point
            p2 = turn_shape[-1]
                        
            # add our turn points
            for point in turn_shape:
              routes[key].append([point, nav[1], None, "Turn to Heading", pr.altitude1])
            
            # now find the intercept point
            intercept = maptools.find_intersection(p2, pr.magnetic_course, nav[0], intercept_course, nav[1])
            routes[key].append([intercept, nav[1], None, "Intercept", pr.altitude1])
        
        elif pt == "CR":
          # Course to a Radial: track a course to intercept a VOR Radial
          print("Procedure.process_route: CR path and termination not supported")
          
        elif pt == "RF":
          # Constant Radius Arc: constant radius arc from pt A to pt B, center defined
          # get our previous point
          arc_begin = routes[key][-1]
          
          # now get our end point and center
          arc_end = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            arc_end[4] = pr.altitude1
          arc_center = self.get_fix(pr.center_fix, pr.center_section)
          if pr.altitude1 != None:
            arc_center[4] = pr.altitude1
          radius_nm = pr.arc_radius
          if pr.turn_direction == "R":
            clockwise = True
          else:
            clockwise = False
          shape = maptools.arc_path(arc_begin[0], arc_end[0], arc_center[0], radius_nm, clockwise, "RF Fix")
          
          for pt in shape:
            routes[key].append([pt, arc_end[1], None, "RF arc", arc_end[4]])
            
          # add our end point
          routes[key].append(arc_end)
          
        elif pt == "AF":
          # Arc to a Fix: DME arc from a radial to a fix
          arc_begin = routes[key][-1]
          arc_end = self.get_fix(pr.fix_identifier, pr.fix_section)
          arc_center = self.get_fix(pr.recommended_nav, pr.nav_section)
          if pr.turn_direction == "R":
            clockwise = True
          else:
            clockwise = False
          shape = maptools.arc_path(arc_begin[0], arc_end[0], arc_center[0], pr.rho, clockwise, "Arc to Fix")
          
          for pt in shape:
            routes[key].append([pt, arc_center[1], None, "DME Arc", pr.altitude1])
          
          # add our fix
          routes[key].append(arc_end)
            
        elif pt == "VA":
          # Heading to an altitude
          # we have no starting point...this is our very first point
          if len(routes[key]) == 0:
            # Probably a runway
            rw = self.get_departure_end(pr.transition_identifier) # (lat, lon, el_ft, new_ident, declination)
            
            # add this point to the list:
            routes[key].append([(rw[0], rw[1]), rw[4], rw[3], "{} Departure end".format(pr.transition_identifier), pr.altitude1])
            
            # now figure how far we have to go in the climb
            dz = pr.altitude1 - rw[2]
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # # build our new point
            new_point = maptools.forward(origin=(rw[0], rw[1]), magnetic_course=pr.magnetic_course, distance_nm=dist, declination=rw[4])
            routes[key].append([new_point, rw[4], "{}".format(pr.altitude1), "Heading to Altitude Point, Position Estimated", pr.altitude1])
          else:
            prev = routes[key][-1]
            
            # figure how far we have to go in the climb
            dz = pr.altitude1 - prev[4]
            dist = dz / self.APP_5_RATE_OF_CLIMB_FPNM
            
            # # build our new point
            new_point = maptools.forward(origin=prev[0], magnetic_course=pr.magnetic_course, distance_nm=dist, declination=prev[1])
            routes[key].append([new_point, prev[1], "{}".format(pr.altitude1), "Heading to Altitude Point, Position Estimated", pr.altitude1])
            
        elif pt == "VD":
          # Heading to a distance from a DME
          # get the previous point
          prev = routes[key][-1]
          
          # get the nav info
          nav = self.get_fix(pr.recommended_nav, pr.nav_section)
          
          # get the heading from the prev to the nav
          heading_to_nav = maptools.get_mag_heading(prev[0], nav[0], nav[1])
          
          dhdg = abs(heading_to_nav - pr.magnetic_course)
          
          if 90.0 <= dhdg and dhdg <= 270.0:
            # the heading to the nav and the course we are flying are opposite, we are heading away
            outbound_course = pr.magnetic_course
          else:
            # we are heading towards the station
            outbound_course = (pr.magnetic_course+180.0)%360.0
          
          point = maptools.forward(nav[0], outbound_course, pr.distance, nav[1])
          
          # add the point
          routes[key].append([point, nav[1], "{}".format(pr.altitude1), "Heading to Distance", pr.altitude1])
          
        elif pt == "VI":
          # Heading to an Intercept
          # if there are no points, maybe we are coming off a runway
          if len(routes[key]) == 0:
            # we know this is a SID and it is a runway transition, so lets figure our point from the runway
            # we have to be careful, the transition name may not be a specific runway...it may also include a B for both runways
            rw = self.get_departure_end(pr.transition_identifier) # (lat, lon, el_ft, new_ident, declination)
            
            # add this point to the list:
            routes[key].append([(rw[0], rw[1]), rw[4], rw[3], "{} Departure end".format(pr.transition_identifier), rw[2]])
          
          # save the heading we can use it to figure the next point on the next line
          intercept_heading = pr.magnetic_course
        
        elif pt == "VM":
          # Heading to Manual Termination
          if len(routes[key]) == 0:
            # we have no points, build one assuming the transition is a runway
            rw = self.get_departure_end(pr.transition_identifier) # (lat, lon, el_ft, new_ident, declination)
            
            # add this point to the list:
            routes[key].append([(rw[0], rw[1]), rw[4], rw[3], "{} Departure end".format(pr.transition_identifier), rw[2]])
            
          # get the starting point
          point = routes[key][-1]
          
          man_fix = maptools.forward(origin=point[0], magnetic_course=pr.magnetic_course, distance_nm=1.0, declination=point[1])
          routes[key].append([man_fix, point[1], None, "VM Manual Termination", point[4]])
          
        elif pt == "VR":
          # Heading to intercept a VOR radial
          point = routes[key][-1]
          fix = self.get_fix(pr.recommended_nav, pr.nav_section)
          
          intersection = maptools.find_intersection(point[0], pr.magnetic_course, fix[0], pr.theta, fix[1])
          
          routes[key].append([intersection, fix[1], None, "Heading to Radial Intercept", None])
          
        elif pt == "PI":
          # Procedure Turn
          fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          
          # we need to compute the outbound heading as it may not be listed if the fix is the recommended navaid
          if pr.turn_direction == "R":
            outbound_course = (pr.magnetic_course+45.0)%360.0
          else:
            outbound_course = (pr.magnetic_course-45.0+360.0)%360.0
          
          shape = maptools.build_procedure_turn(fix[0], outbound_course, pr.magnetic_course, pr.turn_direction, fix[1], pr.distance)
          for point in shape:
            routes[key].append([point, fix[1], None, "PI Procedure Turn", pr.altitude1])
          
          # save the heading we can use it to figure the next point on the next line
          intercept_heading = (outbound_course+180.0)%360.0
          
        elif pt == "HM" or pt == "HF" or pt == "HA":
          # Hold to Manual Termination, Hold to Fix, Hold to Altitude
          hold_fix = self.get_fix(pr.fix_identifier, pr.fix_section)
          if pr.altitude1 != None:
            hold_fix[4] = pr.altitude1
          inbound_course = pr.magnetic_course
          turn_direction = pr.turn_direction
          if pr.time == None:
            leg_distance_nm = pr.distance
          else:
            leg_distance_nm = pr.time*self.APP_5_SPEED_KTS/60.0
          
          shape = maptools.build_hold(hold_fix[0], inbound_course, turn_direction, leg_distance_nm, hold_fix[1], self.APP_5_SPEED_KTS)
          for pt in shape:
            routes[key].append([pt, hold_fix[1], None, "Hold Track", pr.altitude1])
      
      if intercept_heading != None:
        intercept_heading_count += 1
        if intercept_heading_count > 1:
          intercept_heading = None
          intercept_heading_count = 0
                        
    return routes  

  def get_departure_end(self, ident):
    # is this even a runway
    if ident[:2] != "RW":
      return None
    
    # get the opposite runway name
    num = int(ident[2:4])
    opp_num = (num+18)%36
    if opp_num == 0:
      opp_num = 36
      
    # build our runway name
    new_ident = "RW{:02d}".format(opp_num)
    if ident[4] == "L":
      new_ident += "R"
    elif ident[4] == "R":
      new_ident += "L"
    else:
      new_ident += ident[4]
    
    # if we have a legal name get the runway data
    if new_ident[4] != "B":
      rw = self.pg.get_point(new_ident)
      latitude = rw[0][0]
      longitude = rw[0][1]
      elevation = rw[4]
      declination = rw[1]
      
    else:
      # this applies to both runways, find the average position
      rwl = self.pg.get_point(new_ident[:4]+"L")
      rwr = self.pg.get_point(new_ident[:4]+"R")
      latitude = (rwl[0][0]+rwr[0][0])/2.0
      longitude = (rwl[0][1]+rwr[0][1])/2.0
      elevation = (rwl[4]+rwr[4])/2.0
      declination = (rwl[1]+rwr[1])/2.0
    
    return latitude, longitude, elevation, new_ident, declination

      
class ProcedureRecord:
  def __init__(self, record):
    # save the raw data
    self.record = record
    
    # parse the data
    if record[38] == '0' or record[38] == '1':
      self.parse_procedure_record()
    else:
      self.parse_procedure_continuation_record()
    return
  
  def parse_procedure_record(self):
    # SUSAP KDENK2DBAYLR64RW08  010         0        VA                     0826        + 05934     18000                        602692004
    # SUSAP KDENK2DBAYLR64RW08  020         0 E      VM                     0826                                                 602702004
    # SUSAP KDENK2DBAYLR64RW16L 010         0        VI                     1725                    18000                        602712004
    # SUSAP KDENK2DBAYLR64RW16L 020BRKEMK2PC0E       CF DEN K2      2509011524400105D   - 10000                                  602722004
    # SUSAP KDENK2DBAYLR64RW16L 030WAKIRK2PC0EE      TF                                 + 11000                                  602732004
    # SUSAP KDENK2DBAYLR64RW16R 010         0        VI                     1725                    18000                        602742004
    # SUSAP KDENK2DBAYLR64RW16R 020BRKEMK2PC0E       CF DEN K2      2509011524900098D   - 10000                                  602752004
    # SUSAP KDENK2DBAYLR64RW16R 030WAKIRK2PC0EE      TF                                 + 11000                                  602762004
    # SUSAP KDENK2DBAYLR64RW17L 010         0        VI                     1725                    18000                        602772004
    # SUSAP KDENK2DBAYLR64RW17L 020GOROCK2PC0E       CF DEN K2      2089004221900046D                                            602782004
    # SUSAP KDENK2DBAYLR64RW17L 030BRKEMK2PC0E       TF                                 - 10000                                  602792004
    # SUSAP KDENK2DBAYLR64RW17L 040WAKIRK2PC0EE      TF                                 + 11000                                  602802004
    # SUSAP KDENK2DBAYLR64RW17R 010         0        VI                     1725                    18000                        602812004
    # SUSAP KDENK2DBAYLR64RW17R 020GOROCK2PC0E       CF DEN K2      2089004221500037D                                            602822004
    # SUSAP KDENK2DBAYLR64RW17R 030BRKEMK2PC0E       TF                                 - 10000                                  602832004
    # SUSAP KDENK2DBAYLR64RW17R 040WAKIRK2PC0EE      TF                                 + 11000                                  602842004
    # SUSAP KDENK2DBAYLR64RW25  010         0        VA                     2625        + 05934     18000                        602852004
    # SUSAP KDENK2DBAYLR64RW25  020BRKEMK2PC0E       DF                                 - 10000                                  602862004
    # SUSAP KDENK2DBAYLR64RW25  030WAKIRK2PC0EE      TF                                 + 11000                                  602872004
    # SUSAP KDENK2DBAYLR64RW34B 010         0        VA                     3525        + 05934     18000                        602882004
    # SUSAP KDENK2DBAYLR64RW34B 020BRKEMK2PC0E   L   DF                                 - 10000                                  602892004
    # SUSAP KDENK2DBAYLR64RW34B 030WAKIRK2PC0EE      TF                                 + 11000                                  602902004
    # SUSAP KDENK2DBAYLR64RW35B 010         0        VA                     3525        + 05934     18000                        602912004
    # SUSAP KDENK2DBAYLR64RW35B 020BRKEMK2PC0E   L   DF                                 - 10000                                  602922004
    # SUSAP KDENK2DBAYLR64RW35B 030WAKIRK2PC0EE      TF                                 + 11000                                  602932004
    # SUSAP KDENK2DBAYLR65      010WAKIRK2PC0E       IF                                 + 11000     18000                        602942004
    # SUSAP KDENK2DBAYLR65      020TUULOK2PC0E       TF                                 + 14000                                  602952004
    # SUSAP KDENK2DBAYLR65      030HLTONK2PC0E       TF                                                                          602962004
    # SUSAP KDENK2DBAYLR65      040MTSUIK2PC0E       TF                                 + 16000                                  602972004
    # SUSAP KDENK2DBAYLR65      050BAYLRK2EA0EE      TF                                 + 17000                                  602982004
    # SUSAP KDENK2DBAYLR66HBU   010BAYLRK2EA0E       IF                                 + 17000     18000                        602992004
    # SUSAP KDENK2DBAYLR66HBU   020BOBBAK2EA0E       TF                                                                          603002004
    # SUSAP KDENK2DBAYLR66HBU   030HBU  K2D 0VE      TF                                 - FL230                                  603012004
    # SUSAP KDENK2DBAYLR66TEHRU 010BAYLRK2EA0E       IF                                 + 17000     18000                        603022004
    # SUSAP KDENK2DBAYLR66TEHRU 020BOBBAK2EA0E       TF                                                                          603032004
    # SUSAP KDENK2DBAYLR66TEHRU 030TEHRUK2EA0EE      TF                                                                          603042004
    #
    # SUSAP KDENK2EFLATI14FOLSM 010FOLSMK2PC0E       IF                                             18000                        611942004
    # SUSAP KDENK2EFLATI14FOLSM 020BBOCOK2PC0E       TF                                                                          611952004
    # SUSAP KDENK2EFLATI14FOLSM 030FLATIK2PC0EE      TF                                 + FL190                                  611962004
    # SUSAP KDENK2EFLATI14MJANE 010MJANEK1PC0E       IF                                             18000                        611972004
    # SUSAP KDENK2EFLATI14MJANE 020MSTSHK1PC0E       TF                                                                          611982004
    # SUSAP KDENK2EFLATI14MJANE 030HIPEEK2PC0E       TF                                 + FL270                                  611992004
    # SUSAP KDENK2EFLATI14MJANE 040FOLSMK2PC0E       TF                                                                          612002004
    # SUSAP KDENK2EFLATI14MJANE 050BBOCOK2PC0E       TF                                                                          612012004
    # SUSAP KDENK2EFLATI14MJANE 060FLATIK2PC0EE      TF                                 + FL190                                  612022004
    # SUSAP KDENK2EFLATI14TOFUU 010TOFUUK1PC0E       IF                                             18000                        612032004
    # SUSAP KDENK2EFLATI14TOFUU 020GNOLAK1PC0E       TF                                                                          612042004
    # SUSAP KDENK2EFLATI14TOFUU 030HIPEEK2PC0E       TF                                 + FL270                                  612052004
    # SUSAP KDENK2EFLATI14TOFUU 040FOLSMK2PC0E       TF                                                                          612062004
    # SUSAP KDENK2EFLATI14TOFUU 050BBOCOK2PC0E       TF                                                                          612072004
    # SUSAP KDENK2EFLATI14TOFUU 060FLATIK2PC0EE      TF                                 + FL190                                  612082004
    # SUSAP KDENK2EFLATI15      010FLATIK2PC0E       IF                                 + FL190     18000                        612092004
    # SUSAP KDENK2EFLATI15      020ELLDOK2PC0EE      TF                                 B FL21016000     250                     612102004
    # SUSAP KDENK2EFLATI16RW07  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612112004
    # SUSAP KDENK2EFLATI16RW07  020TOTTTK2PC0E       TF                                 B 1700015000                             612122004
    # SUSAP KDENK2EFLATI16RW07  030YESSSK2PC0E       TF                                                                          612132004
    # SUSAP KDENK2EFLATI16RW07  040BAACKK2PC0E       TF                                 + 13000                                  612142004
    # SUSAP KDENK2EFLATI16RW07  050BABAAK2PC0E       TF                                 B 1400012000                             612152004
    # SUSAP KDENK2EFLATI16RW07  060HIMOMK2PC0EY      TF                                   11000          210                     612162004
    # SUSAP KDENK2EFLATI16RW07  070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612172004
    # SUSAP KDENK2EFLATI16RW08  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612182004
    # SUSAP KDENK2EFLATI16RW08  020TOTTTK2PC0E       TF                                 B 1700015000                             612192004
    # SUSAP KDENK2EFLATI16RW08  030YESSSK2PC0E       TF                                                                          612202004
    # SUSAP KDENK2EFLATI16RW08  040BAACKK2PC0E       TF                                 + 13000                                  612212004
    # SUSAP KDENK2EFLATI16RW08  050BABAAK2PC0E       TF                                 B 1400012000                             612222004
    # SUSAP KDENK2EFLATI16RW08  060HIMOMK2PC0EY      TF                                   11000          210                     612232004
    # SUSAP KDENK2EFLATI16RW08  070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612242004
    # SUSAP KDENK2EFLATI16RW16B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612252004
    # SUSAP KDENK2EFLATI16RW16B 020BSAFEK2PC0E       TF                                 - 15000                                  612262004
    # SUSAP KDENK2EFLATI16RW16B 030BDUNNK2PC0E       TF                                 B 1500014000     210                     612272004
    # SUSAP KDENK2EFLATI16RW16B 040TSHNRK2PC0EE      TF                                   13000                                  612282004
    # SUSAP KDENK2EFLATI16RW17B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612292004
    # SUSAP KDENK2EFLATI16RW17B 020BSAFEK2PC0E       TF                                 - 15000                                  612302004
    # SUSAP KDENK2EFLATI16RW17B 030BDUNNK2PC0E       TF                                 B 1500014000     210                     612312004
    # SUSAP KDENK2EFLATI16RW17B 040TSHNRK2PC0EE      TF                                   13000                                  612322004
    # SUSAP KDENK2EFLATI16RW25  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612332004
    # SUSAP KDENK2EFLATI16RW25  020TOTTTK2PC0E       TF                                 B 1700015000                             612342004
    # SUSAP KDENK2EFLATI16RW25  030YESSSK2PC0E       TF                                                                          612352004
    # SUSAP KDENK2EFLATI16RW25  040SKEWDK2PC0E       TF                                 B 1500013000                             612362004
    # SUSAP KDENK2EFLATI16RW25  050LEKEEK2PC0E       TF                                 + 12000                                  612372004
    # SUSAP KDENK2EFLATI16RW25  060XCUTVK2PC0E       TF                                                                          612382004
    # SUSAP KDENK2EFLATI16RW25  070CAPTJK2PC0EY      TF                                   11000          210                     612392004
    # SUSAP KDENK2EFLATI16RW25  080CAPTJK2PC0EE      FM DEN K2      019901060825    D                                            612402004
    # SUSAP KDENK2EFLATI16RW26  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612412004
    # SUSAP KDENK2EFLATI16RW26  020TOTTTK2PC0E       TF                                 B 1700015000                             612422004
    # SUSAP KDENK2EFLATI16RW26  030YESSSK2PC0E       TF                                                                          612432004
    # SUSAP KDENK2EFLATI16RW26  040SKEWDK2PC0E       TF                                 B 1500013000                             612442004
    # SUSAP KDENK2EFLATI16RW26  050LEKEEK2PC0E       TF                                 + 12000                                  612452004
    # SUSAP KDENK2EFLATI16RW26  060XCUTVK2PC0E       TF                                                                          612462004
    # SUSAP KDENK2EFLATI16RW26  070CAPTJK2PC0EY      TF                                   11000          210                     612472004
    # SUSAP KDENK2EFLATI16RW26  080CAPTJK2PC0EE      FM DEN K2      019901060825    D                                            612482004
    # SUSAP KDENK2EFLATI16RW34B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612492004
    # SUSAP KDENK2EFLATI16RW34B 020TOTTTK2PC0E       TF                                 B 1700015000                             612502004
    # SUSAP KDENK2EFLATI16RW34B 030YESSSK2PC0E       TF                                                                          612512004
    # SUSAP KDENK2EFLATI16RW34B 040BAACKK2PC0E       TF                                 + 13000                                  612522004
    # SUSAP KDENK2EFLATI16RW34B 050BABAAK2PC0E       TF                                 B 1400012000                             612532004
    # SUSAP KDENK2EFLATI16RW34B 060HIMOMK2PC0EY      TF                                   11000          210                     612542004
    # SUSAP KDENK2EFLATI16RW34B 070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612552004
    # SUSAP KDENK2EFLATI16RW35L 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612562004
    # SUSAP KDENK2EFLATI16RW35L 020TOTTTK2PC0E       TF                                 B 1700015000                             612572004
    # SUSAP KDENK2EFLATI16RW35L 030YESSSK2PC0E       TF                                                                          612582004
    # SUSAP KDENK2EFLATI16RW35L 040BAACKK2PC0E       TF                                 + 13000                                  612592004
    # SUSAP KDENK2EFLATI16RW35L 050BABAAK2PC0E       TF                                 B 1400012000                             612602004
    # SUSAP KDENK2EFLATI16RW35L 060HIMOMK2PC0EY      TF                                   11000          210                     612612004
    # SUSAP KDENK2EFLATI16RW35L 070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612622004
    # SUSAP KDENK2EFLATI16RW35R 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612632004
    # SUSAP KDENK2EFLATI16RW35R 020TOTTTK2PC0E       TF                                 B 1700015000                             612642004
    # SUSAP KDENK2EFLATI16RW35R 030YESSSK2PC0E       TF                                                                          612652004
    # SUSAP KDENK2EFLATI16RW35R 040SKEWDK2PC0E       TF                                 B 1500013000                             612662004
    # SUSAP KDENK2EFLATI16RW35R 050LEKEEK2PC0E       TF                                 + 12000                                  612672004
    # SUSAP KDENK2EFLATI16RW35R 060XCUTVK2PC0E       TF                                                                          612682004
    # SUSAP KDENK2EFLATI16RW35R 070HDGHGK2PC0E       TF                                 B 1400012000                             612692004
    # SUSAP KDENK2EFLATI16RW35R 080FFFATK2PC0E       TF                                                                          612702004
    # SUSAP KDENK2EFLATI16RW35R 090DOGGGK2PC0EY      TF                                   11000          210                     612712004
    # SUSAP KDENK2EFLATI16RW35R 100DOGGGK2PC0EE      FM DEN K2      088500741727    D                                            612722004
    # 
    # SUSAP KDENK2FH16RZ ACLFFF 010CLFFFK2PC0E  B    IF                                   11000     18000210              A-FS   617831410
    # SUSAP KDENK2FH16RZ ACLFFF 020CEPEEK2PC0E    010TF                                 + 10000                           A FS   617841310
    # SUSAP KDENK2FH16RZ ACLFFF 030AAGEEK2PC0E   R010RF       0027503525    08250043    + 08600                 CFFNB K2PCA FS   617851310
    # SUSAP KDENK2FH16RZ ACLFFF 040JABROK2PC0E    010TF                                 + 08300                           A FS   617861310
    # SUSAP KDENK2FH16RZ ACLFFF 050JETSNK2PC0EE  R010RF       0027500825    17250043    + 07000                 CFPQD K2PCA FS   617871310
    # SUSAP KDENK2FH16RZ ASAKIC 010SAKICK2PC0E  B    IF                                             18000                 A FS   617881310
    # SUSAP KDENK2FH16RZ ASAKIC 020JETSNK2PC0EE   010TF                                 + 07000                           A FS   617891310
    # SUSAP KDENK2FH16RZ H      020JETSNK2PC1E  F    IF                                 + 07000     18000       RW16RBK2PGA FS   617901310
    # SUSAP KDENK2FH16RZ H      020JETSNK2PC2W                                                A031A011                      FS   617911310
    # SUSAP KDENK2FH16RZ H      030RW16RK2PG0GY M 031TF                                   05377             -300          A FS   617921212
    # SUSAP KDENK2FH16RZ H      040         0  M     CA                     1725        + 05900                           A FS   617931212
    # SUSAP KDENK2FH16RZ H      050BINBEK2EA0EY      DF                                 + 10000                           A FS   617941212
    # SUSAP KDENK2FH16RZ H      060BINBEK2EA0EE  R   HM                     25750070    + 10000                           A FS   617951212
    #
    # SUSAP KEIKK2FVDM-A ABJC   010BJC  K2D 0V       IF                                             18000                 3  C   752131301
    # SUSAP KEIKK2FVDM-A ABJC   020SHATZK2PC0E       TF                                 + 08200                           3  C   752141310
    # SUSAP KEIKK2FVDM-A ABJC   030SHATZK2PC0EE AR   HF                     2030T010    + 07200                           3  C   752151310
    # SUSAP KEIKK2FVDM-A D      020SHATZK2PC0E  F    IF BJC K2      02300135        D   + 07200     18000       BJC   K2D 3  C   752161310
    # SUSAP KEIKK2FVDM-A D      021SD203K2PC0E A     CF BJC K2      0231009520300040D   + 06560              000          3  C   752171301
    # SUSAP KEIKK2FVDM-A D      030MAGIHK2PC0EY M    CF BJC K2      0230007520300020D     05880              000          3  C   752181310
    # SUSAP KEIKK2FVDM-A D      040         0  M     CA                     2030        + 05519                           3  C   752191406
    # SUSAP KEIKK2FVDM-A D      050SHATZK2PC0EY  R   CFYBJC K2      0230013502300070D   + 07200                           3  C   752201310
    # SUSAP KEIKK2FVDM-A D      060SHATZK2PC0EE  R   HM                     2030T010    + 07200                           3  C   752211310
    # 
    # SUSAP KBJCK2FI30R  ANSPYR 010NSPYRK2PC0E  A    FC TDD K3      2278234235140016D     07000     18000                 0 PS   294591412
    # SUSAP KBJCK2FI30R  ANSPYR 020BAAWLK2PC0EE B    CF IBJCK2      1153010035140020PI    07000                           0 PS   294601412
    # SUSAP KBJCK2FI30R  AROKXX 010ROKXXK2PC0E  A    IF                                             18000210              0-PS   294611412
    # SUSAP KBJCK2FI30R  AROKXX 020PLAAYK2PC0E       TF                                 + 07000                           0 PS   294621412
    # SUSAP KBJCK2FI30R  AROKXX 030LAWNGK2PC0E       TF                                   07000                           0 PS   294631412
    # SUSAP KBJCK2FI30R  AROKXX 040LAWNGK2PC0E       FC TDD K3      2283229324450009D     07000                           0 PS   294641412
    # SUSAP KBJCK2FI30R  AROKXX 050BAAWLK2PC0EE B    CF IBJCK2      1153010024450020PI    07000                           0 PS   294651412
    # SUSAP KBJCK2FI30R  I      010BAAWLK2PC0E  I    IF IBJCK2      11530100        PI  I 070000700018000                 0 NS   294661412
    # SUSAP KBJCK2FI30R  I      020ALIKEK2PC0E  F    CF IBJCK2      1153006029500040PI  H 0700007000        -300BJC   K2D 0 NS   294671412
    # SUSAP KBJCK2FI30R  I      030RW30RK2PG0GY M    CF IBJCK2      1153001629500043PI    05618             -300          0 NS   294681412
    # SUSAP KBJCK2FI30R  I      040         0  M     CA                     2953        + 06380                           0 NS   294691412
    # SUSAP KBJCK2FI30R  I      050         0        VI                     3600                                          0 NS   294701412
    # SUSAP KBJCK2FI30R  I      060HYGENK2EA0EY      CF FQF K2      3060037930600050D   + 10200                           0 NS   294711412
    # SUSAP KBJCK2FI30R  I      070HYGENK2EA0EE  R   HM                     3060T010    + 10200                           0 NS   294721412
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    self.airport = self.record[6:10].rstrip() # KDEN
    self.subsection_code = self.record[12] # D
    self.procedure_identifier = self.record[13:19].rstrip() # BAYLR6
    self.route_type = self.record[19] # 6
    self.transition_identifier = self.record[20:25]
    self.sequence_number = int(self.record[26:29])
    # get the fix identifier, keep the whole thing for runways
    fix_id = self.record[29:34]
    if fix_id[:2] == "RW":
      self.fix_identifier = fix_id
    else:
      self.fix_identifier = fix_id.rstrip()
    self.fix_section = self.record[36:38]
    self.continuation_count = int(self.record[38])
    self.waypoint_description = self.record[39:43]
    self.turn_direction = self.record[43]
    self.path_and_termination = self.record[47:49]
    self.recommended_nav = self.record[50:54].rstrip()
    self.arc_radius = cf.parse_float(self.record[56:62],1000.0)
    self.theta = cf.parse_float(self.record[62:66], 10.0) # bearing
    self.rho = cf.parse_float(self.record[66:70], 10.0) # distance
    self.magnetic_course = cf.parse_float(self.record[70:74], 10.0) # course
    if self.record[74] == 'T':
      # time distance
      self.time = cf.parse_float(self.record[75:78], 10.0)
      self.distance = None 
    else:
      # nautical mile distance
      self.time = None 
      self.distance = cf.parse_float(self.record[74:78], 10.0)
    self.nav_section = self.record[78:80]
    self.altitude_type = self.record[82]
    self.altitude1 = self.parse_altitude(self.record[84:89].rstrip())
    self.altitude2 = self.parse_altitude(self.record[89:94].rstrip())
    self.speed_limit = self.record[99:102]
    self.center_fix = self.record[106:111]
    self.center_section = self.record[114:116]
    
    return
  
  def parse_altitude(self, s):
    if len(s) == 0:
      return None
    else:
      if s[:2] == "FL":
        alt = int(s[2:])*100
      else:
        alt = int(s)
    return alt
  
  def parse_procedure_continuation_record(self):
    # SUSAP KDENK2FH16RZ H      020JETSNK2PC2W                                                A031A011                      FS   617911310
    # SUSAP KBJCK2FR12L  R      020PYYPPK2PC2WALP        N          ALNAV                                                   JS   294951709
    # SUSAP KBJCK2FR30L  R      020HESDAK2PC2WALPV       ALNAV/VNAV ALNAV                                                   JS   295081412
    # SUSAP KBJCK2FR30R  R      020ALIKEK2PC2WALPV       ALNAV/VNAV ALNAV                                                   JS   295211412
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # W is not in version 17 documentation...not sure what to do with it
    if self.record[39] != "W":
      print("ProcedureRecord: Unhandled continuation record: {}".format(self.record.rstrip()))
    
    return
    
