# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:16:26 2020

@author: Markus Huber
"""
#wrapper for 2D stage and piezo stage - based on Lutz and Karen's script

# ATTENTION!!! Might need to have a blocking move funciton for all stages

import importlib

import clr
importlib.reload(clr)
import sys
from time import sleep
from System import Decimal
sys.path.append(r"C:\Program Files\Thorlabs\Kinesis")  # path of dll
clr.AddReference('Thorlabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.GenericPiezoCLI')
clr.AddReference('Thorlabs.MotionControl.Benchtop.PiezoCLI')
clr.AddReference('Thorlabs.MotionControl.GenericMotorCLI')
clr.AddReference('Thorlabs.MotionControl.Benchtop.BrushlessMotorCLI')
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.GenericPiezoCLI import Piezo
#from Thorlabs.MotionControl.Benchtop.PrecisionPiezoCLI import BenchtopPrecisionPiezo
from Thorlabs.MotionControl.Benchtop.PiezoCLI import BenchtopPiezo
#from Thorlabs.MotionControl.GenericMotorCLI import AdvancedMotor
from Thorlabs.MotionControl.Benchtop.BrushlessMotorCLI  import BenchtopBrushlessMotor
 
print("Thorlabs Libraries imported")



try:
    temp = DeviceManagerCLI.BuildDeviceList()
    device_list_result = DeviceManagerCLI.GetDeviceList()
    print(device_list_result)
except Exception as ex:
    print('Exception raised by BuildDeviceList \n', ex)
    print('Tholabs stage not found')


class Thorlabs2DStageKinesis:

    def __init__(self, SN_motor = '73109504' ):
        #device_list_result = DeviceManagerCLI.BuildDeviceList()
        self.motor = BenchtopBrushlessMotor.CreateBenchtopBrushlessMotor(SN_motor);
        print("device set up")
        self.motor.Connect(SN_motor)
        print("device connected, serial No: ",SN_motor)
        self.channelX=self.motor.GetChannel(1)
        self.channelY=self.motor.GetChannel(2)
        
        if not self.channelX.IsSettingsInitialized:
            try:
                self.channelX.WaitForSettingsInitialized(5000)
            except Exception:
                print("motor failed to initialize")
        if not self.channelY.IsSettingsInitialized:
            try:
                self.channelY.WaitForSettingsInitialized(5000)
            except Exception:
                print("motor failed to initialize")
                
        self.motorConfigurationX = self.channelX.LoadMotorConfiguration(self.channelX.DeviceID)
        self.currentDeviceSettingsX = self.channelX.MotorDeviceSettings
        self.motorConfigurationY = self.channelY.LoadMotorConfiguration(self.channelY.DeviceID)
        self.currentDeviceSettingsY = self.channelY.MotorDeviceSettings
        self.channelX.StartPolling(10);
        sleep(0.5)
        self.channelX.EnableDevice();
        sleep(0.5)
        print("X motor enabled")
        
        self.channelY.StartPolling(10);
        sleep(0.5)
        self.channelY.EnableDevice();
        sleep(0.5)
        print("Y motor enabled")
        
        print("current positionX:",self.getXPosition())
        print("current positionY:",self.getYPosition())
        
        
        
    def home(self):
        self.channelX.Home(60000)
        self.channelY.Home(60000)
        
    def homeX(self):
        self.channelX.Home(60000)
    
    def homeY(self):
        self.channelY.Home(60000)
    
    def moveXTo(self, value):
        self.channelX.MoveTo(Decimal(value), 60000)
        
    def getXPosition(self):
        return Decimal.ToDouble(self.channelX.Position)
    
    def moveYTo(self, value):
        self.channelY.MoveTo(Decimal(value), 60000)
    
    def getYPosition(self):
        return Decimal.ToDouble(self.channelY.Position)
    
    def close(self):
        self.channelX.StopPolling()
        self.channelY.StopPolling()
        self.motor.Disconnect(True)
        print("motor closed")
        
    #X = property(getXPosition, moveXTo, None, ) 
    #Y = property(getYPosition, moveYTo, None, ) 

            
class Thorlabs1DPiezoKinesis:
    def __init__(self, SN_piezo = '41106464'):
        self.piezo = BenchtopPiezo.CreateBenchtopPiezo(SN_piezo);
        self.piezo.Connect(SN_piezo)
        self.channelZ=self.piezo.GetChannel(1)  
        self.MaxVoltage = 150#Decimal.ToDouble(self.channelZ.GetMaxOutputVoltage())
        if not self.channelZ.IsSettingsInitialized:
            try:
                self.channelZ.WaitForSettingsInitialized(5000)
            except Exception as ex:
                print("piezo failed to initialize")
        self.channelZ.StartPolling(10);
        sleep(0.5)
        self.channelZ.EnableDevice();
        sleep(0.5)
        print("piezo initialized")
#        if not self.channelZ.IsClosedLoop():
#            self.piezo.SetPositionControlMode(Piezo.PiezoControlModeTypes.CloseLoop);
        print("piezo Z at Voltage: ",self.getVoltage())
    
    def getVoltage(self):
        return Decimal.ToDouble(self.channelZ.GetOutputVoltage())
    
    def setVoltage(self, value):
        if value >= 0 and value < self.MaxVoltage:
            self.channelZ.SetOutputVoltage(Decimal(value))
        else:
            print('Voltage out of allowed range')
    
    def close(self):
        self.channelZ.StopPolling()
        self.piezo.Disconnect(True)
        print("piezo closed")
        
    #Z = property(getPosition, setPosition, None, ) 
        
    
class Thorlabs1DPiezoDummy:
    def __init__(self, SN_piezo = '111'):
        print("Dummy Stage initialized")
        self.Position = 0
    
    def getPosition(self):
        return self.Position
    
    def setPosition(self, value):
        self.Position = value
    
    def close(self):
        print("Dummy Stage closed")
               
                