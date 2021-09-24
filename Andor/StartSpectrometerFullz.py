# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:02:53 2020

@author: GloveBox
"""

import platform
from ctypes import *
from PIL import Image
import sys

CamDLL = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atmcd64d.dll")
SpecDll = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atspectrograph.dll")

# %%
HowManyCams = c_long()
CamDLL.GetAvailableCameras(byref(HowManyCams))
print('Found '+str(HowManyCams.value)+' Cameras')
CameraHandles = []

print('Starting Cameras')
for CamNumber in range(HowManyCams.value):
    Handle = c_long()
    CamDLL.GetCameraHandle(c_long(CamNumber),byref(Handle))
    CameraHandles.append(Handle)
    
    print('Starting Camera '+str(CamNumber+1))
    CamDLL.SetCurrentCamera(CameraHandles[CamNumber])
    tekst = c_char()  
    error = CamDLL.Initialize(byref(tekst))
    
    serial = c_int()
    CamDLL.GetCameraSerialNumber(byref(serial))
    print("Camera has serial number: "+str(serial.value))
    
    cw = c_int()
    ch = c_int()
    CamDLL.GetDetector(byref(cw), byref(ch))
    print("Camera has dimensions: " + str(cw.value) +" x " + str(ch.value))
    
print("Cameras started")



print("Starting spectrometer")
tekst = c_char()        
error = SpecDll.ShamrockInitialize(byref(tekst))
print("Spectrometer started")

Num = c_int()
print(SpecDll.ShamrockGetNumberDevices(byref(Num)))
print("Found " + str(Num.value) + " spectrometer")


# %%

Num = c_float()
print(SpecDll.ShamrockGetWavelength(0, byref(Num)))
print("Current center wavelength: "+ str(Num.value))

# %%
ctemperature = c_int()
error = CamDLL.GetTemperature(byref(ctemperature))
print(ctemperature.value)


# %%
CurrentCameraHandle = c_long()
CamDLL.GetCurrentCamera(byref(CurrentCameraHandle))
print(CurrentCameraHandle.value)

# %%
Num = c_float(1490.00)
print(SpecDll.ShamrockSetWavelength(0,Num))
print(Num)

# %%
PxWidth = c_float(1490.00)
print(SpecDll.ShamrockGetPixelWidth(0,byref(PxWidth)))
print(PxWidth.value)






# %%
grating = c_int()
error = SpecDll.ShamrockGetGrating(0,byref(grating))
print(grating.value)

# %%

error = SpecDll.ShamrockSetGrating(0,c_int(2))
print(error)

# NUmbers seem to directlzcorrespondto gratings




# %%
shutter = c_int()
error = SpecDll.ShamrockGetShutter(0,byref(shutter))
print(shutter.value)

# 1 seems to be Open!
# 0 is closed
# 2 is external

# %%

error = SpecDll.ShamrockSetShutter(0,c_int(0))


# 1 seems to be Open!
# 0 is closed
# 2 is external



# %%
port = c_int()
error = SpecDll.ShamrockGetPort(0,byref(port))
print(port.value)

# 0 seems to be Port 1
# 1 seems to be port 2

# %%

error = SpecDll.ShamrockSetPort(0,c_int(0))
print(error)



# %%
slit = c_float()
error = SpecDll.ShamrockGetSlit(0,byref(slit))
print(slit.value)

# float in micrometer!


# %%

error = SpecDll.ShamrockSetSlit(0,c_float(150))

# float in micrometer!
# Hello! Kate was here!



# %%
min_wl = c_float()
max_wl = c_float()
SpecDll.ShamrockGetWavelengthLimits(0,c_int(1),byref(min_wl),byref(max_wl))
print(min_wl.value, max_wl.value)
 
# %%
min_wl = c_float()
max_wl = c_float()
SpecDll.ShamrockGetCCDLimits(0,c_int(0),byref(min_wl),byref(max_wl))
print(min_wl.value, max_wl.value)

# %% Shutdown:
print("Shutting down Spectrometer")    
print(SpecDll.ShamrockClose())
for CamNumber in range(HowManyCams.value):
    Handle = c_long()
    CamDLL.GetCameraHandle(c_long(CamNumber),byref(Handle))
    CameraHandles.append(Handle)
    
    print('Shutting down Camera '+str(CamNumber+1))
    CamDLL.SetCurrentCamera(CameraHandles[CamNumber])
    CamDLL.ShutDown()
    
print("Both cameras shut down.")
    
    


