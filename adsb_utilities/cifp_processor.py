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

  May 12, 2020, ksb, created
"""


import cifp_functions as cf
import cifp_point as cp
import airway as airway

import airspace as airspace
import airport as airport
import procedure as procedure
import nation as nation

import simplekml
#import gpxpy
    

class CIFPReader:
    
  def __init__(self, path, cifp_version,  lat_min, lat_max, lon_min, lon_max):
    # save the filename
    self.filename = path+'\\'+cifp_version+'\\FAACIFP18'
    
    # save our boundaries
    self.lat_min = lat_min
    self.lat_max = lat_max
    self.lon_min = lon_min
    self.lon_max = lon_max
    
    # create our data holder
    self.usa = nation.NationalAirspace()
    
    # process the data file
    self.process_file()
    
    # debug testing
    self.debug()
    
    return
  
  def debug(self):
    # debug test
    #                          Airport       Procedure    
    # build a simple kml file to test
    kml = simplekml.Kml()
    kml.document.name = "CIFP Processor Test"
    
    print("=SID =================================")
    for route in self.usa.airports['KDEN'].sids['BAYLR6'].runway_transitions.values():
      for pr in route:
        print("RW {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.usa.airports['KDEN'].sids['BAYLR6'].common_route.values():
      for pr in route:
        print("CR {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.usa.airports['KDEN'].sids['BAYLR6'].enroute_transistions.values():
      for pr in route:
        print("ET {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    
    print("=STAR =================================")
    routes = self.usa.build_procedure_tracks('KDEN', 'FLATI1', 'STAR')
    
    # create a folder for this STAR
    star_folder = kml.newfolder(name='FLATI1')
    track_folder = star_folder.newfolder(name = "Tracks")
    fix_folder = star_folder.newfolder(name = "Fixes")
    
    for key, val in routes.items():
      coords = []
      print(key)
      for pt in val:
        # put the coords in the kml form
        print(pt)
        if len(pt) == 2:
          coords.append((pt[1], pt[0]))
        else:
          coords.append((pt[0][1], pt[0][0]))
          pnt = fix_folder.newpoint(name=pt[2], coords=[coords[-1]], description=pt[3])
          pnt.lookat = simplekml.LookAt(latitude=pt[0][0],longitude=pt[0][1], range=15000., heading=0, tilt=0)
          pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
      
      line = track_folder.newlinestring(name=key, coords=coords)
      line.style.linestyle.width = 4
      line.style.linestyle.color = simplekml.Color.blue





    
    print("==================================")
    
    #                          Airport           Procedure      
    for route in self.usa.airports['KDEN'].approaches['H16RZ'].approach_transition.values():
      for pr in route:
        print("AT {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.usa.airports['KDEN'].approaches['H16RZ'].common_route.values():
      for pr in route:
        print("IP {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))

    print("==================================")
    print(self.usa.restrictive_airspace["COUGAR H Section A"].name)
    print(self.usa.restrictive_airspace["COUGAR H Section A"].controlling_agency)
    print(self.usa.restrictive_airspace["COUGAR H Section A"].build_airspace_shape())
    
    print("==================================")
    print(self.usa.airports['KBKF'].controlled_airspace["Class D Section B"].name)
    print(self.usa.airports['KBKF'].controlled_airspace["Class D Section B"].build_airspace_shape())
    
    
    
    print("= Airway Test =================================")
    print(self.usa.get_airway("J60"))
    print(self.usa.get_airway("J60", "DBL", "DRABS"))
    print(self.usa.get_airway("J60", "DRABS", "DBL", False))
    
    print("= Airport Point Test =================================")
    print(self.usa.get_runways('KBJC'))
    print(self.usa.get_terminal_waypoints('KBJC'))
    
    print("= Individual Point Test =================================")
    print(self.usa.get_vor("BJC"))
    print(self.usa.get_ndb("FN"))
    print(self.usa.get_waypoint("TOMSN"))
    
    print(self.usa.get_terminal_ndb("KFNL", "FN"))
    print(self.usa.get_terminal_waypoint("KBJC", "ALIKE"))
    print(self.usa.get_runway('KBJC', "RW30R"))
    
    kml.save("C:\\Temp\\cifp_processor.kml")
    
    
    
    return
  
  def process_file(self):
    
    with open(self.filename, "r") as f:
      # now process each line in the file
      for record in f:
        # identify the type of line
        self.code = cf.section(record)
        
        # parse the line
        if self.code == "XX":  # Header
          continue
        elif self.code == "AS":  # Grid Minimum Off Route Altitude (MORA)
          continue
        elif self.code == "D ":  # VHF Navaid
          self.process_point(record, self.usa.vors)
        elif self.code == "DB":  # NDB
          self.process_point(record, self.usa.ndbs)
        elif self.code == "EA":  # Waypoint
          self.process_point(record, self.usa.enroute_waypoints)
        elif self.code == "ER":  # Enroute Airway
          if self.is_primary(record):
            data = airway.AirwayFix(record) # returns an AirwayFix
            
            # airways will be confused if they aren't the full route, so add all
            self.usa.add_airway_fix(data)
          else:
            print("CIFPReader.process_file: Unhandled Enroute Airway Continuation: {}".format(record.rstrip()))
        elif self.code == "HA":  # Heliport
          continue
        elif self.code == "HC":  # Helicopter Terminal Waypoint
          continue
        elif self.code == "HF":  # Heliport SID/STAR/Approach
          continue
        elif self.code == "HS":  # Heliport Minimum Sector Altitude
          continue
        elif self.code == "PA":  # Airport Reference Point
          self.process_airport_reference_point(record, self.usa.airports)
        elif self.code == "PC":  # Terminal Waypoint
          self.process_airport_point(record, self.usa.airports)
        elif self.code == "PD":  # Standard Instrument Departure (SID)
          if self.is_primary(record):
            data = procedure.ProcedureRecord(record)
            
            # save the cifp_point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            print("CIFPReader.process_file: Unhandled SID Continuation: {}".format(record.rstrip()))
        
        elif self.code == "PE":  # Standard Terminal Arrival (STAR)
          if self.is_primary(record):
            data = procedure.ProcedureRecord(record)
            
            # save the cifp_point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            print("CIFPReader.process_file: Unhandled STAR Continuation: {}".format(record.rstrip()))
        
        elif self.code == "PF":  # Instrument Approach
          if self.is_primary(record):
            data = procedure.ProcedureRecord(record)
            
            # save the cifp_point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            data = procedure.ProcedureRecord(record)
            continue
        
        elif self.code == "PG":  # Runway
          self.process_airport_point(record, self.usa.airports)
        elif self.code == "PI":  # Localizer/Glideslope
          continue
        elif self.code == "PN":  # Terminal NDB
          self.process_airport_point(record, self.usa.airports)
        elif self.code == "PP":  # Path Point
          continue
        elif self.code == "PS":  # Minimum Sector Altitude
          continue
        elif self.code == "UC":  # Controlled Airspace
          # read a controlled airspace record (4.1.25)
          if self.is_primary(record):
            data = airspace.AirspaceRecord(record)
            
            # save the AirspaceRecord if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_airspace(data)
          else:
            # not handled for UC
            print("CIFPReader.process_file: Unhandled UC Continuation Record: {}".format(record.rstrip()))
        
        elif self.code == "UR":  # Restricted Airspace
          data = airspace.AirspaceRecord(record)
          if self.is_primary(record):
            # if we have a cifp_point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.uc_cr_armed = True
              self.usa.add_airspace(data)
            else:
              self.uc_cr_armed = False
          else:
            if self.uc_cr_armed:
              self.usa.add_airspace(data)
        else:
          print("CIFPReader.process_file: Unprocessed Record: {} {}".format(self.code, record))
      
    return
    
  def in_roi(self, lat, lon):
    if lat == None or lon == None:
      return False
    
    if self.lat_min <= lat and lat <= self.lat_max and self.lon_min <= lon and lon <= self.lon_max:
      return True 
    return False
  
  def is_primary(self, record):
    # find the continuation record number:
    if self.code == "D ":
      continuation_number = record[21]
    elif self.code == "DB":
      continuation_number = record[21]
    elif self.code == "EA":
      continuation_number = record[21]
    elif self.code == "ER":
      continuation_number = record[38]
    elif self.code == "UC":
      continuation_number = record[24]
    elif self.code == "UR":
      continuation_number = record[24]
    elif self.code == "PA":
      continuation_number = record[21]
    elif self.code == "PC":
      continuation_number = record[21]
    elif self.code == "PD":
      continuation_number = record[38]
    elif self.code == "PE":
      continuation_number = record[38]
    elif self.code == "PF":
      continuation_number = record[38]
    elif self.code == "PG":
      continuation_number = record[21]
    elif self.code == "PN":
      continuation_number = record[21]
    else:
      continuation_number = -999
    
    if continuation_number == '0' or continuation_number == '1':
      return True
    return False
  
  def process_point(self, record, point_set):
    # is this a primary or continuation record?
    if self.is_primary(record):
      # primary record
      # create a Point from this record
      point = cp.CIFPPoint(record)
      
      # is this a valid cifp_point in our ROI?
      if point.valid and self.in_roi(point.latitude, point.longitude):
        # add this cifp_point to our PointSet
        point_set.add_point(point)
    else:
      # continuation record
      # create a PointContinuation from this record
      cr = point.PointContinuation(record)
      
      # this will only get added if the primary Point exists
      point_set.add_continuation(cr)
    
    return
  
  def process_airport_reference_point(self, record, airport_dict):
    # is this a primary or continuation record?
    if self.is_primary(record):
      # primary record
      # create a Point from this record
      point = cp.CIFPPoint(record)
      
      # is this a valid cifp_point in our ROI?
      if point.valid and self.in_roi(point.latitude, point.longitude):
        # create the airport
        airport_dict[point.ident] = airport.Airport(point)
    else:
      # continuation record
      # create a PointContinuation from this record
      cr = cp.CIFPPointContinuation(record)
      
      # this will only get added if the primary Point exists
      if point.ident in airport_dict:
        airport_dict[point.ident].add_cr(cr)
    
    return
  
  def process_airport_point(self, record, airport_dict):
    # is this a primary or continuation record?
    if self.is_primary(record):
      # primary record
      # create a Point from this record
      point = cp.CIFPPoint(record)
      
      # is this airport one we are tracking?
      if point.airport in airport_dict:
        airport_dict[point.airport].add_point(point)

    else:
      # continuation record
      # create a PointContinuation from this record
      cr = point.PointContinuation(record)
      
      # is this airport one we are tracking?
      if cr.airport in airport_dict:
        airport_dict[cr.airport].add_cr(cr)
    
    return
  
  

class WaypointsOut:
  def __init__(self, path, cifp_version):
    # save the input
    self.path = path
    self.cifp_version = cifp_version
    
    # create the kml documents
    self.vors = simplekml.Kml()
    self.vors.document.name = "VHF Navaids"
    
    self.ndbs = simplekml.Kml()
    self.ndbs.document.name = "NDBs"
    
    self.enroute_waypoints = simplekml.Kml()
    self.enroute_waypoints.document.name = "Waypoints"
    
    self.terminal_waypoints = simplekml.Kml()
    self.terminal_waypoints.document.name = "Terminal Waypoints"
    
    self.terminal_ndbs = simplekml.Kml()
    self.terminal_ndbs.document.name = "Terminal NDBs"
    
    self.airports = simplekml.Kml()
    self.airports.document.name = "Airports"
    
    self.runways = simplekml.Kml()
    self.runways.document.name = "Runways"
    
    return
  
  def save_files(self):
    # save the kml file
    self.vors.save(self.path + "\\{}_VORs.kml".format(self.cifp_version))
    self.ndbs.save(self.path + "\\{}_NDBs.kml".format(self.cifp_version))
    self.enroute_waypoints.save(self.path + "\\{}_Waypoints.kml".format(self.cifp_version))
    self.terminal_waypoints.save(self.path + "\\{}_TerminalWaypoints.kml".format(self.cifp_version))
    self.terminal_ndbs.save(self.path + "\\{}_TerminalNDBs.kml".format(self.cifp_version))
    self.airports.save(self.path + "\\{}_Airports.kml".format(self.cifp_version))
    self.runways.save(self.path + "\\{}_Runways.kml".format(self.cifp_version))
    
    return
  
  
  def add_point(self, point):
    """add a cifp_point to the document
    
    cifp_point: Point instance
    """
    # build our cifp_point with elevation if available
    if point.elevation_ft != None:
      # convert to meters
      elevation = 0.3048 * point.elevation_ft
      location = (point.longitude, point.latitude, elevation)
    else:
      location = (point.longitude, point.latitude)
    
    # figure out which kml document this cifp_point belongs to and configure the description
    description = ''
    identifier = point.ident
    if point.style == point.Point.POINT_VOR:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_VORDME:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR/DME\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_VORTAC:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VORTAC\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_NDB:
      kml_doc = self.ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_ENROUTE_WAYPOINT:
      kml_doc = self.enroute_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_TERMINAL_WAYPOINT:
      kml_doc = self.terminal_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_TERMINAL_NDB:
      kml_doc = self.terminal_ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_AIRPORT:
      kml_doc = self.airports
      description += "Name:{}\n".format(point.name)
      description += "Elevation:{} feet\n".format(point.elevation_ft)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == point.Point.POINT_RUNWAY:
      kml_doc = self.runways
      identifier = "{}_{}".format(point.airport, point.name)
      description += "Length:{:.0f} feet\n".format(point.length_ft)
      description += "Elevation:{} feet\n".format(point.elevation_ft)
      description += "Runway Heading (mag):{:.1f} degrees\n".format(point.bearing)
      description += "Ruway Width:{:.0f} feet\n".format(point.width_ft)
      description += "Threshold Crossover Height:{} feet\n".format(point.tch_ft)
      description += "Displaced Threshold Distance:{} feet\n".format(point.dthreshold_ft)
    else:
      print("Unknown Point Style: {}".format(point))
    
    # add the cifp_point
    pnt = kml_doc.newpoint(name=identifier, description=description, coords=[location])
    
    # configure the cifp_point
    if point.elevation_ft != None:
      pnt.lookat = simplekml.LookAt(altitudemode=simplekml.AltitudeMode.absolute,
                                    latitude=point.latitude,
                                    longitude=point.longitude,
                                    range=15000, heading=0.0, tilt=0.0)
    else:
      pnt.lookat = simplekml.LookAt(altitudemode=simplekml.AltitudeMode.clamptoground,
                                    latitude=point.latitude,
                                    longitude=point.longitude,
                                    range=15000, heading=0.0, tilt=0.0)
    
    pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
    
    return

class ShapesOut:
  
  OUTCOLOR_RED = 0
  OUTCOLOR_ORANGE = 1
  OUTCOLOR_YELLOW = 2
  OUTCOLOR_GREEN = 3
  OUTCOLOR_AQUA = 4
  OUTCOLOR_BLUE = 5
  OUTCOLOR_MAGENTA = 6
  OUTCOLOR_WHITE = 7
  OUTCOLOR_GRAY = 8
  
  def __init__(self, path, filename, folder_name):
    # open and configure the kml file
    self.kml_filename = path + '\\' + filename + '.kml'
    self.configure_kml(folder_name)
    
    # open the outfile
    self.outfile = open(path + '\\' + filename + '.out', 'w')
    
    # instance necessary variables
    self.folders = {}
    
    return
  
  def save_files(self):
    # save the kml file
    self.kml.save(self.kml_filename)
    
    # finish the outfile
    self.outfile.close()
    
    return
  
  def configure_kml(self, folder_name):
    # create the kml document
    self.kml = simplekml.Kml()
    
    # create the top level folder
    self.kml.document.name = folder_name
    
    return
  
  def add_shape(self, airport, feature, description, shape, kmlcolor=simplekml.Color.blue, outcolor=OUTCOLOR_BLUE):
    """
    airport: airport id (i.e. KDEN)
    feature: feature type (i.e. Class B Sequence A)
    description: note (i.e. Runway Length:9000 feet...)
    
    """
    # get or build the kml folder
    if airport not in self.folders:
      self.folders[airport] = self.kml.newfolder(name=airport)
    folder = self.folders[airport]
    
    # prepare the outfile
    self.outfile.write("{{{}_{}}}\n".format(airport, feature))
    self.outfile.write("$TYPE={}\n".format(outcolor))
    
    # get the coordinates in the kml format
    coords = []
    for point in shape:
      coords.append((point[1], point[0]))
      self.outfile.write("{:.6f}+{:.6f}\n".format(point[0], point[1]))
    
    # add the shape
    line = folder.newlinestring(name="{}".format(feature),
                                coords=coords,
                                altitudemode=simplekml.AltitudeMode.clamptoground,
                                description=description)
    line.style.linestyle.width = 2
    line.style.linestyle.color = kmlcolor
    
    # finish the outfile shape
    self.outfile.write("-1\n")
    
    return
  
   
VERSION = "1.0"

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # define the area of interest
  lat_min = 35.5
  lat_max = 44.5
  lon_min = -110.0
  lon_max = -98.0
  
  cifp = CIFPReader(r"C:\Data\CIFP", "CIFP_200521", lat_min, lat_max, lon_min, lon_max)
  
  """
  runway_processor = RunwayProcessor(runways_out)
  
  # process the runways
  runway_processor.process_runway(runways, airports)

  """
  print("Done.")
  
      
    
  
