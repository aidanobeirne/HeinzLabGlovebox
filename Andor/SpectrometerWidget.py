# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:37:53 2020

@author: marku
"""

from andor import *
import time
import sys
import threading
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import qApp, QCheckBox, QFileDialog, QSpinBox, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D, QIcon
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRect, QPoint
from PyQt5 import QtCore


class SpectrometerWidget(QWidget):
    def closeEvent(self, event):
        self.ThreadRunning = False
        self.Thread.join()    
        print('Spectrometer thread closed')
        self.cam.ShutDown()
        print('Spectrometer camera closed.')
        
        event.accept()
    
    
    def __init__(self):      
        super().__init__()
        basic_layout = QGridLayout()
        self.setLayout(basic_layout)
        
        self.SpectrometerGroupBox = QGroupBox("Spectrometer")
        layout = QGridLayout()
        
        print("Starting Andor")
        
        
        self.cam = Andor(1)
        self.cam.SetSingleScan()
        self.cam.SetShutter(1,1,0,0)
        self.cam.SetCoolerMode(1)
  
        layout.addWidget(QLabel("Temperature: "), 0, 0)
        self.TemperatureSpinBox = QSpinBox()
        self.TemperatureSpinBox.setRange(-95, 25)
        self.TemperatureSpinBox.setValue(-70)
        layout.addWidget(self.TemperatureSpinBox, 0, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(lambda : self.cam.SetTemperature(self.TemperatureSpinBox.value()))
        layout.addWidget(btn, 0, 2)
        self.cam.SetTemperature(-70)
    
        layout.addWidget(QLabel("EMCCD gain: "), 1, 0)
        self.EMCCDSpinBox = QSpinBox()
        self.EMCCDSpinBox.setRange(2, 300)
        self.EMCCDSpinBox.setValue(200)
        layout.addWidget(self.EMCCDSpinBox, 1, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(lambda : self.cam.SetEMCCDGain(self.EMCCDSpinBox.value()))
        layout.addWidget(btn, 1, 2)
        self.cam.SetEMCCDGain(200)
        
        layout.addWidget(QLabel("PreAmp gain: "), 2, 0)
        self.PreampComboBox = QComboBox()
        self.PreampComboBox.addItem("0",0)
        self.PreampComboBox.addItem("1",1)
        self.PreampComboBox.addItem("2",2)
        layout.addWidget(self.PreampComboBox, 2, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(lambda : self.cam.SetPreAmpGain(int(self.PreampComboBox.currentData())))
        layout.addWidget(btn, 2, 2)
        self.cam.SetPreAmpGain(0)
        
        layout.addWidget(QLabel("Trigger: "), 3, 0)
        self.TriggerComboBox = QComboBox()
        self.TriggerComboBox.addItem("Internal",0)
        self.TriggerComboBox.addItem("External",1)
        self.TriggerComboBox.addItem("Bulb",7)
        self.TriggerComboBox.addItem("Soft",10)
        self.TriggerComboBox.setCurrentIndex(2)
        layout.addWidget(self.TriggerComboBox, 3, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(lambda : self.cam.SetTriggerMode((int(self.TriggerComboBox.currentData()))))
        layout.addWidget(btn, 3, 2)
        self.cam.SetTriggerMode(7)
        
        
        layout.addWidget(QLabel("Exposure time: "), 4, 0)
        self.ExposureSpinBox = QDoubleSpinBox()
        self.ExposureSpinBox.setRange(0, 1000)
        self.ExposureSpinBox.setValue(0.1)
        layout.addWidget(self.ExposureSpinBox, 4, 1)
        btn = QPushButton("Set")
        btn.clicked.connect(lambda : self.cam.SetExposureTime(self.ExposureSpinBox.value()))
        layout.addWidget(btn, 4, 2)
        self.cam.SetExposureTime(0.1)
        
        self.StatusLabel1 = QLabel("Status: initializing")
        layout.addWidget(self.StatusLabel1, 5,0,1,3)
        
        self.StatusLabel2 = QLabel("Cooler: --")
        layout.addWidget(self.StatusLabel2, 6,0,1,3)
        if self.cam.IsCoolerOn():
            self.StatusLabel2.setText("Cooler: ON")
        else:
            self.StatusLabel2.setText("Cooler: OFF")
        
        btn = QPushButton("Enable Cooler")
        btn.clicked.connect(self.toggleCooler)
        layout.addWidget(btn, 7, 0)
        
        self.TakeSpectrumButton = QPushButton("Take Spectrum")
        self.TakeSpectrumButton.clicked.connect(self.takeSpectrum)
        layout.addWidget(self.TakeSpectrumButton, 7, 1,1,2)
        
        #Takebackground, normalize tobackground, continuousmode
        self.Background = []
        
        self.BackgroundEnabledCheckbox = QCheckBox('Enable BG')
        layout.addWidget(self.BackgroundEnabledCheckbox, 8, 0)
        self.TakeBackgroundButton = QPushButton("Take Background")
        self.TakeBackgroundButton.clicked.connect(self.takeBackground)
        layout.addWidget(self.TakeBackgroundButton, 8, 1,1,2)
        
        self.ContinousModeEnabledCheckbox = QCheckBox('Continuous mode')
        layout.addWidget(self.ContinousModeEnabledCheckbox, 9, 0)
        self.LatestContinousSpectrum = []
        self.ContinousMode = False
        
        self.ThreadLock = threading.Lock()
        self.ThreadRunning = True
        self.Thread = threading.Thread(target=self.threadingFunction)
        self.Thread.start()
        
        
        self.SpectrometerGroupBox.setLayout(layout)
        basic_layout.addWidget(self.SpectrometerGroupBox,  0,0)
        
        print("Andor started")
        
    def threadingFunction(self):
        while self.ThreadRunning:
             
            self.ThreadLock.acquire()
            self.StatusLabel1.setText("Status: "+self.cam.GetTemperature()+" Temp: "+str(self.cam.temperature))
            if self.cam.IsCoolerOn():
                self.StatusLabel2.setText("Cooler: ON")
            else:
                self.StatusLabel2.setText("Cooler: OFF")
            self.ThreadLock.release()
            
            if self.ContinousModeEnabledCheckbox.isChecked():
                self.ContinousMode = True
                self.LatestContinousSpectrum = self.takeSpectrum()
            else:
                self.ContinousMode = False
                time.sleep(1) 
        
    def toggleCooler(self):
        self.ThreadLock.acquire()
        if self.cam.IsCoolerOn():
            pass
           # I am a little afraid of turning off the cooler, since I read on a different documentation, 
           # taht one can only turn of the Cooler,when the temperature is up to -20 deg C...
           # self.cam.CoolerOFF()
           # self.StatusLabel2.setText("Cooler: OFF")
        else:
           self.cam.CoolerON()
           self.StatusLabel2.setText("Cooler: ON")
        self.ThreadLock.release()
   
    def takeSpectrum(self):
        self.ThreadLock.acquire()
        self.cam.StartAcquisition()
        data = []
        self.cam.GetAcquiredData(data)
        self.ThreadLock.release()
        data = np.array(data)
        if self.BackgroundEnabledCheckbox.isChecked():
            data = data - self.Background

        return data
     
    def takeBackground(self):
        self.ThreadLock.acquire()
        self.cam.StartAcquisition()
        data = []
        self.cam.GetAcquiredData(data)
        self.ThreadLock.release()
        self.Background = np.array(data)
        
if __name__ == '__main__':
    
    app = QApplication([])
    
    MainWindow = SpectrometerWidget()
    MainWindow.show()
    sys.exit(app.exec_())