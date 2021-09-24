# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 16:40:48 2019

@author: Karen
"""

from PyAPT import APTMotor
from time import sleep
import numpy as np
import cv2
import os.path
import tisgrabber as IC
import matplotlib.pyplot as plt

print("libraries imported...")

####### user inuts
data_folder="C:\\Users\\Heinz Group\\Desktop\\autoscan\\scan_test_4af"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    
width=2448
height=2048
#width=2448
#height=2048
overlap=30 #percent

gain_value=0
contrast=30 ##!!!
brightness=0 ##!!!
saturation=145 # 0-255
red = 1
green = 1.0925
blue = 2.09844
exposure_value=[1/2255]

x1=29.5 #small x small y 
y1=20.298
z1=11.715

x2=29.501 #small x large y
y2=21.5
z2=11.738

x3=31.3 #large x small y
y3=20.3
z3=11.71

x4=-x1+x2+x3
y4=-y1+y2+y3
################ initialize motors

SN_X=27252667
SN_Y=27252629
SN_Z=27252673

wait_short=2;
wait_long=3;

motorX=APTMotor(SN_X,HWTYPE=31)
motorY=APTMotor(SN_Y,HWTYPE=31)
motorZ=APTMotor(SN_Z,HWTYPE=31)

print("motorX in positon ",motorX.getPos())
print("motorY in positon ",motorY.getPos())
print("motorZ in positon ",motorZ.getPos())


################ calculate xy grids
FOVx=0.294/640*10/20*width 
FOVy=0.220/480*10/20*height 

x=np.arange(min(x1,x2),max(x3,x4),FOVx*(1-overlap/100))
y=np.arange(min(y1,y3),max(y2,y4),FOVy*(1-overlap/100))
nx=len(x)
ny=len(y)
grid=np.zeros((nx, ny,2))
for i in x:
    grid
print("number of points:",nx,"*",ny,"=",nx*ny)
print(" ")


#find z by the 3d plane defined by ax+by+cz=d
##AC >x
##BD V y
A=np.array([x1,y1,z1])
B=np.array([x2,y2,z2])
C=np.array([x3,y3,z3])
AB=B-A
AC=C-A
n=np.cross(AB,AC)
print(n)
a=n[0]
b=n[1]
c=n[2]
d=a*x1+b*y1+c*z1
slope_h=(y3-y1)/(x3-x1)
slope_v=(y2-y1)/(x2-x1)
#AB= x=(y-y1)/slope_v+x1
#AC= y=slope_h*(x-x1)+y1
#CD= x=(y-y3)/slope_v+x3
#BD= y=slope_h*(x-x2)+y2
grid=np.zeros((nx, ny,2))
for i in np.arange(nx):
    for j in np.arange(ny):
        if y[j]<slope_h*(x[i]-x1)+y1:
            continue
        if y[j]>slope_h*(x[i]-x2)+y2:
            continue
        if x[i]<(y[j]-y1)/slope_v+x1:
            continue
        if x[i]>(y[j]-y3)/slope_v+x3:
            continue
        grid[i,j,1]=1
        grid[i,j,0]=(d-a*x[i]-b*y[j])/c


################ initialize camera
Camera = IC.TIS_CAM()
#Camera.ShowDeviceSelectionDialog()
Camera.open("DFK 33UX264 43810318")


Camera.SetVideoFormat("RGB32 ("+str(width)+"x"+str(height)+")")
#Camera.SetVideoFormat("RGB32 (2448x2048)")
Camera.SetFrameRate( 10.0 )

Camera.SetPropertySwitch("Gain","Auto",0) # 0-off; 1-on
Camera.SetPropertyValue("Gain","Value",gain_value)
gain_value=Camera.GetPropertyValue("Gain","Value")
print("gain=",gain_value)

Camera.SetPropertySwitch("Contrast","Auto",0)
Camera.SetPropertyValue("Contrast","Value",contrast)
contrast=Camera.GetPropertyValue("Contrast","Value")
print("contrast=",contrast)

Camera.SetPropertySwitch("Brightness","Auto",0)
Camera.SetPropertyValue("Brightness","Value",brightness)
brightness=Camera.GetPropertyValue("Brightness","Value")
print("brightness=",brightness)

Camera.SetPropertySwitch("Saturation","Auto",0)
Camera.SetPropertyValue("Saturation","Value",saturation)
brightness=Camera.GetPropertyValue("Saturation","Value")
print("saturation=",saturation)

Camera.SetPropertySwitch("WhiteBalance","Auto",0)
Camera.SetPropertyValue("WhiteBalance","White Balance Red",int(64*red))
Camera.SetPropertyValue("WhiteBalance","White Balance Green",int(64*green))
Camera.SetPropertyValue("WhiteBalance","White Balance Blue",int(64*blue))
red=Camera.GetPropertyValue("WhiteBalance","White Balance Red")
print("red=",red)
green=Camera.GetPropertyValue("WhiteBalance","White Balance Green")
print("green=",green)
blue=Camera.GetPropertyValue("WhiteBalance","White Balance Blue")
print("blue=",blue)

Camera.SetPropertySwitch("Exposure","Auto",0)
Camera.SetPropertyAbsoluteValue("Exposure","Value",exposure_value[0])
Camera.GetPropertyAbsoluteValue("Exposure","Value",exposure_value)
print("exposure=",exposure_value[0])

Camera.StartLive(1)


################ scan
count=0;
for i in np.arange(nx):
    if sum(grid[i,:,1])==0:
        continue
    motorX.mAbs(x[i])
    sleep(wait_long)
    print("moved x to",motorX.getPos())
    for j in np.arange(ny):
        if grid[i,j,1]==0:
            continue
        motorY.mAbs(y[j])
        print("moved y to",motorY.getPos())
        k=grid[i,j,0]
        motorZ.mAbs(k)
        print("moved z to",motorZ.getPos())
        sleep(wait_short)
        # Get the image  
        Camera.SnapImage()
        image = Camera.GetImage()
        
        # insert autofocus procedure here (move to subroutine later). Currently it takes second image and chooses better one.
        th_std = 15
        th_varlap = 14
        roi = image[200:-200,200:-200]
        std_roi = np.std(roi)   
        varlap_roi = cv2.Laplacian(roi, cv2.CV_64F).var()
        print(std_roi)
        print(varlap_roi)
        if std_roi > th_std and varlap_roi < th_varlap:
            print("refocusing...")
            motorZ.mAbs(k+0.005)
            sleep(wait_short)
            Camera.SnapImage()
            image_p = Camera.GetImage()
            roi_p = image_p[200:-200,200:-200]
            varlap_roi_p = cv2.Laplacian(roi_p, cv2.CV_64F).var()
            print(varlap_roi_p)
            if varlap_roi_p > varlap_roi:
                image = image_p
                print("taking second image")
            else:
                print("refocusing...")
                motorZ.mAbs(k-0.005)
                sleep(wait_long)
                Camera.SnapImage()
                image_m = Camera.GetImage()
                roi_m = image_m[200:-200,200:-200]
                varlap_roi_m = cv2.Laplacian(roi_m, cv2.CV_64F).var()
                if varlap_roi_m > varlap_roi:
                    image = image_m
                    print("taking third image")
                else:
                    print("taking first image")
            
#        plt.figure()
#        plt.imshow(image)
#        cv2.imshow('Window', image)
#        cv2.waitKey(0)
        count=count+1
        print("photo number ",count," taken")
        filename=str(count)+" x"+str(x[i])+" y"+str(y[j])+" z"+str(k)+".png"
        file=os.path.join(data_folder,filename)
        cv2.imwrite(file,image)        
    print(" ")


################ release devices
motorX.cleanUpAPT()
motorY.cleanUpAPT()
motorZ.cleanUpAPT()
Camera.StopLive()  
print("finished")