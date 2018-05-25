#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-05-25, ksb, created
"""

from pathlib import Path
import shutil


# define a version for this file
VERSION = "1.0.2018-05-25a"

def mkdir(pathname):
  """If a given pathname doesn't exist, build it
  
  pathname: path to build/verify"""
  #build the path
  try:
    Path(pathname).mkdir(parents=True, exist_ok=True)  # create parents, don't error if it exists
  except:
    print("filetools.mkdir: Unable to build path {:s}".format(pathname))
    return False
  return True

def mv(src, dst):
  """Move a file or directory to another destination
  
  src: source file or directory
  dst: destination (caution, may overwrite)
  
  returns: True if successful, False if unsuccessful"""
  # move the file
  try:
    shutil.move(src, dst)
  except:
    print("filetools.mv: Unable to move {:s} to {:s}".format(src, dst))
    return False
  return True

def cp(src, dst):
  """Copy a file or directory to another destination
  
  src: source file or directory
  dst: destination (caution, may overwrite)
  
  returns: True if successful, False if unsuccessful"""
  # move the file
  try:
    shutil.copy(src, dst)
  except:
    print("filetools.mv: Unable to copy {:s} to {:s}".format(src, dst))
    return False
  return True



if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
