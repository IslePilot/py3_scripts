#!/usr/bin/env python3

"""
************************************************************************************
Copyright 2018 (C) AeroSys Engineering, Inc.
All Rights Reserved

This source code is provided with no warranty expressed or implied.  Suitability for
any purpose is not guaranteed.
************************************************************************************

Revision History:

2018-06-15, ksb, created
"""

import sys
sys.path.append("..")

# define a version for this file
VERSION = "1.0.2018-06-15a"

from multiprocessing import Pool, TimeoutError
import time
import os

class BaseClass():
  def __init__(self, class_id):
    self.class_id = class_id
    self.sequence = 0
    return
  
  def process(self):
    while True:
      self.sequence += 1
      print("I am a process of", self.class_id)
      time.sleep(1.0)
    return

class Derived1(BaseClass):
  def __init__(self, class_id):
    # run the base constructor
    super().__init__(class_id)
    return
  
  def process(self):
    # do some crazy derived process
    while True:
      self.sequence += 1
      print("I am a Derived1 class...I do Derived1 types of things", self.class_id)
      time.sleep(2.0)
    return

class Derived2(BaseClass):
  def __init__(self, class_id):
    # run the base constructor
    super().__init__(class_id)
    return
  
  def process(self):
    # do some crazy derived process
    while True:
      self.sequence += 1
      print("I am a Derived2 class...Nobody is like me!", self.class_id)
      time.sleep(3.0)
    return

def launcher(class_id):
  if class_id == 0:
    myclass = BaseClass(class_id)
  elif class_id == 1:
    myclass = Derived1(class_id)
  elif class_id == 2:
    myclass = Derived2(class_id)
  else:
    print("no such class", class_id)
    return
  
  # run our process to completion
  myclass.process()
  return
  
  

if __name__ == '__main__':
    # start 4 worker processes
    with Pool(processes=4) as pool:

        # print "[0, 1, 4,..., 81]"
        print(pool.map(launcher, range(10)))

        # print same numbers in arbitrary order
        for i in pool.imap_unordered(launcher, range(10)):
            print(i)

        # evaluate "f(20)" asynchronously
        res = pool.apply_async(launcher, (20,))      # runs in *only* one process
        print(res.get(timeout=1))             # prints "400"

        # evaluate "os.getpid()" asynchronously
        res = pool.apply_async(os.getpid, ()) # runs in *only* one process
        print(res.get(timeout=1))             # prints the PID of that process

        # launching multiple evaluations asynchronously *may* use more processes
        multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
        print([res.get(timeout=1) for res in multiple_results])

        # make a single worker sleep for 10 secs
        res = pool.apply_async(time.sleep, (10,))
        try:
            print(res.get(timeout=1))
        except TimeoutError:
            print("We lacked patience and got a multiprocessing.TimeoutError")

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")