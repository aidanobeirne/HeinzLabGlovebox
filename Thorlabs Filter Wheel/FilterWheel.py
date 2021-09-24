# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:42:53 2021

@author: GloveBox
"""

import importlib
import sys
import clr
importlib.reload(clr)
import time

sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Thorlabs Filter Wheel')
# from FWxC_COMMAND_LIB import *

try:
    from FWxC_COMMAND_LIB import *
except OSError as ex:
    print("Filter Wheel Warning: ",ex)

class ThorlabsFilterWheel:
    def __init__(self, SN_wheel = 'TP02394482-18585' ):
        print("Initializing Filter Wheel")
        try:
            devs = FWxCListDevices()
            print(devs)
            if(len(devs)<=0):
                print('There is no devices connected')
                exit()
            
            FWxC= devs[0]
            SN_wheel = FWxC[0]
            
            self.hdl = FWxCOpen(SN_wheel,115200,3)
            if(self.hdl < 0):
                print("Connection failed" )
            else:
                    print("Connection successed, serial number", SN_wheel)
                    # print(self.hdl)
        
            result = FWxCIsOpen(SN_wheel)
            if(result < 0):
                print("Open failed, abort")
            else:
                print("Filter wheel motor is open")
        
            triggermode=[0]
            triggermodeList={0:"input mode", 1:"output mode"}
            result=FWxCGetTriggerMode(self.hdl,triggermode)
            if(result<0):
                print("Failed to get current trigger mode",result)
            else:
                print("Current Trigger Mode:",triggermodeList.get(triggermode[0]))
                
                
            FWxCSetSpeedMode(self.hdl, 1)
            speedmode=[0]
            speedmodeList={0:"slow speed", 1:"high speed"}
            result=FWxCGetSpeedMode(self.hdl,speedmode)
            if(result<0):
                print("Failed to get current speed mode",result)
            else:
                print("Current Speed Mode:",speedmodeList.get(speedmode[0]))

            position=[0]   
            result=FWxCGetPosition(self.hdl,position)
            if(result<0):
                print("Failed to get current position",result)
            else:
                print("Current position: ", position)
                
            print("Initialization successful")
            
        except Exception as ex:
            print("Warning:", ex)
        # input()


    def CheckStates(self):
        # result = FWxCIsOpen(SN_wheel)
        # if(result < 0):
        #     print("Open failed, abort")
        # else:
        #     print("Filter wheel motor is open")
        
        triggermode=[0]
        triggermodeList={0:"input mode", 1:"output mode"}
        result=FWxCGetTriggerMode(self.hdl,triggermode)
        if(result<0):
              print("Failed to get current trigger mode",result)
        else:
            print("Current Trigger Mode:",triggermodeList.get(triggermode[0]))

        speedmode=[0]
        speedmodeList={0:"slow speed", 1:"high speed"}
        result=FWxCGetSpeedMode(self.hdl,speedmode)
        if(result<0):
            print("Failed to get current speed mode",result)
        else:
            print("Current Speed Mode:",speedmodeList.get(speedmode[0]))

        position=[0]   
        result=FWxCGetPosition(self.hdl,position)
        if(result<0):
            print("Failed to get current position",result)
        else:
            print("Current position: ", position)
    
    def home(self):
        result = FWxCSetTriggerMode(self.hdl, 0) #0:input mode,1:output mode
        if(result<0):
            print("Failed to home trigger mode" , result)
        else:
            print("Current trigger Mode: " , "input mode")
            
        result = FWxCSetSpeedMode(self.hdl, 0) #0:slow speed,1:high speed
        if(result<0):
            print("Failed to home speed mode" , result)
        else:
            print("Current Speed Mode: " , "slow speed")
            
            result = FWxCSetPosition(self.hdl, 1) 
        if(result<0):
            print("Cannot get to home position" , result)
        else:
            print("Current position: " , 1)
            time.sleep(5)
    
    def SetPosition(self, pos):
        a = time.time()
        FWxCSetPosition(self.hdl, pos) 
        b = time.time()
        print(b-a)
        # time.sleep(3)
        
    def GetPosition(self):
        # a = time.time()
        position=[0]   
        result=FWxCGetPosition(self.hdl,position)
        # b = time.time()
        # print(b-a)
        if(result<0):
            print("Failed to get current position",result)
        else:
            print("Current position: ",position)
        return(int(position[0]))
        
    def close(self):
        FWxCClose(self.hdl)
        print("Successfully closed filter wheel")
        
