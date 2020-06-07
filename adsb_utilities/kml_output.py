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

  Jun 3, 2020, ksb, created
"""

import sys
sys.path.append("..")

import simplekml

class KMLOutput:
  def __init__(self, foldername, filename):
    self.rootfolder = simplekml.Kml()
    self.rootfolder.document.name = foldername
    self.filename = filename
    return 
  
  def savefile(self):
    self.rootfolder.save(self.filename)
    return
  
  def create_folder(self, foldername, parent=None):
    if parent == None:
      f = self.rootfolder.newfolder(name=foldername)
    else:
      f = parent.newfolder(name=foldername)
    
    return f
  
  def add_point(self, folder, name, point, description):
    pnt = folder.newpoint(name=name, coords=[(point[1], point[0])], description=description)
    pnt.lookat = simplekml.LookAt(latitude=point[0], longitude=point[1], range=15000, heading=0, tilt=0)
    pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
    return
  
  def add_line(self, folder, name, points, color=simplekml.Color.red):
    # convert the points to kml style
    kml_points = []
    for pt in points:
      kml_points.append((pt[1], pt[0]))
      
    line = folder.newlinestring(name=name, coords=kml_points)
    line.style.linestyle.width = 4.0
    line.style.linestyle.color = color
    
    return

