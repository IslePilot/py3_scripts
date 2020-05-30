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
import maptools as maptools
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
    
    print("==================================")
    
    #                          Airport       Procedure      
    for route in self.usa.airports['KDEN'].stars['FLATI1'].enroute_transistions.values():
      for pr in route:
        print("ET {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.usa.airports['KDEN'].stars['FLATI1'].common_route.values():
      for pr in route:
        print("CR {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.usa.airports['KDEN'].stars['FLATI1'].runway_transitions.values():
      for pr in route:
        print("RW {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    
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
    
    for airway_fix in self.usa.enroute_airways['J60'].airway:
      print("{}: {}".format(airway_fix.route_id, airway_fix.fix_id))
    
    print(self.usa.enroute_airways['J60'].get_fixes('JOT', 'DBL'))
    print(self.usa.enroute_airways['J60'].get_fixes('JOT', 'DBL', False))
    
    print("==================================")
    print(self.usa.restrictive_airspace["COUGAR H Section A"].name)
    print(self.usa.restrictive_airspace["COUGAR H Section A"].controlling_agency)
    print(self.usa.restrictive_airspace["COUGAR H Section A"].build_airspace_shape())
    
    print("==================================")
    print(self.usa.airports['KBKF'].controlled_airspace["Class D Section B"].name)
    print(self.usa.airports['KBKF'].controlled_airspace["Class D Section B"].controlling_agency)
    print(self.usa.airports['KBKF'].controlled_airspace["Class D Section B"].build_airspace_shape())
    return
  
  def process_file(self):
    
    with open(self.filename, "r") as f:
      # now process each line in the file
      for line in f:
        # identify the type of line
        info = cf.get_record_info(line)
        code = info.section_code + info.subsection_code
        primary = self.is_primary(code, line)
        
        # parse the line
        if code == "XX":  # Header
          continue
        elif code == "AS":  # Grid Minimum Off Route Altitude (MORA)
          continue
        elif code == "D ":  # VHF Navaid
          # 4.1.2
          if primary:
            data = self.parse_vhf_navaid_primary(line) # returns a cf.Point
              
            # if we have a point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.usa.add_vor(data)
          else:
            print("CIFPReader.process_file: Unhandled VHF Navaid Continuation: {}".format(line.rstrip()))
        
        elif code == "DB":  # NDB
          # 4.1.3
          if primary:
            data = self.parse_ndb_primary(line) # returns a cf.Point
            
            # if we have a point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.usa.add_ndb(data)
          else:
            print("CIFPReader.process_file: Unhandled NDB Continuation: {}".format(line.rstrip()))
        
        elif code == "EA":  # Waypoint
          # 4.1.4
          if primary:
            data = self.parse_waypoint_primary(line) # returns a Point
            
            # if we have a point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.usa.add_enroute_waypoint(data)
          else:
            print("CIFPReader.process_file: Unhandled Enroute Waypoint Continuation: {}".format(line.rstrip()))
        
        elif code == "ER":  # Enroute Airway
          if primary:
            data = procedure.AirwayFix(line) # returns an AirwayFix
            
            # airways will be confused if they aren't the full route, so add all
            self.usa.add_airway_fix(data)
          else:
            print("CIFPReader.process_file: Unhandled Enroute Airway Continuation: {}".format(line.rstrip()))
        elif code == "HA":  # Heliport
          continue
        elif code == "HC":  # Helicopter Terminal Waypoint
          continue
        elif code == "HF":  # Heliport SID/STAR/Approach
          continue
        elif code == "HS":  # Heliport Minimum Sector Altitude
          continue
        elif code == "PA":  # Airport Reference Point
          # 4.1.7 - this is always the first line a a set of airport data
          if primary:
            data = self.parse_airport_primary_record(line) # returns a cf.Point
          
            # if we have a point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.usa.add_airport(airport.Airport(data))
          else:
            print("CIFPReader.process_file: Unhandled Airport Continuation: {}".format(line.rstrip()))
        
        elif code == "PC":  # Terminal Waypoint
          # 4.1.4
          if primary:
            data = self.parse_waypoint_primary(line) # returns a Point
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_waypoint(data)
          else:
            print("CIFPReader.process_file: Unhandled Terminal Waypoint Continuation: {}".format(line.rstrip()))
        
        elif code == "PD":  # Standard Instrument Departure (SID)
          if primary:
            data = procedure.ProcedureRecord(line)
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            print("CIFPReader.process_file: Unhandled SID Continuation: {}".format(line.rstrip()))
        
        elif code == "PE":  # Standard Terminal Arrival (STAR)
          if primary:
            data = procedure.ProcedureRecord(line)
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            print("CIFPReader.process_file: Unhandled STAR Continuation: {}".format(line.rstrip()))
        
        elif code == "PF":  # Instrument Approach
          if primary:
            data = procedure.ProcedureRecord(line)
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_procedure(data)
          else:
            data = procedure.ProcedureRecord(line)
            continue
        
        elif code == "PG":  # Runway
          # 4.1.10
          if primary:
            data = self.parse_runway_primary(line) # returns a Point
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_runway(data)
          else:
            print("CIFPReader.process_file: Unhandled Runway Continuation: {}".format(line.rstrip()))
        
        elif code == "PI":  # Localizer/Glideslope
          continue
        elif code == "PN":  # Terminal NDB
          # 4.1.3
          if primary:
            data = self.parse_ndb_primary(line) # returns a cf.Point
            
            # save the point if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_ndb(data)
          else:
            print("CIFPReader.process_file: Unhandled NDB Continuation: {}".format(line.rstrip()))
        
        elif code == "PP":  # Path Point
          continue
        elif code == "PS":  # Minimum Sector Altitude
          continue
        elif code == "UC":  # Controlled Airspace
          # read a controlled airspace record (4.1.25)
          if primary:
            data = airspace.AirspaceRecord(line)
            
            # save the AirspaceRecord if this is an airport we are including
            if self.usa.has_airport(data.airport):
              self.usa.airports[data.airport].add_airspace(data)
          else:
            # not handled for UC
            print("CIFPReader.process_file: Unhandled UC Continuation Record: {}".format(line.rstrip()))
        
        elif code == "UR":  # Restricted Airspace
          data = airspace.AirspaceRecord(line)
          if primary:
            # if we have a point we want, save it
            if data != None and self.in_roi(data.latitude, data.longitude):
              self.uc_cr_armed = True
              self.usa.add_airspace(data)
            else:
              self.uc_cr_armed = False
          else:
            if self.uc_cr_armed:
              self.usa.add_airspace(data)
        else:
          print("CIFPReader.process_file: Unprocessed Record: {} {}".format(code, line))
      
    return
    
  def in_roi(self, lat, lon):
    if lat == None or lon == None:
      return False
    
    if self.lat_min <= lat and lat <= self.lat_max and self.lon_min <= lon and lon <= self.lon_max:
      return True 
    return False
  
  def is_primary(self, section, record):
    # find the continuation record number:
    if section == "D ":
      continuation_number = record[21]
    elif section == "DB":
      continuation_number = record[21]
    elif section == "EA":
      continuation_number = record[21]
    elif section == "ER":
      continuation_number = record[38]
    elif section == "UC":
      continuation_number = record[24]
    elif section == "UR":
      continuation_number = record[24]
    elif section == "PA":
      continuation_number = record[21]
    elif section == "PC":
      continuation_number = record[21]
    elif section == "PD":
      continuation_number = record[38]
    elif section == "PE":
      continuation_number = record[38]
    elif section == "PF":
      continuation_number = record[38]
    elif section == "PG":
      continuation_number = record[21]
    elif section == "PN":
      continuation_number = record[21]
    else:
      continuation_number = -999
    
    if continuation_number == '0' or continuation_number == '1':
      return True
    return False
  
  def parse_vhf_navaid_primary(self, record):
    """Parse a section 4.1.2 (p.27) VHF Navaid Record"""
    # SCAND        ADK   PA011400 DUW                    ADK N51521587W176402739E0070003291     NARMOUNT MOFFETT                 002361703
    # SLAMD        ANU   TA011450VDHW N17073316W061480060    N17073316W061480060W0150004002     NARV. C. BIRD                    165731707
    # SPACD        AWK   PW011350VTHW N19171169E166373840    N19171169E166373840E0060000182     NARWAKE ISLAND                   179381901
    # SSPAD        TUT   NS011250VTHW S14195732W170422980    S14195730W170422980E0120000102     NARPAGO PAGO                     226421605
    # SUSAD        ABI   K4011370VTHW N32285279W099514843    N32285279W099514843E0100018092     NARABILENE                       227901810
    # SUSAD        BJC   K2011540VDHW N39544695W105082035    N39544695W105082035E0110057372     NARJEFFCO                        228681605
    # SUSAD KACKK6 IACK  K6010910 ITW                    IACKN41144628W070043228W0160000120     NARNANTUCKET MEMORIAL            238471807
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    if record[27] == "V": # 5.35 (p.88)
      # VORs only
      t2 = record[28]
      if t2 == " ":
        style = cf.Point.POINT_VOR
      elif t2 == "D":
        style = cf.Point.POINT_VORDME
      elif t2 == "T" or t2 == "M":
        style = cf.Point.POINT_VORTAC
      else:
        print("CIFPReader.parse_vhf_navaid: Unexpected VOR type: {}".format(record))
        style = None
      
      # now parse the rest of the record
      vor_ident = record[13:17].rstrip()
      continuation_count = record[21]
      frequency = cf.parse_float(record[22:27], 100)
      latitude = cf.parse_lat(record[32:41])
      longitude = cf.parse_lon(record[41:51])
      declination = cf.parse_variation(record[74:79])
      name = record[93:123].rstrip()
    else:
      return None
    
    return cf.Point(ident=vor_ident,
                    name=name,
                    style=style,
                    latitude=latitude,
                    longitude=longitude,
                    continuation_count=continuation_count,
                    declination=declination,
                    frequency=frequency)
  
  def parse_ndb_primary(self, record):
    """Parse a section 4.1.3 (p.29) NDB Record"""
    # DB NDB Navaid 3.2.2.2
    # SCANDB       ACE   PA002770H  W N59382880W151300099                       E0170           NARKACHEMAK                      003632002
    # SLAMDB       DDP   TJ003910H HW N18280580W066244461                       W0110           NARDORADO                        166011605
    # SPACDB       AJA   PG003850H  W N13271270E144441296                       E0020           NARMT MACAJNA                    179711806
    # SSPADB       LOG   NS002420H MW S14211350W170445620                       E0120           NARLOGOTALA HILL                 226441703
    # SUSADB       AA    K3003650HOLW N47003259W096485466                       E0040           NARKENIE                         246741805
    # PN Airport and Heliport Terminal NDB 3.2.4.13
    # SLAMPNTISXTI ST    TI002410HO W N17413092W064530474                       W0130           NARPESTE                         176801605
    # SPACPNPHNLPH HN    PH002420HO W N21192970W158025590                       E0110           NAREWABE                         221111410
    # SUSAPN3J7 K7 VV    K7003530HO W N33384708W083011836                       W0050           NARJUNNE                         439711610
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # identify the style
    if record[4:6] == "DB":
      style = cf.Point.POINT_NDB
    elif record[4:6] == "PN":
      style = cf.Point.POINT_TERMINAL_NDB
    else:
      print("CIFPReader.parse_ndb: Unexpected NDB type: {}".format(record))
      style = None
    
    # parse the record
    airport = record[6:10].rstrip() # populated only for terminal NDBs
    ident = record[13:17].rstrip()
    continuation_count = record[21]
    frequency = cf.parse_float(record[22:27], 10)
    latitude = cf.parse_lat(record[32:41])
    longitude = cf.parse_lon(record[41:51])
    declination = cf.parse_variation(record[74:79])
    name = record[93:123].rstrip()

    
    return cf.Point(ident=ident,
                    name=name,
                    style=style,
                    latitude=latitude,
                    longitude=longitude,
                    continuation_count=continuation_count,
                    declination=declination,
                    frequency=frequency,
                    airport=airport)
  
  def parse_waypoint_primary(self, record):
    """Parse a section 4.1.4 (p.29) Waypoint Record"""
    # EA Enroute Waypoint 3.2.3.1
    # SCANEAENRT   AAMYY PA0    R   H N51301880E171091170                       W0010     NAR           AAMYY                    004572002
    # SEEUEAENRT   AGURA UH0    W  RH N67275200W168582400                       E0077     NAR           AGURA                    165482002
    # SLAMEAENRT   ACREW MM0    R   L N25543661W097394533                       E0036     NAR           ACREW                    166082002
    # SPACEAENRT   AATRE PH0    W  R  N21131105W157551891                       E0094     NAR           AATRE                    179872002
    # SSPAEAENRT   AADPO NZ0    R   L S14100754W170580312                       E0118     NAR           AADPO                    226461901
    # SUSAEAENRT   AAALL K60    W  R  N42071268W071083034                       W0145     NAR           AAALL                    252881901
    # PC Airport Terminal Waypoints 3.2.4.3
    # SCANP PAAKPACBILNE PA0    W     N52155864W174310737                       E0053     NAR           BILNE                    049292002
    # SLAMP TISTTICJAQYY TI0    C     N18195582W065053354                       W0137     NAR           JAQYY                    169302002
    # SPACP PGROPGCCEPOS K20    W     N14100778E145180802                       E0006     NAR           CEPOS                    194721901
    # SSPAP NSTUNSCAPRAN NZ0    R     S14215480W170455857                       E0119     NAR           APRAN                    226592002
    # SUSAP 00R K4CAGEVE K40    W     N30373965W094562178                       E0019     NAR           AGEVE                    753642002
    # SCANP PAAKPACBILNE PA0    W     N52155864W174310737                       E0053     NAR           BILNE                    049292002
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # identify the style
    if record[4:6] == "EA":
      style = cf.Point.POINT_ENROUTE_WAYPOINT
    elif record[4] == "P" and record[12] == "C":
      style = cf.Point.POINT_TERMINAL_WAYPOINT
    else:
      print("CIFPReader.parse_waypoint: Unexpected Waypoint type: {}".format(record))
      style = None
    
    # parse the record
    airport = record[6:10].rstrip()
    ident = record[13:18].rstrip()
    continuation_count = record[21]
    latitude = cf.parse_lat(record[32:41])
    longitude = cf.parse_lon(record[41:51])
    declination = cf.parse_variation(record[74:79])
    name = record[98:123].rstrip()

    
    return cf.Point(ident=ident,
                    name=name,
                    style=style,
                    latitude=latitude,
                    longitude=longitude,
                    continuation_count=continuation_count,
                    declination=declination,
                    airport=airport)
  
  def parse_airport_primary_record(self, record):
    """parse an airport primary record (Section 4.1.7) (p.32)
    
    record: CIFP string containing a PA record
    
    returns: tuple containing:(Airport ICAO Identifier,
                               Airport Reference Point Latitude,
                               Airport Reference Point Longitude,
                               Magnetic Variation (W positive),
                               Airport Elevation,
                               Airport Name)"""
    # PA Airport Reference Points 3.2.4.1
    # SCANP 00AKPAA        0     025NSN59565600W151413200E014800252         1800018000P    MNAR    LOWELL FIELD                  041982002
    # SLAMP 02PRTJA        0     020NSN18271200W066220100W012000015                   P    MNAR    CUYLERS                       169231703
    # SPACP 03N PKA03N     0     024NSN11140000E169510000E009000004                   C    MNAR    UTIRIK                        194471703
    # SSPAP NSASNSAZ08     0     020NHS14110366W169401209E012000009                   C    MNAR    OFU                           226521703
    # SUSAP 00AAK3A        0     034NSN38421448W101282608E006003435         1800018000P    MNAR    AERO B RANCH                  753182002
    # SUSAP KDENK2ADEN     0     160YHN39514200W104402340E008005434         1800018000C    MNAR    DENVER INTL                   599261208
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    ident = record[6:10].rstrip()
    continuation_count = record[21]
    latitude = cf.parse_lat(record[32:41])
    longitude = cf.parse_lon(record[41:51])
    declination = cf.parse_variation(record[51:56])
    elevation_ft = float(record[56:61])
    name = record[93:123].rstrip()
    
    return cf.Point(ident=ident, 
                    name=name, 
                    style=cf.Point.POINT_AIRPORT, 
                    latitude=latitude, 
                    longitude=longitude,
                    continuation_count=continuation_count,
                    declination=declination, 
                    elevation_ft=elevation_ft,
                    airport=ident)
  
  def parse_runway_primary(self, record):
    """Parse a section 4.1.10 (p.25) Runway Record"""
    # PG Airport Runway 3.2.4.7
    # SCANP 01A PAGRW05    0011760463 N62562477W152162256               02034000050050D                                          042001703
    # SLAMP TISTTIGRW10    0070001000 N18201272W064590034               00024000055150I                                          169431613
    # SPACP PGROPGGRW09    0070000900 N14102878E145135249               00586000045150R                                          195061404
    # SSPAP NSASNSGRW08    0020000860 S14110237W169402216               00009000050060D                                          226531703
    # SUSAP 00ARK3GRW18    0025361765 N38582010W097360830               01328000050250D                                          753212002
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    airport = record[6:10].rstrip()
    runway = record[13:18]
    continuation_count = record[21]
    length = cf.parse_float(record[22:27])
    bearing = cf.parse_float(record[27:31], 10.0)
    latitude = cf.parse_lat(record[32:41])
    longitude = cf.parse_lon(record[41:51])
    elevation = cf.parse_float(record[66:71])
    dthreshold = cf.parse_float(record[71:75])
    tch = cf.parse_float(record[75:77])
    width = cf.parse_float(record[77:80])
    
    return cf.Point(ident=airport, 
                    name=runway, 
                    style=cf.Point.POINT_RUNWAY, 
                    latitude=latitude, 
                    longitude=longitude, 
                    continuation_count=continuation_count,
                    elevation_ft=elevation, 
                    length_ft=length,
                    bearing=bearing, 
                    tch_ft=tch, 
                    width_ft=width, 
                    dthreshold_ft=dthreshold, 
                    airport=airport)

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
    """add a point to the document
    
    point: Point instance
    """
    # build our point with elevation if available
    if point.elevation_ft != None:
      # convert to meters
      elevation = 0.3048 * point.elevation_ft
      location = (point.longitude, point.latitude, elevation)
    else:
      location = (point.longitude, point.latitude)
    
    # figure out which kml document this point belongs to and configure the description
    description = ''
    identifier = point.ident
    if point.style == cf.Point.POINT_VOR:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_VORDME:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR/DME\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_VORTAC:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VORTAC\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_NDB:
      kml_doc = self.ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_ENROUTE_WAYPOINT:
      kml_doc = self.enroute_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_TERMINAL_WAYPOINT:
      kml_doc = self.terminal_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_TERMINAL_NDB:
      kml_doc = self.terminal_ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_AIRPORT:
      kml_doc = self.airports
      description += "Name:{}\n".format(point.name)
      description += "Elevation:{} feet\n".format(point.elevation_ft)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == cf.Point.POINT_RUNWAY:
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
    
    # add the point
    pnt = kml_doc.newpoint(name=identifier, description=description, coords=[location])
    
    # configure the point
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
  
class RunwayProcessor:
  def __init__(self, runway_writer):
    """
    runway_writer: instance of ShapesOut class for writing the runway shapes
    """
    self.runway_writer=runway_writer
    
    self.done = []
    
    return
    
  def process_runway(self, runways, airports):
    """
    runways: dictionary of RUNWAY namedtuples (airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width)
    airports: dictionary of AIRPORT namedtuples (icao_code, latitude, longitude, declination, elevation, name)
    
    """
    for name, data in runways.items():
         
      # check if this is a real runway number (not something like N or S, but something like 36 or 18)
      if len(data.runway.rstrip()) < 4:
        print("process_runway: skipping {}".format(name))
        continue
      
      # if we already handled this runway (probably from the other side) we are already done
      if name in self.done:
        continue 
      
      # build the opposite runway name
      num = int(data.runway[2:4])  # numbers only 29, 07, etc.
      side = data.runway[4]  # space, L, R, or C
      op_num = (num+18)%36
      # if 36 was the answer the above changed it to 0
      if op_num == 0:
        op_num = 36
      if side == "L":
        op_side = "R"
      elif side == "R":
        op_side = "L"
      else:
        op_side = side  # space and C stay the same
      op_runway = "RW{:02d}{}".format(op_num, op_side)
      op_name = "{}_{}".format(data.airport, op_runway)
    
      # save both of these in to our list so we don't create a duplicate
      self.done.append(name)
      self.done.append(op_name)
      
      # find the opposite end data
      if op_name in runways:
        op_data = runways[op_name]
      else:
        print("{} not found in runways[], skipping runway".format(op_name))
        continue
      
      # get the runway points
      arrival_end = (data.latitude, data.longitude)
      departure_end = (op_data.latitude, op_data.longitude)
      
      # get the declination
      if data.airport in airports:
        declination = airports[data.airport].declination
      else:
        print("{} not found in airports[], skipping runway".format(data.airport))
        continue
      
      # build the description
      # airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width
      description = ""
      description += "Name:{} {}\n".format(data.airport, data.runway)
      description += "Length:{:.0f} feet\n".format(data.length)
      description += "Elevation:{} feet\n".format(data.elevation)
      description += "Runway Heading (mag):{:.1f} degrees\n".format(data.bearing)
      description += "Ruway Width:{:.0f} feet\n".format(data.width)
      description += "Threshold Crossover Height:{} feet\n".format(data.tch)
      description += "Displaced Threshold Distance:{} feet\n".format(data.dthreshold)
      
      shape = maptools.build_runway(arrival_end, departure_end, data.width, data.bearing, declination)
      
      self.runway_writer.add_shape(data.airport, data.runway, description, shape, simplekml.Color.yellow, ShapesOut.OUTCOLOR_YELLOW)
      
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
  
      
    
  
