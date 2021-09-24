# -*- coding: utf-8 -*-
"""
Created on Fri May 31 17:13:28 2019

@author: Karen
"""
import numpy as np
import cv2
import os.path
from time import sleep
import thorlabs_apt as apt
print("libraries imported...")

SN_X=27252667
SN_Y=27252629
SN_Z=27252673

du=30/1029120 #mm

devices=apt.list_available_devices()
print("available devices:",devices)
motorX=apt.Motor(SN_X)
motorY=apt.Motor(SN_Y)
motorZ=apt.Motor(SN_Z)
print("devices initialized...")
#    motor.move_home(True)
#    motor.move_by(45)

x1=7.5/du #TopLeftX
y1=10.9/du

x2=7.6/du #BottomLeft
y2=11/du

x3=8/du #TopRight
y3=12/du

x4=8.1/du #BottomRight
y4=11.9/du

overlap=25 #percent

FOVx=0.1/du
FOVy=0.08/du

move_time=0.1;

x=np.arange(min(x1,x3),max(x3,x4),FOVx*(1-overlap/100))
y=np.arange(min(y1,y3),max(y2,y4),FOVy*(1-overlap/100))
nx=len(x)
ny=len(y)
print("number of points:",nx,"*",ny,"=",nx*ny)

data_folder="C:\\Users\\Heinz Group\\Desktop\\autoscan\\new"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

cap = cv2.VideoCapture(0)
for i in x:
    print("move x to",i*du)
    motorX.move_to(i*du)
    for j in y:
        print("move y to",j*du)
        motorY.move_to(j*du)
        sleep(move_time)
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            print("phototaken")
            filename="x"+str(i*du)+"y"+str(j*du)+".png"
            file=os.path.join(data_folder,filename)
            cv2.imwrite(file,frame)

cap.release()
print("end")
