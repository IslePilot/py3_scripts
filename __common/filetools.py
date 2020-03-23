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
import os
import re



# define a version for this file
VERSION = "1.0.20200323a"

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

def get_listing(pathname, regexp):
  """Get a listing of the files in a path matching regexp
  
  pathname: directory to search
  regexp: regular expression string"""
  print("filetools.get_listing(): Searching {:s} for files matching {:s}".format(pathname, regexp))
  
  # work through everything in the directory
  listing = []
  for filename in os.listdir(pathname):
    # is this a file?
    if os.path.isfile(pathname + "/" + filename):
      # does it match our expression?
      if re.search(regexp, filename):
        listing.append(pathname + "/" + filename)
  
  # sort our listing and return
  listing.sort()
  return listing

def rm(filename):
  """Remove a file
  
  filename: full pathname of the file to remove"""
  try:
    os.remove(filename)
  except Exception:
    print("filetools.rm():  Unable to remove file {:s}".format(filename))
    return False
  
  return True

def wait_for_change(path_to_watch):
  """block waiting for a directory to change
  
  path_to_watch: the directory to wait for changes in"""
  import win32file
  import win32con
  
  ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Updated",
    4 : "Renamed from something",
    5 : "Renamed to something"
  }
  # Thanks to Claudio Grondi for the correct set of numbers
  FILE_LIST_DIRECTORY = 0x0001
  
  hDir = win32file.CreateFile (
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
  )
  
  #
  # ReadDirectoryChangesW takes a previously-created
  # handle to a directory, a buffer size for results,
  # a flag to indicate whether to watch subtrees and
  # a filter of what changes to notify.
  #
  # NB Tim Juchcinski reports that he needed to up
  # the buffer size to be sure of picking up all
  # events when a large number of files were
  # deleted at once.
  #
  results = win32file.ReadDirectoryChangesW (hDir,
                                             1024,
                                             True,
                                             win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                                             win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                                             win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                                             win32con.FILE_NOTIFY_CHANGE_SIZE |
                                             win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                                             win32con.FILE_NOTIFY_CHANGE_SECURITY,
                                             None,
                                             None)
  
  return results

if __name__ == '__main__':
  # when this file is run directly, run this code
  print(VERSION)
  
  path_to_watch = r"C:\Temp\Wx_Raw"
  results = wait_for_change(path_to_watch)
