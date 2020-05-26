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
    self.arc_radius = cf.parse_float(self.record[56:62],1000.0)
    self.theta = cf.parse_float(self.record[62:66], 10.0) # bearing
    self.rho = cf.parse_float(self.record[66:70], 10.0) # distance
    self.magnetic_course = cf.parse_float(self.record[70:74], 10.0) # course
    if self.record[74] == 'T':
      # time distance
      self.time = cf.parse_float(self.record[75:78], 10.0)
      self.distance = None 
    else:
      # nautical mile distance
      self.time = None 
      self.distance = cf.parse_float(self.record[74:78], 10.0)
    self.nav_section = self.record[79:81]
    self.altitude_type = self.record[82]
    self.altitude1 = self.record[84:89]
    self.altitude2 = self.record[89:94]
    self.speed_limit = self.record[99:102]
    self.center_fix = self.record[106:111]
    self.center_section = self.record[114:116]
    
    return


