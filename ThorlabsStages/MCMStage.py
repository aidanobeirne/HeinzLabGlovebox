# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 19:45:49 2020

@author: Markus A. Huber
"""

import serial
import struct
import time

class MCMStage(serial.Serial):

    def __init__(self, port='COM5'):

        self.ser = serial.Serial("COM5", baudrate=460800, bytesize=8, parity='N', timeout=0.1)
        time.sleep(1)
        self.lastCorrectPosition = 0 
        self.lastCorrectPosition = self.getPosition()
        
    def setPosition(self, EncoderInt):
        
#        s = EncoderInt.to_bytes(4,'little') #this is strange since the doku says it should be little endian...
        
        s = struct.pack('<i', EncoderInt)
        self.ser.write(serial.to_bytes([0x53,0x04,0x06,0x00,0x00,0x00, 0x00, 0x00]))
        self.ser.write(s)
        
    def getPosition(self): 
        while self.ser.readline() != b'':
            print("Read random messages from MCM stage")
        
        self.ser.write(serial.to_bytes([0x0A,0x04,0x00,0x00,0x00,0x00]))
        response = self.ser.read(100)
        
#        EncoderString = response.hex()[16:24].encode()
#        EncoderInt = int(EncoderString,16)
        if len(response) == 12 and response[0:5] == b'\x0b\x04\x06\x00\x00':      
            EncoderInt = struct.unpack('<i', response[8:12])[0]
            self.lastCorrectPosition = EncoderInt
            return EncoderInt
        else:
            print("MCM Readout Error!")
            print(response)
            return self.lastCorrectPosition
            
    
    def getPositionInMM(self):
        return self.getPosition() * 0.2116667 /1000.0
    
    
    def setPositionInMM(self, PositionInMM):
        if PositionInMM > 20.0:
            self.setPosition(int( 1000.0/0.2116667*20.0 ))
        else:
            self.setPosition(int( 1000.0/0.2116667*PositionInMM ))

    
    def close(self):
        self.ser.close()
        

#Demo :
#m = MCMStage() 
#m.setPosition(m.getPosition()-10000)


# 2136539392 somewhere in the middle...
# 1500381183 all the waz up top...
# 443744255 also on top...
# 229245184 all the waz down
# 1571094784 also down....


## This seems to be a working transfer back and forth ...
#s = '7f590100'
#a = int(s, 16)
#s2 = a.to_bytes(4,'big')
#print(s == s2.hex())
#
##move funciton
##ser.write(serial.to_bytes([0x53,0x04,0x06,0x00,0x00,0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00]))
#
##split it in header and position...
#ser.write(serial.to_bytes([0x53,0x04,0x06,0x00,0x00,0x00, 0x00, 0x00]))
#ser.write(s2)