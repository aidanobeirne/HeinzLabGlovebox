# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 17:00:24 2020

@author: Markus A. Huber
"""

import serial
import time
import numpy as np

class ArduinoRotationStage():
    
    def __init__(self, Port='COM4'):
        self.ser = serial.Serial(
            port = Port,
            baudrate = 115200,
            timeout = 1)
        self.Ypresetpositions =	{
                                    "10x": 0,
                                    "20x": 0.960,
                                    "50x": 1.925,
                                    "50xIR": 2.885,                                    
                                    }
        self.Xpresetpositions = {
                                    "White light": 0,
                                    "Empty": -0.33,
                                    "Blue light": -0.69,
                                    }
        # self.Ypresetpositions = {
        #                             "F1": 0,
        #                             "F2": -0.2,
        #                             "F3": -0.18,}
        print("Arduino connected")
        self.read()
        time.sleep(0.75)
        self.home()
        
    def home(self):
        self.ser.write(b'\r\n$H\r\n')
        self.ser.write(b'\r\nG28\r\n')
        self.ser.write(b'\r\nG10L20P0X0Y0Z0\r\n')
            
    def read(self):
        time.sleep(0.01)
        line = b'start'
        while line != b'': 
            line = self.ser.readline()
            print(line.decode())
            
    def getPosmm(self): 
        self.ser.write(b'?')
        line = b'start'
        while line != b'': 
            line = self.ser.readline()
            if 'WPos:' in line.decode():     
                positions = str(line.decode()).split('WPos:')[1].split('>')[0]
        positions = positions.split(',')
        positions =[float(i) for i in positions] 
        return positions

    def whichOptic(self): #Very hacky would love a more elegant solution
        X, Y, Z = self.getPosmm()
        optics =[]
        Xkey, Xval = min(self.Xpresetpositions.items(), key= lambda i: abs(X - i[1]))
        Ykey, Yval = min(self.Ypresetpositions.items(), key= lambda i: abs(Y - i[1]))
        # Zkey, Zval = min(self.Zpresetpositions.items(), key= lambda i: abs(Z - i[1]))
        if abs(self.Xpresetpositions[Xkey]-X) < 0.02:
            optics.append(Xkey)
        else:
            optics.append('N/A')
        if abs(self.Ypresetpositions[Ykey]-Y) < 0.02:
            optics.append(Ykey)
        else:
            optics.append('N/A')
        # if abs(self.Zpresetpositions[Zkey]-Z) < 0.02:
        #     optics.append(Zkey)
        # else:
        #     optics.append('N/A')
        return optics
    
    def reset(self):
        self.ser.write(b'\r\n$X\r\n')
        self.ser.write(b'\030')
        self.ser.write(b'\r\n$X\r\n')
        self.ser.write(b'\030')
        self.ser.write(b'\r\nG28\r\n')
        self.ser.write(b'\r\nG10L20P0X0Y0Z0\r\n')
        self.read()   
        
    def moveAbsolutemm(self, axis, distance):
        command = '\r\nG21G90G1'+str(axis)+str(distance)+'F40\r\n'
        self.ser.write(command.encode())
        # self.read()

    def moveRelativemm(self, axis, distance):
        command = '\r\nG21G91G1'+str(axis)+str(distance)+'F40\r\n'
        self.ser.write(command.encode())
        # self.read()
        
    def swapWLBL(self):
        currentfilter = self.whichOptic()[0]
        if currentfilter == 'White light':
            self.moveAbsolutemm('X', self.Xpresetpositions["Blue light"])
        else:
            self.moveAbsolutemm('X', self.Xpresetpositions["White light"])
            
    # def MoveFilter(self):
    #     dic = list(self.Ypresetpositions)
    #     currentfilter = self.whichOptic()[1]
    #     nextfilter = dic[(dic.index(currentfilter) + 1) % len(dic)] 
    #     self.moveAbsolutemm('Y', self.Ypresetpositions[str(nextfilter)])
        
    def IncreaseObjective(self):
        dic = list(self.Ypresetpositions)
        currentobjective = self.whichOptic()[1]
        nextobjective = dic[(dic.index(currentobjective) + 1) % len(dic)] 
        if '50xIR' not in currentobjective:
            self.moveAbsolutemm('Y', self.Ypresetpositions[str(nextobjective)]) 
        else:
            pass
        
    def DecreaseObjective(self):
        dic = list(self.Ypresetpositions)
        currentobjective = self.whichOptic()[1]
        nextobjective = dic[(dic.index(currentobjective) - 1) % len(dic)]
        if '10x' not in currentobjective:
            self.moveAbsolutemm('Y', self.Ypresetpositions[str(nextobjective)])
        else:
            pass
        
    def close(self):
        print('Close connection to Arduino Rotation Stage')
        self.ser.close()
        print("Connection to Arduino Rotation Stage closed")


