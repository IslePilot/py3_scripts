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


import procedure as procedure
import airspace as airspace

class Airport:
  def __init__(self, pa_point):
    # save the reference cifp_point
    self.reference_point = pa_point
    self.airport = self.reference_point.airport
    self.ident = self.reference_point.ident
            
    # initialize holders
    self.runways = cp.CIFPPointSet()
    self.ndbs = cp.CIFPPointSet()
    self.waypoints = cp.CIFPPointSet()
    
    self.controlled_airspace = {} # dictionary containing AirspaceShapes
    
    # Procedure Dictionaries (dictionaries of Procedures)
    self.sids = {}
    self.stars = {}
    self.approaches = {}
    
    return 
  
  def add_point(self, point):
    if point.code == "PN":
      # terminal NDB
      self.ndbs.add_point(point)
    elif point.code == "PC":
      # terminal waypoint
      self.waypoints.add_point(point)
    elif point.code == "PG":
      # runways
      self.runways.add_point(point)      
    return 
  
  def add_cr(self, cr):
    # essentially do nothing for now
    if cr.code == "PA":
      print("Airport.add_cr: Airport Reference continuation record not supported")
    elif cr.code ==  "PN":
      print("Airport.add_cr: Terminal NDB continuation record not supported")
    elif cr.code ==  "PC":
      print("Airport.add_cr: Terminal Waypoint continuation record not supported")
    elif cr.code ==  "PG":
      print("Airport.add_cr: Runway continuation record not supported")
    
    return 
  
  def add_nationwide_data(self, vors, ndbs, waypoints):
    """add D, DB, and EA data access"""
    self.vors = vors
    self.enroute_ndbs = ndbs
    self.enroute_waypoints = waypoints
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
  
  def get_runways(self):
    # get a list of runways, position, and description
    return self.runways.get_points()
  
  def get_ndbs(self):
    # get a list of terminal NDBs, position, and description
    return self.ndbs.get_points()
  
  def get_waypoints(self):
    # get a list of terminal waypoints, position, and description
    return self.waypoints.get_points()
    

