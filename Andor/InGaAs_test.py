# -*- coding: utf-8 -*-
"""
Created on Tue May 11 09:26:27 2021

@author: GloveBox
"""

import platform
from ctypes import *
from PIL import Image
import sys

import time
import threading
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import qApp, QCheckBox, QFileDialog, QSpinBox, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D, QIcon
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRect, QPoint
from PyQt5 import QtCore

class InGaAs():
    def close(self):
        self.CamDLL.ShutDown()      

    def __init__(self):
        self.CamDLL = WinDLL(r"C:\Users\GloveBox\Documents\Python Scripts\Andor\atmcd64d.dll")
        self.HowManyCams = c_long()
        self.CamDLL.GetAvailableCameras(byref(self.HowManyCams))
        print('Found '+str(self.HowManyCams.value)+' Cameras')
        self.CameraHandles = []
        
        for CamNumber in range(self.HowManyCams.value):
            Handle = c_long()
            self.CamDLL.GetCameraHandle(c_long(CamNumber), byref(Handle))
            self.CameraHandles.append(Handle)

            print('Starting Camera '+str(CamNumber+1))
            self.CamDLL.SetCurrentCamera(self.CameraHandles[CamNumber])
            tekst = c_char()  
            error = self.CamDLL.Initialize(byref(tekst))

            serial = c_int()
            self.CamDLL.GetCameraSerialNumber(byref(serial))
            print("Camera has serial number: "+str(serial.value))

            cw = c_int()
            ch = c_int()
            self.CamDLL.GetDetector(byref(cw), byref(ch))
            print("Camera has dimensions: " + str(cw.value) +" x " + str(ch.value))
            
            if cw.value == 512:
                self.ReadMode = 0 # Full vertial binning! 4 = full image
                self.AcquisitionMode = 1 # Single Scan
                self.CamDLL.SetAcquisitionMode(c_int(self.AcquisitionMode))
                self.CamDLL.SetReadMode(c_int(self.ReadMode)) # Full vertical binning!
                self.CamDLL.SetTemperature(c_int(-75))
                self.CamDLL.CoolerON()
                break
            else:
                print('Oops that was the CCD, swapping to the InGaAs now!')
            
            
    def toggleGain(self):
        gain = c_int()
        self.CamDLL.SetOutputAmplifier(byref(gain))
        if gain.value == 1:
            self.CamDLL.SetOutputGain(c_int(0))  ## High sensitivity
        else:
            self.CamDLL.SetOutputGain(c_int(1))  ## High Dynamic Range
            
        # if self.gainCheckbox.isChecked():
        #     self.CamDLL.SetHighCapacity(c_int(1))
        # else:
        #     self.CamDLL.SetHighCapacity(c_int(0))
            
        # self.CamDLL.SetHighCapacity(c_int(self.gainCheckbox.isChecked()))


    def setTemperature(self, value):
        self.CamDLL.SetTemperature(c_int(value))
        
    def setExposureTime(self, value):
        self.CamDLL.SetExposureTime(c_float(value))
        
    def toggleCooler(self):
        print("c1")

        iCoolerStatus = c_int()
        error = self.CamDLL.IsCoolerOn(byref(iCoolerStatus))
        print("c2")
        if iCoolerStatus.value != 0:
            self.CamDLL.CoolerOFF()
           # I am a little afraid of turning off the cooler, since I read on a different documentation, 
           # taht one can only turn of the Cooler,when the temperature is up to -20 deg C...
           # self.CamDLL.CoolerOFF()
           # self.StatusLabel2.setText("Cooler: OFF")
        else:
           self.CamDLL.CoolerON()
        
    def getSingleSpectrum(self):

        error = self.CamDLL.StartAcquisition()
        print("Spectrum wait for data")
        self.CamDLL.WaitForAcquisition()
        print("Spectrum data is here, waiting for dimension")
        cw = c_int()
        ch = c_int()
        self.CamDLL.GetDetector(byref(cw), byref(ch))
        
        if self.ReadMode == 0 and self.AcquisitionMode == 1 : # Full vertialb binning , single scan
            dim = int(cw.value)#*ch.value)
        elif self.ReadMode == 4 and self.AcquisitionMode == 1 :# full image, single scan
            dim = int(cw.value*ch.value)
        else:
            print("Sorry not implemented!!!!!! ")
            # return self.wl_calibration
        
        
        # print("Spectrum dimensions is here")
        cimageArray = c_int * dim
        cimage = cimageArray()
        error = self.CamDLL.GetAcquiredData(pointer(cimage),dim)
        # print("Spectrum got data")
        
        # print("Spectrum restructuring data")
        data = []
        for i in range(len(cimage)):
            data.append(cimage[i])
            
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(data)
        
        return data