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
import procedure as procedure
import airspace as airspace

class NationalAirspace:
  """Once populated, this class contains descriptions of the nations airports, airways, airspace, and nav stations"""
  
  def __init__(self):
    """A NationalAirspace constructor.  Creates the holder for airspace information related to the nation"""
    # D  - VHF Navaids
    self.vors = {}  # dictionary of cf.Point instances, key=3 letter ID of the VOR i.e. DEN, SEY, or BJC
    
    # DB - NDB Navaids
    self.ndbs = {} # dictionary of cf.Point instances, key 2 or 3 letter ID of the NDB i.e. FN, or IHS
    
    # EA - Enroute Waypoints
    self.enroute_waypoints = {} # dictionary of cf.Point instances, key 5 letter ID of the waypoint i.e. LANDR or SAYGE
    
    # ER - Enroute Airways
    self.enroute_airways = {} # dictionary of TBD, key ID of the airway i.e. V85, J56, Q88
    
    # UR
    self.restrictive_airspace = {} # dictionary of TBD, key designator of the airspace i.e. COUGAR H
    
    # Airports encapsulate multiple P* records:
    #   PA - Airport Reference Point
    #   PC - Terminal Waypoints
    #   PD - SIDs
    #   PE - STARs
    #   PF - Instrument Approaches
    #   PG - Runways
    #   PN - Terminal NDBs
    self.airports = {} # dictionary of airport.Airport instances, key=4 letter ID of the airport i.e. KBJC, KDEN, KBID
    
    return
  
  def add_vor(self, point):
    self.vors[point.ident] = point
    return
  
  def add_ndb(self, point):
    self.ndbs[point.ident] = point
    return
  
  def add_enroute_waypoint(self, point):
    self.enroute_waypoints[point.ident] = point
    return
  
  def add_airway_fix(self, airway_fix):
    # if we don't already have this airway, create it
    if airway_fix.route_id not in self.enroute_airways:
      self.enroute_airways[airway_fix.route_id] = procedure.Airway()
    
    # save this fix to our airway
    self.enroute_airways[airway_fix.route_id].add_fix(airway_fix)
    
    return
  
  def add_airport(self, airport):
    self.airports[airport.ident] = airport
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
  
  
  
  
  