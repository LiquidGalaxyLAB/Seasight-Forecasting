# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:40:29 2020

@author: gizqu
"""

import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 21567

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    counter, latitude, longitude, altitude, heading, tilt, roll, time_start, time_end, planet_name  = data.decode("utf-8").split(',')    
    print("received message: {} - {}".format(latitude, longitude))
