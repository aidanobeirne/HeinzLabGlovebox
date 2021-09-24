# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:16:26 2020

@author: Markus Huber
"""
#wrapper for 2D stage and piezo stage - based on Lutz and Karen's script

# ATTENTION!!! Might need to have a blocking move funciton for all stages

import importlib
import sys
sys.path.append(r'c:\users\heinz lab computing\appdata\roaming\python\python36\site-packages')
import clr
importlib.reload(clr)
import time
from time import sleep
from System import Decimal, UInt32
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

clr.AddReference('Thorlabs.MotionControl.FilterFlipperCLI')
from Thorlabs.MotionControl.FilterFlipperCLI import FilterFlipper
from Thorlabs.MotionControl.GenericMotorCLI import ControlParameters
from Thorlabs.MotionControl.GenericMotorCLI import AdvancedMotor
from Thorlabs.MotionControl.GenericMotorCLI import Settings

# Rotation cage mounts
clr.AddReference('Thorlabs.MotionControl.IntegratedStepperMotorsCLI')
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import CageRotator
 
clr.AddReference('Thorlabs.MotionControl.KCube.DCServoCLI')
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo 



print("Thorlabs Libraries imported")


try:
    temp = DeviceManagerCLI.BuildDeviceList()
    device_list_result = DeviceManagerCLI.GetDeviceList()
    print(device_list_result)
except Exception as ex:
    print('Exception raised by BuildDeviceList \n', ex)
    print('Tholabs stage not found')


class ThorlabsCageRotator:
    def __init__(self, SN_motor = '55164244' ):
        print("Initializing cage rotator")
        self.motor = CageRotator.CreateCageRotator(SN_motor)
        self.motor.Connect(SN_motor)
        if not self.motor.IsSettingsInitialized:
            try:
                self.motor.WaitForSettingsInitialized(5000)
            except Exception as ex:
                print("Cage Rotator failed to initialize")
        self.motor.StartPolling(10);
        sleep(0.5)
        self.motor.EnableDevice();
        sleep(0.5)
        print("Cage Rotator initialized")
        self.motor.LoadMotorConfiguration(SN_motor)
        # self.home()
        
    def getRotation(self):
        return Decimal.ToDouble(self.motor.Position)
    
    def moveToDeg(self, value):
        if value < 0:
            value = 360 + value
        if value > 360:
            value = value - 360
        self.motor.MoveTo(Decimal(value), 60000)
        
    def home(self):
        print('homing HWP...')
        self.motor.Home(60000)
        
    def close(self):
        self.motor.StopPolling()
        self.motor.Disconnect(True)
        print("Cage Rotator closed")

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
        # start = time.time()
        # print("In move X:" ,value, "dec: ", Decimal(value))
        self.channelX.MoveTo(Decimal(value), 60000)
        # print("In move X readout:" ,self.getXPosition())
        # stop = time.time()
        # print('X move time = ', stop-start)
        
    def getXPosition(self):
        return Decimal.ToDouble(self.channelX.Position)
    
    def moveYTo(self, value):
        # start = time.time()
        # print("In move Y:" ,value, "dec: ", Decimal(value))
        self.channelY.MoveTo(Decimal(value), 60000)
        # print("In move Y readout:" ,self.getYPosition())
        # stop = time.time()
        # print('Y move time = ', stop-start)
    
    def getYPosition(self):
        return Decimal.ToDouble(self.channelY.Position)
    
    def close(self):
        self.channelX.StopPolling()
        self.channelY.StopPolling()
        self.motor.Disconnect(True)
        print("Motors closed")
        
    #X = property(getXPosition, moveXTo, None, ) 
    #Y = property(getYPosition, moveYTo, None, ) 

            
class Thorlabs1DPiezoKinesis:
    def __init__(self, SN_piezo = '41106464'):
        self.piezo = BenchtopPiezo.CreateBenchtopPiezo(SN_piezo);
        self.piezo.Connect(SN_piezo)
        self.channelZ= self.piezo.GetChannel(1)  
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
#        print(value)
#        print(self.MaxVoltage)
        if value >= 0 and value < self.MaxVoltage:
            self.channelZ.SetOutputVoltage(Decimal(value))
        else:
            print('Voltage out of allowed range')
    
    def close(self):
        print("Piezo stopping")
        self.channelZ.StopPolling()
        print("Piezo stopped polling. Trying to disconnect channel.")
        self.channelZ.Disconnect()
        print("Channel disconnected. Trying to disconnect device")
        self.piezo.Disconnect(True)
        print("Piezo disconnected and closed")
        
    #Z = property(getPosition, setPosition, None, ) 
        
class LaserShutter:
    def __init__(self, SN_flipper = '37002951'):
        self.flipper = FilterFlipper.CreateFilterFlipper(SN_flipper)
        self.flipper.Connect(SN_flipper)
        if not self.flipper.IsSettingsInitialized:
            try:
                self.flipper.WaitForSettingsInitialized(5000)
            except Exception as ex:
                print("flipper failed to initialize")
        self.flipper.StartPolling(10);
        sleep(0.5)
        self.flipper.EnableDevice();
        sleep(0.5)
        print("flipper initialized")
        self.flipper.GetDeviceConfiguration('37002951', int(1))
        # self.flipper.Home(60000)
        self.flipperOff()
    
    def flip(self):
        if self.flipper.get_Position() == 1:
            self.flipper.SetPosition(UInt32(2), 60000)
        else:
            self.flipper.SetPosition(UInt32(1), 60000)
    
    def flipperOff(self):
        self.flipper.SetPosition(UInt32(2), 60000)
    
    def flipperOn(self):
        self.flipper.SetPosition(UInt32(1), 60000)
        
    def close(self):
        self.flipper.StopPolling()
        self.flipper.Disconnect(True)
    
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
               
                
# K cubes!!
        
class ThorlabsKCubeDCServoKinesis:
    def __init__(self, SN_servo = '27252667'):
        self.Servo = KCubeDCServo.CreateKCubeDCServo(SN_servo)
        self.Servo.Connect(SN_servo)

        if not self.Servo.IsSettingsInitialized():
            try:
                self.Servo.WaitForSettingsInitialized(5000)
            except Exception as ex:
                print("piezo failed to initialize")
        self.Servo.StartPolling(10);
        sleep(0.5)
        self.Servo.EnableDevice();
        sleep(0.5)
        
        self.motorSettings = self.Servo.LoadMotorConfiguration(SN_servo);
        print("Set backlash to 0")
        self.Servo.SetBacklash(Decimal(0))
        
        print("Servo initialized")
#        if not self.channelZ.IsClosedLoop():
#            self.piezo.SetPositionControlMode(Piezo.PiezoControlModeTypes.CloseLoop);
#        print("Servo at Position: ",self.getPosition())
    
    def moveTo(self, position):
        self.Servo.MoveTo(Decimal(position), 60000)
#        while abs(self.getPosition() - position) > 0.00005:
#            print("Trying to reach position!")
#            sleep(0.01)
#            self.Servo.MoveTo(Decimal(position), 60000)
    
    def getPosition(self):
        return Decimal.ToDouble(self.Servo.Position)
    
    def setVelocity(self, velocity):
        velPars = self.Servo.GetVelocityParams()
        velPars.MaxVelocity = Decimal(velocity)
        self.Servo.SetVelocityParams(velPars)
    
    def home(self):
        self.Servo.Home(60000)
    
    def close(self):
        print("Servo stopping")
        self.Servo.StopPolling()
        print("Servo stopped polling. Trying to disconnect.")
        self.Servo.Disconnect(True)
        print("Servo disconnected and closed")