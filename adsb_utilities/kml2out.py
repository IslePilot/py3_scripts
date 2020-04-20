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

2018-05-20, ksb, created
"""

import sys
sys.path.append("..")
import __common.filetools as filetools

# define a version for this file
VERSION = "1.0.20200418a"

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # ##################### AIRPORTS ############################
  # open the output file
  output_file = open("C:\\Data\\DEN\\CO_Airports.out", "w")
  
  # write the header
  output_file.write("{Airports}\n")
  output_file.write("$TYPE=2\n")
  
  with open("C:\\Data\\DEN\\CO_Airports.kml", "r") as f:
    while True:
      line = f.readline()
      
      # EOF?
      if not line:
        break
      
      # clean up the line
      cline = line.strip()
      if cline == "<coordinates>":
        # get the next line and print it
        coords = f.readline().strip().split(' ')
        
        # put each coordinate into the file
        for point in coords:
          pos = point.split(',')
          output_file.write("{:.6f}+{:.6f}\n".format(float(pos[1]), float(pos[0])))
        output_file.write("-1\n")
        
  # ##################### AIRSPACE ############################
  # open the output file
  output_file = open("C:\\Data\\DEN\\CO_Airspace.out", "w")
  
  # write the header
  output_file.write("{Airspace}\n")
  output_file.write("$TYPE=6\n")
  
  with open("C:\\Data\\DEN\\CO_Airspace.kml", "r") as f:
    while True:
      line = f.readline()
      
      # EOF?
      if not line:
        break
      
      # clean up the line
      cline = line.strip()
      if cline == "<coordinates>":
        # get the next line and print it
        coords = f.readline().strip().split(' ')
        
        # put each coordinate into the file
        for point in coords:
          pos = point.split(',')
          output_file.write("{:.6f}+{:.6f}\n".format(float(pos[1]), float(pos[0])))
        output_file.write("-1\n")
        
 
  
  output_file.close()

  
  
