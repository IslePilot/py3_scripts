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

import cifp_point as cp
import airway as airway


import airspace as airspace

class NationalAirspace:
  """Once populated, this class contains descriptions of the nations airports, airways, airspace, and nav stations"""
  
  def __init__(self):
    """A NationalAirspace constructor.  Creates the holder for airspace information related to the nation"""
    # D  - VHF Navaids
    self.vors = cp.CIFPPointSet()
    
    # DB - NDB Navaids
    self.ndbs = cp.CIFPPointSet()
    
    # EA - Enroute Waypoints
    self.enroute_waypoints = cp.CIFPPointSet()
    
    # Airports encapsulate multiple records:
    #   PA - Airport Reference Point
    #   PC - Terminal Waypoints
    #   PD - SIDs
    #   PE - STARs
    #   PF - Instrument Approaches
    #   PG - Runways
    #   PN - Terminal NDBs
    #   UC - Controlled Airspace
    self.airports = {} # dictionary of airport.Airport, key is airport ident i.e. KBJC
    
    # ER - Enroute Airways
    self.enroute_airways = {} # dictionary of Airways, key ID of the airway i.e. V85, J56, Q88
    
    # UR
    self.restrictive_airspace = {} # dictionary containing AirspaceShapes, key is "<airspace_designation> Section <multiple_code>"
    
    return
  
  def add_airway_fix(self, airway_fix):
    # if we don't already have this airway, create it
    if airway_fix.route_id not in self.enroute_airways:
      self.enroute_airways[airway_fix.route_id] = airway.Airway()
    
    # save this fix to our airway
    self.enroute_airways[airway_fix.route_id].add_fix(airway_fix)
    
    return
  
  def add_airspace(self, airspace_record):
    # identify where this airspace record belongs
    key = "{} Section {}".format(airspace_record.airspace_designation, airspace_record.multiple_code)
    
    # add this key if it doesn't already exist
    if key not in self.restrictive_airspace:
      self.restrictive_airspace[key] = airspace.AirspaceShape()
    
    # add the record
    self.restrictive_airspace[key].add_airspace_record(airspace_record)
  
  def has_airport(self, ident):
    if ident in self.airports:
      return True
    return False
  
  def get_vor(self, ident):
    return self.vors.get_point(ident)
  def get_vors(self):
    # get a list of the vors, location, and description
    return self.vors.get_points()
  
  def get_ndb(self, ident):
    return self.ndbs.get_point(ident)
  def get_ndbs(self):
    # get a list of the ndbs, location, and description
    return self.ndbs.get_points()
  
  def get_waypoint(self, ident):
    return self.enroute_waypoints.get_point(ident)
  def get_waypoints(self):
    # get a list of the enroute waypoints, location, and description
    return self.enroute_waypoints.get_points()
  
  
  def get_runway(self, airport, rw):
    return self.airports[airport].runways.get_point(rw)
  def get_runways(self, airport):
    return self.airports[airport].get_runways()
  
  def get_terminal_waypoint(self, airport, ident):
    return self.airports[airport].waypoints.get_point(ident)
  def get_terminal_waypoints(self, airport):
    return self.airports[airport].get_waypoints()
  
  def get_terminal_ndb(self, airport, ident):
    return self.airports[airport].ndbs.get_point(ident)
  def get_terminal_ndbs(self, airport):
    return self.airports[airport].get_ndbs()
  
  def build_procedure_tracks(self, airport, ident, proc_type):
    # set the databases for this airport
    self.airports[airport].add_nationwide_data(self.vors, self.ndbs, self.enroute_waypoints)
    return self.airports[airport].build_procedure_tracks(ident, proc_type)
  
  def get_airway(self, route_id, initial_fix=None, final_fix=None, include_end_points=True):
    if route_id in self.enroute_airways:
      # airway exists
      return self.enroute_airways[route_id].get_fixes(initial_fix, final_fix, self.vors, self.ndbs, self.enroute_waypoints, include_end_points)
    else:
      print("NationalAirspace.get_airway: Airway {} doesn't exist".format(route_id))
    
    return []
    
  
  
  
  