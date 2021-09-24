# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 19:13:51 2019

@author: Karen
"""

# Import APTMotor class from PyAPT
from PyAPT import APTMotor
from time import sleep
import numpy as np
import cv2
import os.path
print("libraries imported...")

####### user inuts
width=640
height=480
x1=14.91 #small x small y 
y1=18.07

x2=15.00 #small x large y
y2=19.5

x3=16.01 #large x small y
y3=18.8

x4=16.12 #large x large y
y4=19.8

overlap=30 #percent
################


SN_X=27252667
SN_Y=27252629
SN_Z=27252673

wait_short=1;
wait_long=5;

motorX=APTMotor(SN_X,HWTYPE=31)
motorY=APTMotor(SN_Y,HWTYPE=31)
motorZ=APTMotor(SN_Z,HWTYPE=31)

print("motorX in positon ",motorX.getPos())
print("motorY in positon ",motorY.getPos())
print("motorZ in positon ",motorZ.getPos())

FOVx=0.294/640*width #1.129
FOVy=0.220/480*height #0.945

x=np.arange(min(x1,x2),max(x3,x4),FOVx*(1-overlap/100))
y=np.arange(min(y1,y3),max(y2,y4),FOVy*(1-overlap/100))
nx=len(x)
ny=len(y)
print("number of points:",nx,"*",ny,"=",nx*ny)

print(" ")
data_folder="C:\\Users\\Heinz Group\\Desktop\\autoscan\\new2"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)
count=0;
for i in x:
    motorX.mAbs(i)
    sleep(wait_long)
    print("moved x to",motorX.getPos())
    for j in y:
        motorY.mAbs(j)
        print("moved y to",motorY.getPos())
        sleep(wait_short)
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            count=count+1
            print("photo number ",count," taken")
            filename=str(count)+" x"+str(i)+" y"+str(j)+".png"
            file=os.path.join(data_folder,filename)
            cv2.imwrite(file,frame)
    print(" ")

motorX.cleanUpAPT()
motorY.cleanUpAPT()
motorZ.cleanUpAPT()
cap.release()
print("finished")