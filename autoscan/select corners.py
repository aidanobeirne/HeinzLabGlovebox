# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:43:18 2019

@author: Karen
"""


from PyAPT import APTMotor
from time import sleep
import numpy as np
import cv2
import os.path
import tisgrabber as IC
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import winsound

def Xforward(*args):
    Xstepsize=float(stepXentry.get())
    Xvelocity=float(vXentry.get())
    print("move x forward in step ", Xstepsize, " with velocity ",Xvelocity)
    motorX.mcRel(Xstepsize,Xvelocity)

def Xbackward(*args):
    Xstepsize=float(stepXentry.get())
    Xvelocity=float(vXentry.get())
    print("move x backward", -Xstepsize)
    motorX.mcRel(-Xstepsize,Xvelocity)
    
def Yforward(*args):
    Ystepsize=float(stepYentry.get())
    Yvelocity=float(vYentry.get())
    motorY.mcRel(Ystepsize,Yvelocity)

def Ybackward(*args):
    Ystepsize=float(stepYentry.get())
    Yvelocity=float(vYentry.get())
    motorY.mcRel(-Ystepsize,Yvelocity)
    
def Zforward(*args):
    Zstepsize=float(stepZentry.get())
    Zbacklash=float(bZentry.get())
    setattr(motorZ, 'blCorr', Zbacklash )
    motorZ.mbRel(Zstepsize)
       
def Zbackward(*args):
    Zstepsize=float(stepZentry.get())
    Zbacklash=float(bZentry.get())
    motorZ.blCorr=Zbacklash
    setattr(motorZ, 'blCorr', Zbacklash )
    motorZ.mbRel(-Zstepsize)
    
def select1(*args):
    x1=motorX.getPos()
    y1=motorY.getPos()
    z1=motorZ.getPos()
    print("x1 set to ",x1)
    print("y1 set to ",y1)
    print("z1 set to ",z1)

def select2(*args):
    x2=motorX.getPos()
    y2=motorY.getPos()
    z2=motorZ.getPos()
    print("x2 set to ",x2)
    print("y2 set to ",y2)
    print("z2 set to ",z2)

def select3(*args):
    x3=motorX.getPos()
    y3=motorY.getPos()
    z3=motorZ.getPos()
    print("x3 set to ",x3)
    print("y3 set to ",y3)
    print("z3 set to ",z3)


#-------------------initialize motors
x1=0
y1=0
z1=0
x2=0
y2=0
z2=0
x3=0
y3=0
z3=0
SN_X=27252667
SN_Y=27252629
SN_Z=27252673
motorX=APTMotor(SN_X,HWTYPE=31)
motorY=APTMotor(SN_Y,HWTYPE=31)
motorZ=APTMotor(SN_Z,HWTYPE=31)

#-------------------initialize camera
Camera = IC.TIS_CAM()
open_success=Camera.open("DFK 33UX264 43810318")
Camera.StartLive(1)
#if open_success==0:
#    winsound.beep(1000,1)
#    motorX.cleanUpAPT()
#    motorY.cleanUpAPT()
#    motorZ.cleanUpAPT()
#    exit()

#-------------------initialize GUI
root=tk.Tk()
root.title("Find 3 corners")

forwardXbut=tk.Button(root, text="X+", command=Xforward)
forwardXbut.pack()
backwardXbut=tk.Button(root, text="X-", command=Xbackward)
backwardXbut.pack()
forwardYbut=tk.Button(root, text="Y+", command=Yforward)
forwardYbut.pack()
backwardYbut=tk.Button(root, text="Y-", command=Ybackward)
backwardYbut.pack()
forwardZbut=tk.Button(root, text="Z+", command=Zforward)
forwardZbut.pack()
backwardZbut=tk.Button(root, text="Z-", command=Zbackward)
backwardZbut.pack()

Xposvar = tk.StringVar()
Xposstr="X position = "+str(motorX.getPos())
Xposvar.set(Xposstr)
ttk.Label(root, textvariable=Xposvar).pack()

Yposvar = tk.StringVar()
Yposstr="Y position = "+str(motorY.getPos())
Yposvar.set(Yposstr)
ttk.Label(root, textvariable=Yposvar).pack()

Zposvar = tk.StringVar()
Zposstr="Z position = "+str(motorZ.getPos())
Zposvar.set(Zposstr)
ttk.Label(root, textvariable=Zposvar).pack()

ttk.Label(root, text="step size X").pack()
stepXentry=ttk.Entry(root)
stepXentry.pack()
stepXentry.insert(0,"0.1")
ttk.Label(root, text="step size Y").pack()
stepYentry=ttk.Entry(root)
stepYentry.pack()
stepYentry.insert(0,"0.1")
ttk.Label(root, text="step size Z").pack()
stepZentry=ttk.Entry(root)
stepZentry.pack()
stepZentry.insert(0,"0.01")
ttk.Label(root, text="velocity X").pack()
vXentry=ttk.Entry(root)
vXentry.pack()
vXentry.insert(0,"0.1")
ttk.Label(root, text="velocity Y").pack()
vYentry=ttk.Entry(root)
vYentry.pack()
vYentry.insert(0,"0.1")
ttk.Label(root, text="backlash Z").pack()
bZentry=ttk.Entry(root)
bZentry.pack()
bZentry.insert(0,"0.01")

first=tk.Button(root, text="Select the 1st corner: upper left", command=select1)
first.pack()
second=tk.Button(root, text="Select the 2nd corner: lower left", command=select2)
second.pack()
third=tk.Button(root, text="Select the 3rd corner: upper right", command=select3)
third.pack()

root.mainloop()

motorX.cleanUpAPT()
motorY.cleanUpAPT()
motorZ.cleanUpAPT()
Camera.StopLive()  
print("finished")





