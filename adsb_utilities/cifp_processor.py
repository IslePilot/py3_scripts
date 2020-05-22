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
import __common.maptools as maptools

from collections import namedtuple
import simplekml
import gpxpy
    
class CIFPReader:
  SECTIONS = namedtuple('SECTIONS', 'area_code, section_code, subsection_code')
  
  NAVAID = namedtuple('VHF_NAVAID', 'ident, frequency, latitude, longitude, declination, name')
  WAYPOINT = namedtuple('WAYPOINT', 'ident, latitude, longitude, declination, name')
  
  AIRPORT = namedtuple('AIRPORT', 'icao_code, latitude, longitude, declination, elevation, name')
  RUNWAY = namedtuple('RUNWAY', 'airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width')
  
  UC_DATA = namedtuple('UC_Data', 'airspace_type, airspace_center, airspace_classification,'\
                       ' multiple_code, sequence_number,'\
                       ' continuation_record_number, boundary_via, latitude, longitude,'\
                       ' arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing, name')
  
  
  def __init__(self, lat_min, lat_max, lon_min, lon_max):
    self.lat_min = lat_min
    self.lat_max = lat_max
    self.lon_min = lon_min
    self.lon_max = lon_max
    
    
    return
  
  def in_roi(self, lat, lon):
    if lat == None or lon == None:
      return False
    
    if self.lat_min <= lat and lat <= self.lat_max and self.lon_min <= lon and lon <= self.lon_max:
      return True 
    return False
  
  @staticmethod
  def get_record_info(record):
    """determine the record classification information
    
    record: CIFP string
    
    returns: tuple containing:(Record Type,
                               Area Code,
                               Section Code,
                               Airport ICAO Identifier,
                               Subsection Code)"""
    record_type = record[0]
    area_code = record[1:4]
    section_code = record[4]
    
    if record_type == 'S':
      if section_code == 'D':  # NAVAID Section
        subsection_code = record[5]
      elif section_code == 'E': # Enroute Section
        subsection_code = record[5]
      elif section_code == 'P': # Airport Section
        if record[5] == " ":
          subsection_code = record[12]
        else:
          subsection_code = record[5]
      elif section_code == 'U': # Special Use Airspace Section
        subsection_code = record[5]
      elif section_code == 'A': # Minimum Off Route Altitude Section
        subsection_code = record[5]
      elif section_code == 'H': # Heliport Section
        subsection_code = record[12]
      elif section_code == 'T': # Cruising Table Section
        subsection_code = record[5]
      else:
        print("Unexpected Section Code: {}".format(section_code))
        subsection_code = ''
    if record_type == 'H':
      subsection_code = ' '

    return CIFPReader.SECTIONS(area_code, section_code, subsection_code)
  
  @staticmethod
  def parse_controlled_airspace(record):
    """parse a controlled airport record (UC)
    
    Types: A: Class C
           R: TRSA
           T: Class B
           Z: Class D
    
    Boundary Via: A: Arc by edge
                  C: Full circle
                  G: Great circle
                  H: Rhumb line
                  L: CCW Arc
                  R: CW Arc"""
    # SUSAUCK2ZKBJC PAD  A00100     CE                   N39543200W1050702000050       GND  A07999MDENVER                        473321703
    
    # SUSAUCK2ZKEGE PAD  A00100     G N39342405W106564855                              GND  A09100MEAGLE                         473842004
    # SUSAUCK2ZKEGE PAD  A00200     R N39322480W106574152N39383390W10654574000651990                                             473852004
    # SUSAUCK2ZKEGE PAD  A00300     G N39392116W107031860                                                                        473862004
    # SUSAUCK2ZKEGE PAD  A00400     R N39390596W107003665N39383390W10654574000442770                                             473872004
    # SUSAUCK2ZKEGE PAD  A00500     G N39414066W106505555                                                                        473882004
    # SUSAUCK2ZKEGE PAD  A00600     R N39430974W106490000N39383390W10654574000650450                                             473892004
    # SUSAUCK2ZKEGE PAD  A00700     G N39370580W106464564                                                                        473902004
    # SUSAUCK2ZKEGE PAD  A00800     REN39373433W106492447N39383390W10654574000441030                                             473912004

    # SUSAUCK2ZKBKF PAD  A00100     R N39393650W104402500N39420630W10445071000441245   GND  A07499MAURORA                        473331703
    # SUSAUCK2ZKBKF PAD  A00200     G N39460130W104474270                                                                        473341703
    # SUSAUCK2ZKBKF PAD  A00300     G N39455530W104472450                                                                        473351703
    # SUSAUCK2ZKBKF PAD  A00400     G N39453560W104462610                                                                        473361703
    # SUSAUCK2ZKBKF PAD  A00500     G N39452270W104454850                                                                        473371703
    # SUSAUCK2ZKBKF PAD  A00600     G N39451240W104451840                                                                        473381703
    # SUSAUCK2ZKBKF PAD  A00700     G N39450370W104450200                                                                        473391703
    # SUSAUCK2ZKBKF PAD  A00800     G N39450000W104445630                                                                        473401703
    # SUSAUCK2ZKBKF PAD  A00900     G N39445390W104444630                                                                        473411703
    # SUSAUCK2ZKBKF PAD  A01000     G N39443000W104440480                                                                        473421703
    # SUSAUCK2ZKBKF PAD  A01100     GEN39442600W104435020                                                                        473431703
    # SUSAUCK2ZKBKF PAD  B01200     G N39442600W104435020                              GND  A06499MAURORA                        473441703
    # SUSAUCK2ZKBKF PAD  B01300     G N39442380W104434230                                                                        473451703
    # SUSAUCK2ZKBKF PAD  B01400     G N39442450W104425950                                                                        473461703
    # SUSAUCK2ZKBKF PAD  B01500     G N39442430W104414800                                                                        473471703
    # SUSAUCK2ZKBKF PAD  B01600     G N39442410W104402340                                                                        473481703
    # SUSAUCK2ZKBKF PAD  B01700     R N39442390W104401490N39420630W10445071000440586                                             473491703
    # SUSAUCK2ZKBKF PAD  B01800     GEN39393650W104402500                                                                        473501703
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    airspace_type = record[8]
    airspace_center = record[9:14].rstrip()
    airspace_classification = record[16]
    multiple_code = record[19]
    sequence_number = int(record[20:24])
    continuation_record_number = CIFPReader.parse_int(record[24])
    boundary_via = record[30:32]
    latitude = CIFPReader.parse_lat(record[32:41])
    longitude = CIFPReader.parse_lon(record[41:51])
    arc_origin_latitude = CIFPReader.parse_lat(record[51:60])
    arc_origin_longitude = CIFPReader.parse_lon(record[60:70])
    arc_distance = CIFPReader.parse_float(record[70:74], 10.0)
    arc_bearing = CIFPReader.parse_float(record[74:78], 10.0)
    name = record[93:123].rstrip()
    
    return CIFPReader.UC_DATA(airspace_type, airspace_center, airspace_classification, multiple_code, 
                              sequence_number, continuation_record_number, boundary_via, latitude, longitude, 
                              arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing, name)
  
  @staticmethod
  def parse_vhf_navaid(record):
    """
    """
    # D  VHF Navaid 3.2.2.1
    # SCAND        ADK   PA011400 DUW                    ADK N51521587W176402739E0070003291     NARMOUNT MOFFETT                 002361703
    # SLAMD        ANU   TA011450VDHW N17073316W061480060    N17073316W061480060W0150004002     NARV. C. BIRD                    165731707
    # SPACD        AWK   PW011350VTHW N19171169E166373840    N19171169E166373840E0060000182     NARWAKE ISLAND                   179381901
    # SSPAD        TUT   NS011250VTHW S14195732W170422980    S14195730W170422980E0120000102     NARPAGO PAGO                     226421605
    # SUSAD        ABI   K4011370VTHW N32285279W099514843    N32285279W099514843E0100018092     NARABILENE                       227901810
    # SUSAD        BJC   K2011540VDHW N39544695W105082035    N39544695W105082035E0110057372     NARJEFFCO                        228681605
    # SUSAD KACKK6 IACK  K6010910 ITW                    IACKN41144628W070043228W0160000120     NARNANTUCKET MEMORIAL            238471807
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # make sure this isn't a continuation record
    if record[21] == "0":
      # first record only
      if record[27] == "V":
        # VORs only
        ident = record[13:17].rstrip()
        frequency = CIFPReader.parse_float(record[22:27], 100)
        latitude = CIFPReader.parse_lat(record[32:41])
        longitude = CIFPReader.parse_lon(record[41:51])
        declination = CIFPReader.parse_variation(record[74:79])
        name = record[93:123].rstrip()
      else:
        return None
    else:
      print("VHF Continuation Record not handled:")
      print(record)
      return None
    
    return CIFPReader.NAVAID(ident, frequency, latitude, longitude, declination, name)
  
  @staticmethod
  def parse_ndbs(record):
    """
    """
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
    # make sure this isn't a continuation record
    if record[21] == "0":
      # first record only
      ident = record[13:17].rstrip()
      frequency = CIFPReader.parse_float(record[22:27], 10)
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      declination = CIFPReader.parse_variation(record[74:79])
      name = record[93:123].rstrip()
    else:
      print("NDB Continuation Record not handled:")
      print(record)
      return None
    
    return CIFPReader.NAVAID(ident, frequency, latitude, longitude, declination, name)
  
  @staticmethod
  def parse_waypoint(record):
    """
    """
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
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # make sure this isn't a continuation record
    if record[21] == "0":
      # first record only
      ident = record[13:18].rstrip()
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      declination = CIFPReader.parse_variation(record[74:79])
      name = record[98:123].rstrip()
    else:
      print("Waypoint Continuation Record not handled:")
      print(record)
      return None
    
    return CIFPReader.WAYPOINT(ident, latitude, longitude, declination, name)
  
  @staticmethod
  def parse_airport_primary_record(record):
    """parse an airport primary record (Section 4.1.7.1)
    
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
    icao_code = record[6:10].rstrip()
    latitude = CIFPReader.parse_lat(record[32:41])
    longitude = CIFPReader.parse_lon(record[41:51])
    declination = CIFPReader.parse_variation(record[51:56])
    elevation = float(record[56:61])
    name = record[93:123].rstrip()
    
    return CIFPReader.AIRPORT(icao_code, latitude, longitude, declination, elevation, name)
  
  @staticmethod
  def parse_runway(record):
    """
    """
    # PG Airport Runway 3.2.4.7
    # SCANP 01A PAGRW05    0011760463 N62562477W152162256               02034000050050D                                          042001703
    # SLAMP TISTTIGRW10    0070001000 N18201272W064590034               00024000055150I                                          169431613
    # SPACP PGROPGGRW09    0070000900 N14102878E145135249               00586000045150R                                          195061404
    # SSPAP NSASNSGRW08    0020000860 S14110237W169402216               00009000050060D                                          226531703
    # SUSAP 00ARK3GRW18    0025361765 N38582010W097360830               01328000050250D                                          753212002
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    if record[21] == "0":
      # first record only
      airport = record[6:10].rstrip()
      runway = record[13:18]
      length = CIFPReader.parse_float(record[22:27])
      bearing = CIFPReader.parse_float(record[27:31], 10.0)
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      elevation = CIFPReader.parse_float(record[66:71])
      dthreshold = CIFPReader.parse_float(record[71:75])
      tch = CIFPReader.parse_float(record[75:77])
      width = CIFPReader.parse_float(record[77:80])
    else:
      return None

    return CIFPReader.RUNWAY(airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width)
  
  @staticmethod
  def parse_float(fstr, divisor=1.0):
    # if fstr is empty we are done
    if fstr.strip() == "":
      return None
    return float(fstr)/divisor
  
  @staticmethod
  def parse_int(istr):
    # if istr is empty we are done
    if istr.strip() == "":
      return None
    return int(istr)
  
  @staticmethod
  def parse_lat(lat):
    # if lat is an empty string (just whitespace), we are done
    if lat.strip() == "":
      return None
    
    # 5.36
    # N39514200
    # 012345678
    hem = lat[0]
    deg = float(lat[1:3])
    mn = float(lat[3:5])
    sec = float(lat[5:])/100.0
    latitude = deg + mn/60.0 + sec/3600.0
    if hem == "S":
      latitude = -latitude
    return latitude
  
  @staticmethod
  def parse_lon(lon):
    # if lon is an empty string (just whitespace), we are done
    if lon.strip() == "":
      return None
    
    # 5.37
    # W104402340
    # 0123456789
    hem = lon[0]
    deg = float(lon[1:4])
    mn = float(lon[4:6])
    sec = float(lon[6:])/100.0
    longitude = deg + mn/60.0 + sec/3600.0
    if hem == "W":
      longitude = -longitude
    return longitude
  
  @staticmethod
  def parse_variation(var):
    # 5.39
    # E0080
    # 01234
    hem = var[0]
    variation = float(var[1:])/10.0
    if hem == "E":
      variation = -variation
    return variation


# define a version for this file
VERSION = "1.0"

class WaypointsOut:
  def __init__(self, path, filename, folder_name):
    self.kml_filename = path + '\\' + filename + '.kml'
    self.gpx_filename = path + '\\' + filename + '.gpx'
    
    self.configure_kml(folder_name)
    
    return
  
  def save_files(self):
    # save the kml file
    self.kml.save(self.kml_filename)
    return
  
  def configure_kml(self, folder_name):
    # create the kml document
    self.kml = simplekml.Kml()
    
    # create the top level folder
    self.kml.document.name = folder_name
    
    # create the folder structure
    self.d_folder = self.kml.newfolder(name="VHF Navaids (D )")
    self.db_folder = self.kml.newfolder(name="NDBs (DB)")
    self.pn_folder = self.kml.newfolder(name="Terminal NDBs (PN)")
    self.ea_folder = self.kml.newfolder(name="Enroute Waypoints (EA)")
    self.pc_folder = self.kml.newfolder(name="Terminal Waypoints (PC)")
    self.pa_folder = self.kml.newfolder(name="Airports (PA)")
    self.pg_folder = self.kml.newfolder(name="Runways (PG)")
    
    return
  
  def add_point(self, station_type, identifier, latitude, longitude, elevation_ft=None, name=None, frequency=None, declination=None, runway=None,
                length=None, bearing=None, width=None, dthreshold=None, tch=None):
    # 'VHF_NAVAID', 'ident,    frequency, latitude, longitude, declination,            name'
    # 'WAYPOINT',   'ident,               latitude, longitude, declination,            name'
    # 'AIRPORT',    'icao_code,           latitude, longitude, declination, elevation, name'
    # 'RUNWAY',     'airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width'
    
    
    # build our point with elevation if available
    if elevation_ft != None:
      # convert to meters
      elevation = 0.3048 * elevation_ft
      point = (longitude, latitude, elevation)
    else:
      point = (longitude, latitude)
    
    description = ''
    if station_type == "D ":
      description += "Name:{}\n".format(name)
      description += "Frequency:{:.2f} MHz\n".format(frequency)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.d_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "DB":
      description += "Name:{}\n".format(name)
      description += "Frequency:{:.0f} kHz\n".format(frequency)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.db_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "PN":
      description += "Name:{}\n".format(name)
      description += "Frequency:{:.0f} kHz\n".format(frequency)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.pn_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "EA":
      description += "Name:{}\n".format(name)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.ea_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "PC":
      description += "Name:{}\n".format(name)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.pc_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "PA":
      description += "Name:{}\n".format(name)
      description += "Elevation:{} feet\n".format(elevation_ft)
      description += "Declination:{:.1f} degrees\n".format(declination)
      pnt = self.pa_folder.newpoint(name=identifier, description=description, coords=[point])
    elif station_type == "PG":
      description += "Name:{} {}\n".format(identifier, runway)
      description += "Length:{:.0f} feet\n".format(length)
      description += "Elevation:{} feet\n".format(elevation_ft)
      description += "Runway Heading (mag):{:.1f} degrees\n".format(bearing)
      description += "Ruway Width:{:.0f} feet\n".format(width)
      description += "Threshold Crossover Height:{} feet\n".format(tch)
      description += "Displaced Threshold Distance:{} feet\n".format(dthreshold)
      pnt = self.pg_folder.newpoint(name="{}_{}".format(identifier, runway), description=description, coords=[point])
    
    # configure the point
    if elevation_ft != None:
      pnt.lookat = simplekml.LookAt(altitudemode=simplekml.AltitudeMode.absolute,
                                    latitude=latitude,
                                    longitude=longitude,
                                    range=15000, heading=0.0, tilt=0.0)
    else:
      pnt.lookat = simplekml.LookAt(altitudemode=simplekml.AltitudeMode.clamptoground,
                                    latitude=latitude,
                                    longitude=longitude,
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
      


if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # define the area of interest
  lat_min = 36.0
  lat_max = 44.5
  lon_min = -110.0
  lon_max = -98.0
  
  cifp = CIFPReader(lat_min, lat_max, lon_min, lon_max)
  
  location_out = WaypointsOut(r"C:\Data\CIFP\CIFP_200521\Processed", "CIFP_200521_Locations", "Locations")
  airspace_out = ShapesOut(r"C:\Data\CIFP\CIFP_200521\Processed", "CIFP_200521_Airspace", "Airspace")
  runways_out = ShapesOut(r"C:\Data\CIFP\CIFP_200521\Processed", "CIFP_200521_Runways", "Runways")
  
  runway_processor = RunwayProcessor(runways_out)
  
  vhf_navaids = {}
  ndbs = {}
  airports = {}
  waypoints = {}
  runways = {}
  
  first_uc = True
  
  with open(r"C:\Data\CIFP\CIFP_200521\FAACIFP18", "r") as f:
    seen = []
    for line in f:
      info = CIFPReader.get_record_info(line)
           
      # D  VHF Navaid 3.2.2.1
      # Process All
      if info.section_code == "D" and info.subsection_code == " ":
        # 'ident, frequency, latitude, longitude, declination, name'
        data = CIFPReader.parse_vhf_navaid(line)
        if data != None and cifp.in_roi(data.latitude, data.longitude):
          vhf_navaids[data.ident] = data
          location_out.add_point(station_type=info.section_code+info.subsection_code,
                                 identifier=data.ident,
                                 latitude=data.latitude,
                                 longitude=data.longitude,
                                 name=data.name,
                                 frequency=data.frequency,
                                 declination=data.declination)
      
      # DB NDB Navaid 3.2.2.2
      # PN Airport and Heliport Terminal NDB 3.2.4.13
      if (info.section_code == "D" and info.subsection_code == "B") or (info.section_code == "P" and info.subsection_code == "N"):
        # 'ident, frequency, latitude, longitude, declination, name'
        data = CIFPReader.parse_ndbs(line)
        if data != None and cifp.in_roi(data.latitude, data.longitude):
          ndbs[data.ident] = data
          location_out.add_point(station_type=info.section_code+info.subsection_code,
                                 identifier=data.ident,
                                 latitude=data.latitude,
                                 longitude=data.longitude,
                                 name=data.name,
                                 frequency=data.frequency,
                                 declination=data.declination)
      
      # PA Airport Reference Points 3.2.4.1
      if info.section_code == "P" and info.subsection_code == "A":
        # 'icao_code, latitude, longitude, declination, elevation, name'
        data = CIFPReader.parse_airport_primary_record(line)
        if data != None and cifp.in_roi(data.latitude, data.longitude):
          airports[data.icao_code] = data
          location_out.add_point(station_type=info.section_code+info.subsection_code,
                                 identifier=data.icao_code,
                                 latitude=data.latitude,
                                 longitude=data.longitude,
                                 elevation_ft=data.elevation,
                                 name=data.name,
                                 declination=data.declination)
      
      # EA Enroute Waypoint 3.2.3.1
      # PC Airport Terminal Waypoints 3.2.4.3
      if (info.section_code == "E" and info.subsection_code == "A") or (info.section_code == "P" and info.subsection_code == "C"):
        # 'ident, latitude, longitude, declination, name'
        data = CIFPReader.parse_waypoint(line)
        if data != None and cifp.in_roi(data.latitude, data.longitude):
          waypoints[data.ident] = data
          location_out.add_point(station_type=info.section_code+info.subsection_code,
                                 identifier=data.ident,
                                 latitude=data.latitude,
                                 longitude=data.longitude,
                                 name=data.name,
                                 declination=data.declination)
      
      # PG Airport Runway 3.2.4.7
      if (info.section_code == "P" and info.subsection_code == "G"):
        # 'airport, runway, length, bearing, latitude, longitude, elevation, dthreshold, tch, width'
        data = CIFPReader.parse_runway(line)
        if data != None and cifp.in_roi(data.latitude, data.longitude):
          runways[data.airport+'_'+data.runway] = data
          location_out.add_point(station_type=info.section_code+info.subsection_code,
                                 identifier=data.airport,
                                 latitude=data.latitude,
                                 longitude=data.longitude,
                                 elevation_ft=data.elevation,
                                 name=data.runway,
                                 runway=data.runway,
                                 length=data.length,
                                 bearing=data.bearing,
                                 width=data.width,
                                 dthreshold=data.dthreshold,
                                 tch=data.tch)

      # UC Controlled Airspace 3.2.6.3
      if info.section_code == "U" and info.subsection_code == "C":
        data = CIFPReader.parse_controlled_airspace(line)
        # is this even in our ROI?
        if cifp.in_roi(data.arc_origin_latitude, data.arc_origin_longitude) or cifp.in_roi(data.latitude, data.longitude):
          if first_uc:
            if data.boundary_via == "CE":
              # this is a complete shape for this airport, save and reset
              shape = maptools.circle((data.arc_origin_latitude, data.arc_origin_longitude), data.arc_distance)
              airspace_out.add_shape(data.airspace_center, 
                                     "Class {} Sequence {}".format(data.airspace_classification, data.multiple_code), 
                                     "", 
                                     shape, 
                                     simplekml.Color.blue, 
                                     ShapesOut.OUTCOLOR_MAGENTA)
            else:
              # save this point and continue
              uc_current = [data]
              first_uc = False
          else:
            # add this point to our list
            uc_current.append(data)
            
            # is this the last point in the shape?
            last = data.boundary_via[1] == "E"
            if last:
              # process this shape, begin with the first point
              shape = [(uc_current[0].latitude, uc_current[0].longitude)]
              for i in range(len(uc_current)):
                if uc_current[i].boundary_via[0] == "A":
                  # arc by edge
                  print("Arc by edge not yet supported")
                elif uc_current[i].boundary_via[0] == "C":
                  # circle
                  print("Circle should have been supported above")
                elif uc_current[i].boundary_via[0] == "G":
                  # great circle
                  # simply add the next point
                  if uc_current[i].boundary_via[1] == 'E':
                    shape.append((uc_current[0].latitude, uc_current[0].longitude))
                  else:
                    shape.append((uc_current[i+1].latitude, uc_current[i+1].longitude))
                elif uc_current[i].boundary_via[0] == "H":
                  # rhumb line
                  print("Rhumb line not yet supported")
                elif uc_current[i].boundary_via[0] == "L" or uc_current[i].boundary_via[0] == "R":
                  # CCW arc
                  arc_begin = (uc_current[i].latitude, uc_current[i].longitude)
                  
                  if uc_current[i].boundary_via[1] == 'E':
                    arc_end = (uc_current[0].latitude, uc_current[0].longitude)
                  else:
                    arc_end = (uc_current[i+1].latitude, uc_current[i+1].longitude)
                    
                  arc_center = (uc_current[i].arc_origin_latitude, uc_current[i].arc_origin_longitude)
                  
                  radius_nm = uc_current[i].arc_distance
                  
                  if uc_current[i].boundary_via[0] == "R":
                    clockwise = True
                  else:
                    clockwise = False
                  arc = maptools.arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise)
                  for p in arc:
                    shape.append(p)
                else:
                  print("Unrecognized boundary via")
                  print(data)
              
              # add the data to the files
              airspace_out.add_shape(data.airspace_center, 
                                     "Class {} Sequence {}".format(data.airspace_classification, data.multiple_code), 
                                     "", 
                                     shape, 
                                     simplekml.Color.blue, 
                                     ShapesOut.OUTCOLOR_MAGENTA)
              
              # reset
              first_uc = True
              
                 
      # ER Enroute Airways 3.2.3.4
      # SCANER       A1          0150BBGVPPAEA0E    O                         312104802987 05200                                   024982002
      # SEEUER       B96         0100LARSAUHEA0E    O                         12050213     05000     18000                         165712006
      # SLAMER       A517        0100ZPATATJEA0E    O                         34900375     06000     45000                         167211901
      # SPACER       A216        0100MONPIP EA0E    O                         16302692     18000     60000                         188692002
      # SUSAER       A1          0110CFMTLK1EA0E    O                         22290226     02800                                   510572002      
      
      # PF Airport Approaches 3.2.4.6
      # SUSAP 00R K4FR30   ADAS   010DAS  K4D 0V       IF                                             18000                 B JS   753670804
      
      # PP Airport and Heliport Path Point 3.2.4.14
      # SUSAP 02A K7PR08   RW08 001 0000W08A0N3250577430W08637041540+014950000N3251157585W08635205635106751528000000F4000001D1CE6EA754871610
      
      # PE Airport Standard Terminal Arrival Routes 3.2.4.5
      # SUSAP 05C K5EGSH7  1FWA   010FWA  K5D 0V       IF                                             18000                        757471705
      
      # PD Airport Standard Instrument Departures 3.2.4.4
      # SUSAP 05U K2DMINES14RW36  010         0        VA                     3580        + 06500     18000                        758611309
      
      # PI Airport and Heliport Localizer/Glide Slope 3.2.4.8
      # SUSAP 3J7 K7IIVVM0   011090RW25 N33353920W0830850922491                   0370     0600   W0050                            862591209
      
      # UC Controlled Airspace 3.2.6.3
      # SUSAUCK1ACYVR PAC  A00100     G N49000000W123192000                              02500M12500MVANCOUVER                     442391703
      
      # UR Restrictive Airspace 3.2.6.1
      # SUSAURK1A680       A00100L    CE                   N48105900W1223805000030       GND  A03000MA-680                         553831703
      
      # No need to process
      
      # HA Heliport 3.3.3
      # SUSAH 00A K6A00AH1   0     NARN N40041500W074560100W012000011         1800018000C    080080M TOTAL RF                      689881703
      
      # HC Heliport Terminal Waypoints 3.3.4
      # SUSAH 87N K6CCRANN K60    W     N40514240W072275511                       W0136     NAR           CRANN                    721662002
      
      # HF Heliport Approaches 3.3.7
      # SUSAH 87N K6FR190  ACCC   010CCC  K6D 0V       IF                                             18000                 B JH   721691505

  # process the runways
  runway_processor.process_runway(runways, airports)
   
  # save the location files
  location_out.save_files()
  airspace_out.save_files()
  runways_out.save_files()
  
  print("Done.")
  
      
    
  
