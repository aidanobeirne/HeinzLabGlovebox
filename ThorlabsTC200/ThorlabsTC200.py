# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 18:26:36 2020

@author: Markus A. Huber
"""


import serial

class ThorlabsTC200():

    def __init__(self, Port='COM7'):
        self.ser = serial.Serial(
            port = Port,
            baudrate = 115200,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = 2
            )
        self.SanityTimeout = 10
        if self.connectionEstablished():
            print('Connection to heater established')
        else:
            print('Could not connect to heater!')
            self.ser.close()
            raise RuntimeError('TC200 could not be connected! Maybe the port was wrong or the heater is not properly connected. Try finding the TC200 in the device manager or the proprietary software of Thorlabs. After that you can try to connect using e.g. the program Putty and the documentation in the Manual Chapter 6 (not the programming documentation, just the manual)')
    
    def getEnabled(self):
        StatusByte = self.sendCommand('stat?') 
        if StatusByte[0] == '1':
            return True
        else:
            return False
        
    def setEnabled(self, EnableTrue):
        CurrentStatus = self.getEnabled()
        if EnableTrue == True:
            if CurrentStatus == False:
                response = self.sendCommand('ens')
                CurrentStatusNow = self.getEnabled()
                if CurrentStatusNow == True:
                    print('Enabled device')
                    return
                else:
                    print('Error. Could not enable device!')
            else:
                print('Device was already enabled')
                return
        else: #EnableTrue == false... menas you want to disable
            if CurrentStatus == True:
                response = self.sendCommand('ens')
                CurrentStatusNow = self.getEnabled()
                if CurrentStatusNow == False:
                    print('Device disabled')
                    return
                else:
                    print('Error. Could not disable device!')
            else:
                print('Device was already disabled')
                return
            
    def enable(self):
        self.setEnabled(True)
        
    def disable(self):
        self.setEnabled(False)
            
    def getCurrentTemp(self):
        response = self.sendCommand('tact?')
        print(response)
        return float(response)
    
    def getTargetTemperature(self):
        response = self.sendCommand('tset?')
        print(response)
        return float(response)
    
    def setTargetTemp(self, value):
        response = self.sendCommand('tset='+"{:.1f}".format(value).zfill(5)) # maybe the zfill is unnecessary...
        print(response)
        return self.getTargetTemperature()
    
    
    def sendCommand(self, command):
        if self.connectionEstablished():
            self.ser.write(b''+command.encode()+b'\r')
            response = self.ser.readline()
            return response
        else:
            print('Could not send command!')
            return 'Error! Could not connect to heater!'
    
    def connectionEstablished(self):
        works = False
        for i in range(self.SanityTimeout):
            self.ser.write(b'\r')
            line = self.ser.readline()
            if line == 'Command error CMD_NOT_DEFINED':
                works = True
                break
            else:
                print('Sent command. Expected string: Command error CMD_NOT_DEFINED')
                print('Instead received:')
                print(line)
                print('Will try again for '+str(self.SanityTimeout-i) + ' times')
        return works
            