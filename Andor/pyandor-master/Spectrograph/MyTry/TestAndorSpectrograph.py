# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 19:06:47 2020

@author: GloveBox
"""
# %%

import platform
from ctypes import *
from PIL import Image
import sys

dll = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\pyandor-master\Spectrograph\MyTry\atspectrograph.dll")

# %%
tekst = c_char()        
error = dll.ATSpectrographInitialize(byref(tekst))



# %%
Num = c_int()
print(dll.ATSpectrographGetNumberDevices(byref(Num)))
print(Num)

# %%

Num = c_int()
print(dll.ATSpectrographGetWavelength(byref(Num)))
print(Num)

# %%

Num = c_double(1000)
print(dll.ATSpectrographSetWavelength(byref(Num)))
print(Num)



# %%

print(dll.ATSpectrographClose())
