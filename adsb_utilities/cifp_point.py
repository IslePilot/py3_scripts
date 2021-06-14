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

  May 30, 2020, ksb, created
"""

import sys
from sympy.physics.quantum.tests.test_qapply import po
sys.path.append("..")

import cifp_functions as cf

class CIFPPointSet:
  """a set of Points of similar type (i.e. vors or ndbs)"""
  
  def __init__(self):
    self.points = {}  # dictionary of CIFPPoint, key is ident
    
    return
  
  def has_point(self, ident):
    if ident in self.points:
      return True
    return False
  
  def add_point(self, point):
    self.points[point.ident] = point
    return
  
  def add_continuation(self, continuation):
    if continuation.ident in self.points:
      # add the continuation information to the appropriate point
      print("PointSet.add_continuation: No continuation data defined")
    return
  
  def get_data(self, ident):
    if ident not in self.points:
      return None
    
    return self.points[ident]
  
  def get_point(self, ident):
    if ident not in self.points:
      # do we have a whitespace issue?
      if ident.rstrip() in self.points:
        # yup...use the stripped version
        ident = ident.rstrip()
      else:
        # point is probably outside the ROI
        return None
    
    position = (self.points[ident].latitude, self.points[ident].longitude)
    
    # build the description
    description = ""
    heading = None
    if self.points[ident].style == CIFPPoint.POINT_VOR:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Type: VOR\n"
      description += "Frequency:{:.2f} MHz\n".format(self.points[ident].frequency)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_VORDME:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Type: VOR/DME\n"
      description += "Frequency:{:.2f} MHz\n".format(self.points[ident].frequency)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_VORTAC:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Type: VORTAC\n"
      description += "Frequency:{:.2f} MHz\n".format(self.points[ident].frequency)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_NDB:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Frequency:{:.0f} kHz\n".format(self.points[ident].frequency)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_ENROUTE_WAYPOINT:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_TERMINAL_WAYPOINT:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_TERMINAL_NDB:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Frequency:{:.0f} kHz\n".format(self.points[ident].frequency)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_AIRPORT:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Elevation:{} feet\n".format(self.points[ident].elevation_ft)
      description += "Declination:{:.1f} degrees\n".format(self.points[ident].declination)
    elif self.points[ident].style == CIFPPoint.POINT_RUNWAY:
      description += "Name:{}\n".format(self.points[ident].name)
      description += "Length:{:.0f} feet\n".format(self.points[ident].length_ft)
      description += "Elevation:{} feet\n".format(self.points[ident].elevation_ft)
      description += "Runway Heading (mag):{:.1f} degrees\n".format(self.points[ident].bearing)
      description += "Ruway Width:{:.0f} feet\n".format(self.points[ident].width_ft)
      description += "Threshold Crossover Height:{} feet\n".format(self.points[ident].tch_ft)
      description += "Displaced Threshold Distance:{} feet\n".format(self.points[ident].dthreshold_ft)
      heading = self.points[ident].bearing
    
    return cf.ProcedureFix(position, self.points[ident].declination, self.points[ident].ident, description, self.points[ident].elevation_ft, heading)
  
  def get_points(self):
    """return a list of points with details
    
    each list member will include: (ident, (latitude, longitude), description)"""
    # initialize the list
    point_list = []
    
    # loop through all of the points
    for key, point in self.points.items():
      # get the position
      position = (point.latitude, point.longitude)
      
      # build the description
      description = ""
      if point.style == CIFPPoint.POINT_VOR:
        description += "Name:{}\n".format(point.name)
        description += "Type: VOR\n"
        description += "Frequency:{:.2f} MHz\n".format(point.frequency)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_VORDME:
        description += "Name:{}\n".format(point.name)
        description += "Type: VOR/DME\n"
        description += "Frequency:{:.2f} MHz\n".format(point.frequency)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_VORTAC:
        description += "Name:{}\n".format(point.name)
        description += "Type: VORTAC\n"
        description += "Frequency:{:.2f} MHz\n".format(point.frequency)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_NDB:
        description += "Name:{}\n".format(point.name)
        description += "Frequency:{:.0f} kHz\n".format(point.frequency)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_ENROUTE_WAYPOINT:
        description += "Name:{}\n".format(point.name)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_TERMINAL_WAYPOINT:
        description += "Name:{}\n".format(point.name)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_TERMINAL_NDB:
        description += "Name:{}\n".format(point.name)
        description += "Frequency:{:.0f} kHz\n".format(point.frequency)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_AIRPORT:
        description += "Name:{}\n".format(point.name)
        description += "Elevation:{} feet\n".format(point.elevation_ft)
        description += "Declination:{:.1f} degrees\n".format(point.declination)
      elif point.style == CIFPPoint.POINT_RUNWAY:
        description += "Name:{}\n".format(point.name)
        description += "Length:{:.0f} feet\n".format(point.length_ft)
        description += "Elevation:{} feet\n".format(point.elevation_ft)
        description += "Runway Heading (mag):{:.1f} degrees\n".format(point.bearing)
        description += "Ruway Width:{:.0f} feet\n".format(point.width_ft)
        description += "Threshold Crossover Height:{} feet\n".format(point.tch_ft)
        description += "Displaced Threshold Distance:{} feet\n".format(point.dthreshold_ft)

      # add our data to the list
      point_list.append((key, position, point.name, description, point.elevation_ft))
    
    return point_list

    
class CIFPPoint:
  """Points are locations in 3D space and include VORs, NDBs, Waypoints, 
  runway locations, and airport locations"""
  POINT_VOR = 0
  POINT_VORDME = 1
  POINT_VORTAC = 2
  POINT_NDB = 3
  POINT_TERMINAL_NDB = 4
  POINT_ENROUTE_WAYPOINT = 5
  POINT_TERMINAL_WAYPOINT = 6
  POINT_AIRPORT = 7
  POINT_RUNWAY = 8
  POINT_LOCALIZER_ONLY = 9
  POINT_LOCALIZER_CATI = 10
  POINT_LOCALIZER_CATII = 11
  POINT_LOCALIZER_CATIII = 12
  POINT_IGS = 13
  POINT_LDA_GS = 14
  POINT_LDA = 15
  POINT_SDF_GS = 16
  POINT_SDF = 17
  POINT_DME = 18
  POINT_TACAN = 19
  
  def __init__(self, record):
    """read and parse a CIFPPoint record"""
    # determine the code for this record
    # identify the type of line
    self.code = cf.section(record)  # valid while we process this record
    
    # initialize all values
    # standard items
    self.valid = False
    self.ident = None # ident: Identifier for the point (DEN, FN, TOMSN, KBJC)
    self.name = None  # name: Expanded name of the point (Denver, COLLN, TOMSN, Rocky Mountain Metropolitan)
    self.style = None # style: Type of waypoint (self.POINT_VOR, etc.)
    self.latitude = None  # latitude: WGS84 latitude (decimal degrees, northern hemisphere positive)
    self.longitude = None # longitude: WGS84 longitude (decimal degrees, eastern hemisphere positive)
    self.continuation_count = None  # continuation: continuation number
    
    # some points
    self.declination = None # declination: [optional] magnetic variation at the point, or the alignment of the navaid
    self.frequency = None # frequency: [optional] radio frequency of the navaid (VOR in MHz, NDB in kHz)
    self.elevation_ft = None  # elevation_ft: [optional] elevation in feet above sea level
    self.airport = None # airport: [optional] ident of the airport this item "belongs" to
    
    # runway points
    self.length_ft = None # length_ft: [optional] runway length in feet
    self.bearing = None # bearing: [optional] runway magnetic alignment
    self.tch_ft = None  # tch_ft: [optional] threshold crossover height in feet
    self.width_ft = None  # width_ft: [optional] runway width in feet
    self.dthreshold_ft = None # dthreshold_ft: [optional] displaced threshold distance in feet
    
    # process the record
    if self.code == "D ":
      self.parse_vhf_navaid_primary(record)
    elif self.code == "DB":
      self.parse_ndb_primary(record)
    elif self.code == "PN":
      self.parse_ndb_primary(record)
    elif self.code == "PA":
      self.parse_airport_primary(record)
    elif self.code == "PG":
      self.parse_runway_primary(record)
    elif self.code == "EA":
      self.parse_waypoint_primary(record)
    elif self.code == "PC":
      self.parse_waypoint_primary(record)
    elif self.code == "PI":
      self.parse_localizer_primary(record)
    
    return
  
  def set_declination(self, declination):
    if self.declination == None:
      self.declination = declination
    else:
      print("CIFPPoint.set_declination: Attempt to set declination that is already set ignored")
    return
  
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
        self.style = self.POINT_VOR
      elif t2 == "D":
        self.style = self.POINT_VORDME
      elif t2 == "T" or t2 == "M":
        self.style = self.POINT_VORTAC
      else:
        print("Point.parse_vhf_navaid: Unexpected VOR type: {}".format(record))
      
      self.latitude = cf.parse_lat(record[32:41])
      self.longitude = cf.parse_lon(record[41:51])
    
    elif record[28] == "D": # this is just a DME
      self.style = self.POINT_DME
      self.latitude = cf.parse_lat(record[55:64])
      self.longitude = cf.parse_lon(record[64:74])
    elif record[28] == "T": # this is just a TACAN
      self.style = self.POINT_TACAN
      self.latitude = cf.parse_lat(record[55:64])
      self.longitude = cf.parse_lon(record[64:74])
    

    # now parse the rest of the record
    self.ident = record[13:17].rstrip()
    self.continuation_count = record[21]
    self.frequency = cf.parse_float(record[22:27], 100)
    self.declination = cf.parse_variation(record[74:79])
    self.name = record[93:123].rstrip()
    
    # good point!
    self.valid = True
    
    return
  
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
    # SUSAPNKFNLK2 FN    K2004000HO W N40214744W104581691                       E0090           NARCOLLN                         440511712
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # identify the style
    if self.code == "DB":
      self.style = self.POINT_NDB
    elif self.code == "PN":
      self.style = self.POINT_TERMINAL_NDB
      self.airport = record[6:10].rstrip() # populated only for terminal NDBs
    else:
      print("CIFPReader.parse_ndb: Unexpected NDB type: {}".format(record))

    
    # parse the record
    self.ident = record[13:17].rstrip()
    self.continuation_count = record[21]
    self.frequency = cf.parse_float(record[22:27], 10)
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.declination = cf.parse_variation(record[74:79])
    self.name = record[93:123].rstrip()
    
    # good point
    self.valid = True
    
    return 
  
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
    if self.code == "EA":
      self.style = self.POINT_ENROUTE_WAYPOINT
    elif self.code == "PC":
      self.style = self.POINT_TERMINAL_WAYPOINT
      self.airport = record[6:10].rstrip()
    else:
      print("CIFPReader.parse_waypoint: Unexpected Waypoint type: {}".format(record))
    
    # parse the record
    self.ident = record[13:18].rstrip()
    self.continuation_count = record[21]
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.declination = cf.parse_variation(record[74:79])
    self.name = record[98:123].rstrip()

    # good point
    self.valid = True
    
    return
  
  def parse_airport_primary(self, record):
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
    self.style = self.POINT_AIRPORT
    
    self.ident = record[6:10].rstrip()
    self.continuation_count = record[21]
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.declination = cf.parse_variation(record[51:56])
    self.elevation_ft = float(record[56:61])
    self.name = record[93:123].rstrip()
    self.airport = self.ident
    
    # good point
    self.valid = True
    
    return
  
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
    self.style = self.POINT_RUNWAY
    
    self.airport = record[6:10].rstrip()
    self.ident = record[13:18]
    self.name = self.airport + ' ' + self.ident
    self.continuation_count = record[21]
    self.length_ft = cf.parse_float(record[22:27])
    self.bearing = cf.parse_float(record[27:31], 10.0)
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.elevation_ft = cf.parse_float(record[66:71])
    self.dthreshold_ft = cf.parse_float(record[71:75])
    self.tch_ft = cf.parse_float(record[75:77])
    self.width_ft = cf.parse_float(record[77:80])
    
    # good point
    self.valid = True
    
    return

  def parse_localizer_primary(self, record):
    # SUSAP KDENK2IIACX1   010850RW17RN39493182W1043938101725N39513091W1043931421019 09650308300E00806605378                     625201808
    # SUSAP KDENK2IIAQD3   010850RW35LN39515060W1043936443525N39495276W1043932601020 11010308300E00805705423                     625211808
    # SUSAP KDENK2IIBXP1   011015RW17LN39494517W1043830281725N39514406W1043823561023 09840308300E00804805326                     625221212
    # SUSAP KDENK2IIDPP3   011015RW35RN39520394W1043828573525N39500636W1043824771023 11260308300E00805905360                     625231212
    # SUSAP KDENK2IIDQQ1   011190RW16RN39505678W1044147831725N39533482W1044151281009 10200236300E00805505317                     625241408
    # SUSAP KDENK2IIDXU3   011190RW34LN39535488W1044145783525N39511760W1044152851013 10900236300E00805505318                     625251506
    # SUSAP KDENK2IIDZG1   011155RW07 N39502628W1044049060825N39502327W1044322661020 10420308300E00805505341                     625261702
    # SUSAP KDENK2IIERP1   011155RW25 N39502749W1044349072625N39502241W1044115791023 10580308300E00805505344                     625271212
    # SUSAP KDENK2IIFUI1   010890RW08 N39523798W1043657040825N39524315W1043929861023 11010308300E00805205342                     625281212
    # SUSAP KDENK2IIJOY1   010890RW26 N39523930W1043957142626N39524222W1043722391023 09580308300E00805505293                     625291212
    # SUSAP KDENK2IILTT1   011110RW16LN39514067W1044114001725N39533955W1044117871019 09940308300E00806005347                     625301408
    # SUSAP KDENK2IIOUF3   011110RW34RN39535944W1044112383525N39520139W1044119011024 10710308300E00805905346                     625311212
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    # get the style
    ils_cat = record[17]
    if ils_cat == '0':
      self.style = CIFPPoint.POINT_LOCALIZER_ONLY
    elif ils_cat == '1':
      self.style = CIFPPoint.POINT_LOCALIZER_CATI
    elif ils_cat == '2':
      self.style = CIFPPoint.POINT_LOCALIZER_CATII
    elif ils_cat == '3':
      self.style = CIFPPoint.POINT_LOCALIZER_CATII
    elif ils_cat == 'I':
      self.style = CIFPPoint.POINT_IGS
    elif ils_cat == 'L':
      self.style = CIFPPoint.POINT_LDA_GS
    elif ils_cat == 'A':
      self.style = CIFPPoint.POINT_LDA
    elif ils_cat == 'S':
      self.style = CIFPPoint.POINT_SDF_GS
    elif ils_cat == 'F':
      self.style = CIFPPoint.POINT_SDF
    else:
      print("CIFPPoint.parse_localizer_primary: Unexpected Localizer type: {}:".format(record.rstrip()))
    
    # now parse the rest of the record
    self.airport = record[6:10].rstrip()
    self.ident = record[13:17].rstrip()
    self.name = self.airport + ' ' + self.ident
    self.continuation_count = record[21]
    self.frequency = cf.parse_float(record[22:27], 100)
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.bearing = cf.parse_float(record[51:55], 10.0)
    self.declination = cf.parse_variation(record[90:95])
    self.tch_ft = cf.parse_float(record[95:97])
    self.elevation_ft = cf.parse_float(record[97:102])
      
    # good point!
    self.valid = True
    
    return

class CIFPPointContinuation:
  def __init__(self, record):
    # get the section
    self.code = cf.section(record)
    
    # parse the base information from the record
    self.parse_base(record)
    
    # add further processing calls here
    print("PointContinuation.__init__: No continuation records supported: {}".format(record.rstrip()) )
    
    return 
  
  def parse_base(self, record):
    self.ident = record[6:10].rstrip()
    self.continuation_count = record[21]
    self.application_type = record[22]
    