'''
Created on Mar 19, 2024

@author: keith
'''
import socket
import struct

if __name__ == '__main__':
  mcast_address = ('', 5252)
  
  # configure the socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(mcast_address)
  
  mreq = struct.pack("4sl", socket.inet_aton('239.100.100.0'), socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  
  while True:
    # wait here for a message
    bs = sock.recv(1024)
    
    packet, t, az, el, r, x, y, z, gs, track = struct.Struct('Ld8f').unpack(bs)
    print(packet, t, az, el, r, x, y, z, gs, track)
