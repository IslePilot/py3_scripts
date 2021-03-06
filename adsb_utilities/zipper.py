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

  Dec 4, 2020, ksb, created
"""

import sys
sys.path.append("..")
import __common.filetools as filetools

import os

import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

modes = { zipfile.ZIP_DEFLATED: 'deflated',
          zipfile.ZIP_STORED:   'stored',
          }

# define a version for this file
VERSION = "1.0"



if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  # Modify this ################# vvvvvv #############
  processed = r'C:\Data\CIFP\CIFP_210325\Processed'
  eram = r'C:\Data\CIFP\ERAM'
  output = r'C:\Data\CIFP\ToShare'
  charts = r'C:\COAA\PlanePlotter\Chart files'
  
  # get a list of files in the form KXXX.kml
  listing = filetools.get_listing(processed, '^K\w\w\w\.kml')
  ids = []
  for f in listing:
    base = os.path.basename(f)
    ids.append(os.path.splitext(base)[0])
  
  # process each airport
  for icao in ids:
    print("Processing ", icao, "...")
    listing = filetools.get_listing(processed, '^{}'.format(icao))
    zf = zipfile.ZipFile("{}/{}.zip".format(output, icao), mode='w')
    for f in listing:
      print("     adding ", f)
      zf.write(f, compress_type=compression)
    zf.close()
  
  # copy USA files
  listing = filetools.get_listing(processed, "^USA_")
  for f in listing:
    filetools.cp(f, output)
    filetools.cp(f, charts)
  
  # copy ERAM files
  listing = filetools.get_listing(eram, "^USA_")
  for f in listing:
    filetools.cp(f, output)
    filetools.cp(f, charts)
    
  # update chart files
  listing = filetools.get_listing(charts, '')
  chartlist = []
  for f in listing:
    chartlist.append(os.path.basename(f))
  
  listing = filetools.get_listing(processed, '')
  for f in listing:
    basename = os.path.basename(f)
    if basename in chartlist:
      print("Copying ", basename, " to charts directory")
      filetools.cp(f, charts)
  
    
      
    
  
