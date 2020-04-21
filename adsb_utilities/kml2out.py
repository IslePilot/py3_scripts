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

2020-04-18, ksb, created
2020-04-20, ksb, added method to simplify multiple file processing
"""

import sys
sys.path.append("..")
import __common.filetools as filetools

def build_out(path, filename, color):
  # open the output file
  output_file = open(path + "\\" + filename + ".out", "w")
  
  # write the header
  output_file.write("{{{}}}\n".format(filename))
  output_file.write("$TYPE={}\n".format(color))
  
  with open(path + "\\" + filename + ".kml", "r") as f:
    while True:
      line = f.readline().strip('\t\n\r ')
      
      # EOF?
      if not line:
        break
      
      # does this get us into a coordinate block?
      if "<coordinates>" in line:
        # remove the starter
        proc_line = line.replace("<coordinates>", "")
        
        # process the line
        process = True
        while process:
          # identify if this is the end
          if "</coordinates>" in proc_line:
            # remove the closer
            proc_line = proc_line.replace("</coordinates>", "")
            process = False # we are done after we process this line
            
          coords = proc_line.split(' ')
          
          # put each coordinate into the file
          for point in coords:
            pos = point.split(',')
            if len(pos) == 3:
              output_file.write("{:.6f}+{:.6f}\n".format(float(pos[1]), float(pos[0])))
          
          # do we get another line of data or end this block?
          if process:
            proc_line = f.readline().strip()
          else:
            output_file.write("-1\n")
  
  output_file.close()
  
  return
  
# define a version for this file
VERSION = "1.0.20200420a"

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  path = "C:\\Data\\DEN"
  
  # colors:
  # 1 - Orange
  # 2 - Yellow
  # 3 - Green
  # 4 - Aqua
  # 5 - Blue
  # 6 - Magenta
  # 7 - White
  # 8 - Gray
  build_out(path, "CO_Airports", 2)
  build_out(path, "CO_Airspace", 6)
  build_out(path, "CO_Interstates", 4)
  build_out(path, "KDEN_Approaches", 1)
  build_out(path, "KDEN_SIDs", 8)
  build_out(path, "KDEN_STARS", 5)
  build_out(path, "Special", 2)
  
  path = "C:\\Data\\BJC"
  build_out(path, "KBJC_Approaches", 1)
  build_out(path, "KBJC_SIDs", 8)
  build_out(path, "KBJC_STARS", 5)
  
  print("Done")


  
  
