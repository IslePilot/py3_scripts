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
  processed = r'C:\Data\CIFP\CIFP_221103\Processed'
  eram = r'C:\Data\CIFP\ERAM'
  output = r'C:\Data\CIFP\ToShare'
  charts = r'C:\COAA\PlanePlotter\Chartfiles'
  
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
  
  
  # update planeplotter charts
  # get a list of the new files
  new_files = filetools.get_listing(processed, '')
  used_charts = filetools.get_listing(charts, '')
  
  # work through the used files to get new ones
  for f in used_charts:
    # get the basename of the file
    basename = os.path.basename(f)
    full_base = basename
    
    # if this file is a SID or STAR the filename might not match if the revision was updated, so ignore that part
    if "SIDS" in basename or "STAR" in basename:
      basename = basename[:-5]
    
    # work through all of the new files
    for nf in new_files:
      if basename in nf:
        new_base = os.path.basename(nf)
        
        # if there is a difference, flag it for awareness
        if full_base != new_base:
          print("************************************************************************************")
          print("***** REVISED SID or STAR: ", full_base, " to ", new_base)
          print("************************************************************************************")
          
        # remove the existing file
        filetools.rm(f)
        
        # copy over the new
        filetools.cp(nf, charts) 

        
  
    
      
    
  
