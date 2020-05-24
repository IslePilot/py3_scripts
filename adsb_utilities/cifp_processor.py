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
from scipy.io.matlab.tests.test_mio import theta
from _pylief import NONE
sys.path.append("..")
import __common.maptools as maptools

from collections import namedtuple
import simplekml
#import gpxpy
    

class Airport:
  def __init__(self):
    # initialize holders
    self.runways = {}
    self.ndbs = {}
    self.waypoints = {}
    self.airport = None
    
    # Procedure Dictionaries
    self.sids = {}
    self.stars = {}
    self.approaches = {}
    
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
  
  def add_reference_point(self, point):
    self.airport = point
    return
  
  def add_procedure(self, procedure_record):
    if procedure_record.subsection_code == "D":
      # Standard Instrument Departures (SIDS)
      # if this procedure doesn't exist, create it (i.e. BAYLR6)
      if procedure_record.procedure_identifier not in self.sids:
        self.sids[procedure_record.procedure_identifier] = Procedure()
      
      # add the procedure_record to the Procedure
      self.sids[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    elif procedure_record.subsection_code == "E":
      # Standard Terminal Arrivals (STARS)
    # if this procedure doesn't exist, create it (i.e. FLATI1)
      if procedure_record.procedure_identifier not in self.stars:
        self.stars[procedure_record.procedure_identifier] = Procedure()
      
      # add the procedure_record to the Procedure
      self.stars[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    elif procedure_record.subsection_code == "F":
      # Instrument Approach Procedures
      if procedure_record.procedure_identifier not in self.approaches:
        self.approaches[procedure_record.procedure_identifier] = Procedure()
      
      # add the procedure_record to the Procedure
      self.approaches[procedure_record.procedure_identifier].add_procedure_record(procedure_record)
    
    else:
      print("Airport.add_procedure: Skipping Unknown Subsection Code: {}".format(procedure_record.subsection_code))
    
    return

class Point:
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
  
  def __init__(self, ident, name, style, latitude, longitude, 
               declination=None, frequency=None, elevation_ft=None, 
               length_ft=None, bearing=None, tch_ft=None, width_ft=None, 
               dthreshold_ft=None, airport=None):
    """Create a point instance
    
    ident: Identifier for the point (DEN, FN, TOMSN, KBJC)
    name: Expanded name of the point (Denver, COLLN, TOMSN, Rocky Mountain Metropolitan)
    style: Type of waypoint (POINT_VOR, etc.)
    latitude: WGS84 latitude (decimal degrees, northern hemisphere positive)
    longitude: WGS84 longitude (decimal degrees, eastern hemisphere positive)
    declination: [optional] magnetic variation at the point, or the alignment of the navaid
    frequency: [optional] radio frequency of the navaid (VOR in MHz, NDB in kHz)
    elevation_ft: [optional] elevation in feet above sea level
    length_ft: [optional] runway length in feet
    bearing: [optional] runway magnetic alignment
    tch_ft: [optional] threshold crossover height in feet
    width_ft: [optional] runway width in feet
    dthreshold_ft: [optional] displaced threshold distance in feet
    airport: [optional] airport name if this point is associated with an airport
    """
    self.ident = ident
    self.name = name
    self.style = style
    self.latitude = latitude
    self.longitude = longitude
    self.declination = declination
    self.frequency = frequency
    self.elevation_ft = elevation_ft
    self.length_ft = length_ft
    self.bearing = bearing
    self.tch_ft = tch_ft
    self.width_ft = width_ft
    self.dthreshold_ft = dthreshold_ft
    self.airport = airport
        
    return

class Procedure:
  # SID Route Types (PD, HD)
  D_TYPE_ENGINE_OUT_SID = '0'
  D_TYPE_SID_RUNWAY_TRANSITION = '1'
  D_TYPE_SID_COMMON_ROUTE = '2'
  D_TYPE_SID_ENROUTE_TRANSITION = '3'
  D_TYPE_RNAV_SID_RUNWAY_TRANSITION = '4'
  D_TYPE_RNAV_SID_COMMON_ROUTE = '5'
  D_TYPE_RNAV_SID_ENROUTE_TRANSITION = '6'
  D_TYPE_FMS_SID_RUNWAY_TRANSITION = 'F'
  D_TYPE_FMS_SID_COMMON_ROUTE = 'M'
  D_TYPE_FMS_SID_ENROUTE_TRANSITION = 'S'
  D_TYPE_VECTOR_SID_RUNWAY_TRANSITION = 'T'
  D_TYPE_VECTOR_SID_ENROUTE_TRANSITION = 'V'

  D_RUNWAY_TRANSITIONS = D_TYPE_SID_RUNWAY_TRANSITION + \
                         D_TYPE_RNAV_SID_RUNWAY_TRANSITION + \
                         D_TYPE_FMS_SID_RUNWAY_TRANSITION + \
                         D_TYPE_VECTOR_SID_RUNWAY_TRANSITION
  D_COMMON_ROUTES = D_TYPE_SID_COMMON_ROUTE + \
                    D_TYPE_RNAV_SID_COMMON_ROUTE + \
                    D_TYPE_FMS_SID_COMMON_ROUTE
  D_ENROUTE_TRANISTIONS = D_TYPE_SID_ENROUTE_TRANSITION + \
                          D_TYPE_RNAV_SID_ENROUTE_TRANSITION + \
                          D_TYPE_FMS_SID_ENROUTE_TRANSITION + \
                          D_TYPE_VECTOR_SID_ENROUTE_TRANSITION

  # STAR Route Types (PE, HE)
  E_TYPE_STAR_ENROUTE_TRANSITION = '1'
  E_TYPE_STAR_COMMON_ROUTE = '2'
  E_TYPE_STAR_RUNWAY_TRANSITION = '3'
  E_TYPE_RNAV_STAR_ENROUTE_TRANSITION = '4'
  E_TYPE_RNAV_STAR_COMMON_ROUTE = '5'
  E_TYPE_RNAV_STAR_RUNWAY_TRANSITION = '6'
  E_TYPE_PROFILE_DESCENT_ENROUTE_TRANSITION = '7'
  E_TYPE_PROFILE_DESCENT_COMMON_ROUTE = '8'
  E_TYPE_PROFILE_DESCENT_RUNWAY_TRANSITION = '9'
  E_TYPE_FMS_STAR_ENROUTE_TRANSITION = 'F'
  E_TYPE_FMS_STAR_COMMON_ROUTE = 'M'
  E_TYPE_FMS_STAR_ENROUTE_TRANSITION = 'S'

  E_ENROUTE_TRANSITIONS = E_TYPE_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_RNAV_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_PROFILE_DESCENT_ENROUTE_TRANSITION + \
                          E_TYPE_FMS_STAR_ENROUTE_TRANSITION + \
                          E_TYPE_FMS_STAR_ENROUTE_TRANSITION
  E_COMMON_ROUTES = E_TYPE_STAR_COMMON_ROUTE + \
                    E_TYPE_RNAV_STAR_COMMON_ROUTE + \
                    E_TYPE_PROFILE_DESCENT_COMMON_ROUTE + \
                    E_TYPE_FMS_STAR_COMMON_ROUTE
  E_RUNWAY_TRANSITIONS = E_TYPE_STAR_RUNWAY_TRANSITION + \
                         E_TYPE_RNAV_STAR_RUNWAY_TRANSITION + \
                         E_TYPE_PROFILE_DESCENT_RUNWAY_TRANSITION

  # Approach Route Types (PF, HF)
  F_TYPE_APPROACH_TRANSITION = 'A'
  F_TYPE_LOCALIZER_BACKCOURSE_APPROACH = 'B'
  F_TYPE_VORDME_APPROACH = 'D'
  F_TYPE_FMS_APPROACH = 'F'
  F_TYPE_IGS_APPROACH = 'G'
  F_TYPE_RNP_APPROACH = 'H'
  F_TYPE_ILS_APPROACH = 'I'
  F_TYPE_GLS_APPROACH = 'J'
  F_TYPE_LOC_APPROACH = 'L'
  F_TYPE_MLS_APPROACH = 'M'
  F_TYPE_NDB_APPROACH = 'N'
  F_TYPE_GPS_APPROACH = 'P'
  F_TYPE_NDBDME_APPROACH = 'Q'
  F_TYPE_RNAV_APPROACH = 'R'
  F_TYPE_VORTAC_APPROACH = 'S'
  F_TYPE_TACAN_APPROACH = 'T'
  F_TYPE_SDF_APPROACH = 'U'
  F_TYPE_VOR_APPROACH = 'V'
  F_TYPE_MLSA_APPROACH = 'W'
  F_TYPE_LDA_APPROACH = 'X'
  F_TYPE_MLSBC_APPROACH = 'Y'
  F_TYPE_MISSED_APPROACH = 'Z'

  F_APPROACH_TRANSITIONS = F_TYPE_APPROACH_TRANSITION
  F_APPROACHES = F_TYPE_LOCALIZER_BACKCOURSE_APPROACH + \
                 F_TYPE_VORDME_APPROACH + \
                 F_TYPE_FMS_APPROACH + \
                 F_TYPE_IGS_APPROACH + \
                 F_TYPE_RNP_APPROACH + \
                 F_TYPE_ILS_APPROACH + \
                 F_TYPE_GLS_APPROACH + \
                 F_TYPE_LOC_APPROACH + \
                 F_TYPE_MLS_APPROACH + \
                 F_TYPE_NDB_APPROACH + \
                 F_TYPE_GPS_APPROACH + \
                 F_TYPE_NDBDME_APPROACH + \
                 F_TYPE_RNAV_APPROACH + \
                 F_TYPE_VORTAC_APPROACH + \
                 F_TYPE_TACAN_APPROACH + \
                 F_TYPE_SDF_APPROACH + \
                 F_TYPE_VOR_APPROACH + \
                 F_TYPE_MLSA_APPROACH + \
                 F_TYPE_LDA_APPROACH + \
                 F_TYPE_MLSBC_APPROACH + \
                 F_TYPE_MISSED_APPROACH

  def __init__(self):
    # these dictionaries each contain a list of ProcedureRecords in order, the key is the transition name
    # SIDS/STARS
    self.runway_transitions = {}  
    
    self.enroute_transistions = {}
    
    # Approaches
    self.approach_transition = {}
    
    # All Procedures
    self.common_route = {} 
    
    return
  
  def add_procedure_record(self, pr):
    # we need to add this procedure data to the appropriate procedure dictionary
    if pr.subsection_code == "D":
      # SID
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.D_RUNWAY_TRANSITIONS:
        if pr.transition_identifier not in self.runway_transitions:
          self.runway_transitions[pr.transition_identifier] = []
        self.runway_transitions[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.D_COMMON_ROUTES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.D_ENROUTE_TRANISTIONS:
        if pr.transition_identifier not in self.enroute_transistions:
          self.enroute_transistions[pr.transition_identifier] = []
        self.enroute_transistions[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled SID route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))
    
    elif pr.subsection_code == "E":
      # STAR
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.E_RUNWAY_TRANSITIONS:
        if pr.transition_identifier not in self.runway_transitions:
          self.runway_transitions[pr.transition_identifier] = []
        self.runway_transitions[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.E_COMMON_ROUTES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.E_ENROUTE_TRANSITIONS:
        if pr.transition_identifier not in self.enroute_transistions:
          self.enroute_transistions[pr.transition_identifier] = []
        self.enroute_transistions[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled STAR route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))
    
    elif pr.subsection_code == "F":
      # IAP
      # figure out what kind of route type we are dealing with and add this procedure record to the correct dictionary
      if pr.route_type in self.F_APPROACH_TRANSITIONS:
        if pr.transition_identifier not in self.approach_transition:
          self.approach_transition[pr.transition_identifier] = []
        self.approach_transition[pr.transition_identifier].append(pr)
      
      elif pr.route_type in self.F_APPROACHES:
        if pr.transition_identifier not in self.common_route:
          self.common_route[pr.transition_identifier] = []
        self.common_route[pr.transition_identifier].append(pr)
      else:
        print("Procedure.add_procedure_record: Unhandled IAP route type: {} {} {}".format(pr.airport, pr.procedure_identifier, pr.route_type))

    return

class ProcedureRecord:
  def __init__(self, record):
    # save the raw data
    self.record = record
    
    # parse the data
    self.parse_procedure_record()
    return
  
  def parse_procedure_record(self):
    # SUSAP KDENK2DBAYLR64RW08  010         0        VA                     0826        + 05934     18000                        602692004
    # SUSAP KDENK2DBAYLR64RW08  020         0 E      VM                     0826                                                 602702004
    # SUSAP KDENK2DBAYLR64RW16L 010         0        VI                     1725                    18000                        602712004
    # SUSAP KDENK2DBAYLR64RW16L 020BRKEMK2PC0E       CF DEN K2      2509011524400105D   - 10000                                  602722004
    # SUSAP KDENK2DBAYLR64RW16L 030WAKIRK2PC0EE      TF                                 + 11000                                  602732004
    # SUSAP KDENK2DBAYLR64RW16R 010         0        VI                     1725                    18000                        602742004
    # SUSAP KDENK2DBAYLR64RW16R 020BRKEMK2PC0E       CF DEN K2      2509011524900098D   - 10000                                  602752004
    # SUSAP KDENK2DBAYLR64RW16R 030WAKIRK2PC0EE      TF                                 + 11000                                  602762004
    # SUSAP KDENK2DBAYLR64RW17L 010         0        VI                     1725                    18000                        602772004
    # SUSAP KDENK2DBAYLR64RW17L 020GOROCK2PC0E       CF DEN K2      2089004221900046D                                            602782004
    # SUSAP KDENK2DBAYLR64RW17L 030BRKEMK2PC0E       TF                                 - 10000                                  602792004
    # SUSAP KDENK2DBAYLR64RW17L 040WAKIRK2PC0EE      TF                                 + 11000                                  602802004
    # SUSAP KDENK2DBAYLR64RW17R 010         0        VI                     1725                    18000                        602812004
    # SUSAP KDENK2DBAYLR64RW17R 020GOROCK2PC0E       CF DEN K2      2089004221500037D                                            602822004
    # SUSAP KDENK2DBAYLR64RW17R 030BRKEMK2PC0E       TF                                 - 10000                                  602832004
    # SUSAP KDENK2DBAYLR64RW17R 040WAKIRK2PC0EE      TF                                 + 11000                                  602842004
    # SUSAP KDENK2DBAYLR64RW25  010         0        VA                     2625        + 05934     18000                        602852004
    # SUSAP KDENK2DBAYLR64RW25  020BRKEMK2PC0E       DF                                 - 10000                                  602862004
    # SUSAP KDENK2DBAYLR64RW25  030WAKIRK2PC0EE      TF                                 + 11000                                  602872004
    # SUSAP KDENK2DBAYLR64RW34B 010         0        VA                     3525        + 05934     18000                        602882004
    # SUSAP KDENK2DBAYLR64RW34B 020BRKEMK2PC0E   L   DF                                 - 10000                                  602892004
    # SUSAP KDENK2DBAYLR64RW34B 030WAKIRK2PC0EE      TF                                 + 11000                                  602902004
    # SUSAP KDENK2DBAYLR64RW35B 010         0        VA                     3525        + 05934     18000                        602912004
    # SUSAP KDENK2DBAYLR64RW35B 020BRKEMK2PC0E   L   DF                                 - 10000                                  602922004
    # SUSAP KDENK2DBAYLR64RW35B 030WAKIRK2PC0EE      TF                                 + 11000                                  602932004
    # SUSAP KDENK2DBAYLR65      010WAKIRK2PC0E       IF                                 + 11000     18000                        602942004
    # SUSAP KDENK2DBAYLR65      020TUULOK2PC0E       TF                                 + 14000                                  602952004
    # SUSAP KDENK2DBAYLR65      030HLTONK2PC0E       TF                                                                          602962004
    # SUSAP KDENK2DBAYLR65      040MTSUIK2PC0E       TF                                 + 16000                                  602972004
    # SUSAP KDENK2DBAYLR65      050BAYLRK2EA0EE      TF                                 + 17000                                  602982004
    # SUSAP KDENK2DBAYLR66HBU   010BAYLRK2EA0E       IF                                 + 17000     18000                        602992004
    # SUSAP KDENK2DBAYLR66HBU   020BOBBAK2EA0E       TF                                                                          603002004
    # SUSAP KDENK2DBAYLR66HBU   030HBU  K2D 0VE      TF                                 - FL230                                  603012004
    # SUSAP KDENK2DBAYLR66TEHRU 010BAYLRK2EA0E       IF                                 + 17000     18000                        603022004
    # SUSAP KDENK2DBAYLR66TEHRU 020BOBBAK2EA0E       TF                                                                          603032004
    # SUSAP KDENK2DBAYLR66TEHRU 030TEHRUK2EA0EE      TF                                                                          603042004
    #
    # SUSAP KDENK2EFLATI14FOLSM 010FOLSMK2PC0E       IF                                             18000                        611942004
    # SUSAP KDENK2EFLATI14FOLSM 020BBOCOK2PC0E       TF                                                                          611952004
    # SUSAP KDENK2EFLATI14FOLSM 030FLATIK2PC0EE      TF                                 + FL190                                  611962004
    # SUSAP KDENK2EFLATI14MJANE 010MJANEK1PC0E       IF                                             18000                        611972004
    # SUSAP KDENK2EFLATI14MJANE 020MSTSHK1PC0E       TF                                                                          611982004
    # SUSAP KDENK2EFLATI14MJANE 030HIPEEK2PC0E       TF                                 + FL270                                  611992004
    # SUSAP KDENK2EFLATI14MJANE 040FOLSMK2PC0E       TF                                                                          612002004
    # SUSAP KDENK2EFLATI14MJANE 050BBOCOK2PC0E       TF                                                                          612012004
    # SUSAP KDENK2EFLATI14MJANE 060FLATIK2PC0EE      TF                                 + FL190                                  612022004
    # SUSAP KDENK2EFLATI14TOFUU 010TOFUUK1PC0E       IF                                             18000                        612032004
    # SUSAP KDENK2EFLATI14TOFUU 020GNOLAK1PC0E       TF                                                                          612042004
    # SUSAP KDENK2EFLATI14TOFUU 030HIPEEK2PC0E       TF                                 + FL270                                  612052004
    # SUSAP KDENK2EFLATI14TOFUU 040FOLSMK2PC0E       TF                                                                          612062004
    # SUSAP KDENK2EFLATI14TOFUU 050BBOCOK2PC0E       TF                                                                          612072004
    # SUSAP KDENK2EFLATI14TOFUU 060FLATIK2PC0EE      TF                                 + FL190                                  612082004
    # SUSAP KDENK2EFLATI15      010FLATIK2PC0E       IF                                 + FL190     18000                        612092004
    # SUSAP KDENK2EFLATI15      020ELLDOK2PC0EE      TF                                 B FL21016000     250                     612102004
    # SUSAP KDENK2EFLATI16RW07  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612112004
    # SUSAP KDENK2EFLATI16RW07  020TOTTTK2PC0E       TF                                 B 1700015000                             612122004
    # SUSAP KDENK2EFLATI16RW07  030YESSSK2PC0E       TF                                                                          612132004
    # SUSAP KDENK2EFLATI16RW07  040BAACKK2PC0E       TF                                 + 13000                                  612142004
    # SUSAP KDENK2EFLATI16RW07  050BABAAK2PC0E       TF                                 B 1400012000                             612152004
    # SUSAP KDENK2EFLATI16RW07  060HIMOMK2PC0EY      TF                                   11000          210                     612162004
    # SUSAP KDENK2EFLATI16RW07  070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612172004
    # SUSAP KDENK2EFLATI16RW08  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612182004
    # SUSAP KDENK2EFLATI16RW08  020TOTTTK2PC0E       TF                                 B 1700015000                             612192004
    # SUSAP KDENK2EFLATI16RW08  030YESSSK2PC0E       TF                                                                          612202004
    # SUSAP KDENK2EFLATI16RW08  040BAACKK2PC0E       TF                                 + 13000                                  612212004
    # SUSAP KDENK2EFLATI16RW08  050BABAAK2PC0E       TF                                 B 1400012000                             612222004
    # SUSAP KDENK2EFLATI16RW08  060HIMOMK2PC0EY      TF                                   11000          210                     612232004
    # SUSAP KDENK2EFLATI16RW08  070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612242004
    # SUSAP KDENK2EFLATI16RW16B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612252004
    # SUSAP KDENK2EFLATI16RW16B 020BSAFEK2PC0E       TF                                 - 15000                                  612262004
    # SUSAP KDENK2EFLATI16RW16B 030BDUNNK2PC0E       TF                                 B 1500014000     210                     612272004
    # SUSAP KDENK2EFLATI16RW16B 040TSHNRK2PC0EE      TF                                   13000                                  612282004
    # SUSAP KDENK2EFLATI16RW17B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612292004
    # SUSAP KDENK2EFLATI16RW17B 020BSAFEK2PC0E       TF                                 - 15000                                  612302004
    # SUSAP KDENK2EFLATI16RW17B 030BDUNNK2PC0E       TF                                 B 1500014000     210                     612312004
    # SUSAP KDENK2EFLATI16RW17B 040TSHNRK2PC0EE      TF                                   13000                                  612322004
    # SUSAP KDENK2EFLATI16RW25  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612332004
    # SUSAP KDENK2EFLATI16RW25  020TOTTTK2PC0E       TF                                 B 1700015000                             612342004
    # SUSAP KDENK2EFLATI16RW25  030YESSSK2PC0E       TF                                                                          612352004
    # SUSAP KDENK2EFLATI16RW25  040SKEWDK2PC0E       TF                                 B 1500013000                             612362004
    # SUSAP KDENK2EFLATI16RW25  050LEKEEK2PC0E       TF                                 + 12000                                  612372004
    # SUSAP KDENK2EFLATI16RW25  060XCUTVK2PC0E       TF                                                                          612382004
    # SUSAP KDENK2EFLATI16RW25  070CAPTJK2PC0EY      TF                                   11000          210                     612392004
    # SUSAP KDENK2EFLATI16RW25  080CAPTJK2PC0EE      FM DEN K2      019901060825    D                                            612402004
    # SUSAP KDENK2EFLATI16RW26  010ELLDOK2PC0E       IF                                 B FL2101600018000                        612412004
    # SUSAP KDENK2EFLATI16RW26  020TOTTTK2PC0E       TF                                 B 1700015000                             612422004
    # SUSAP KDENK2EFLATI16RW26  030YESSSK2PC0E       TF                                                                          612432004
    # SUSAP KDENK2EFLATI16RW26  040SKEWDK2PC0E       TF                                 B 1500013000                             612442004
    # SUSAP KDENK2EFLATI16RW26  050LEKEEK2PC0E       TF                                 + 12000                                  612452004
    # SUSAP KDENK2EFLATI16RW26  060XCUTVK2PC0E       TF                                                                          612462004
    # SUSAP KDENK2EFLATI16RW26  070CAPTJK2PC0EY      TF                                   11000          210                     612472004
    # SUSAP KDENK2EFLATI16RW26  080CAPTJK2PC0EE      FM DEN K2      019901060825    D                                            612482004
    # SUSAP KDENK2EFLATI16RW34B 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612492004
    # SUSAP KDENK2EFLATI16RW34B 020TOTTTK2PC0E       TF                                 B 1700015000                             612502004
    # SUSAP KDENK2EFLATI16RW34B 030YESSSK2PC0E       TF                                                                          612512004
    # SUSAP KDENK2EFLATI16RW34B 040BAACKK2PC0E       TF                                 + 13000                                  612522004
    # SUSAP KDENK2EFLATI16RW34B 050BABAAK2PC0E       TF                                 B 1400012000                             612532004
    # SUSAP KDENK2EFLATI16RW34B 060HIMOMK2PC0EY      TF                                   11000          210                     612542004
    # SUSAP KDENK2EFLATI16RW34B 070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612552004
    # SUSAP KDENK2EFLATI16RW35L 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612562004
    # SUSAP KDENK2EFLATI16RW35L 020TOTTTK2PC0E       TF                                 B 1700015000                             612572004
    # SUSAP KDENK2EFLATI16RW35L 030YESSSK2PC0E       TF                                                                          612582004
    # SUSAP KDENK2EFLATI16RW35L 040BAACKK2PC0E       TF                                 + 13000                                  612592004
    # SUSAP KDENK2EFLATI16RW35L 050BABAAK2PC0E       TF                                 B 1400012000                             612602004
    # SUSAP KDENK2EFLATI16RW35L 060HIMOMK2PC0EY      TF                                   11000          210                     612612004
    # SUSAP KDENK2EFLATI16RW35L 070HIMOMK2PC0EE      FM DEN K2      250000701732    D                                            612622004
    # SUSAP KDENK2EFLATI16RW35R 010ELLDOK2PC0E       IF                                 B FL2101600018000                        612632004
    # SUSAP KDENK2EFLATI16RW35R 020TOTTTK2PC0E       TF                                 B 1700015000                             612642004
    # SUSAP KDENK2EFLATI16RW35R 030YESSSK2PC0E       TF                                                                          612652004
    # SUSAP KDENK2EFLATI16RW35R 040SKEWDK2PC0E       TF                                 B 1500013000                             612662004
    # SUSAP KDENK2EFLATI16RW35R 050LEKEEK2PC0E       TF                                 + 12000                                  612672004
    # SUSAP KDENK2EFLATI16RW35R 060XCUTVK2PC0E       TF                                                                          612682004
    # SUSAP KDENK2EFLATI16RW35R 070HDGHGK2PC0E       TF                                 B 1400012000                             612692004
    # SUSAP KDENK2EFLATI16RW35R 080FFFATK2PC0E       TF                                                                          612702004
    # SUSAP KDENK2EFLATI16RW35R 090DOGGGK2PC0EY      TF                                   11000          210                     612712004
    # SUSAP KDENK2EFLATI16RW35R 100DOGGGK2PC0EE      FM DEN K2      088500741727    D                                            612722004
    # 
    # SUSAP KDENK2FH16RZ ACLFFF 010CLFFFK2PC0E  B    IF                                   11000     18000210              A-FS   617831410
    # SUSAP KDENK2FH16RZ ACLFFF 020CEPEEK2PC0E    010TF                                 + 10000                           A FS   617841310
    # SUSAP KDENK2FH16RZ ACLFFF 030AAGEEK2PC0E   R010RF       0027503525    08250043    + 08600                 CFFNB K2PCA FS   617851310
    # SUSAP KDENK2FH16RZ ACLFFF 040JABROK2PC0E    010TF                                 + 08300                           A FS   617861310
    # SUSAP KDENK2FH16RZ ACLFFF 050JETSNK2PC0EE  R010RF       0027500825    17250043    + 07000                 CFPQD K2PCA FS   617871310
    # SUSAP KDENK2FH16RZ ASAKIC 010SAKICK2PC0E  B    IF                                             18000                 A FS   617881310
    # SUSAP KDENK2FH16RZ ASAKIC 020JETSNK2PC0EE   010TF                                 + 07000                           A FS   617891310
    # SUSAP KDENK2FH16RZ H      020JETSNK2PC1E  F    IF                                 + 07000     18000       RW16RBK2PGA FS   617901310
    # SUSAP KDENK2FH16RZ H      020JETSNK2PC2W                                                A031A011                      FS   617911310
    # SUSAP KDENK2FH16RZ H      030RW16RK2PG0GY M 031TF                                   05377             -300          A FS   617921212
    # SUSAP KDENK2FH16RZ H      040         0  M     CA                     1725        + 05900                           A FS   617931212
    # SUSAP KDENK2FH16RZ H      050BINBEK2EA0EY      DF                                 + 10000                           A FS   617941212
    # SUSAP KDENK2FH16RZ H      060BINBEK2EA0EE  R   HM                     25750070    + 10000                           A FS   617951212
    #
    # SUSAP KEIKK2FVDM-A ABJC   010BJC  K2D 0V       IF                                             18000                 3  C   752131301
    # SUSAP KEIKK2FVDM-A ABJC   020SHATZK2PC0E       TF                                 + 08200                           3  C   752141310
    # SUSAP KEIKK2FVDM-A ABJC   030SHATZK2PC0EE AR   HF                     2030T010    + 07200                           3  C   752151310
    # SUSAP KEIKK2FVDM-A D      020SHATZK2PC0E  F    IF BJC K2      02300135        D   + 07200     18000       BJC   K2D 3  C   752161310
    # SUSAP KEIKK2FVDM-A D      021SD203K2PC0E A     CF BJC K2      0231009520300040D   + 06560              000          3  C   752171301
    # SUSAP KEIKK2FVDM-A D      030MAGIHK2PC0EY M    CF BJC K2      0230007520300020D     05880              000          3  C   752181310
    # SUSAP KEIKK2FVDM-A D      040         0  M     CA                     2030        + 05519                           3  C   752191406
    # SUSAP KEIKK2FVDM-A D      050SHATZK2PC0EY  R   CFYBJC K2      0230013502300070D   + 07200                           3  C   752201310
    # SUSAP KEIKK2FVDM-A D      060SHATZK2PC0EE  R   HM                     2030T010    + 07200                           3  C   752211310
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    self.airport = self.record[6:10].rstrip() # KDEN
    self.subsection_code = self.record[12] # D
    self.procedure_identifier = self.record[13:19].rstrip() # BAYLR6
    self.route_type = self.record[19] # 6
    self.transition_identifier = self.record[20:25]
    self.sequence_number = int(self.record[26:29])
    self.fix_identifier = self.record[29:34].rstrip()
    self.fix_section = self.record[36:38]
    self.continuation_count = int(self.record[38])
    self.waypoint_description = self.record[39:43]
    self.turn_direction = self.record[43]
    self.path_and_termination = self.record[47:49]
    self.recommended_nav = self.record[50:54].rstrip()
    self.arc_radius = CIFPReader.parse_float(self.record[56:62],1000.0)
    self.theta = CIFPReader.parse_float(self.record[62:66], 10.0) # bearing
    self.rho = CIFPReader.parse_float(self.record[66:70], 10.0) # distance
    self.magnetic_course = CIFPReader.parse_float(self.record[70:74], 10.0) # course
    if self.record[74] == 'T':
      # time distance
      self.time = CIFPReader.parse_float(self.record[75:78], 10.0)
      self.distance = None 
    else:
      # nautical mile distance
      self.time = None 
      self.distance = CIFPReader.parse_float(self.record[74:78], 10.0)
    self.nav_section = self.record[79:81]
    self.altitude_type = self.record[82]
    self.altitude1 = self.record[84:89]
    self.altitude2 = self.record[89:94]
    self.speed_limit = self.record[99:102]
    self.center_fix = self.record[106:111]
    self.center_section = self.record[114:116]
    
    return

class CIFPReader:
  SECTIONS = namedtuple('SECTIONS', 'area_code, section_code, subsection_code')
  
  """
  UC_DATA = namedtuple('UC_DATA', 'airspace_type, airspace_center, airspace_classification,'\
                       ' multiple_code, sequence_number,'\
                       ' continuation_record_number, boundary_via, latitude, longitude,'\
                       ' arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing, name')
  
  UR_DATA = namedtuple('UR_DATA', 'airspace_type, designation, multiple_code, sequence_number,'\
                       ' boundary_via, latitude, longitude, arc_origin_latitude, arc_origin_longitude,'\
                       ' arc_distance, arc_bearing, name')
  """
  
  def __init__(self, path, cifp_version,  lat_min, lat_max, lon_min, lon_max, output=False):
    # save the filename
    self.filename = path+'\\'+cifp_version+'\\FAACIFP18'
    
    # save our boundaries
    self.lat_min = lat_min
    self.lat_max = lat_max
    self.lon_min = lon_min
    self.lon_max = lon_max
    
    # initializations
    self.continuation_count = 0
    self.controlling_agency = ""
    
    # create the data dictionaries
    self.vors = {}  # dictionary of Point instances
    self.ndbs = {}  # dictionary of Point instances
    self.enroute_waypoints = {} # dictionary of Point instances
    
    self.airports = {} # dictionary of Airport instances
    
    self.enroute_airways = {}
    self.restricted_airspace = {}
    
    # create our output tools if requested
    self.output = output
    if self.output:
      self.location_out = WaypointsOut(path+'\\'+cifp_version+'\\Processed', cifp_version)
      #self.airspace_out = ShapesOut(path+'\\'+cifp_version+'\\Processed', cifp_version+"_Airspace", "Airspace")
      #self.restricted_out = ShapesOut(path+'\\'+cifp_version+'\\Processed', cifp_version+"_URAirspace", "Restricted")
      #self.runways_out = ShapesOut(path+'\\'+cifp_version+'\\Processed', cifp_version+"_Runways", "Runways")
    
    self.process_file()
    
    self.debug()
    
    # save the files if requested
    if self.output:
      self.location_out.save_files()
      #self.airspace_out.save_files()
      #self.restricted_airspace.save_files()
      #self.runways_out.save_files()
      
    return
  
  def debug(self):
    # debug test
    #                          Airport       Procedure    
    for route in self.airports['KDEN'].sids['BAYLR6'].runway_transitions.values():
      for pr in route:
        print("RW {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.airports['KDEN'].sids['BAYLR6'].common_route.values():
      for pr in route:
        print("CR {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.airports['KDEN'].sids['BAYLR6'].enroute_transistions.values():
      for pr in route:
        print("ET {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    
    print("==================================")
    
    #                          Airport       Procedure      
    for route in self.airports['KDEN'].stars['FLATI1'].enroute_transistions.values():
      for pr in route:
        print("ET {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.airports['KDEN'].stars['FLATI1'].common_route.values():
      for pr in route:
        print("CR {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.airports['KDEN'].stars['FLATI1'].runway_transitions.values():
      for pr in route:
        print("RW {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    
    print("==================================")
    
    #                          Airport           Procedure      
    for route in self.airports['KDEN'].approaches['H16RZ'].approach_transition.values():
      for pr in route:
        print("AT {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    for route in self.airports['KDEN'].approaches['H16RZ'].common_route.values():
      for pr in route:
        print("IP {} {} {} {}".format(pr.airport,
                                      pr.procedure_identifier,
                                      pr.transition_identifier,
                                      pr.fix_identifier))
    
    return
  
  def process_file(self):
    
    with open(self.filename, "r") as f:
      # now process each line in the file
      for line in f:
        # identify the type of line
        info = self.get_record_info(line)
        code = info.section_code + info.subsection_code
        
        # parse the line
        if code == "XX":  # Header
          continue
        elif code == "AS":  # Grid Minimum Off Route Altitude (MORA)
          continue
        elif code == "D ":  # VHF Navaid
          # 4.1.2
          data = self.parse_vhf_navaid(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            self.vors[data.ident] = data
          
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
        
        elif code == "DB":  # NDB
          # 4.1.3
          data = self.parse_ndb(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            self.ndbs[data.ident] = data
          
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
        
        elif code == "EA":  # Waypoint
          # 4.1.4
          data = self.parse_waypoint(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            self.enroute_waypoints[data.ident] = data
          
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
        
        elif code == "ER":  # Enroute Airway
          continue
        elif code == "HA":  # Heliport
          continue
        elif code == "HC":  # Helicopter Terminal Waypoint
          continue
        elif code == "HF":  # Heliport SID/STAR/Approach
          continue
        elif code == "HS":  # Heliport Minimum Sector Altitude
          continue
        elif code == "PA":  # Airport Reference Point
          # 4.1.7
          data = self.parse_airport_primary_record(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            # save this data
            if data.airport not in self.airports:
              # create the airport if it doesn't already exist
              self.airports[data.airport] = Airport()
            self.airports[data.airport].add_reference_point(data)
            
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
                
        elif code == "PC":  # Terminal Waypoint
          # 4.1.4
          data = self.parse_waypoint(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            # save this to our airport
            if data.airport not in self.airports:
              # create the airport if it doesn't already exist
              self.airports[data.airport] = Airport()
            self.airports[data.airport].add_waypoint(data)
          
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
        
        elif code == "PD":  # Standard Instrument Departure (SID)
          data = self.parse_procedure(line)
          
          # if this airport exists in our database, then we want to keep processing
          if data != None and data.airport in self.airports:
            # add this procedure item to the airport
            self.airports[data.airport].add_procedure(data)
        
        elif code == "PE":  # Standard Terminal Arrival (STAR)
          data = self.parse_procedure(line)
          
          # if this airport exists in our database, then we want to keep processing
          if data != None and data.airport in self.airports:
            # add this procedure item to the airport
            self.airports[data.airport].add_procedure(data)
        
        elif code == "PF":  # Instrument Approach
          data = self.parse_procedure(line)
          
          # if this airport exists in our database, then we want to keep processing
          if data != None and data.airport in self.airports:
            # add this procedure item to the airport
            self.airports[data.airport].add_procedure(data)
        
        elif code == "PG":  # Runway
          # 4.1.10
          data = self.parse_runway(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            # save this to our airport
            if data.airport not in self.airports:
              # create the airport if it doesn't already exist
              self.airports[data.airport] = Airport()
            self.airports[data.airport].add_runway(data)
            
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
         
        elif code == "PI":  # Localizer/Glideslope
          continue
        elif code == "PN":  # Terminal NDB
          # 4.1.3
          data = self.parse_ndb(line) # returns a Point
          
          # if we have a point we want, save it
          if data != None and self.in_roi(data.latitude, data.longitude):
            # save this to our airport
            if data.airport not in self.airports:
              # create the airport if it doesn't already exist
              self.airports[data.airport] = Airport()
            self.airports[data.airport].add_ndb(data)
          
            # save this point in our output
            if self.output:
              self.location_out.add_point(data)
        
        elif code == "PP":  # Path Point
          continue
        elif code == "PS":  # Minimum Sector Altitude
          continue
        elif code == "UC":  # Controlled Airspace
          continue
        elif code == "UR":  # Restricted Airspace
          continue
        else:
          print("CIFPReader.process_file: Unprocessed Record: {} {}".format(code, line))
      
    return
    
  def in_roi(self, lat, lon):
    if lat == None or lon == None:
      return False
    
    if self.lat_min <= lat and lat <= self.lat_max and self.lon_min <= lon and lon <= self.lon_max:
      return True 
    return False
  
  def get_record_info(self, record):
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
    
    # Record
    # ID  SS SS  Same        Type
    
    # AS  6                  Grid Minimum Off Route Altitude (MORA)
    # AS: S   AS       N04E150          UNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNKUNK   000011703
    
    # D   6                  VHF Navaid
    # D : SCAND        ADK   PA011400 DUW                    ADK N51521587W176402739E0070003291     NARMOUNT MOFFETT                 002361703
    # DB  6      (PN)        NDB Navaid
    # DB: SCANDB       ACE   PA002770H  W N59382880W151300099                       E0170           NARKACHEMAK                      003632002
    
    # EA  6  13  (PC)        Waypoint
    # EA: SCANEAENRT   AAMYY PA0    R   H N51301880E171091170                       W0010     NAR           AAMYY                    004572002
    # ER  6                  Enroute Airways
    # ER: SCANER       A1          0150BBGVPPAEA0E    O                         312104802987 05200                                   024982002
    
    # HA  13*                Heliport
    # HA: SCANH 01AKPAA   H1   0     NARN N60062086W149264652E023000120         1800018000P    040040M PROVIDENCE SEWARD MEDICAL CENT041361703
    # HC  13*                Helicopter Terminal Waypoint
    # HC: SUSAH 87N K6CCRANN K60    W     N40514240W072275511                       W0136     NAR           CRANN                    721662002
    # HF  13*    (HD, HE)    Heliport SIDS/STARS/Approach
    # HF: SUSAH 87N K6FR190  ACCC   010CCC  K6D 0V       IF                                             18000                 B JH   721691505
    # HS  13*                Heliport Minimum Sector Altitude (MSA)
    # HS: SUSAH 87N K6SCRANNK6HC                0   18018001925                                                                  M   721811505
    
    # PA  13*                Airport
    # PA: SCANP 00AKPAA        0     025NSN59565600W151413200E014800252         1800018000P    MNAR    LOWELL FIELD                  041982002
    # PC  6  13  (EA)        Waypoint ********************Careful
    # PC: SCANP PAAKPACBILNE PA0    W     N52155864W174310737                       E0053     NAR           BILNE                    049292002
    # PD  13*     (PE, PF)   Airport SIDS/STARS/Approach
    # PD: SCANP CYQGCYDBARII25ALL   010HUUTZK5EA0E       IF                                 + 04000     18000                        046811909
    # PE  13*     (PD, PF)   Airport SIDS/STARS/Approach
    # PE: SCANP CYQGCYEFOREY24BOBCT 010BOBCTK5EA0E       IF                                             18000                        047721911
    # PF  13*     (PD, PE)   Airport SIDS/STARS/Approach
    # PF: SCANP PAAKPAFRNV-A AHIMKI 010HIMKIPAEA0E       IF                                             18000                 B PC   049391913
    # PG  13*                Runway
    # PG: SCANP 01A PAGRW05    0011760463 N62562477W152162256               02034000050050D                                          042001703
    # PI  13*                Airport & Heliport Localizer and Glideslope
    # PI: SCANP PABEPAIIBET1   011150RW19RN60460657W1615047081925N60470649W1614945101306 08980510300E01105200106                     052091707
    # PN  6*     (DB)        NDB Navaid
    # PN: SLAMPNTISXTI ST    TI002410HO W N17413092W064530474                       W0130           NARPESTE                         176801605
    # PP  13*                Path Point
    # PP: SCANP PAAQPAPR10   RW10 001 0000W10A0N6135419550W14906023005+008180300N6135067710W14903110925106751648000400F400000FDCE99BD050001812
    # PS  13*                Airport Minimum Sector Altitude (MSA)
    # PS: SCANP PAAKPASMACSUPAPC                0   18018006325                                                                  M   049541310
    
    # UC  6                  Controlled Airspace
    # UC: SCANUCPAAPANC PAC  A00100     G N61103600W149585900                              GND  A04100MANCHORAGE                     134421703
    # UR  6                  Restrictive Airpsace
    # UR: SCANURPAMBIRCH     A00101L    G N64311700W146093100                              00500A04999MBIRCH MOA                     136841703
    
    # Others in File
    # XX: HDR01FAACIFP18      001P013203790892006  30-APR-202012:09:31  U.S.A. DOT FAA                                                37D006AB
    
    # Not in file
    # EM  6                  Airway Markers
    # EP  6                  Holding Pattern
    # ET  6                  Preferred Routes
    # EU  6                  Enroute Airways Restriction Records
    # EV  6                  Enroute Comm
    # HD  13*    (HE, HF)    Heliport SIDS/STARS/Approach
    # HE  13*    (HD, HF)    Heliport SIDS/STARS/Approach
    # HK  13*                Heliport TAA
    # HV  13*                Heliport Comm
    # PB  13*                Airport Gate
    # PK  13*                Airport TAA
    # PL  13*                Airport & Heliport MLS
    # PM  13*                Airport & Heliport Localizer Marker/Locators
    # PR  13*                Flight Planning Arrival/Departure
    # PT  13*                GLS
    # PV  13*                Airport Comm
    # TC  6                  Cruising Tables
    # UF  6                  FIR/UIR
    # R   6                  Company Route
    # RA  6                  Alternate Record
    # TG  6                  Geographical Reference Table
    if record_type == 'S':
      if section_code == "H":
        subsection_code = record[12]
      elif section_code == "P":
        if record[5] == " ":
          subsection_code = record[12]
        else:
          subsection_code = record[5]
      else:
        subsection_code = record[5]
    elif record_type == 'H':
      area_code = 'HDR'
      section_code = "X"
      subsection_code = "X"

    return CIFPReader.SECTIONS(area_code, section_code, subsection_code)
  
  @staticmethod
  def parse_controlled_airspace(record):
    """parse a controlled airport record (UR)
    
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
  
  def parse_restricted_airspace(self, record):
    """parse a controlled airport record (UR)
    
    Types: A: Alert
           C: Caution
           D: Danger
           M: Military Operations Area (MOA)
           P: Prohibited
           R: Restricted
           T: Training
           W: Warning
           U: Unspecified
    
    Boundary Via: A: Arc by edge
                  C: Full circle
                  G: Great circle
                  H: Rhumb line
                  L: CCW Arc
                  R: CW Arc"""
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
    if self.ur_continuation_count > 0:
      # process the continuation record
      if record[25] == "C": # controlling agency record
        self.controlling_agency = record[99:123].rstrip()
      else:
        print("Unhandled UR Continuation record: {}".format(record))
      # reduce the count
      self.ur_continuation_count -= 1
      # return nothing
      return None
      
    airspace_type = record[8]
    designation = record[9:19].rstrip()
    multiple_code = record[19]
    sequence_number = int(record[20:24])
    boundary_via = record[30:32]
    latitude = CIFPReader.parse_lat(record[32:41])
    longitude = CIFPReader.parse_lon(record[41:51])
    arc_origin_latitude = CIFPReader.parse_lat(record[51:60])
    arc_origin_longitude = CIFPReader.parse_lon(record[60:70])
    arc_distance = CIFPReader.parse_float(record[70:74], 10.0)
    arc_bearing = CIFPReader.parse_float(record[74:78], 10.0)
    name = record[93:123].rstrip()
    
    continuation_record_number = CIFPReader.parse_int(record[24])
    self.ur_continuation_count = continuation_record_number
    
    return CIFPReader.UR_DATA(airspace_type, designation, multiple_code, sequence_number, boundary_via, latitude, longitude, 
                              arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing, name)

  def get_controlling_agency(self):
    return self.controlling_agency
  def reset_controlling_agency(self):
    self.controlling_agency = ""
    return
  
  def parse_vhf_navaid(self, record):
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
    # make sure this isn't a continuation record
    if record[21] == "0": # continuation record number (count)
      # first record only
      if record[27] == "V": # 5.35 (p.88)
        # VORs only
        t2 = record[28]
        if t2 == " ":
          style = Point.POINT_VOR
        elif t2 == "D":
          style = Point.POINT_VORDME
        elif t2 == "T" or t2 == "M":
          style = Point.POINT_VORTAC
        else:
          print("CIFPReader.parse_vhf_navaid: Unexpected VOR type: {}".format(record))
          style = None
        
        # now parse the rest of the record
        vor_ident = record[13:17].rstrip()
        frequency = CIFPReader.parse_float(record[22:27], 100)
        latitude = CIFPReader.parse_lat(record[32:41])
        longitude = CIFPReader.parse_lon(record[41:51])
        declination = CIFPReader.parse_variation(record[74:79])
        name = record[93:123].rstrip()
      else:
        return None
    else:
      print("CIFPReader.parse_vhf_navaid: VHF Continuation Record not handled: {}".format(record))
      return None
    
    return Point(ident=vor_ident,
                 name=name,
                 style=style,
                 latitude=latitude,
                 longitude=longitude,
                 declination=declination,
                 frequency=frequency)
  
  def parse_ndb(self, record):
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
    # make sure this isn't a continuation record
    if record[21] == "0":
      # first record only
      
      # identify the style
      if record[4:6] == "DB":
        style = Point.POINT_NDB
      elif record[4:6] == "PN":
        style = Point.POINT_TERMINAL_NDB
      else:
        print("CIFPReader.parse_ndb: Unexpected NDB type: {}".format(record))
        style = None
      
      # parse the record
      airport = record[6:10].rstrip()
      ident = record[13:17].rstrip()
      frequency = CIFPReader.parse_float(record[22:27], 10)
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      declination = CIFPReader.parse_variation(record[74:79])
      name = record[93:123].rstrip()
    else:
      print("CIFPReader.parse_ndb: NDB Continuation Record not handled:")
      print(record)
      return None
    
    return Point(ident=ident,
                 name=name,
                 style=style,
                 latitude=latitude,
                 longitude=longitude,
                 declination=declination,
                 frequency=frequency,
                 airport=airport)
  
  def parse_waypoint(self, record):
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
    # make sure this isn't a continuation record
    if record[21] == "0":
      # first record only
      
      # identify the style
      if record[4:6] == "EA":
        style = Point.POINT_ENROUTE_WAYPOINT
      elif record[4] == "P" and record[12] == "C":
        style = Point.POINT_TERMINAL_WAYPOINT
      else:
        print("CIFPReader.parse_waypoint: Unexpected Waypoint type: {}".format(record))
        style = None
      
      # parse the record
      airport = record[6:10].rstrip()
      ident = record[13:18].rstrip()
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      declination = CIFPReader.parse_variation(record[74:79])
      name = record[98:123].rstrip()
    else:
      print("CIFPReader.parse_waypoint: Waypoint Continuation Record not handled:")
      print(record)
      return None
    
    return Point(ident=ident,
                 name=name,
                 style=style,
                 latitude=latitude,
                 longitude=longitude,
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
    if record[21] == "0":
      # first record only
      airport = record[6:10].rstrip()
      latitude = CIFPReader.parse_lat(record[32:41])
      longitude = CIFPReader.parse_lon(record[41:51])
      declination = CIFPReader.parse_variation(record[51:56])
      elevation_ft = float(record[56:61])
      name = record[93:123].rstrip()
    else:
      print("CIFPReader.parse_airport_primary_record: Continuation Record not handled:")
      print(record)
      return None
    
    return Point(ident=airport, 
                 name=name, 
                 style=Point.POINT_AIRPORT, 
                 latitude=latitude, 
                 longitude=longitude, 
                 declination=declination, 
                 elevation_ft=elevation_ft, 
                 airport=airport)
  
  def parse_runway(self, record):
    """Parse a section 4.1.10 (p.25) Runway Record"""
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
      print("CIFPReader.parse_runway: Continuation Record not handled: {}".format(record))
      return None
    
    return Point(ident=airport, 
                 name=runway, 
                 style=Point.POINT_RUNWAY, 
                 latitude=latitude, 
                 longitude=longitude, 
                 elevation_ft=elevation, 
                 length_ft=length,
                  bearing=bearing, 
                  tch_ft=tch, 
                  width_ft=width, 
                  dthreshold_ft=dthreshold, 
                  airport=airport)
  
  def parse_procedure(self, record):
    """parse PD, PE, PF, HD, HE, and HF records"""
    if self.continuation_count == 0:
      # process first records
      procudure_record = ProcedureRecord(record)
      self.continuation_count = procudure_record.continuation_count
    else:
      # process continuation records
      #print("Procedure.parse_procedure: Continuation Record Not Parsed: {}".format(record.rstrip()))
      self.continuation_count -= 1
      return None

    return procudure_record
    
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
    if point.style == Point.POINT_VOR:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_VORDME:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VOR/DME\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_VORTAC:
      kml_doc = self.vors
      description += "Name:{}\n".format(point.name)
      description += "Type: VORTAC\n"
      description += "Frequency:{:.2f} MHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_NDB:
      kml_doc = self.ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_ENROUTE_WAYPOINT:
      kml_doc = self.enroute_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_TERMINAL_WAYPOINT:
      kml_doc = self.terminal_waypoints
      description += "Name:{}\n".format(point.name)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_TERMINAL_NDB:
      kml_doc = self.terminal_ndbs
      description += "Name:{}\n".format(point.name)
      description += "Frequency:{:.0f} kHz\n".format(point.frequency)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_AIRPORT:
      kml_doc = self.airports
      description += "Name:{}\n".format(point.name)
      description += "Elevation:{} feet\n".format(point.elevation_ft)
      description += "Declination:{:.1f} degrees\n".format(point.declination)
    elif point.style == Point.POINT_RUNWAY:
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
  
  cifp = CIFPReader(r"C:\Data\CIFP", "CIFP_200521", lat_min, lat_max, lon_min, lon_max, output=False)
  
  """
  runway_processor = RunwayProcessor(runways_out)
  

  first_uc = True
  first_ur = True
  
  with open(r"C:\Data\CIFP\CIFP_200521\FAACIFP18", "r") as f:
    seen = {}
    for line in f:
      info = CIFPReader.get_record_info(line)
            
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
        if cifp.in_roi(data.arc_origin_latitude, data.arc_origin_longitude) or cifp.in_roi(data.latitude, data.longitude) or first_uc == False:
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
                  arc = maptools.arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise, uc_current[i].airspace_center)
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
      
      # UR Restrictive Airspace 3.2.6.1
      # airspace_type, designation, multiple_code, sequence_number, boundary_via, latitude, longitude, 
      # arc_origin_latitude, arc_origin_longitude, arc_distance, arc_bearing, name
                              
      if info.section_code == "U" and info.subsection_code == "R":
        data = cifp.parse_restricted_airspace(line)
        if data != None:
          if cifp.in_roi(data.arc_origin_latitude, data.arc_origin_longitude) or cifp.in_roi(data.latitude, data.longitude) or first_ur == False:
            if first_ur:
              # clear the agency name because we don't have it yet
              cifp.reset_controlling_agency()
              
              if data.boundary_via == "CE":
                # this is a complete shape for this airport, save and reset
                shape = maptools.circle((data.arc_origin_latitude, data.arc_origin_longitude), data.arc_distance)
                restricted_out.add_shape(data.designation, 
                                         "Type {} Sequence {}".format(data.airspace_type, data.multiple_code), 
                                         "", 
                                         shape, 
                                         simplekml.Color.magenta, 
                                         ShapesOut.OUTCOLOR_ORANGE)
              else:
                # save this point and continue
                ur_current = [data]
                first_ur = False
            else:
              # add the point to our list
              ur_current.append(data)
              
              # is this the last point in the shape?
              last = data.boundary_via[1] == "E"
              if last:
                # process this shape, begin with the first point
                shape = [(ur_current[0].latitude, ur_current[0].longitude)]
                for i in range(len(ur_current)):
                  if ur_current[i].boundary_via[0] == "A":
                    # arc by edge
                    print("Arc by edge not yet supported")
                  elif ur_current[i].boundary_via[0] == "C":
                    # circle
                    print("Circle should have been supported above: {}".format(ur_current[i]))
                    
                  elif ur_current[i].boundary_via[0] == "G":
                    # great circle
                    # simply add the next point
                    if ur_current[i].boundary_via[1] == 'E':
                      shape.append((ur_current[0].latitude, ur_current[0].longitude))
                    else:
                      shape.append((ur_current[i+1].latitude, ur_current[i+1].longitude))
                  elif ur_current[i].boundary_via[0] == "H":
                    # rhumb line
                    # treat this like a great circle and warn
                    #print("Caution: Treating Rhumb Line path as a Great Circle: {}".format(ur_current[i].designation))
                    # simply add the next point
                    if ur_current[i].boundary_via[1] == 'E':
                      shape.append((ur_current[0].latitude, ur_current[0].longitude))
                    else:
                      shape.append((ur_current[i+1].latitude, ur_current[i+1].longitude))
                  elif ur_current[i].boundary_via[0] == "L" or ur_current[i].boundary_via[0] == "R":
                    # CCW arc
                    arc_begin = (ur_current[i].latitude, ur_current[i].longitude)
                    
                    if ur_current[i].boundary_via[1] == 'E':
                      arc_end = (ur_current[0].latitude, ur_current[0].longitude)
                    else:
                      arc_end = (ur_current[i+1].latitude, ur_current[i+1].longitude)
                      
                    arc_center = (ur_current[i].arc_origin_latitude, ur_current[i].arc_origin_longitude)
                    
                    radius_nm = ur_current[i].arc_distance
                    
                    if ur_current[i].boundary_via[0] == "R":
                      clockwise = True
                    else:
                      clockwise = False
                    arc = maptools.arc_path(arc_begin, arc_end, arc_center, radius_nm, clockwise,
                                            "{} {}".format(ur_current[i].designation, ur_current[i].sequence_number))
                    for p in arc:
                      shape.append(p)
                  else:
                    print("UR Unrecognized boundary via")
                    print(data)
                
                # add the data to the files
                restricted_out.add_shape(data.designation, 
                                         "Type {} Sequence {}".format(data.airspace_type, data.multiple_code), 
                                         "{}".format(cifp.get_controlling_agency()), 
                                         shape, 
                                         simplekml.Color.magenta, 
                                         ShapesOut.OUTCOLOR_ORANGE)
                
                # reset
                first_ur = True

  # process the runways
  runway_processor.process_runway(runways, airports)
   

  
  """
  print("Done.")
  
      
    
  
