# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:45:46 2020

@author: Markus A. Huber
"""
#%%

import serial

ser = serial.Serial("COM4", 115200, timeout=1)


# %%

line = ser.readline()
print(line)

# %% relative coordinates

ser.write(b'\r\nG21G91G1X0.96F25\r\n')
line == b'start'
while line != b'': 
    line = ser.readline()
    print(line)

# %% all units in mm

ser.write(b'G28;')
line = ser.readline()
print(line)

# %%
#
#
#timeout_count = 0
#received = []
#data_count = 0
#while 1:
#    buffer = ser.read(32768)
#    if buffer:
#        received.append(buffer)
#        data_count += len(buffer)
#        timeout_count = 0
#        continue
#    if data_count > 100:
#        # Break if we received at least 100 bytes of data,
#        # and haven't received any data for at least 2 seconds
#        break
#    timeout_count += 1
#    if timeout_count >= 5:
#        # Break if we haven't received any data for at
#        # least 10 seconds, even if we never received
#        # any data
#        break
#
#    received = b''.join(received)  # If you need all the data