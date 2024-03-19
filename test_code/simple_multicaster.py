'''
Created on Mar 19, 2024

@author: keith
'''
import socket
import struct
import time

from astropy.time import Time
from datetime import datetime, timezone

if __name__ == '__main__':
  mcast_address = ('239.100.100.0', 5252)
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
  
  packet = 0
  while True:
    now = datetime.now(timezone.utc)
    t = Time(now.strftime("%Y-%m-%d %H:%M:%S.%f"), format='iso', scale='utc').gps
    
    packet += 1
    
    az = 90.0
    el = 45.0
    r = 1234.5678
    
    x = 10.0
    y = 20.0
    z = 30.0
    
    gs = 0.51444
    track = 292.3
    
    fmt = 'Ld8f'
    datastring = struct.Struct(fmt).pack(packet, t, az, el, r, x, y, z, gs, track)

    sock.sendto(datastring, mcast_address)  
    
    print(packet, t, az, el, r, x, y, z, gs, track)
    
    time.sleep(1.0)
    
    
  