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

class Airport:
  def __init__(self, pa_record):
    # save the reference point
    self.reference_point = pa_record
    self.airport = self.reference_point.airport
    self.ident = self.reference_point.ident
            
    # initialize holders (dictionaries of Points)
    self.runways = {}
    self.ndbs = {}
    self.waypoints = {}
    
    self.controlled_airspace = {} # dictionary containing AirspaceShapes
    
    # Procedure Dictionaries (dictionaries of Procedrues)
    self.sids = {}
    self.stars = {}
    self.approaches = {}
    
    return 
  
  def add_nationwide_data(self, vors, ndbs, waypoints):
    """add D, DB, and EA data access"""
    self.vors = vors
    self.enroute_ndbs = ndbs
    self.enroute_waypoints = waypoints
    return 
  
  def add_waypoint(self, point):
    self.waypoints[point.ident] = point
    return
  
  def add_ndb(self, point):
    self.ndbs[point.ident] = point
    return
  
  def add_runway(self, point):
    self.runways[point.name] = point
    return
  
  def add_procedure(self, procedure_record):
    if procedure_record.subsection_code == "D":
      # Standard Instrument Departures (SIDS)
      # if this procedure doesn't exist, create it (i.e. BAYLR6)
      if procedure_record.procedure_identifier not in self.sids:
        self.sids[procedure_record.procedure_identifier] = procedure.Procedure()
      
      # add the procedure_record to the Procedure
      self.sids[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    elif procedure_record.subsection_code == "E":
      # Standard Terminal Arrivals (STARS)
    # if this procedure doesn't exist, create it (i.e. FLATI1)
      if procedure_record.procedure_identifier not in self.stars:
        self.stars[procedure_record.procedure_identifier] = procedure.Procedure()
      
      # add the procedure_record to the Procedure
      self.stars[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    elif procedure_record.subsection_code == "F":
      # Instrument Approach Procedures
      if procedure_record.procedure_identifier not in self.approaches:
        self.approaches[procedure_record.procedure_identifier] = procedure.Procedure()
      
      # add the procedure_record to the Procedure
      self.approaches[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    else:
      print("Airport.add_procedure: Skipping Unknown Subsection Code: {}".format(procedure_record.subsection_code))
    
    return
  
  def add_airspace(self, airspace_record):
    # identify where this airspace record belongs
    key = "Class {} Section {}".format(airspace_record.airspace_classification, airspace_record.multiple_code)
    
    # add this key if it doesn't already exist
    if key not in self.controlled_airspace:
      self.controlled_airspace[key] = airspace.AirspaceShape()
    
    # add the record
    self.controlled_airspace[key].add_airspace_record(airspace_record)
    
    return 
    


