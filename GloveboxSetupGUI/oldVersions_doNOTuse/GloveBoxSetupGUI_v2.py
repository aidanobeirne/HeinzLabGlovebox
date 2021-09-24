# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:07:18 2020

@author: Markus A. Huber
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import datetime
import sys
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\PS4Controller')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ThorlabsStages')

#sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\GrasshoperCamera3')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ThorlabsCamera')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ICMeasureCamera')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\MCMStage')

sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ElliptecMotor')



import ThorlabsStages
import MCMStage
import PS4Controller
#import Grasshopper3Cam


#-------------------------
#Aidans ugly fix of the problem
#sys.path.append(r'C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Interfaces\SDK\Python Compact Scientific Camera Toolkit\examples')

#from polling_example import *
#-------------------------    

import ThorlabsCamera



# ----------------------------------
# really nasty workaround / I don't like it but I found no other easz fix
import os
directory = os.getcwd()
os.chdir(r'C:\Users\Heinz Group\Documents\Python Scripts\ICMeasureCamera')
import ICMeasureCamera
os.chdir(directory)
# ----------------------------------


import ElliptecMotor
import time

import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import threading

from PyQt5.QtWidgets import qApp, QCheckBox, QFileDialog, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRect, QPoint

import cv2
from scipy.ndimage.filters import median_filter
import numpy as np

class GloveBoxSetupWindow(QWidget):

    def eventLoop(self):
        self.Controller.doEvents()
        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)
                
            else:
                image = self.Camera.getImageAsNumpyArray().T
                
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)
        else:
            image = self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2)
            
        #self.ROI.setPen((125,125,125))
        
        self.XYSpeed.setValue(self.SpeedModifier)    
        self.XPositionLabel.setText(str(self.Stage.getXPosition()))
        self.YPositionLabel.setText(str(self.Stage.getYPosition()))
        self.ZPositionLabel.setText(str(self.ZStage.getVoltage()))
        
    
            
        self.ImageView.setImage(image)
    
    def isImageInteresting(self, CurrentImage, enableSelectedFilters=True):
        image = CurrentImage
        if enableSelectedFilters:
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(image,5)         
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)  
                
        ROIData = self.ROI.getArrayRegion(image, self.ImageView.imageItem)
        AmountOfInterestingPixels = np.sum(ROIData > self.GrayScaleThresholdLine.value())      
        return AmountOfInterestingPixels > self.InterestingnessThresholdLine.value() 
        
    
    def threadingFunction(self):
        while self.ThreadRunning:
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)
                
            else:
                image = self.Camera.getImageAsNumpyArray().T
                
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)
                
            ROIData = self.ROI.getArrayRegion(image, self.ImageView.imageItem)
                
                
            #hist, pos = np.histogram(ROIData, bins=100)
            #self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
            AmountOfInterestingPixels = np.sum(ROIData > self.GrayScaleThresholdLine.value())
            
            if AmountOfInterestingPixels > self.InterestingnessThresholdLine.value() :
                self.ROI.setPen((0,255,0))
            else:
                self.ROI.setPen((255,0,0))
                
            if self.imageProcessingEnabled.isChecked():
                # Median filtering
                gray_image_mf = median_filter(ROIData, 1)
                # Calculate the Laplacian
                lap = cv2.Laplacian(gray_image_mf,cv2.CV_64F, ksize = 31)
                self.LaplacianVarArray.append(lap.var()) 
                
                
                if len(self.LaplacianVarArray) > 50:
                    self.LaplacianVarArray.pop(0)
                
                #self.LaplacianVarPlot.clear()
                
                self.LaplacianVarPlot.setData(self.LaplacianVarArray, pen=(255,0,0))
                
                
                hist, pos = np.histogram(ROIData, bins=100)
                self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
                
                self.InterestingnessArray.append(AmountOfInterestingPixels)
                
                if len(self.InterestingnessArray) > 50:
                    self.InterestingnessArray.pop(0)
                    
                self.InterestingnessPlot.setData(self.InterestingnessArray, pen=(0,0,255))
            
                
        
            
        
    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        print("Closing Controller")
        self.Controller.closeController()
        self.ThreadRunning = False
#        print("stopping Thread")
#        self.Thread.join()
        print("Stopped Thread")
        print("Closing peripheral devices")
        self.timer.stop()
        print("Closing Monochrom Camera")
        self.Camera.endImageAcquisition()
        self.Camera.close()
        print("Closing Color Camera")
        self.WhiteLightCamera.endImageAcquisition()
        self.WhiteLightCamera.close()

        print('Closing Slider Whitelight-Bluelight')
        self.WhiteLightBlueLightSlider.close()
        print("Closing XYStage")
        self.Stage.close()
        print("Closing ZStage")
        self.ZStage.close()
        print("Closing Coarse Position Stage")
        self.MCMStage.close()
        print("Closing finished successfully")
        event.accept()
        
    def setPointOnPlane(self, PointNumber, xCoord, yCoord, zCoord):
        print(self.PointsOnPlane)
        self.PointsOnPlane[PointNumber] = QVector3D(xCoord, yCoord, zCoord)
        print(PointNumber)
        print(xCoord)
        if type(self.PointsOnPlane[0]) == QVector3D and type(self.PointsOnPlane[1]) == QVector3D:
            self.currentDirection = 1
            self.EdgePoints2DScan[0] = QVector3D(np.min([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x()]), np.min([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y()]),0)
            self.EdgePoints2DScan[1] = QVector3D(np.max([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x()]), np.max([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y()]),0)
            self.currentPosition = self.EdgePoints2DScan[0]
            self.currentPosition.setZ(zCoord)
        if type(self.PointsOnPlane[0]) == QVector3D and type(self.PointsOnPlane[1]) == QVector3D and type(self.PointsOnPlane[2]) == QVector3D:
            n = QVector3D.crossProduct(self.PointsOnPlane[1]-self.PointsOnPlane[0],self.PointsOnPlane[2]-self.PointsOnPlane[0])
            s = self.PointsOnPlane[0]
            self.PlaneEquationGetZFromXandY = lambda x,y : (-n.x()*(x - s.x()) - n.y()*(y - s.y()) )/n.z() + s.z() 
            self.EdgePoints2DScan[0] = QVector3D(np.min([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.min([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.EdgePoints2DScan[1] = QVector3D(np.max([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.max([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.currentPosition = self.EdgePoints2DScan[0]
            self.currentPosition.setZ(self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y()))
            # %%
 #HERE IS WHERE I HAVE TO CONTINUE
    def rasterScanProcedurally(self):
        self.Controller.disableAxes()
        path = "C:\\Users\\Heinz Group\\Desktop\\GrasshopperImages\\"
        file = str(QFileDialog.getExistingDirectory(self, "Select Save Directory"))
        if file != '':
            path = file +'/'
            
        Scanning = True
        while Scanning:
            self.Stage.moveXTo(self.currentPosition.x())
            self.Stage.moveYTo(self.currentPosition.y())
            self.ZStage.setPosition(self.currentPosition.z())
            
            #jump to next position if image is not interesting
            if self.isImageInteresting(self.Camera.getImageAsNumpyArray().T, enableSelectedFilters=True):        
                _filename = path + 'Scan_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getPosition()).replace('.','p') + '.jpg'
                print(_filename)
                self.Camera.saveImageAsJpg(filename=_filename)
            
            self.currentPosition = self.currentPosition + QVector3D(self.XStepSize.value()*self.currentDirection, 0, 0)
            print(self.currentPosition)
            height = self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y())
            if height != None:
                self.currentPosition.setZ(height)
            
            if self.currentPosition.x() >= self.EdgePoints2DScan[1].x() or self.currentPosition.x() <= self.EdgePoints2DScan[0].x():
                self.Stage.moveXTo(self.currentPosition.x())
                self.Stage.moveYTo(self.currentPosition.y())
                self.ZStage.setPosition(self.currentPosition.z())
                
                if self.isImageInteresting(self.Camera.getImageAsNumpyArray().T, enableSelectedFilters=True):     
                    _filename = path + 'Scan_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getPosition()).replace('.','p') + '.jpg'
                    print(_filename)
                    self.Camera.saveImageAsJpg(filename=_filename)
                
                self.currentPosition = self.currentPosition + QVector3D(0, self.YStepSize.value(), 0)
                self.currentDirection *= -1
                
            if self.currentPosition.y() >= self.EdgePoints2DScan[1].y():
                Scanning = False
                    
            #QApplication.processEvents()
        print('Scan complete')
        self.Controller.enableAxes()   
    # %%
    def __init__(self):      
        super().__init__()
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        self.setWindowTitle('glOVER - BP Awesomeness with Python')
        
        self.ImageView = pg.ImageView()#levelMode='mono')
        
        self.ROI = pg.ROI((20,20),(100,100))
        self.ROI.addScaleHandle((1,1),(0,0))
        self.ImageView.addItem(self.ROI)
        
        #self.ImageView.setFixedWidth(1500)
        grid_layout.addWidget(self.ImageView, 0, 0, 8, 8)
        grid_layout.setColumnStretch(0,2147483647)
        
        self.PointsOnPlane = [object,object,object]
        self.EdgePoints2DScan = [object,object]
        self.PlaneEquationGetZFromXandY = lambda x,y : None
        
        self.SpeedModifier = 10.0
        self.XYSpeed = QProgressBar(self)
        self.XYSpeed.setMaximum( 100)
        self.XYSpeed.setValue( self.SpeedModifier)
        #self.progress.setGeometry(200, 80, 250, 20)
        grid_layout.addWidget(self.XYSpeed, 0, 10)
        
        grid_layout.addWidget(QLabel("XY Speed: "), 0, 9)
        
        #TODO : Put this into a groupbox - just because it looks better
        
        self.horizontalGroupBox = QGroupBox("Stage Position")
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        
        self.XPositionLabel = QLabel("--")
        self.YPositionLabel = QLabel("--")
        self.ZPositionLabel = QLabel("--")
          
        layout.addWidget(self.XPositionLabel, 0, 1)
        layout.addWidget(QLabel("X: "), 0, 0)
        layout.addWidget(self.YPositionLabel, 1, 1)
        layout.addWidget(QLabel("Y: "), 1, 0)
        layout.addWidget(self.ZPositionLabel, 2, 1)
        layout.addWidget(QLabel("Z: "), 2, 0)
         #layout.addStretch(1)
        self.horizontalGroupBox.setLayout(layout)
        grid_layout.addWidget(self.horizontalGroupBox, 1, 9)
        
   
        grid_layout.addWidget(QLabel("X step size: "), 6, 9)
        self.XStepSize = QDoubleSpinBox()
        self.XStepSize.setValue(0.3)
        grid_layout.addWidget(self.XStepSize, 6, 10)
        
        grid_layout.addWidget(QLabel("Y step size: "), 7 , 9)
        self.YStepSize = QDoubleSpinBox()
        self.YStepSize.setValue(0.3)
        grid_layout.addWidget(self.YStepSize, 7, 10)
        
        self.Stage = ThorlabsStages.Thorlabs2DStageKinesis(SN_motor = '73126054')
        print('asdasd')
        self.ZStage = ThorlabsStages.Thorlabs1DPiezoKinesis(SN_piezo = '41106464')
        print('fff')
#        self.ZStage = ThorlabsStages.Thorlabs1DPiezoDummy()
        self.WhiteLightBlueLightSlider = ElliptecMotor.ElliptecMotor("COM3")
        self.WhiteLightBlueLightSlider.moveHome()
        
        self.Controller = PS4Controller.PS4Controller()
        print("jkjhk")
#        self.Camera = Grasshopper3Cam.Grasshopper3Cam()
        self.Camera = []#ThorlabsCamera.ThorlabsCam()
        print("jkjhkljkhlkjj")
        self.WhiteLightCamera = ICMeasureCamera.ICMeasureCam()
        print("jkjhk 6655+6465165")
        self.MCMStage = MCMStage.MCMStage()
        
        self.Controller.AxisFunctions[0] = lambda AxisValue :  self.Stage.moveXTo(self.Stage.getXPosition() - AxisValue*0.1*self.SpeedModifier/10)
        self.Controller.AxisFunctions[1] = lambda AxisValue :  self.Stage.moveYTo(self.Stage.getYPosition() + AxisValue*0.1*self.SpeedModifier/10)
        self.Controller.AxisFunctions[2] = lambda AxisValue :  self.modifySpeed(AxisValue)
        self.Controller.AxisFunctions[3] = lambda AxisValue : self.ZStage.setVoltage(self.ZStage.getVoltage() - AxisValue*0.1*self.SpeedModifier/10)
        
        self.Controller.ButtonFunctions[1] = self.capture
        self.Controller.ButtonFunctions[0] = self.move2#lambda x : self.moveSlider(0)
        self.Controller.ButtonFunctions[3] = self.move0#lambda x : self.moveSlider(1)
        self.Controller.ButtonFunctions[2] = self.move2#lambda x : self.moveSlider(2)
        self.Controller.ButtonFunctions[7] = self.close
        
        self.Controller.ButtonFunctions[4] = lambda: self.MCMStage.setPosition(self.MCMStage.getPosition() - 10000 )
        self.Controller.ButtonFunctions[5] = lambda: self.MCMStage.setPosition(self.MCMStage.getPosition() + 10000 )
        
        self.ScanRunning2D = False
        self.currentPosition = QPoint(-1,-1)
        self.currentDirection = 1
        
        #self.Camera.startImageAcquisition()
        self.WhiteLightCamera.startImageAcquisition()
        
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()
        
        button = QPushButton('Set top left corner')
        grid_layout.addWidget(button, 2, 9, 1, 1)
        button.clicked.connect(lambda _ : self.setPointOnPlane(0, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getPosition()))
        
        checkbox = QCheckBox('invert X')
        grid_layout.addWidget(checkbox, 9, 9, 1, 1)
        checkbox.stateChanged.connect(self.checkboxchanged)
        
        
        button = QPushButton('Set bottom right corner')
        grid_layout.addWidget(button, 3, 9, 1, 1)
        button.clicked.connect(lambda _ : self.setPointOnPlane(1, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getPosition()))
        
        button = QPushButton('Set additional point on plane')
        grid_layout.addWidget(button, 4, 9, 1, 1)
        button.clicked.connect(lambda _ : self.setPointOnPlane(2, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getPosition()))
        
        button = QPushButton('Run scan')
        grid_layout.addWidget(button, 5, 9, 1, 1)
        button.clicked.connect(self.rasterScanProcedurally)
        
        
        self.imageProcessingEnabled = QCheckBox('do ImageProcessing')
        grid_layout.addWidget(self.imageProcessingEnabled, 0, 11, 1, 1)
        
        self.LaplacianGraph = pg.GraphicsWindow(title="Laplacian")
#        grid_layout.addWidget(self.LaplacianGraph, 1, 11, 3, 1)
        
        plotWindow1 = self.LaplacianGraph.addPlot(title="Laplacian Variance ~ Focussing")
        self.LaplacianVarPlot = plotWindow1.plot([0,0,0])
        
        self.LaplacianVarArray = []
        
        self.LaplacianGraph.nextRow()
        plotWindow2 = self.LaplacianGraph.addPlot(title="Color Distribution")
        self.DistributionAndThresholdPlot = plotWindow2.plot([0,0,0])
        
        self.GrayScaleThresholdLine = pg.InfiniteLine(pos=40, angle=90, movable=True, pen=(255,0,0)) 
        plotWindow2.addItem(self.GrayScaleThresholdLine)
        
        plotWindow3 = self.LaplacianGraph.addPlot(title="Amount of Interestingness")
        self.InterestingnessPlot = plotWindow3.plot([0,0,0])
        
        plotWindow3.addItem(self.InterestingnessPlot)
        
        self.InterestingnessThresholdLine = pg.InfiniteLine(pos=40, angle=0, movable=True, pen=(0,0,255)) 
        plotWindow3.addItem(self.InterestingnessThresholdLine)
        self.InterestingnessArray = []

        
        self.LaplacianSharpnessSlider = QSlider()
        self.LaplacianSharpnessSlider.setRange(0, 100)
        self.LaplacianSharpnessSlider.setValue(0)
        grid_layout.addWidget(self.LaplacianSharpnessSlider, 1, 12, 3, 1)
        
        self.MedianEnableBlur = QCheckBox('Blur')
        grid_layout.addWidget(self.MedianEnableBlur, 0, 12, 1, 1)
        
        self.GaussianEnableBlur = QCheckBox('Gaussian')
        grid_layout.addWidget(self.GaussianEnableBlur, 0, 13, 1, 1)
        
        self.WhiteLightBlueLightSliderComboBox = QComboBox()
        self.WhiteLightBlueLightSliderComboBox.addItem("0")
        self.WhiteLightBlueLightSliderComboBox.addItem("1")
        self.WhiteLightBlueLightSliderComboBox.addItem("2")
        self.WhiteLightBlueLightSliderComboBox.addItem("3")
        self.WhiteLightBlueLightSliderComboBox.currentIndexChanged.connect(lambda x : self.WhiteLightBlueLightSlider.moveToPosition(x) )
        grid_layout.addWidget(self.WhiteLightBlueLightSliderComboBox, 7, 12, 1, 2)
        
        self.ICCameraSettings = QPushButton("IC MEasure settings")
        self.ICCameraSettings.clicked.connect(self.ICCameraSetProperties)
        grid_layout.addWidget(self.ICCameraSettings, 6, 12, 1, 2)
        
        self.SliderReset = QPushButton("Reset frozen slider")
        self.SliderReset.clicked.connect(self.sliderReset)
        grid_layout.addWidget(self.SliderReset, 5, 12, 1, 2)
        
        btn = QPushButton("Home X,Y")
        btn.clicked.connect(self.Stage.home)
        grid_layout.addWidget(btn, 4, 12, 1, 2)
        
        
        self.showMaximized()
        
#        self.ThreadRunning = True
#        self.Thread = threading.Thread(target=self.threadingFunction)
#        self.Thread.start()
        
    def ICCameraSetProperties(self):
        pass
#        x = threading.Thread(target = self.WhiteLightCamera.showCameraProperties )
#        x.start()
        
        
    def sliderReset(self):
        self.WhiteLightBlueLightSlider.close()
        self.WhiteLightBlueLightSlider = ElliptecMotor.ElliptecMotor("COM3")
        self.WhiteLightBlueLightSlider.moveHome()
        
#        self.EventLoop = True
#
#    def closeEverything(self):
#        self.EventLoop = False
    def moveSlider(self, position):
#        self.WhiteLightBlueLightSlider.close()
#        self.WhiteLightBlueLightSlider = ElliptecMotor.ElliptecMotor("COM3")
        print(position)
        self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(position)
        self.WhiteLightBlueLightSliderComboBox.update()
        QApplication.processEvents()
        time.sleep(0.02)
        QApplication.processEvents()
        
    def move2(self):
        self.moveSlider(2)

    def move0(self):
        self.moveSlider(0)
        
    def capture(self):
        path = "C:\\Users\\Heinz Group\\Desktop\\GloveboxMicroscopeImages\\"
        
        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            _filename = path + str(datetime.datetime.now()).replace(':','-').replace('.','-').replace(' ','_') + '_Fluorescence.jpg'
            self.Camera.saveImageAsJpg(filename=_filename)
        else:
            _filename = path + str(datetime.datetime.now()).replace(':','-').replace('.','-').replace(' ','_') + '_WhiteLight.jpg'
            self.WhiteLightCamera.saveImageAsJpg(filename=_filename)
    
    def checkboxchanged(self, cb):
        if cb != 0:
            self.Controller.AxisFunctions[0] = lambda AxisValue :  self.Stage.moveXTo(self.Stage.getXPosition() + AxisValue*0.1*self.SpeedModifier/10)  
            self.MoveThreshold = 0.3
        else:
            self.Controller.AxisFunctions[0] = lambda AxisValue :  self.Stage.moveXTo(self.Stage.getXPosition() - AxisValue*0.1*self.SpeedModifier/10)
            
        
    def modifySpeed(self,AxisValue):
        self.SpeedModifier
        self.SpeedModifier -= AxisValue
        if self.SpeedModifier > 100:
            self.SpeedModifier = 100
        if self.SpeedModifier < 1:
            self.SpeedModifier = 1
        #print(self.SpeedModifier)
   
        # set the layout
     
# %%

if __name__ == '__main__':
    
    #app = QApplication([])
    MainWindow = GloveBoxSetupWindow()
    MainWindow.show()
    #sys.exit(app.exec_())