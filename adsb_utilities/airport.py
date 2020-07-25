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
    self.elevation_ft = self.reference_point.elevation_ft
    self.latitude = self.reference_point.latitude
    self.longitude = self.reference_point.longitude
            
    # initialize holders
    self.runways = cp.CIFPPointSet()
    self.ndbs = cp.CIFPPointSet()
    self.waypoints = cp.CIFPPointSet()
    self.ils = cp.CIFPPointSet()
    
    self.all_waypoints = {} # keys are all waypoints encountered at this airport, value is the section the waypoint is found in
    
    self.controlled_airspace = {} # dictionary containing AirspaceShapes
    
    # Procedure Dictionaries (dictionaries of Procedures)
    self.sids = {}  # dictionary containing Procedures, key is SID Name i.e. BAYLR6
    self.stars = {} # dictionary containing Procedures, key is STAR Name i.e. FLATI1
    self.approaches = {}  # dictionary containing Procedures, key is SID Name i.e. I30R
    
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
      # runways need declination too...use the airport declination
      point.set_declination(self.reference_point.declination)
      self.runways.add_point(point)
    elif point.code == "PI":
      self.ils.add_point(point)
           
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
    elif cr.code == "PI":
      print("Airport.add_cr: Localizer continuation record not supported")
    
    return 
  
  def add_nationwide_data(self, vors, ndbs, waypoints):
    """add D, DB, and EA data access"""
    self.D = vors
    self.DB = ndbs
    self.EA = waypoints
    return 
  
  def build_procedure_tracks(self, ident, proc_type, include_missed):
    if proc_type == "SID":
      print(ident)
      return self.sids[ident].build_procedure_shape(self.D, self.DB, self.EA, self.ndbs, self.waypoints, self.runways, self.ils, self.reference_point, self.elevation_ft, include_missed)
    elif proc_type == "STAR":
      print(ident)
      return self.stars[ident].build_procedure_shape(self.D, self.DB, self.EA, self.ndbs, self.waypoints, self.runways, self.ils, self.reference_point, self.elevation_ft, include_missed)
    elif proc_type == "APPROACH":
      print(ident)
      return self.approaches[ident].build_procedure_shape(self.D, self.DB, self.EA, self.ndbs, self.waypoints, self.runways, self.ils, self.reference_point, self.elevation_ft, include_missed)
    
    return None
  
  def add_procedure(self, procedure_record):
    # add any waypoints in this line to our list
    if procedure_record.fix_identifier not in self.all_waypoints:
      self.all_waypoints[procedure_record.fix_identifier] = procedure_record.fix_section
    if procedure_record.recommended_nav not in self.all_waypoints:
      self.all_waypoints[procedure_record.recommended_nav] = procedure_record.nav_section
    
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
    
  def get_localizers(self):
    # get a list of localizers for this airport
    return self.ils.get_points()
  
  def get_all_waypoints(self):
    # return a list of all waypoints this airport utilizes
    wp_dict = {}
    
    # work through our list of waypoints
    for wp, section in self.all_waypoints.items():
      if wp not in wp_dict:
        if section == "D ":
          pf = self.D.get_point(wp)
        elif section == "DB":
          pf = self.DB.get_point(wp)
        elif section == "EA":
          pf = self.EA.get_point(wp)
        elif section == "PC":
          pf = self.waypoints.get_point(wp)
        elif section == "PG":
          pf = self.runways.get_point(wp)
        elif section == "PN":
          pf = self.ndbs.get_point(wp)
        elif section == "PI":
          pf = self.ils.get_point(wp)
        elif section == "  ":
          pf = None
          continue
        else:
          print("Airport.get_all_waypoints: Error Section {} for waypoint {} not found".format(section, wp))
          pf = None
          continue
        
        if pf != None:
          wp_dict[wp] = (wp, pf.latlon, pf.ident, pf.description, pf.altitude)
    
    return list(wp_dict.values())

    
