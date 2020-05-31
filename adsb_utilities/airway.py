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
sys.path.append("..")


class Airway:
  def __init__(self):
    # An airway is simply an ordered set of fixes defining a path
    self.fixes = [] # list of fix ids
    self.airway = [] # list of AirwayFixes
  
  def add_fix(self, airway_fix):
    self.airway.append(airway_fix)
    self.fixes.append(airway_fix.fix_id)
    return 
  
  def get_fixes(self, initial_fix, final_fix, d, db, ea, include_end_points=True):
    """get a list of fixes along the airway from the initial_fix to the final_fix
    
    initial_fix: [optional, default first] fix identifier for the initial fix
    final_fix: [optional, default last] fix identifier for the final fix
    include_end_points: [optional, default True] include the initial and final fixes in the list
    d: VHF Navaid PointSet
    db: NDB PointSet
    ea: Enroute Waypoints Point Set
    returns: list of (fix, (latitude, longitude), description"""
    # find the indices for the initial and final fixes
    if initial_fix != None:
      initial_index = self.fixes.index(initial_fix)
    else:
      initial_index = 0
      
    if final_fix != None:
      final_index = self.fixes.index(final_fix)
    else:
      final_index = len(self.fixes)-1
    
    # get the start and end indices
    start = min(initial_index, final_index)
    end = max (initial_index, final_index)
    
    # get our list
    if include_end_points:
      airway_list = self.airway[start:end+1]
    else:
      airway_list = self.airway[start+1:end]
    
    # reverse our list if the order is opposite to the list order
    if final_index < initial_index:
      airway_list.reverse()
    
    # now cross reference the fix to the database and get position and description
    fix_list = []
    for af in airway_list:
      ident = af.fix_id
      
      # get the fix info
      if af.fix_section == "D ":
        info = d.get_point(ident)
      elif af.fix_section == "DB":
        info = db.get_point(ident)
      elif af.fix_section == "EA":
        info = ea.get_point(ident)
      
      fix_list.append((ident, info[0], info[1]))
      
    return fix_list
    
class AirwayFix:
  def __init__(self, record):
    # save the raw data
    self.record = record
    
    # parse the data
    self.parse_airway_record(record)
    return
  
  def parse_airway_record(self, record):
    # SUSAER       J60         0100LAX  K2D 0V    OH                        07590450     18000     45000                         534541709
    # SUSAER       J60         0110PDZ  K2D 0V    OH                        029900990759 18000     45000                         534551709
    # SUSAER       J60         0120CIVETK2EA0E    OH                        033303010332 18000     45000                         534562002
    # SUSAER       J60         0130RESORK2EA0E    OH                        033603470334 18000     45000                         534572002
    # SUSAER       J60         0140HEC  K2D 0V    OH                        032110640302 18000     45000                         534581709
    # SUSAER       J60         0150BLD  K2D 0V    OH                        034815970321 18000     45000                         534591709
    # SUSAER       J60         0160BCE  K2D 0V    OH                        044708760348 18000     45000                         534601709
    # SUSAER       J60         0170HVE  K2D 0V    OH                        054818840447 18000     45000                         534611709
    # SUSAER       J60         0180DBL  K2D 0V    OH                        062710870578 18000     45000                         534621709
    # SUSAER       J60         0190DVV  K2D 0V    OH                        069717350667 18000     45000                         534631709
    # SUSAER       J60         0200HCT  K3D 0V    OH                        069211790667 18000     45000                         534641709
    # SUSAER       J60         0210DRABSK3EA0E    OH                        077807500761 18000     45000                         534652002
    # SUSAER       J60         0220LNK  K3D 0V    OH                        070619500729 18000     45000                         534661709
    # SUSAER       J60         0230CNOTAK3EA0E    OH                        082603990798 18000     45000                         534672002
    # SUSAER       J60         0240IOW  K3D 0V    OH                        083310260774 18000     45000                         534681709
    # SUSAER       J60         0250VORINK5EA0E    OH                        092504590910 18000     45000                         534692002
    # SUSAER       J60         0260JOT  K5D 0V    OH                        087905000878 18000     45000                         534701709
    # SUSAER       J60         0270HOBARK5EA0E    OH                        095005320942 18000     45000                         534711901
    # SUSAER       J60         0280GSH  K5D 0V    OH                        092006230907 18000     45000                         534721709
    # SUSAER       J60         0290ASHENK5EA0E    OH                        099202230983 18000     45000                         534732002
    # SUSAER       J60         0300NAPOLK5EA0E    OH                        099902210996 18000     45000                         534742002
    # SUSAER       J60         0310MAYZEK5EA0E    OH                        100604801002 18000     45000                         534751901
    # SUSAER       J60         0320JERRIK5EA0E    OH                        102102001014 18000     45000                         534762002
    # SUSAER       J60         0330DJB  K5D 0V    OH                        101602660993 18000     45000                         534771709
    # SUSAER       J60         0340CANCRK5EA0E    OH                        105505301051 18000     45000                         534782002
    # SUSAER       J60         0350HAGUDK6EA0E    OH                        107001191062 18000     45000                         534791709
    # SUSAER       J60         0360TYSUNK6EA0E    OH                        107307931072 18000     45000                         534801710
    # SUSAER       J60         0370MIDSTK6EA0E    OH                        109602001084 18000     45000                         534811710
    # SUSAER       J60         0380PSB  K6D 0V    OH                        110101401091 18000     45000                         534821709
    # SUSAER       J60         0390DOOTHK6EA0E    OH                        111101181110 18000     45000                         534831709
    # SUSAER       J60         0400FORTTK6EA0E    OH                        111405551112 18000     45000                         534841709
    # SUSAER       J60         0410DANNRK6EA0E    OH                        083904021121 18000     45000                         534851709
    # SUSAER       J60         0420GYNTSK6EA0E    OH                        085001090844 18000     45000                         534861710
    # SUSAER       J60         0430NEWELK6EA0E    OH                        085201000851 18000     45000                         534871901
    # SUSAER       J60         0440CANDRK6EA0E    OH                        085402000853 18000     45000                         534882002
    # SUSAER       J60         0450SAX  K6D 0VE   OH                                0840                                         534891709
    # 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #          1         2         3         4         5         6         7         8         9         10        11        12        13
    self.route_id = record[13:18].rstrip()
    self.sequence_number = int(record[25:29])
    self.fix_id = record[29:34].rstrip()
    self.fix_section = record[36:38]
    self.continuation_count = record[38]
    self.waypoint_description = record[39:43]
    self.boundary_code = record[44]
    
    return
