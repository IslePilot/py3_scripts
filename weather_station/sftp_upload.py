#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2020 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2020-03-23, ksb, created
"""

import sys
sys.path.append("..")
import __common.filetools as filetools

import subprocess
import time

# define a version for this file
VERSION = "1.0.20200323a"

raw_dir = r"C:\Temp\Wx_Raw"
image_file = r"\\roofpi\share\timelapse\image.jpg"

if __name__ == '__main__':
  print(VERSION)
  
  while True:
    # wait for changes to be detected in the directory
    print("Waiting for new files...")
    filetools.wait_for_change(raw_dir)
    
    # wait for the files to complete
    time.sleep(5)
    
    # get the latest webcam image
    filetools.cp(image_file, raw_dir)
    
    # get a listing of the files
    listing = filetools.get_listing(raw_dir, r"\.jpg")
    
    # scp the files to the server
    subprocess.run(["C:\Program Files\PuTTY\pscp.exe",
                    "-P", "4830",
                    "C:\Temp\Wx_Raw\*.jpg", 
                    "keithbarr@droplet1.colorado-barrs.com:/home/keithbarr/public_html/wx"])


  
  
      