# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:02:53 2020

@author: GloveBox
"""


import platform
from ctypes import *
from PIL import Image
import sys

dll = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atmcd64d.dll")




# %%
HowManyCams = c_long()
dll.GetAvailableCameras(byref(HowManyCams))

CameraHandles = []

for CamNumber in range(HowManyCams.value):
    Handle = c_long()
    dll.GetCameraHandle(c_long(CamNumber),byref(Handle))
    CameraHandles.append(Handle)
    
print(CameraHandles)
    
# %%
WhichCamera= 1 # 0 or 1  
  
dll.SetCurrentCamera(CameraHandles[WhichCamera])
#%%

tekst = c_char()  
error = dll.Initialize(byref(tekst))
print(tekst)


# %%
serial = c_int()
dll.GetCameraSerialNumber(byref(serial))

print(serial.value)
# %%
cw = c_int()
ch = c_int()
dll.GetDetector(byref(cw), byref(ch))
print(cw.value, ch.value)

# %%
wave = c_float()
dll.GetWavelength(byref(wave))

print(wave.value)


# %% Wait until BOTH!!! Cameras are at -20 before closing!!
dll.ShutDown()



# %%

# %% seems to work any time

CurrentCameraHandle = c_long()
dll.GetCurrentCamera(byref(CurrentCameraHandle))
print(CurrentCameraHandle.value)


# %% NOw start with spectrometer
SpecDll = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atspectrograph.dll")

# %%

tekst = c_char()        
error = SpecDll.ShamrockInitialize(byref(tekst))



# %%
Num = c_int()
print(SpecDll.ShamrockGetNumberDevices(byref(Num)))
print(Num)

# %%

Num = c_float()
print(SpecDll.ShamrockGetWavelength(0, byref(Num)))
print(Num)

# %%

Num = c_float(1490)
print(SpecDll.ShamrockSetWavelength(0, byref(Num)))
print(Num)



# %%

print(SpecDll.ShamrockClose())