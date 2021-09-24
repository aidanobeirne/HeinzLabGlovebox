# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:43:18 2019

@author: Karen
"""


from PyAPT import APTMotor
import tisgrabber as IC
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk


def updatePos(*args):
    x1=motorX.getPos()
    y1=motorY.getPos()
    z1=motorZ.getPos()
    
    
def moveX(*args):
    targetX=float(posXentry.get())
    motorX.mAbs(targetX)
    print("move x to position ", targetX)
    
def moveY(*args):
    targetY=float(posYentry.get())
    motorY.mAbs(targetY)
    print("move y to position ", targetY)
    
def moveZ(*args):
    targetZ=float(posZentry.get())
    motorZ.mAbs(targetZ)
    print("move z to position ", targetZ)    
    
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
    global x1,y1,z1
    x1=motorX.getPos()
    y1=motorY.getPos()
    z1=motorZ.getPos()
    print("x1 set to ",x1)
    print("y1 set to ",y1)
    print("z1 set to ",z1)

def select2(*args):
    global x2,y2,z2
    x2=motorX.getPos()
    y2=motorY.getPos()
    z2=motorZ.getPos()
    print("x2 set to ",x2)
    print("y2 set to ",y2)
    print("z2 set to ",z2)

def select3(*args):
    global x3,y3,z3
    x3=motorX.getPos()
    y3=motorY.getPos()
    z3=motorZ.getPos()
    print("x3 set to ",x3)
    print("y3 set to ",y3)
    print("z3 set to ",z3)

class UpdatePos:
    def __init__(self, parent, motor, axis):
        # variable storing pos
        self.pos=0
        # label displaying pos
        self.label = tk.Label(parent, text=axis+" position= 0 mm", font="Arial 30", width=10)
        self.label.pack()
        # start the timer
        self.label.after(100, self.refresh_label, motor, axis)

    def refresh_label(self, motor, axis):
        ## refresh the content of the label every 0.1 second
        # increment the time
        self.pos=motor.getPos()
        # display the new time
        self.label.configure(text=axis+" position= %f mm" % self.self.pos)
        # request tkinter to call self.refresh after 0.1s (the delay is given in ms)
        self.label.after(100, self.refresh_label, motor, axis)
        
def main(*args):
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
#    motorX=APTMotor(SN_X,HWTYPE=31)
#    motorY=APTMotor(SN_Y,HWTYPE=31)
#    motorZ=APTMotor(SN_Z,HWTYPE=31)
    
    #-------------------initialize camera
#    Camera = IC.TIS_CAM()
#    open_success=Camera.open("DFK 33UX264 43810318")
#    Camera.StartLive(1)
#    if open_success==0:
#        motorX.cleanUpAPT()
#        motorY.cleanUpAPT()
#        motorZ.cleanUpAPT()
#        exit()
    
    #-------------------initialize GUI
    root=tk.Tk()
    root.title("Find 3 corners")
    
#    #---------------------column 0
#    ttk.Label(root, text="X position = ").grid(row=0,column=0)
#    ttk.Label(root, text="Y position = ").grid(row=1,column=0)
#    ttk.Label(root, text="Z position = ").grid(row=2,column=0)
#
#    #---------------------column 1
#    Xposvar = tk.StringVar()
#    #Xposstr=str(motorX.getPos())
#    Xposstr=str(11.11)
#    Xposvar.set(Xposstr)
#    ttk.Label(root, textvariable=Xposvar).grid(row=0,column=1)
#    
#    Yposvar = tk.StringVar()
#    #Yposstr=str(motorY.getPos())
#    Yposstr=str(22.22)
#    Yposvar.set(Yposstr)
#    ttk.Label(root, textvariable=Yposvar).grid(row=1,column=1)
#    
#    Zposvar = tk.StringVar()
#    #Zposstr=str(motorZ.getPos())
#    Zposstr=str(33.33)
#    Zposvar.set(Zposstr)
#    ttk.Label(root, textvariable=Zposvar).grid(row=2,column=1)
    Xupdate = UpdatePos(root,motorX,"X")
    Yupdate = UpdatePos(root,motorY,"Y")
    Zupdate = UpdatePos(root,motorZ,"Z")
    
    #---------------------column 2
    first=tk.Button(root, text="Select the 1st corner: upper left", command=select1)
    first.grid(row=0,column=2)
    second=tk.Button(root, text="Select the 2nd corner: lower left", command=select2)
    second.grid(row=1,column=2)
    third=tk.Button(root, text="Select the 3rd corner: upper right", command=select3)
    third.grid(row=2,column=2)
    
    #---------------------column 4-7
    ttk.Label(root, text="target pos X").grid(row=0,column=4)
    posXentry=ttk.Entry(root)
    posXentry.grid(row=0,column=5)
    posXentry.insert(0,"12")
    moveXbut=tk.Button(root, text="X move to", command=moveX)
    moveXbut.grid(row=0,column=6, columnspan=2)
    
    ttk.Label(root, text="target pos Y").grid(row=1,column=4)
    posYentry=ttk.Entry(root)
    posYentry.grid(row=1,column=5)
    posYentry.insert(0,"12")
    moveYbut=tk.Button(root, text="Y move to", command=moveY)
    moveYbut.grid(row=1,column=6, columnspan=2)
    
    ttk.Label(root, text="target pos Z").grid(row=2,column=4)
    posZentry=ttk.Entry(root)
    posZentry.grid(row=2,column=5)
    posZentry.insert(0,"12")
    moveZbut=tk.Button(root, text="Z move to", command=moveZ)
    moveZbut.grid(row=2,column=6, columnspan=2)
    
    ttk.Label(root, text="step size X").grid(row=3,column=4)
    stepXentry=ttk.Entry(root)
    stepXentry.grid(row=3,column=5)
    stepXentry.insert(0,"0.1")
    forwardXbut=tk.Button(root, text="X+", command=Xforward)
    forwardXbut.grid(row=3,column=6)
    backwardXbut=tk.Button(root, text="X-", command=Xbackward)
    backwardXbut.grid(row=3,column=7)
    
    ttk.Label(root, text="step size Y").grid(row=4,column=4)
    stepYentry=ttk.Entry(root)
    stepYentry.grid(row=4,column=5)
    stepYentry.insert(0,"0.1")
    forwardYbut=tk.Button(root, text="Y+", command=Yforward)
    forwardYbut.grid(row=4,column=6)
    backwardYbut=tk.Button(root, text="Y-", command=Ybackward)
    backwardYbut.grid(row=4,column=7)
    
    ttk.Label(root, text="step size Z").grid(row=5,column=4)
    stepZentry=ttk.Entry(root)
    stepZentry.grid(row=5,column=5)
    stepZentry.insert(0,"0.01")
    forwardZbut=tk.Button(root, text="Z+", command=Zforward)
    forwardZbut.grid(row=5,column=6)
    backwardZbut=tk.Button(root, text="Z-", command=Zbackward)
    backwardZbut.grid(row=5,column=7)
    
    ttk.Label(root, text="velocity X").grid(row=6,column=4)
    vXentry=ttk.Entry(root)
    vXentry.grid(row=6,column=5)
    vXentry.insert(0,"0.1")
    ttk.Label(root, text="velocity Y").grid(row=7,column=4)
    vYentry=ttk.Entry(root)
    vYentry.grid(row=7,column=5)
    vYentry.insert(0,"0.1")
    ttk.Label(root, text="backlash Z").grid(row=8,column=4)
    bZentry=ttk.Entry(root)
    bZentry.grid(row=8,column=5)
    bZentry.insert(0,"0.01")
    
    for child in root.winfo_children():
        child.grid_configure(padx=5, pady=5)
    
    root.mainloop()
    
    motorX.cleanUpAPT()
    motorY.cleanUpAPT()
    motorZ.cleanUpAPT()
    Camera.StopLive()  
    xylist=[x1,y1,z1,x2,y2,z2,y3,x3,z3]
    print("final: ",xylist)
    return xylist

if __name__ == '__main__':
    xylist=main()





