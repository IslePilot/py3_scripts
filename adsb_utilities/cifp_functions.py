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
from collections import namedtuple

SECTIONS = namedtuple('SECTIONS', 'area_code, section_code, subsection_code')

# basic CIFP Processing functions
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
  
  # Not in CIFP_200521 file
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

  return SECTIONS(area_code, section_code, subsection_code)
  
def section(record):
  info = get_record_info(record)
  return info.section_code + info.subsection_code

def parse_float(fstr, divisor=1.0):
  # if fstr is empty we are done
  if fstr.strip() == "":
    return None
  return float(fstr)/divisor

def parse_int(istr):
  # if istr is empty we are done
  if istr.strip() == "":
    return None
  return int(istr)

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

def parse_variation(var):
  # 5.39
  # E0080
  # 01234
  hem = var[0]
  variation = float(var[1:])/10.0
  if hem == "E":
    variation = -variation
  return variation

