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

  May 29, 2020, ksb, created
"""

import sys
sys.path.append("..")

import maptools as maptools

import simplekml


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
   




# define a version for this file
VERSION = "1.0"

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
