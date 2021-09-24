# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 18:59:11 2020

@author: Heinz Group
"""
# %%
import datetime
import sys
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\PS4Controller')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ThorlabsStages')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\GrasshoperCamera3')

import ThorlabsStages
import PS4Controller
import Grasshopper3Cam
import time

import matplotlib.pyplot as plt

SpeedModifier = 10.0

EventLoop = True

def closeEverything():
    global EventLoop
    EventLoop = False
    
def capture():
    path = "C:\\Users\\Heinz Group\\Desktop\\GrasshopperImages\\"
    _filename = path + 'Image_' + str(datetime.datetime.now()).replace(':','-').replace('.','-').replace(' ','_') + '.jpg'
    Camera.saveImageAsJpg(filename=_filename)
    

def modifySpeed(AxisValue):
    global SpeedModifier
    SpeedModifier += AxisValue
    if SpeedModifier > 100:
        SpeedModifier = 100
    if SpeedModifier < 1:
        SpeedModifier = 1
    print(SpeedModifier)

Stage = ThorlabsStages.Thorlabs2DStageKinesis()
ZStage = ThorlabsStages.Thorlabs1DPiezoKinesis()
Controller = PS4Controller.PS4Controller()
Camera = Grasshopper3Cam.Grasshopper3Cam()

Controller.AxisFunctions[0] = lambda AxisValue :  Stage.moveXTo(Stage.getXPosition() + AxisValue*0.1*SpeedModifier/10)
Controller.AxisFunctions[1] = lambda AxisValue :  Stage.moveYTo(Stage.getYPosition() - AxisValue*0.1*SpeedModifier/10)
Controller.AxisFunctions[2] = lambda AxisValue :  modifySpeed(AxisValue)
Controller.AxisFunctions[3] = lambda AxisValue : ZStage.setPosition(ZStage.getPosition() - AxisValue)

Controller.ButtonFunctions[0] = capture
Controller.ButtonFunctions[7] = closeEverything


Camera.startImageAcquisition()
plt.figure(1)
plt.title("X: take image | option: close | L2,R2: speed xy | ")

while EventLoop:
    Controller.doEvents()
    plt.figure(1)
    plt.title("X: take image | option: close | L2,R2: speed xy | ")
    plt.imshow(Camera.getImageAsNumpyArray(), cmap='gray')
    plt.pause(0.001)
    plt.clf()
    #time.sleep(0.1)
    
plt.close(plt.figure(1))
Camera.endImageAcquisition()
Controller.closeController()
Stage.close()
ZStage.close()