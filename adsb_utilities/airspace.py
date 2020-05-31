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

import cifp_functions as cf
import maptools as maptools

# define a version for this file
VERSION = "1.0"

class AirspaceShape:
  """define a basic block of airspace, either controlled or restrictive"""  
  def __init__(self):
    self.ar = []
    
    self.name = None
    self.controlling_agency = None
    
    return
  
  def add_airspace_record(self, airspace_record):
    if airspace_record.controlling_agency != None:
      # this must be a continuation record
      self.controlling_agency = airspace_record.controlling_agency
    else:
      # simply append this record to our list
      self.ar.append(airspace_record)
      
      # the first record in the set will have the full name
      if airspace_record.name != "":
        self.name = airspace_record.name
    
    return

  def build_airspace_shape(self):
    """build a list of (lat, lon) tuples defining and airspace shape"""
    # initialize our shape with the first cifp_point
    shape = [(self.ar[0].latitude, self.ar[0].longitude)]
    
    # work through the list of points
    for i in range(len(self.ar)):
      via = self.ar[i].boundary_via[0]
      end = self.ar[i].boundary_via[1]
      
      if via == "A":
        # arc by edge
        print("AirspaceShape.build_airspace_shape: Arc by edge not yet supported")
      elif via == "C":
        # circle
        shape = maptools.circle((self.ar[0].arc_origin_latitude, self.ar[0].arc_origin_longitude), self.ar[0].arc_distance)
      elif via == "G":
        # Great circle cifp_point
        # if this is an end, add the first cifp_point otherwise add the next cifp_point
        if end == "E":
          shape.append((self.ar[0].latitude, self.ar[0].longitude))
        else:
          shape.append((self.ar[i+1].latitude, self.ar[i+1].longitude))
      elif via == "H":
        # Rhumb line -- not really correct, but just treat as a great circle, error won't be large for normal distances
        if end == "E":
          shape.append((self.ar[0].latitude, self.ar[0].longitude))
        else:
          shape.append((self.ar[i+1].latitude, self.ar[i+1].longitude))
      elif via == "L" or via == "R":
        # define the start
        arc_begin = (self.ar[i].latitude, self.ar[i].longitude)
        
        # define the end
        if end == "E":
          arc_end = (self.ar[0].latitude, self.ar[0].longitude)
        else:
          arc_end = (self.ar[i+1].latitude, self.ar[i+1].longitude)
        
        # define the center
        arc_center = (self.ar[i].arc_origin_latitude, self.ar[i].arc_origin_longitude)
        
        # get the radius
        radius_nm = self.ar[i].arc_distance_nm
        
        # get the direction
        if via == "R":
          clockwise = True
        else:
          clockwise = False
        
        # create a name
        if self.ar[i].airspace_classification != None:
          # UC Airspace
          name = "Class {} Section {}".format(self.ar[i].airspace_classification, self.ar[i].multiple_code)
        else:
          name = "{} Section {}".format(airspace_record.airspace_designation, airspace_record.multiple_code)
        
        # build the arc
        arc = maptools.arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise, name)
        for p in arc:
          shape.append(p)
      else:
        print("AirspaceShape.build_airspace_shape: Unrecognized boundary via")
        
    return shape
  

class AirspaceRecord:
  
  TYPE_CONTROLLED_CLASS_C = 'A'
  TYPE_CONTROLLED_CONTROL_AREA = 'C'
  TYPE_CONTROLLED_TERMINAL = 'M'
  TYPE_CONTROLLED_TRSA = 'R'
  TYPE_CONTROLLED_CLASS_B = 'T'
  TYPE_CONTROLLED_CLASS_D = 'Z'
  
  TYPE_RESTRICTIVE_ALERT = 'A'
  TYPE_RESTRICTIVE_CAUTION = 'C'
  TYPE_RESSTRICTIVE_DANGER = 'D'
  TYPE_RESTRICTIVE_MOA = 'M'
  TYPE_RESTRICTIVE_PROHIBITED = 'P'
  TYPE_RESTRICTIVE_RESTRICTED = 'R'
  TYPE_RESTRICTIVE_TRAINING = 'T'
  TYPE_RESTRICTIVE_WARNING = 'W'
  TYPE_RESTRICTIVE_UNSPECIFIED = 'U'
  
  def __init__(self, record):
    # save the raw data
    self.record = record
    
    # parse the data
    self.section = record[4:6]
    
    self.continuation = False
    
    if self.section == "UC":
      self.parse_controlled_airspace(record)
    elif self.section == "UR":
      if record[24] == '0' or record[24] == '1':
        self.parse_restrictive_airspace(record)
      else:
        self.continuation = True
        self.parse_continuation_record(record)
    else:
      print("AirspaceRecord.__init__: Unknown airspace type: {}".format(self.section))
    return 
  
  def parse_controlled_airspace(self, record):
    """parse a controlled airport record (UC)"""
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
    self.airport = record[9:14].rstrip() # airport identifier
    self.airspace_center_section = record[14:16]
    self.airspace_classification = record[16]  # A through G
    
    # unused members
    self.airspace_designation = None
    self.controlling_agency = None
    
    # same as UR
    self.airspace_type = record[8]  # eg: self.TYPE_CONTROLLED_CLASS_C
    self.multiple_code = record[19] # designator defining airspace section (A-)...airspace with only one section will only have A
    self.sequence_number = int(record[20:24])
    self.continuation_count = cf.parse_int(record[24])
    self.boundary_via = record[30:32]
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.arc_origin_latitude = cf.parse_lat(record[51:60])
    self.arc_origin_longitude = cf.parse_lon(record[60:70])
    self.arc_distance_nm = cf.parse_float(record[70:74], 10.0)
    self.arc_bearing = cf.parse_float(record[74:78], 10.0)
    self.name = record[93:123].rstrip()
    
    return
  
  def parse_restrictive_airspace(self, record):
    """parse a restrictive airport record (UR)"""
    # SUSAURK2MCOUGAR H  A00101L    G N38533000W103000000                              11000M17999MCOUGAR HIGH MOA               580281703
    # SUSAURK2MCOUGAR H  A00102C                                                                         FAA DENVER ARTCC        580291703
    # SUSAURK2MCOUGAR H  A00200L    G N39071900W102144300                                                                        580301703
    # SUSAURK2MCOUGAR H  A00300L    G N39014000W101000000                                                                        580311703
    # SUSAURK2MCOUGAR H  A00400L    G N38381000W101000000                                                                        580321703
    # SUSAURK2MCOUGAR H  A00500L    H N38233000W102120400                                                                        580331703
    # SUSAURK2MCOUGAR H  A00600L    G N38233000W102443400                                                                        580341703
    # SUSAURK2MCOUGAR H  A00700L    GEN38344100W103000000                                                                        580351703
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    self.airspace_designation = record[9:19].rstrip()
    
    # unused records
    self.airport = None
    self.airspace_center_section = None
    self.airspace_classification = None
    self.controlling_agency = None
    
    # same as UC
    self.airspace_type = record[8]  # eg: self.TYPE_RESTRICTIVE_PROHIBITED
    self.multiple_code = record[19] # designator defining airspace section (A-)...airspace with only one section will only have A
    self.sequence_number = int(record[20:24])
    self.continuation_count = cf.parse_int(record[24])
    self.boundary_via = record[30:32]
    self.latitude = cf.parse_lat(record[32:41])
    self.longitude = cf.parse_lon(record[41:51])
    self.arc_origin_latitude = cf.parse_lat(record[51:60])
    self.arc_origin_longitude = cf.parse_lon(record[60:70])
    self.arc_distance_nm = cf.parse_float(record[70:74], 10.0)
    self.arc_bearing = cf.parse_float(record[74:78], 10.0)
    self.name = record[93:123].rstrip()

    return
  
  def parse_continuation_record(self, record):
    # Continuation Types (5.91, p 105)
    # C - Call Sign/Controlling Agency
    self.airspace_designation = record[9:19].rstrip()
    
    # same as UC
    self.multiple_code = record[19] # designator defining airspace section (A-)...airspace with only one section will only have A
    
    # check the application type to know what to parse
    if record[25] == "C":
      self.controlling_agency = record[99:123].rstrip()
    else:
      self.controlling_agency = None
      print("AirpsaceRecord.parse_continuation_record: Unhandled Continuation Record {}".format(record))
    
    return
    


