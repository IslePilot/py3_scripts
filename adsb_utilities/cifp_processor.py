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

import sys
sys.path.append("..")

import __common.filetools as filetools

import cifp_functions as cf
import cifp_point as cp
import airway
import maptools
import airspace
import airport
import procedure
import nation
import kml_output as kmlout

import simplekml

import gpxpy.gpx


     

class CIFPReader:
  OUTCOLOR_RED = 0
  OUTCOLOR_ORANGE = 1
  OUTCOLOR_YELLOW = 2
  OUTCOLOR_GREEN = 3
  OUTCOLOR_AQUA = 4
  OUTCOLOR_BLUE = 5
  OUTCOLOR_MAGENTA = 6
  OUTCOLOR_WHITE = 7
  OUTCOLOR_GRAY = 8
  
  def __init__(self, path, cifp_version,  lat_min=-90.0, lat_max=90.0, lon_min=-180.0, lon_max=180.0, directory="Processed"):
    # save the filename
    self.outpath = path+'\\'+cifp_version+'\\{}\\'.format(directory)
    filetools.mkdir(self.outpath)
    
    self.filename = path+'\\'+cifp_version+'\\FAACIFP18'
    
    # save our boundaries
    self.lat_min = lat_min
    self.lat_max = lat_max
    self.lon_min = lon_min
    self.lon_max = lon_max
    
    # create our data holder
    self.usa = nation.NationalAirspace()
    
    # process the data file
    print("Reading CIFP file...")
    self.process_file()
    
    # debug testing
    #self.debug()
    
    return
  
  def process_terminal_waypoints(self, airport):
    # get the waypoints
    waypoints = self.usa.airports[airport].get_all_waypoints()
    
    # build the GPX file
    self.build_gpx_waypoints(self.outpath+"{}_Terminal_Waypoints.gpx".format(airport), waypoints)
      
    if len(waypoints) > 0:
      # build the KML base
      kml = kmlout.KMLOutput("Terminal Waypoints", self.outpath+"{}_Terminal_Waypoints.kml".format(airport))
      
      # build a folder for this airport
      folder = kml.create_folder("{}".format(airport))
      
      for waypoint in waypoints:
        kml.add_point(folder, waypoint[0], waypoint[1], waypoint[3])
      
      kml.savefile()
    
    return      
  
  def build_gpx_waypoints(self, filename, waypoints, lat_min=-90.0, lat_max=90.0, lon_min=-180.0, lon_max=180.0):
    if len(waypoints) > 0:
      # build the GPX file
      gpx = gpxpy.gpx.GPX()
      
      for waypoint in waypoints:
        lat = waypoint[1][0]
        lon = waypoint[1][1]
        if lat != None and lon != None:
          if lat_min <= lat and lat <= lat_max and lon_min <= lon and lon <= lon_max:
            gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(latitude=lat,
                                                       longitude=lon, 
                                                       name=waypoint[0], 
                                                       description=waypoint[3]))
      
      with open(filename, "w") as gpxfile:
        gpxfile.write(gpx.to_xml())
    return 
  
  def build_enroute_waypoints(self, lat_min=-90.0, lat_max=90.0, lon_min=-180.0, lon_max=180.0, outbase="USA_Waypoints"):
    # Waypoints
    print("Building Enroute Waypoints")
    waypoints = self.usa.get_waypoints()
    
    # build the GPX file
    self.build_gpx_waypoints(self.outpath+"{}.gpx".format(outbase), waypoints, lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max)
    
    # build the KML base
    self.kml = kmlout.KMLOutput(outbase, self.outpath+"{}.kml".format(outbase))
        
    for wp in waypoints:
      lat = wp[1][0]
      lon = wp[1][1]
      if lat_min <= lat and lat <= lat_max and lon_min <= lon and lon <= lon_max:
        self.kml.add_point(self.kml.rootfolder, wp[0], wp[1], wp[3])
    
    self.kml.savefile()
    
    return 
  
  def build_nationwide_items(self):
    """ build the nationwide items for the USA"""
    
    # VHF Navaids
    print("Building VHF Navaids")
    vors = self.usa.get_vors()
    
    # build the GPX file
    self.build_gpx_waypoints(self.outpath+"USA_Navaids.gpx", vors)
    
    # build the KML base
    self.kml = kmlout.KMLOutput("VHF Navaids", self.outpath+"USA_Navaids.kml")
    
    for vor in vors:
      self.kml.add_point(self.kml.rootfolder, vor[0], vor[1], vor[3])
    
    self.kml.savefile()
    
    
    
    # build Airways
    print("Building Airways")
    airways = self.usa.get_airways()
    
    # build the KML structure
    self.kml = kmlout.KMLOutput("Airways", self.outpath+"USA_Airways.kml")
    
    record_type_folder = {}
    for id, fixes in airways.items():
      first_digit = [x.isdigit() for x in id].index(True)
      type = id[:first_digit]
      print("{} {}".format(type, id))
      
      # if this type doesn't exist, create it
      if type not in record_type_folder:
        record_type_folder[type] = self.kml.create_folder("{}".format(type))
      
      # create a folder for this airway
      airway_folder = self.kml.create_folder("{}".format(id), record_type_folder[type])
      
      # parse each point
      points = []
      for fix in fixes:
        # add the fix to our folder
        self.kml.add_point(airway_folder, fix[0], fix[1], fix[2])
        
        # do we have a huge jump?  If so, let's break the airway in two
        if len(points):
          dist = maptools.get_dist_ll(points[-1], fix[1])/1852.0
        else:
          dist = 0
        if dist > 600.0:
          self.kml.add_line(airway_folder, id, points, color=simplekml.Color.blue)
          points = []
        points.append(fix[1])
      
      self.kml.add_line(airway_folder, id, points, color=simplekml.Color.blue)
    
    self.kml.savefile()


    # build the KML structure
    self.kml = kmlout.KMLOutput("Airspace", self.outpath+"USA_Airspace.kml")

    # add the controlled airspace
    print("Building Controlled Airspace")
    controlled_airspace = self.kml.create_folder("Controlled Airspace")
    outfile = open(self.outpath+"USA_ControlledAirspace.out", "w")
    outfile.write("{{USA Controlled Airspace}}\n")
    outfile.write("$TYPE={}\n".format(self.OUTCOLOR_MAGENTA))
    
    for airport in self.usa.airports.keys():
      if len(self.usa.airports[airport].controlled_airspace) > 0:
        print("   {}".format(airport))
        airport_folder = self.kml.create_folder("{}".format(airport), controlled_airspace)
        for name, ashape in self.usa.airports[airport].controlled_airspace.items():
          # shape is an AirspaceShape
          # build the shape in lat/lon points
          shape = ashape.build_airspace_shape()
          
          # add the shape to the files
          self.kml.add_line(airport_folder, name, shape, simplekml.Color.blue)
          
          # add the shape to the out file
          for pt in shape:
            outfile.write("{:.6f}+{:.6f}\n".format(*pt))
          outfile.write("-1\n")
    outfile.close()
    
    # add the restricted airspace
    print("Building Restricted Airspace")
    restricted_airspace = self.kml.create_folder("Restricted Airspace")
    outfile = open(self.outpath+"USA_RestrictedAirspace.out", "w")
    outfile.write("{{USA Restricted Airspace}}\n")
    outfile.write("$TYPE={}\n".format(self.OUTCOLOR_MAGENTA))
    
    ra_folders = {}
    for key, ashape in self.usa.restrictive_airspace.items():
      key_parts = key.split(",")
      name = "{}".format(key_parts[0])
      sect = "Section {}".format(key_parts[1])
      print("     {}: {}".format(name, sect))
      
      if name not in ra_folders:
        # create a folder and save it
        ra_folders[name] = self.kml.create_folder("{}".format(name), restricted_airspace)
      
      # the shape is an AirspaceShape, build the shape in lat/lon points
      shape = ashape.build_airspace_shape()
      
      # add the shape to the kml file
      self.kml.add_line(ra_folders[name], sect, shape, simplekml.Color.magenta)
      
      # add the shape to the out file
      for pt in shape:
        outfile.write("{:.6f}+{:.6f}\n".format(*pt))
      outfile.write("-1\n")
    outfile.close()
    
    # write out the airspace kml
    self.kml.savefile()
    
    # add the runway boundaries
    self.kml = kmlout.KMLOutput("Runways", self.outpath+"USA_Runways.kml")
    
    print("Building Runways")
    outfile = open(self.outpath+"USA_Runways.out", "w")
    outfile.write("{{USA Runways}}\n")
    outfile.write("$TYPE={}\n".format(self.OUTCOLOR_YELLOW))
    
    for airport in self.usa.airports.keys():
      if len(self.usa.airports[airport].runways.points) > 0:
        print("{}".format(airport))
        airport_folder = self.kml.create_folder("{}".format(airport))
        
        # get a dictionary of the runways at the airport
        processed = []
        for rw, point in self.usa.airports[airport].runways.points.items():
          if rw not in processed:
            print("  {}".format(rw))
            # find the opposite runway
            orw = self.opposite_runway(rw)
            
            # only keep working if the opposite runway exists
            if orw in self.usa.airports[airport].runways.points:
              # get the opposite runway data
              opoint = self.usa.airports[airport].runways.points[orw]
              
              # add both to the processed list...once we have done a set, we are done
              processed.append(rw)
              processed.append(orw)
              
              # build a name for the runway
              name = "Runway {}-{}".format(rw[2:].rstrip(), orw[2:].rstrip())
              print("  {}".format(name))
              
              # build the runway shape
              shape = maptools.build_runway((point.latitude, point.longitude), (opoint.latitude, opoint.longitude), point.width_ft, point.bearing, point.declination)
              
              # add the shape to the kml file
              self.kml.add_line(airport_folder, name, shape, simplekml.Color.yellow)
              
              # add the shape to the out file
              for pt in shape:
                outfile.write("{:.6f}+{:.6f}\n".format(*pt))
              outfile.write("-1\n")
      
    outfile.close()
    self.kml.savefile()
    
    return
  
  def build_airport(self, airport, include_missed):
    """ build all procedures (SIDS, STARS, and Approaches) related to an airport"""
    self.kml = kmlout.KMLOutput(airport, self.outpath+"{}.kml".format(airport))
    
    added_data = False
    # process the STARS
    stars = self.kml.create_folder("STARS")
    for name in self.usa.airports[airport].stars.keys():
      # create a folder for this procedure
      folder = self.kml.create_folder(name, stars)
      tracks = self.kml.create_folder("Tracks", folder)
      fixes = self.kml.create_folder("Fixes", folder)
      
      # get the routes
      routes = self.usa.build_procedure_tracks(airport, name, "STAR")
      
      # add to the kml file
      self.build_output(routes, tracks, fixes, simplekml.Color.red)
      
      # build the out and GPX files
      self.build_pp_files(routes, "STAR", airport, name, self.OUTCOLOR_AQUA)
      
      added_data = True
    
    # process the SIDS
    sids = self.kml.create_folder("SIDS")
    for name in self.usa.airports[airport].sids.keys():
      # create a folder for this procedure
      folder = self.kml.create_folder(name, sids)
      tracks = self.kml.create_folder("Tracks", folder)
      fixes = self.kml.create_folder("Fixes", folder)
      
      # get the routes
      routes = self.usa.build_procedure_tracks(airport, name, "SID")
      
      # add to the kml file
      self.build_output(routes, tracks, fixes, simplekml.Color.blue)
      added_data = True
      
      # build the out and GPX files
      self.build_pp_files(routes, "SIDS", airport, name, self.OUTCOLOR_RED)
    
    # process the Approaches
    approaches = self.kml.create_folder("APPROACHES")
    for name in self.usa.airports[airport].approaches.keys():
      # create a folder for this procedure
      folder = self.kml.create_folder(name, approaches)
      tracks = self.kml.create_folder("Tracks", folder)
      fixes = self.kml.create_folder("Fixes", folder)
      
      # get the routes
      routes = self.usa.build_procedure_tracks(airport, name, "APPROACH", include_missed)
      
      # add to the kml file
      self.build_output(routes, tracks, fixes, simplekml.Color.yellow)
      added_data = True
      
      # build the out and GPX files
      self.build_pp_files(routes, "APPR", airport, name, self.OUTCOLOR_AQUA)
    
    # add the airspace
    airspace = self.kml.create_folder("AIRSPACE")
    shapes = []
    for name, ashape in self.usa.airports[airport].controlled_airspace.items():
      # shape is an AirspaceShape
      # build the shape in lat/lon points
      shape = ashape.build_airspace_shape()
      shapes.append(shape)
      # add the shape to the files
      self.kml.add_line(airspace, name, shape, simplekml.Color.magenta)
    
    # build the OUT file
    self.build_pp_airspace(shapes, airport, self.OUTCOLOR_MAGENTA)
    
    if added_data:
      self.kml.savefile()
    return
  
  def build_output(self, routes, tracks, fixes, color):
    for key, val in routes.items():
      coords = []
      for pt in val:
        # put the coords in kml form
        if pt.ident == None:
          # this is just a point, add it for the track, but don't create a fix
          coords.append(pt.latlon)
        else:
          coords.append(pt.latlon)
          self.kml.add_point(fixes, pt.ident, coords[-1], pt.description)
      self.kml.add_line(tracks, key, coords, color)
    
    return
  
  def build_pp_files(self, routes, proc_type, airport, name, color):
    # build the OUT file
    outfile = open(self.outpath+"{}_{}_{}.out".format(airport, proc_type, name), "w")
    
    # add the header and color
    outfile.write("{{{}_{}_{}}}\n".format(airport, proc_type, name))
    outfile.write("$TYPE={}\n".format(color))
        
    for _, val in routes.items():
      for pt in val:
        # output
        outfile.write("{:.6f}+{:.6f}\n".format(*pt.latlon))
      outfile.write("-1\n")
    
    outfile.close()
    return
  
  def build_pp_airspace(self, shapes, airport, color):
    if len(shapes) > 0:
      # build the OUT file
      outfile = open(self.outpath+"{}_Airspace.out".format(airport), "w")
      
      # add the header and color
      outfile.write("{{{}_Airspace}}\n".format(airport))
      outfile.write("$TYPE={}\n".format(color))
      
      # add each shape
      for shape in shapes:
        for pt in shape:
          # output
          outfile.write("{:.6f}+{:.6f}\n".format(*pt))
        outfile.write("-1\n")
      
      outfile.close()
        
  def debug(self):
    # debug test
    #                          Airport       Procedure    
    # build a simple kml file to test
    kml = simplekml.Kml()
    kml.document.name = "CIFP Processor Test"
    
    print("=SID =================================")
    routes = self.usa.build_procedure_tracks('KDEN', 'BAYLR6', 'SID')
    
    # create a folder for this STAR
    sid_folder = kml.newfolder(name='BAYLR6')
    sid_track_folder = sid_folder.newfolder(name = "Tracks")
    sid_fix_folder = sid_folder.newfolder(name = "Fixes")
    
    for key, val in routes.items():
      coords = []
      for pt in val:
        # put the coords in the kml form
        if len(pt) == 2:
          coords.append((pt[1], pt[0]))
        else:
          coords.append((pt[0][1], pt[0][0]))
          pnt = sid_fix_folder.newpoint(name=pt[2], coords=[coords[-1]], description=pt[3])
          pnt.lookat = simplekml.LookAt(latitude=pt[0][0],longitude=pt[0][1], range=15000., heading=0, tilt=0)
          pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
      
      line = sid_track_folder.newlinestring(name=key, coords=coords)
      line.style.linestyle.width = 4
      line.style.linestyle.color = simplekml.Color.red

    print("=STAR =================================")
    routes = self.usa.build_procedure_tracks('KDEN', 'FLATI1', 'STAR')
    
    # create a folder for this STAR
    star_folder = kml.newfolder(name='FLATI1')
    star_track_folder = star_folder.newfolder(name = "Tracks")
    star_fix_folder = star_folder.newfolder(name = "Fixes")
    
    for key, val in routes.items():
      coords = []
      for pt in val:
        # put the coords in the kml form
        if len(pt) == 2:
          coords.append((pt[1], pt[0]))
        else:
          coords.append((pt[0][1], pt[0][0]))
          pnt = star_fix_folder.newpoint(name=pt[2], coords=[coords[-1]], description=pt[3])
          pnt.lookat = simplekml.LookAt(latitude=pt[0][0],longitude=pt[0][1], range=15000., heading=0, tilt=0)
          pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
      
      line = star_track_folder.newlinestring(name=key, coords=coords)
      line.style.linestyle.width = 4
      line.style.linestyle.color = simplekml.Color.blue

    print("=Approach =================================")
    routes = self.usa.build_procedure_tracks('KDEN', 'H16RZ', 'APPROACH')
    
    # create a folder for this STAR
    app_folder = kml.newfolder(name='KDEN H16RZ')
    app_track_folder = app_folder.newfolder(name = "Tracks")
    app_fix_folder = app_folder.newfolder(name = "Fixes")
    
    for key, val in routes.items():
      coords = []
      for pt in val:
        # put the coords in the kml form
        if len(pt) == 2:
          coords.append((pt[1], pt[0]))
        else:
          coords.append((pt[0][1], pt[0][0]))
          pnt = app_fix_folder.newpoint(name=pt[2], coords=[coords[-1]], description=pt[3])
          pnt.lookat = simplekml.LookAt(latitude=pt[0][0],longitude=pt[0][1], range=15000., heading=0, tilt=0)
          pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
      
      line = app_track_folder.newlinestring(name=key, coords=coords)
      line.style.linestyle.width = 4
      line.style.linestyle.color = simplekml.Color.yellow
    
    routes = self.usa.build_procedure_tracks('KEIK', 'VDM-A', 'APPROACH')
    # create a folder for this STAR
    app_folder = kml.newfolder(name='KEIK VDM-A')
    app_track_folder = app_folder.newfolder(name = "Tracks")
    app_fix_folder = app_folder.newfolder(name = "Fixes")
    
    for key, val in routes.items():
      coords = []
      for pt in val:
        # put the coords in the kml form
        if len(pt) == 2:
          coords.append((pt[1], pt[0]))
        else:
          coords.append((pt[0][1], pt[0][0]))
          pnt = app_fix_folder.newpoint(name=pt[2], coords=[coords[-1]], description=pt[3])
          pnt.lookat = simplekml.LookAt(latitude=pt[0][0],longitude=pt[0][1], range=15000., heading=0, tilt=0)
          pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
      
      line = app_track_folder.newlinestring(name=key, coords=coords)
      line.style.linestyle.width = 4
      line.style.linestyle.color = simplekml.Color.yellow
    
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
          self.process_point(record, self.usa.vors, True)
        elif self.code == "DB":  # NDB
          self.process_point(record, self.usa.ndbs, True)
        elif self.code == "EA":  # Waypoint
          self.process_point(record, self.usa.enroute_waypoints, True)
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
          self.process_airport_point(record, self.usa.airports)
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
          self.usa.add_airspace(airspace.AirspaceRecord(record))
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
    elif self.code == "PI":
      continuation_number = record[21]
    else:
      continuation_number = -999
    
    if continuation_number == '0' or continuation_number == '1':
      return True
    return False
  
  def process_point(self, record, point_set, add_all=False):
    # is this a primary or continuation record?
    if self.is_primary(record):
      # primary record
      # create a Point from this record
      point = cp.CIFPPoint(record)
      
      # is this a valid cifp_point in our ROI?
      if point.valid and (self.in_roi(point.latitude, point.longitude) or add_all):
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
        # include the airport declination in case this is a runway
        airport_dict[point.airport].add_point(point)

    else:
      # continuation record
      # create a PointContinuation from this record
      cr = point.PointContinuation(record)
      
      # is this airport one we are tracking?
      if cr.airport in airport_dict:
        airport_dict[cr.airport].add_cr(cr)
    
    return
  
  def opposite_runway(self, ident):
    if len(ident.rstrip()) == 1:
      if ident == "E    ":
        new_ident = "W    "
      elif ident == "W    ":
        new_ident = "E    "
      elif ident == "N    ":
        new_ident = "S    "
      elif ident == "S    ":
        new_ident = "N    "
      else:
        print("Unhandled 1 character Runway ID")
        new_ident = "X    "
    elif len(ident.rstrip()) == 2:
      if ident == "NE   ":
        new_ident = "SW   "
      elif ident == "NW   ":
        new_ident = "SE   "
      elif ident == "SE   ":
        new_ident = "NW    "
      elif ident == "SW   ":
        new_ident = "NE   "
    elif len(ident.rstrip()) >= 4:
      # get the opposite runway number
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
    
    return new_ident

def process_airport(cifp, airport, include_missed):
  print("Processing {} ========================".format(airport))
  cifp.build_airport(airport, include_missed)
  cifp.process_terminal_waypoints(airport)
  return

def process_center_boundaries(filename, outpath):
  print("Processing ARTCC Boundaries")
  
  # output the boundaries to kml and out files
  kml = kmlout.KMLOutput("ARTCC", outpath+"\\USA_ARTCC.kml")
  
  # open the outfile
  outfile = open(outpath+"\\USA_ARTCC.out", "w")
  outfile.write("$TYPE={}\n".format(CIFPReader.OUTCOLOR_GRAY))
  
  firstline = True
  artcc = {}
  with open(filename, "r") as csvfile:
    for line in csvfile:
      # skip the header
      if firstline:
        firstline = False
        continue
      
      # parse the data
      if line[0] == "Z":
        point = line.rstrip().split(",")
        ctr = point[0]
        latdeg = int(point[3][0:2])
        latmin = int(point[3][2:4])
        latsec = int(point[3][4:8])/100.0
        lathem = point[3][8]
        londeg = int(point[4][0:3])
        lonmin = int(point[4][3:5])
        lonsec = int(point[4][5:9])/100.0
        lonhem = point[4][9]
        position = maptools.dms2deg(lathem, latdeg, latmin, latsec, lonhem, londeg, lonmin, lonsec)
        
        # add the point
        if ctr not in artcc:
          artcc[ctr] = []
          print("   Processing {} Center".format(ctr))
        artcc[ctr].append(position)
  

  
  for ctr, shape in artcc.items():
    # add a folder
    folder = kml.create_folder(ctr)
    
    kml.add_line(folder, ctr, shape, simplekml.Color.gray)
    
    for pt in shape:
      outfile.write("{:.6f}+{:.6f}\n".format(*pt))
    outfile.write("-1\n")
  
  outfile.close()
  kml.savefile()
  
  return
  


if __name__ == '__main__':
  # Steps
  # Update data sets:
  # https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/cifp/download/
  # https://www.faa.gov/air_traffic/flight_info/aeronav/Aero_Data/Center_Surface_Boundaries/
  #
  # Check KFSO Runway 19...YJN may need to be added to SCAND
  #
  # 1. Modify paths and versions in the block below
  # 2. Run cifp_processor
  # 3. Modify zipper.py path to data and run zipper.py
  # 4. Update txt filename in ToShare to represent appropriate data
  # 5. Update PNG files if there are significant changes
  # 6. Run 000_scp.bat to upload data to website
  # 7. Edit index.html on website to indicate versions
  # 8. Notify PlanePlotter users if desired
  # 9. Zip Processed_DTS and send to David Stark if desired
  
  
  
  # when this file is run directly, run this code
  cifp_path = r"C:\Data\CIFP"
  cifp_version = "CIFP_210617"
  eram_version = "2021-06-17"
  eram_path = r"C:\Data\CIFP\ERAM"
  
  
  # process the center boundaries
  # https://www.faa.gov/air_traffic/flight_info/aeronav/Aero_Data/Center_Surface_Boundaries/
  process_center_boundaries(eram_path+"\\Ground_Level_ARTCC_Boundary_Data_{}.csv".format(eram_version), eram_path)
  
  # process the CIFP file
  cifp = CIFPReader(cifp_path, cifp_version)
  
  # build the national items
  cifp.build_nationwide_items()
  
  # build select procedures for every airport with a tower in our area, plus a few others
  cifp.build_enroute_waypoints(lat_min=37.0, lat_max=41.0, lon_min=-109.0, lon_max=-102.0, outbase="CO_Enroute_Waypoints")
  
  process_airport(cifp, "KDEN", False)
  process_airport(cifp, "KBJC", False)
  process_airport(cifp, "KEIK", False)
  process_airport(cifp, "KLMO", False)
  process_airport(cifp, "KAPA", False)
  process_airport(cifp, "KFNL", False)
  process_airport(cifp, "KGXY", False)
  
  process_airport(cifp, "KCOS", False)
  process_airport(cifp, "KASE", False)
  process_airport(cifp, "KEGE", False)
  process_airport(cifp, "KSLC", False)
  process_airport(cifp, "KPHX", False)
  process_airport(cifp, "KABQ", False)
  process_airport(cifp, "KLAX", False)
  process_airport(cifp, "KMCI", False)
  process_airport(cifp, "KSTL", False)
  process_airport(cifp, "KMSP", False)
  
  
  # standard requests
  process_airport(cifp, "KJFK", False)
  process_airport(cifp, "KSFO", False)
  process_airport(cifp, "KLAS", False)
  process_airport(cifp, "KMEM", False)
  process_airport(cifp, "KEWR", False)
  process_airport(cifp, "KORD", False)
  
  # PlanePlotter Requested Airports
  process_airport(cifp, "KATL", False)  # Requested by Greg Gilbert greggilbert195@gmail.com
  
  process_airport(cifp, "KJAX", False)  # Requested by Gary Moyer zonian149@gmail.com
  
  process_airport(cifp, "KALB", False)  # Requested by David Stark davidthomasstark@gmail.com
  process_airport(cifp, "KBOS", False)  # Requested by David Stark davidthomasstark@gmail.com
  process_airport(cifp, "KLGA", False)  # Requested by David Stark davidthomasstark@gmail.com
  process_airport(cifp, "KSCH", False)  # Requested by David Stark davidthomasstark@gmail.com

  process_airport(cifp, "KDFW", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KDAL", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KADS", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KTKI", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KGVT", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KGYI", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KNFW", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KAFW", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KSPS", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KLTS", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KEND", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KTIK", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KBAD", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  process_airport(cifp, "KDYS", False)  # Requested by Clay Carrington clay.carrington@hotmail.com
  
  process_airport(cifp, "KMSN", False)  # Requested by Dan Egan egandp@ameritech.net
  
  process_airport(cifp, "KMDW", False)  # Requested by Don Froula
  process_airport(cifp, "KDPA", False)  # Requested by Don Froula
  process_airport(cifp, "KARR", False)  # Requested by Don Froula
  process_airport(cifp, "KPWK", False)  # Requested by Don Froula
  
  process_airport(cifp, "KLNK", False)  # Requested by Ron Kokarik
  process_airport(cifp, "KOFF", False)  # Requested by Ron Kokarik
  process_airport(cifp, "KOMA", False)  # Requested by Ron Kokarik
  
  process_airport(cifp, "KIND", False)  # Requested by Jason Webb jason.prime65334@gmail.com
  
  process_airport(cifp, "KMSO", False)  # Requested by Jim De Witt dewittjim@gmail.com


  # process_airport(cifp, "", False)
  # cifp.process_terminal_waypoints("")  # Requested by
  
  # Denver Area
  # lat_min = 35.5
  # lat_max = 44.5
  # lon_min = -110.0
  # lon_max = -98.0
  #cifp = CIFPReader(cifp_path, cifp_version, lat_min, lat_max, lon_min, lon_max)
  
  # for David Stark davidthomasstark@gmail.com
  cifp = CIFPReader(cifp_path, cifp_version, 39.0, 46.0, -81.0, -72.0, "Processed_DTS")
  for airport in cifp.usa.airports.keys():
    process_airport(cifp, airport, False)
  
  print("Done.")
  
      
    
  
