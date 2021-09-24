# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:07:18 2020

@author: Markus A. Huber
"""

#objective 4.8 mm for a roundtrip
# --> 4.8/5 = 0.96 mm between objectives ( G21G91G1X0.96F25 )

# 12 threshold - 100 cts : WSe2 on SiO2 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import ctypes
myappid = u'HeinzLab.PythonScripts.GloveBoxSetup.v1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
import datetime
import time
import sys
import os
import os.path
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PS4Controller')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
#sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrasshoperCamera3')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsCamera')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ICMeasureCamera')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\MCMStage')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrblRotationStation')
#sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ArduinoController')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ElliptecMotor')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Andor')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI')
import pickle
import glob
import ThorlabsStages
import MCMStage
import PS4Controller
#import ArduinoController
#import Grasshopper3Cam
from matplotlib.image import imread
import matplotlib
from PIL import ImageTk, Image

import ArduinoRotationStage
import AdvancedSpectrometerWidget
import PLMapGUI

import ElliptecMotor
import time
import pyqtgraph as pg
from pyqtgraph.dockarea import *
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
import threading
from PyQt5.QtWidgets import qApp, QCheckBox, QSpinBox, QFileDialog, QSplitter, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit, QInputDialog
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D, QMessageBox, QIcon, QMainWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QRect, QPoint
from PyQt5 import QtCore
import cv2
from scipy.ndimage.filters import median_filter
import numpy as np
from multiprocessing import Process, Queue
print("Done importing most modules")


def Subprocess_Function(queue):
    print("Start subproces for PL Map")
    app2 = QApplication(sys.argv)
    window = PLMapGUI.PLMapGUI(queue)
    window.show()
    app2.exec_()
    print("PL Map Subprocess ended")
    # print('trying to stop process')
    # PLMapSubprocess.join()
    # print('killed and ate zombie process')

PLMapSubprocessQueue = Queue()
PLMapSubprocess = Process(target=Subprocess_Function, args=(PLMapSubprocessQueue,))

class GloveBoxSetupWindow(QMainWindow):
    
    def eventLoop(self):
        
        if self.RCBModeOn :
            self.counter += 2
            self.ImageView.setImage(self.RCBImg)
            self.ImageView.imageItem.setTransform(self.ImageView.imageItem.dataTransform().rotate(self.counter))
            self.ImageView.autoRange()
            return
        
        
        self.Controller.doEvents()
        imageWL = []
        image = []
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)
                
            else:
                image = self.Camera.getImageAsNumpyArray().T
                
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)
        else:
            imageWL = np.flip(self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2),0)
            # imageWL = self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2)
        
        self.XYSpeed.setValue(self.SpeedModifier)
        self.ZSpeed.setValue(self.SpeedModifierFocus)
        self.XPositionLabel.setText(str(np.round(self.Stage.getXPosition(),4)))
        self.YPositionLabel.setText(str(np.round(self.Stage.getYPosition(),4)))
        self.ZPositionLabel.setText(str(np.round(self.ZStage.getVoltage() ,4)))
        
        self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.lastCorrectPosition* 0.2116667 /1000.0,4)))
        # self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.getPositionInMM(),4)))
        self.LinPolLabel.setText(str(np.round(self.LinearPolarizer.getRotation(),4)))
        self.HWPLabel.setText(str(np.round(self.HalfWavePlate.getRotation(),4)))
 

        if self.WhiteLightBlueLightSliderComboBox.currentIndex():
            if len(image) > 0:
                self.ImageView.setImage(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoRange = False, autoHistogramRange=False)
                if self.ROIColorCheckEnabled.isChecked():
                    if self.isImageInteresting(image):
                        self.ROI.setPen((0,255,0))
                    else:
                        self.ROI.setPen((255,0,0))
                else:
                    self.ROI.setPen((125,125,125))
        else:
            self.ROI.setPen((125,125,125))
            if len(imageWL) > 0:
                self.ImageView.setImage(imageWL, autoLevels=False, levels=(self.ColorScaleMin.value(), self.ColorScaleMax.value()), autoRange = False, autoHistogramRange=False)
        
        
        
        if self.SpectrometerWidget.SpectrometerWidget != None:        
            if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                self.SpecPlot.setData(  self.SpectrometerWidget.SpectrometerWidget.wl_calibration , self.SpectrometerWidget.SpectrometerWidget.LatestContinousSpectrum, pen=(0,0,255))

        
    
    def isImageInteresting(self, CurrentImage, enableSelectedFilters=True):
        image = CurrentImage
        if enableSelectedFilters:
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(image,5)         
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)  
        p = self.ROI.pos()
        s = self.ROI.size()
        ImageSize = np.shape(image)
        for i in (0,1):
            if p[i] < 0:
                p[i] = 0
            if p[i]+s[i] > ImageSize[i]:
                s[i] = ImageSize[i] - p[i]
                
        ROIData = image[int(p[0]):int(p[0]+s[0]),int(p[1]):int(p[1]+s[1])]
        self.ThreadLock.acquire()
        self.savedROIData = ROIData
        self.ThreadLock.release()
        AmountOfInterestingPixels = np.sum(ROIData > self.GrayScaleThresholdLine.value())      
        return AmountOfInterestingPixels > self.InterestingnessThresholdLine.value() 
    
    def threadingFunction(self):
        while self.ThreadRunning:
            time.sleep(0.05)  
            if self.imageProcessingEnabled.isChecked():
                if not self.ROIColorCheckEnabled.isChecked():
                    self.ROIColorCheckEnabled.setChecked(True)
                
                self.ThreadLock.acquire()
                hist, pos = np.histogram(self.savedROIData, bins=100)
                self.ThreadLock.release()
                
                self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
                AmountOfInterestingPixels = np.sum(self.savedROIData > self.GrayScaleThresholdLine.value())
                self.InterestingnessArray.append(AmountOfInterestingPixels)
                
                if len(self.InterestingnessArray) > 50:
                    self.InterestingnessArray.pop(0)
                    
                self.InterestingnessPlot.setData(self.InterestingnessArray, pen=(0,0,255))
                self.InterestingnessPlotWindowItem.setXRange(0,50, padding = 0)
                           
        
    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        print("Stopping event loop")
        self.timer.stop()
        
        # Test 1
        # self.timerController.stop()
        
        
        
        self.ThreadRunning = False
        print("stopping Thread")
        self.Thread.join()    
        
        #Test 2
        #self.ControllerThread.join()
            
        print("Stopped Thread")
        print("Closing Controller")
        self.Controller.closeController()
        print("Closing peripheral devices")   
        print("Closing Monochrom Camera")
        self.Camera.endImageAcquisition()
        self.Camera.close()
        print("Closing Color Camera")
        self.WhiteLightCamera.endImageAcquisition()
        self.WhiteLightCamera.close()
        print('Closing Slider Whitelight-Bluelight')

        print("Closing XYStage")
        self.Stage.close()
        print('Closing Arduino Rotation Stage')
        self.Arduino.close()
        print("Closing Coarse Position Stage")
        self.MCMStage.close()
        print("Closed Coarse Position Stage")
        
        self.Shutter.flipperOff()
        self.Shutter.close()
        print("Shutter disconnected")
        
        self.LinearPolarizer.close()
        print("Linear polarizer closed")
        
        self.HalfWavePlate.close()
        print("HWP closed")
    
        print("Closing ZStage")
        self.ZStage.close()
        
        print("Closing Andor")
        self.SpectrometerWidget.close()
        print("Andor closed")
        
        time.sleep(0.2)
        print("Save GUI state")
        self.saveStateOnClosing()
        time.sleep(0.2)
        print("Closing finished successfully - Program quits in 1 second!")
        time.sleep(1)
        print("Program exited!")
        event.accept()
        app.quit()
        
                    # %%
        
    def setPointOnPlane(self, PointNumber, xCoord, yCoord, zCoord):
        print(self.PointsOnPlane)
        self.PointsOnPlane[PointNumber] = QVector3D(xCoord, yCoord, zCoord)
        self.saveCurrentPositionAsCorner(str(PointNumber))
        
        self.BottomRight.setText('Set bottom right corner')
        self.Additional.setText('Set additional point on plane')
        self.TopLeft.setText('Set top left corner')
        
        if type(self.PointsOnPlane[0]) == QVector3D:
            self.TopLeft.setText('Top left [SET]')
        
        if type(self.PointsOnPlane[0]) == QVector3D and type(self.PointsOnPlane[1]) == QVector3D:
            self.currentDirection = 1
            self.EdgePoints2DScan[0] = QVector3D(np.min([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x()]), np.min([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y()]),0)
            self.EdgePoints2DScan[1] = QVector3D(np.max([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x()]), np.max([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y()]),0)
            self.currentPosition = self.EdgePoints2DScan[0]
            self.currentPosition.setZ(zCoord)
            self.TopLeft.setText('Top left [SET]')
            self.BottomRight.setText('Bottom right [SET]')
            
        if type(self.PointsOnPlane[0]) == QVector3D and type(self.PointsOnPlane[1]) == QVector3D and type(self.PointsOnPlane[2]) == QVector3D:
            n = QVector3D.crossProduct(self.PointsOnPlane[1]-self.PointsOnPlane[0],self.PointsOnPlane[2]-self.PointsOnPlane[0])
            s = self.PointsOnPlane[0]
            self.PlaneEquationGetZFromXandY = lambda x,y : (-n.x()*(x - s.x()) - n.y()*(y - s.y()) )/n.z() + s.z() 
            self.EdgePoints2DScan[0] = QVector3D(np.min([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.min([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.EdgePoints2DScan[1] = QVector3D(np.max([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.max([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.currentPosition = self.EdgePoints2DScan[0]
            self.currentPosition.setZ(self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y()))
            self.TopLeft.setText('Top left [SET]')
            self.BottomRight.setText('Bottom right [SET]')
            self.Additional.setText('Additional [SET]')
            
        if type(self.PointsOnPlane[0]) == QVector3D and type(self.PointsOnPlane[2]) == QVector3D:
            self.TopLeft.setText('Top left [SET]')
            self.Additional.setText('Additional [SET]')
            
        if type(self.PointsOnPlane[1]) == QVector3D and type(self.PointsOnPlane[2]) == QVector3D:
            self.BottomRight.setText('Bottom right [SET]')
            self.Additional.setText('Additional [SET]')
            
 
    def rasterScanProcedurally(self):
        self.Controller.disableAxes()
        self.currentDirection = 1
        saveCurrentPositionFromBeforeScanToResetAfterwards = self.currentPosition
        path = r"C:\Users\GloveBox\Documents\Python Scripts\ScanImages/"
        StartTime = time.time()
        StartTimeFull = datetime.datetime.now()
        path = path + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S')
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of directory %s failed" % path)
            return
        else:
            print ("Successfully created directory %s " % path)
        path = path + "/"
       
        #Save corners
        data_obj = {}
        data_obj['PointsOnPlane'] = self.PointsOnPlane
        data_obj['EdgePoints2DScan'] = self.EdgePoints2DScan 
        print("Save corners: ", data_obj)
        
        with open(path+"CornerInfo.pickle", 'wb') as f:
            pickle.dump(data_obj, f)
        
        self.stopRunningScan.setChecked(False)
        self.stopRunningScan.show()
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() != 2:
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(2)
            self.update()
            QApplication.processEvents()
            time.sleep(2)
            self.update()
            QApplication.processEvents()
        Scanning = True
        print("Getting exposure time...")
        wait = self.Camera.getExposureTime()
        print(wait)
        Difference = self.EdgePoints2DScan[1] - self.EdgePoints2DScan[0]
        XSteps = Difference.x()/self.XStepSize.value() + 1
        YSteps = Difference.y()/self.YStepSize.value() + 1
        RoughEstimateOfPoints = XSteps * YSteps
        ProgressCounter = 0
        self.RunScanButton.setText('Scanning')
        self.RunScanButton.setEnabled(False)
        self.RasterAndSaveAllScanButton.setEnabled(False)
        while Scanning:
            ProgressCounter = ProgressCounter + 1
            progress = ProgressCounter/RoughEstimateOfPoints
            
            if ProgressCounter%10 == 0:
                ElapsedTime = (time.time() - StartTime)
                ProjectedTime = ElapsedTime/progress
                FinalTime = StartTimeFull + datetime.timedelta(seconds=ProjectedTime)
                self.RunScanButton.setText('Scanning [' +str(np.round(100*progress,2))+ '%]')
                self.TimingLabel.setText("Scan - Elapsed: "+str(np.round(ElapsedTime/60,2)) + " min - Projected final time: "+str(FinalTime))
                self.update()
                QApplication.processEvents()
                
                if self.stopRunningScan.isChecked():
                    Scanning = False
                    break
                self.update()
            self.Stage.moveXTo(self.currentPosition.x())
            self.Stage.moveYTo(self.currentPosition.y())
            self.ZStage.setVoltage(self.currentPosition.z())
            #jump to next position if image is not interesting        
            time.sleep(0.3*wait/1000.0)
            image = self.Camera.getImageAsNumpyArray().T
            time.sleep(0.3*wait/1000.0)
            
            if self.isImageInteresting(image, enableSelectedFilters=True): 
                nr = self.saveCurrentPosition()
                  
                _filename = path + 'Position_'+str(nr)+'_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getVoltage()).replace('.','p') + '.jpg'
#                print(_filename)
                cv2.imwrite(_filename, image)

                self.ImageView.setImage(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoHistogramRange=False)
                self.update()
                QApplication.processEvents()
                self.update()

            self.currentPosition = self.currentPosition + QVector3D(self.XStepSize.value()*self.currentDirection, 0, 0)
#            print("     Update Height")
            height = self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y())
#            print("     Adjusted height")
            if height != None:
                self.currentPosition.setZ(height)
            
#            print("     Check scan boundaries")
            if self.currentPosition.x() >= self.EdgePoints2DScan[1].x() or self.currentPosition.x() <= self.EdgePoints2DScan[0].x():
#                print("     Outside boundaries - move to new position")
                self.Stage.moveXTo(self.currentPosition.x())
                self.Stage.moveYTo(self.currentPosition.y())
                self.ZStage.setVoltage(self.currentPosition.z())
                
                time.sleep(3.0*wait/1000.0)
                image = self.Camera.getImageAsNumpyArray().T
                time.sleep(1.0*wait/1000.0)
                
                if self.isImageInteresting(image, enableSelectedFilters=True):
#                    print("     Save position to List")
                    nr = self.saveCurrentPosition()
#                    print("     Start saving image")
                    _filename = path + 'Position_'+str(nr)+'_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getVoltage()).replace('.','p') + '.jpg'
                    cv2.imwrite(_filename, image)
                
                self.currentPosition = self.currentPosition + QVector3D(0, self.YStepSize.value(), 0)
                self.currentDirection *= -1
                
            if self.currentPosition.y() >= self.EdgePoints2DScan[1].y():
                Scanning = False
                    
            #QApplication.processEvents()
        print('Scan complete')
        self.stopRunningScan.hide()
        self.stopRunningScan.setChecked(False)
        self.RunScanButton.setText('Run scan')
        self.RunScanButton.setEnabled(True)
        self.RasterAndSaveAllScanButton.setEnabled(True)
        self.TimingLabel.setText("[Currently no scan running]")
        self.currentPosition = saveCurrentPositionFromBeforeScanToResetAfterwards
        self.Controller.enableAxes() 
        
        
    def rasterAndSaveImages(self):
        self.Controller.disableAxes()
        self.currentDirection = 1
        saveCurrentPositionFromBeforeScanToResetAfterwards = self.currentPosition
        path = r"C:\Users\GloveBox\Documents\Python Scripts\ScanImages/"
        StartTime = time.time()
        StartTimeFull = datetime.datetime.now()
        path = path + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S')
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            path = path + '_PL'
        else:
            path = path + '_WL'
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of directory %s failed" % path)
            return
        else:
            print ("Successfully created directory %s " % path)
        path = path + "/"

        #Save corners
        data_obj = {}
        data_obj['PointsOnPlane'] = self.PointsOnPlane
        data_obj['EdgePoints2DScan'] = self.EdgePoints2DScan 
        print("Save corners: ", data_obj)
        
        with open(path+"CornerInfo.pickle", 'wb') as f:
            pickle.dump(data_obj, f)
        
        self.stopRunningScan.setChecked(False)
        self.stopRunningScan.show()
        
        Scanning = True
        
        print("Getting exposure time...")
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            wait = self.Camera.getExposureTime()
            print(wait)
        else:
            wait = self.WhiteLightCamera.getExposureTime()
            print(wait)
            
        Difference = self.EdgePoints2DScan[1] - self.EdgePoints2DScan[0]
        XSteps = Difference.x()/self.XStepSize.value() + 1
        YSteps = Difference.y()/self.YStepSize.value() + 1
        RoughEstimateOfPoints = XSteps * YSteps
        ProgressCounter = 0
        self.RunScanButton.setText('Scanning')
        self.RunScanButton.setEnabled(False)
        
        self.RasterAndSaveAllScanButton.setEnabled(False)
        
        while Scanning:
            ProgressCounter = ProgressCounter + 1
            progress = ProgressCounter/RoughEstimateOfPoints
            
            if ProgressCounter%10 == 0:
                ElapsedTime = (time.time() - StartTime)
                ProjectedTime = ElapsedTime/progress
                FinalTime = StartTimeFull + datetime.timedelta(seconds=ProjectedTime)
                self.RunScanButton.setText('Scanning [' +str(np.round(100*progress,2))+ '%]')
                self.TimingLabel.setText("Scan - Elapsed: "+str(np.round(ElapsedTime/60,2)) + " min - Projected final time: "+str(FinalTime))
                self.update()
                QApplication.processEvents()
                
                if self.stopRunningScan.isChecked():
                    Scanning = False
                    break
                self.update()

            self.Stage.moveXTo(self.currentPosition.x())

            self.Stage.moveYTo(self.currentPosition.y())

            self.ZStage.setVoltage(self.currentPosition.z())
            
           
            time.sleep(2.0*wait/1000.0)
            if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
                image = self.Camera.getImageAsNumpyArray().T
            else:
                image = self.WhiteLightCamera.getImageAsNumpyArray()
                
            nr = self.saveCurrentPosition() 
            _filename = path + 'Position_'+str(nr)+'_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getVoltage()).replace('.','p') + '.jpg'
            cv2.imwrite(_filename, image)

                
#            self.ImageView.setImage(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoHistogramRange=False)
#            self.update()
#            QApplication.processEvents()
#            self.update()

            self.currentPosition = self.currentPosition + QVector3D(self.XStepSize.value()*self.currentDirection, 0, 0)

            height = self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y())

            if height != None:
                self.currentPosition.setZ(height)
            
            if self.currentPosition.x() >= self.EdgePoints2DScan[1].x() or self.currentPosition.x() <= self.EdgePoints2DScan[0].x():
                self.Stage.moveXTo(self.currentPosition.x())
                self.Stage.moveYTo(self.currentPosition.y())
                self.ZStage.setVoltage(self.currentPosition.z())
                
                time.sleep(2.0*wait/1000.0)
                if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
                    image = self.Camera.getImageAsNumpyArray().T
                else:
                    image = self.WhiteLightCamera.getImageAsNumpyArray()

                
                nr = self.saveCurrentPosition()
                _filename = path + 'Position_'+str(nr)+'_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getVoltage()).replace('.','p') + '.jpg'
                cv2.imwrite(_filename, image)

                
                self.currentPosition = self.currentPosition + QVector3D(0, self.YStepSize.value(), 0)
                self.currentDirection *= -1
                
            if self.currentPosition.y() >= self.EdgePoints2DScan[1].y():
                Scanning = False

        print('Scan complete')
        self.stopRunningScan.hide()
        self.stopRunningScan.setChecked(False)
        self.RunScanButton.setText('Run scan')
        self.RunScanButton.setEnabled(True)
        self.RasterAndSaveAllScanButton.setEnabled(True)
        self.TimingLabel.setText("[Currently no scan running]")
        self.currentPosition = saveCurrentPositionFromBeforeScanToResetAfterwards
        self.Controller.enableAxes() 
        
        

    def startPLandWLScan(self):
        self.StartPLandWLScanButton.setText('Scan running: Part 1')
        self.StartPLandWLScanButton.setEnabled(False)
        self.update()
        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() != 2:

            self.update()
            QApplication.processEvents()
            time.sleep(2)
            self.update()
            QApplication.processEvents()
        
        self.rasterAndSaveImages()

        
        self.StartPLandWLScanButton.setText('Scan running: Part 2')
        self.SavePositionList.clear()
        self.update()
        
        # self.WhiteLightBlueLightSlider.close()
        # self.WhiteLightBlueLightSlider.open()                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        # self.WhiteLightBlueLightSlider.moveHome()
        self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(0)
        self.update()
        QApplication.processEvents()
        time.sleep(2)
        self.update()
        QApplication.processEvents()
        
        self.rasterAndSaveImages()
        
        self.StartPLandWLScanButton.setText('1. PL --> 2. WL')
        self.StartPLandWLScanButton.setEnabled(True)
 
    # %%
    def __init__(self):      
        super().__init__()       
        self.setWindowTitle('glOVER - BP Awesomeness with Python')
        self.setWindowIcon(QIcon(r'C:\Users\GloveBox\Documents\Python Scripts\GloveboxSetupGUI\microscope.png'))
        print("Loading old GUIState")
        oldGuiState = {}
        with open(r'C:\Users\GloveBox\Documents\Python Scripts\GloveboxSetupGUI\GUIState.pickle', 'rb') as f:
            oldGuiState = pickle.load(f)
        self.ImageView = pg.ImageView(view=pg.PlotItem())#levelMode='mono')
        self.ImageView.getHistogramWidget().setHistogramRange(0, 300)
        if 'ROI_pos' in oldGuiState and 'ROI_size' in oldGuiState:
            self.ROI = pg.ROI(oldGuiState['ROI_pos'] ,oldGuiState['ROI_size'])
        else:
            self.ROI = pg.ROI((20,20),(100,100))
                
        self.ROI.addScaleHandle((1,1),(0,0))
        self.ImageView.addItem(self.ROI)
        self.ROI.sigRegionChanged.connect(lambda: print(self.ROI.pos(), self.ROI.size()))
        hist = self.ImageView.getHistogramWidget()
        hist.sigLevelChangeFinished.connect(self.updateBoxesFromHistogram)
        self.MeasurementLine = pg.LineSegmentROI([[10, 10], [120,10]], pen = (255, 0, 0))
        self.MeasurementLine.sigRegionChanged.connect(self.updateMeasurementLine)
        self.ImageView.addItem(self.MeasurementLine)
        _ViewBox = self.ImageView.getView().getViewBox()
        _ViewBox.disableAutoRange(_ViewBox.XYAxes)
        self.savedROIData = []
        #self.ImageView.setFixedWidth(1500)
        
        self.RCBModeOn = False
        self.counter= 0
        self.RCBImg = np.asarray(Image.open(r'C:\Users\GloveBox\Documents\Python Scripts\RCB\RCB.png'))
        self.RCBImg = self.RCBImg[::7,::7,:]
        
        self.SpecView = pg.GraphicsWindow()
        self.SpecPlotWindowItem = self.SpecView.addPlot()
        self.SpecPlot = self.SpecPlotWindowItem.plot([0,0,0])
        self.SpecPlotWindowItem.addItem(self.SpecPlot)
        
        ImageAndSpecSplitter = QSplitter(Qt.Vertical)
        ImageAndSpecSplitter.addWidget(self.ImageView)
        ImageAndSpecSplitter.addWidget(self.SpecView)
        
        
        # grid_layout.addWidget(ImageAndSpecSplitter, 0, 0, 5, 1)
        # grid_layout.setColumnStretch(0,2147483647)
        
        self.PointsOnPlane = [object,object,object]
        self.EdgePoints2DScan = [object,object]
        self.PlaneEquationGetZFromXandY = lambda x,y : None
        
        self.Stage = ThorlabsStages.Thorlabs2DStageKinesis(SN_motor = '73126054')
        print('2D Stage initialized, Starting up Z piezo')
        self.ZStage = ThorlabsStages.Thorlabs1DPiezoKinesis(SN_piezo = '41106464')
        self.Shutter = ThorlabsStages.LaserShutter()
        print('Piezo initialized')
        self.Arduino = ArduinoRotationStage.ArduinoRotationStage()
        time.sleep(0.5)
        print('Arduino Started')
        
        print("Initializing Linear Polarizer")
        self.LinearPolarizer = ThorlabsStages.ThorlabsCageRotator(SN_motor = '55164244')
        print("Linear polarizer initialized, start HWP")
        
        self.HalfWavePlate = ThorlabsStages.ThorlabsCageRotator(SN_motor = '55164594')
        print("Halfwaveplate initialized, start MCM stage")
        
        self.MCMStage = MCMStage.MCMStage()
        print("MCM Stage started")
        
        area = DockArea()
        self.setCentralWidget(area)
        
        self.StageControlGroupBox = Dock('Stage Control')#, size=(100, 500))
        self.ScanGroupBox = Dock('Scan')#, size=(100, 400))
        self.PositionListGroupBox = Dock('Position List')#, size=(100, 1000))
        self.CameraSettingsGroupBox = Dock('Camera Setting')#, size=(100, 500))
        self.SpectrometerWidgetGroupBox = Dock('Spectrometer Widget')#, size=(100, 200))
        self.MiscGroupBox = Dock('Misc')#, size = (100, 100))
        self.GraphingWindowGroupBox = Dock('Graphing Window', size=(1000, 1500))
        self.MiniButtonGroupBox = Dock('')#, size=(100,100))
        self.ImageProcessingGroupBox = Dock('Image Processing')#, size=(100, 1500))
        self.PLMapGroupBox = Dock('PL Map')#, size=(100,200))
        
  
        area.addDock(self.GraphingWindowGroupBox, 'left')
        area.addDock(self.StageControlGroupBox, 'right', self.GraphingWindowGroupBox)
        # area.addDock(self.PLMapGroupBox, 'right', self.StageControlGroupBox)
        # area.addDock(self.SpectrometerWidgetGroupBox, 'above', self.PLMapGroupBox)
        area.addDock(self.SpectrometerWidgetGroupBox, 'right', self.StageControlGroupBox)
        area.addDock(self.ImageProcessingGroupBox, 'right', self.SpectrometerWidgetGroupBox)
        area.addDock(self.ScanGroupBox, 'bottom', self.StageControlGroupBox)
        area.addDock(self.PLMapGroupBox, 'below', self.ScanGroupBox)
        area.addDock(self.CameraSettingsGroupBox, 'bottom', self.ScanGroupBox)
        area.addDock(self.MiscGroupBox, 'bottom', self.CameraSettingsGroupBox)
        area.addDock(self.PositionListGroupBox, 'bottom', self.SpectrometerWidgetGroupBox)
        area.addDock(self.MiniButtonGroupBox, 'bottom', self.GraphingWindowGroupBox)
        
        self.StageControlGroupBox.setOrientation(o="vertical")
        self.ScanGroupBox.setOrientation(o="vertical")
        self.PositionListGroupBox.setOrientation(o="vertical")
        self.CameraSettingsGroupBox.setOrientation(o="horizontal")
        self.SpectrometerWidgetGroupBox.setOrientation(o="vertical")
        self.MiscGroupBox.setOrientation(o="vertical")
        self.GraphingWindowGroupBox.setOrientation(o="vertical")
        self.MiniButtonGroupBox.setOrientation(o="vertical")
        self.ImageProcessingGroupBox.setOrientation(o="vertical")
        self.PLMapGroupBox.setOrientation(o="vertical")
        
        self.GraphingWindowGroupBox.addWidget(ImageAndSpecSplitter)


        #--------------------------------------------------------------------------------------------------------
        # Stage Control groupbox
        #--------------------------------------------------------------------------------------------------------
        
        # self.horizontalGroupBox = QGroupBox("Stage Control")
        StageControl = pg.LayoutWidget()
        # layout = QGridLayout()
        self.originalSpeed = 10.0
        self.SpeedModifier = 10.0
        self.fineSpeedModifier = 1.0
        self.XYSpeed = QProgressBar(self)
        self.XYSpeed.setMaximum( 100)
        self.XYSpeed.setValue( self.SpeedModifier)
        #self.progress.setGeometry(200, 80, 250, 20)
        StageControl.addWidget(self.XYSpeed, 0, 1, 1, 3)
        StageControl.addWidget(QLabel("XY Speed: "), 0, 0)
        StageControl.addWidget(QLabel("Z Speed: "), 1, 0)
        self.SpeedModifierFocus = 10.0
        self.ZSpeed = QProgressBar(self)
        self.ZSpeed.setMaximum( 100)
        self.ZSpeed.setValue( self.SpeedModifierFocus)
        StageControl.addWidget(self.ZSpeed, 1, 1, 1, 3)
        self.XPositionLabel = QLabel("--")
        self.YPositionLabel = QLabel("--")
        self.ZPositionLabel = QLabel("--")
        self.ObjectivePositionLabel = QLabel("--")
        self.LinPolLabel = QLabel("--")
        self.HWPLabel = QLabel("--")
        
        self.XMoveToSpinBox = QDoubleSpinBox()
        self.XMoveToSpinBox.setRange(0, 110)
        StageControl.addWidget(self.XMoveToSpinBox, 2, 2)
        self.YMoveToSpinBox = QDoubleSpinBox()
        self.YMoveToSpinBox.setRange(0, 75)
        StageControl.addWidget(self.YMoveToSpinBox, 3, 2)
        self.ZMoveToSpinBox = QDoubleSpinBox()
        self.ZMoveToSpinBox.setRange(0, 150)
        StageControl.addWidget(self.ZMoveToSpinBox, 4, 2)
        self.MCMMoveToSpinBox = QDoubleSpinBox()
        self.MCMMoveToSpinBox.setRange(-5, 5)
        StageControl.addWidget(self.MCMMoveToSpinBox, 5, 2)
        self.LinPolMoveToSpinBox = QDoubleSpinBox()
        self.LinPolMoveToSpinBox.setRange(0, 360)
        StageControl.addWidget(self.LinPolMoveToSpinBox, 6, 2)
        self.HWPMoveToSpinBox = QDoubleSpinBox()
        self.HWPMoveToSpinBox.setRange(0, 360)
        StageControl.addWidget(self.HWPMoveToSpinBox, 7, 2)
        
        
        btn = QPushButton("Set X")
        btn.clicked.connect(lambda : self.Stage.moveXTo(self.XMoveToSpinBox.value()))
        StageControl.addWidget(btn, 2, 3)
        btn = QPushButton("Set Y")
        btn.clicked.connect(lambda : self.Stage.moveYTo(self.YMoveToSpinBox.value()))
        StageControl.addWidget(btn, 3, 3)
        btn = QPushButton("Set Z")
        btn.clicked.connect(lambda : self.ZStage.setVoltage(self.ZMoveToSpinBox.value()))
        StageControl.addWidget(btn, 4, 3)
        
        btn = QPushButton("Set MCM")
        btn.clicked.connect(self.setMCMWithButton)
        StageControl.addWidget(btn, 5, 3)
        
        
        btn = QPushButton("Set LinPol")
        btn.clicked.connect(lambda : self.LinearPolarizer.moveToDeg(self.LinPolMoveToSpinBox.value()))
        StageControl.addWidget(btn, 6, 3)
        btn = QPushButton("Set HWP")
        btn.clicked.connect(lambda : self.HalfWavePlate.moveToDeg(self.HWPMoveToSpinBox.value()))
        StageControl.addWidget(btn, 7, 3)
        
        StageControl.addWidget(self.XPositionLabel, 2, 1)
        StageControl.addWidget(QLabel("X: "), 2, 0)
        StageControl.addWidget(self.YPositionLabel, 3, 1)
        StageControl.addWidget(QLabel("Y: "), 3, 0)
        StageControl.addWidget(self.ZPositionLabel, 4, 1)
        StageControl.addWidget(QLabel("Z: "), 4, 0)
        StageControl.addWidget(self.ObjectivePositionLabel, 5, 1)
        StageControl.addWidget(QLabel("O: (!?)"), 5, 0)
        StageControl.addWidget(self.LinPolLabel, 6, 1)
        StageControl.addWidget(QLabel("LP: "), 6, 0)
        StageControl.addWidget(self.HWPLabel, 7, 1)
        StageControl.addWidget(QLabel("HWP: "), 7, 0)
        
        
        
        btn = QPushButton("Home X,Y")
        btn.clicked.connect(self.Stage.home)
        StageControl.addWidget(btn, 8, 0, 1, 2)
        self.loadunloadsamplebtn = QPushButton('(un)load sample')
        self.loadunloadsamplebtn.clicked.connect(self.loadSample)
        StageControl.addWidget(self.loadunloadsamplebtn, 8, 2, 1, 2)
        
        self.StageControlGroupBox.addWidget(StageControl)
        
        #--------------------------------------------------------------------------------------------------------
        # Arduino Control groupbox
        #-------------------------------------------------------------------------------------------------------
        # ArduinoControl = pg.LayoutWidget()

        self.ArduinoReset = QPushButton("Reset arduino")
        self.ArduinoReset.clicked.connect(self.resetSliderandComboboxes)
        StageControl.addWidget(self.ArduinoReset, 9, 2, 1, 2)
        
        self.AlignmentSample = QPushButton("Spectrometer Alignment")
        self.AlignmentSample.clicked.connect(self.SpecAlignment)
        StageControl.addWidget(self.AlignmentSample, 9, 0, 1, 2)
        
        turtle = QIcon(r"turtle.png") 
        self.fineSteps = QCheckBox('Slow Mode')
        self.fineSteps.stateChanged.connect(self.reduceStepSize)
        self.fineSteps.setIcon(turtle)
        StageControl.addWidget(self.fineSteps, 10, 2, 1, 2)
        
        # checkbox = QCheckBox('invert X')
        # checkbox.stateChanged.connect(self.checkboxchanged)
        # layout.addWidget(checkbox, 9, 3, 1, 2)
        
        # self.BacklashCheckbox = QCheckBox('Backlash Correction')
        # layout.addWidget(self.BacklashCheckbox, 9, 0, 1, 2)
        bunny = QIcon(r"rabbit.png") 
        self.sprintCheckbox = QCheckBox('Fast Mode')
        self.sprintCheckbox.stateChanged.connect(self.sprintMode)
        self.sprintCheckbox.setIcon(bunny)
        StageControl.addWidget(self.sprintCheckbox, 10, 0, 1, 2)
        
        # self.horizontalGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.horizontalGroupBox, 0, 1)
        # grid_layout.setRowStretch(1,0)
        
        # ArduinoControlDock.addWidget(ArduinoControl)
        
        #--------------------------------------------------------------------------------------------------------
        # Scan Groupbox
        #--------------------------------------------------------------------------------------------------------
        
        # self.ScanGroupBox = QGroupBox("Take Scan")
        # layout = QGridLayout()
        
        Scan = pg.LayoutWidget()
   
        Scan.addWidget(QLabel("X step size: "), 0, 0)
        self.XStepSize = QDoubleSpinBox()
        if 'xStep' in oldGuiState:
            self.XStepSize.setValue(oldGuiState['xStep'])
        else:
            self.XStepSize.setValue(0.3)
        Scan.addWidget(self.XStepSize, 0, 1)
        
        Scan.addWidget(QLabel("Y step size: "), 1 , 0)
        self.YStepSize = QDoubleSpinBox()
        if 'yStep' in oldGuiState:
            self.YStepSize.setValue(oldGuiState['yStep'])
        else:
            self.YStepSize.setValue(0.3)
        Scan.addWidget(self.YStepSize, 1, 1)
        
        self.TopLeft = QPushButton('Set top left corner')
        Scan.addWidget(self.TopLeft, 2, 0, 1, 2)
        self.TopLeft.clicked.connect(self.setPoint0)
        
        self.BottomRight = QPushButton('Set bottom right corner')
        Scan.addWidget(self.BottomRight, 3, 0, 1, 2)
        self.BottomRight.clicked.connect(self.setPoint1)
        
        self.Additional = QPushButton('Set additional point on plane')
        Scan.addWidget(self.Additional, 4, 0, 1, 2)
        self.Additional.clicked.connect(self.setPoint2)
        
        
        self.imageProcessingEnabled = QCheckBox('do ImageProcessing')
        self.imageProcessingEnabled.stateChanged.connect(self.imageProcessingEnabledBoxChanged)
        Scan.addWidget(self.imageProcessingEnabled, 5, 1, 1, 1)
        
        self.ROIColorCheckEnabled = QCheckBox('ROI check')
        self.ROIColorCheckEnabled.setChecked(True)
        Scan.addWidget(self.ROIColorCheckEnabled, 5, 0, 1, 1)

        self.RunScanButton = QPushButton('Run scan')
        Scan.addWidget(self.RunScanButton, 6, 0, 1, 1)
        self.RunScanButton.clicked.connect(self.rasterScanProcedurally)
        
        self.RasterAndSaveAllScanButton = QPushButton('Save all')
        Scan.addWidget(self.RasterAndSaveAllScanButton, 6, 1, 1, 1)
        self.RasterAndSaveAllScanButton.clicked.connect(self.rasterAndSaveImages)
        
        self.TimingLabel = QLabel("[Currently no scan running]")
        Scan.addWidget(self.TimingLabel, 7, 0, 1, 2)
        
        self.stopRunningScan = QCheckBox('Stop scan in next iteration! (Give it time after clicking!)')
        Scan.addWidget(self.stopRunningScan, 8, 0, 1, 2)
        self.stopRunningScan.setChecked(False)
        self.stopRunningScan.hide()
        
        self.StartPLandWLScanButton = QPushButton('1. PL --> 2. WL')
        Scan.addWidget(self.StartPLandWLScanButton, 9, 0, 1, 2)
        self.StartPLandWLScanButton.clicked.connect(self.startPLandWLScan)

        # self.ScanGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.ScanGroupBox, 1, 1)
        
        self.ScanGroupBox.addWidget(Scan)
        
        #--------------------------------------------------------------------------------------------------------
        # Device initialization continued
        #--------------------------------------------------------------------------------------------------------
        
    
#        self.ZStage = ThorlabsStages.Thorlabs1DPiezoDummy()
        #self.WhiteLightBlueLightSlider = ElliptecMotor.ElliptecMotor("COM6")
        # self.WhiteLightBlueLightSlider.moveHome()
        self.Controller = PS4Controller.PS4Controller()
        print("Controller Started, starting Thorlabs cam")
#        self.Camera = Grasshopper3Cam.Grasshopper3Cam()
        self.Camera = ThorlabsCamera.ThorlabsCam()#[]
        print("Thorlabs Cam online, start ICMeasure cam")
        self.WhiteLightCamera = ICMeasureCamera.ICMeasureCam(name='DFK 33UX265 24910240',  videoFormat="RGB32 (2048x1536)") # 1600x1200 , 2048x1536, 1280x720
        print("ICMeasure Cam online")
        

        
    

    
        self.Controller.AxisFunctions[0] = lambda AxisValue :  self.Stage.moveXTo(self.Stage.getXPosition() - AxisValue*0.1*self.SpeedModifier/10*self.fineSpeedModifier)
        self.Controller.AxisFunctions[1] = lambda AxisValue :  self.Stage.moveYTo(self.Stage.getYPosition() + AxisValue*0.1*self.SpeedModifier/10*self.fineSpeedModifier)
        self.Controller.AxisFunctions[3] = lambda AxisValue : self.ZStage.setVoltage(self.ZStage.getVoltage() - AxisValue*0.3*self.SpeedModifierFocus/10)
        self.Controller.ButtonFunctions[0] = self.capture
        self.Controller.ButtonFunctions[1] = self.SwapWLBL
        self.Controller.ButtonFunctions[2] = self.SwapFilter
        self.Controller.ButtonFunctions[3] = self.SwapShutter
        self.Controller.ButtonFunctions[4] = self.DecreaseObjective
        self.Controller.ButtonFunctions[5] = self.IncreaseObjective
        # self.Controller.ButtonFunctions[6] = 
        # self.Controller.ButtonFunctions[7] = self.inactive
        self.Controller.ButtonFunctions[10] = self.sprintCheckbox.toggle

        self.Controller.ButtonFunctions[6] = lambda: self.MCMStage.setPositionInMM(self.MCMStage.getPositionInMM() - 0.05 )
        self.Controller.ButtonFunctions[7] = lambda: self.MCMStage.setPositionInMM(self.MCMStage.getPositionInMM() + 0.05 )
        
        self.Controller.HatFunctions[0] = lambda hat : self.changeSpeedWithHatButtons(hat) 
        

        self.ScanRunning2D = False
        self.currentPosition = QVector3D(-1,-1,-1)
        self.currentDirection = 1
        
#        self.Camera.startImageAcquisition(threadedOperation = False)#
        self.WhiteLightCamera.startImageAcquisition()
        
        self.timer = QTimer()
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()

        
        #Test 1 - Test 2 is further down below
        # self.timerController = QTimer()
        # self.timerController.setInterval(40)
        # self.timerController.timeout.connect(self.Controller.doEvents)
        # self.timerController.start()
        
        #--------------------------------------------------------------------------------------------------------
        # Graphing window
        #--------------------------------------------------------------------------------------------------------
        
        # GraphingWin = pg.LayoutWidget()
        
        self.LaplacianGraph = pg.GraphicsWindow(title="Laplacian")
        self.ImageProcessingGroupBox.addWidget(self.LaplacianGraph)
        self.ImageProcessingGroupBox.hide()
        
#        plotWindow1 = self.LaplacianGraph.addPlot(title="Laplacian Variance ~ Focusing")
#        self.LaplacianVarPlot = plotWindow1.plot([0,0,0])
#        
#        self.LaplacianVarArray = []
        
#        self.LaplacianGraph.nextRow()
        plotWindow2 = self.LaplacianGraph.addPlot(title="Color Distribution")
        plotWindow2.setXRange(0, 50, padding=0)
        plotWindow2.setYRange(0,200, padding=0)
        self.DistributionAndThresholdPlot = plotWindow2.plot([0,0,0])
        
        
        if 'GrayThreshold' in oldGuiState:
            self.GrayScaleThresholdLine = pg.InfiniteLine(pos=oldGuiState['GrayThreshold'], angle=90, movable=True, pen=(255,0,0))
        else:
            self.GrayScaleThresholdLine = pg.InfiniteLine(pos=40, angle=90, movable=True, pen=(255,0,0)) 
                
        
        plotWindow2.addItem(self.GrayScaleThresholdLine)
        
        self.LaplacianGraph.nextRow()
        
        plotWindow3 = self.LaplacianGraph.addPlot(title="Amount of Interestingness")
        self.InterestingnessPlotWindowItem = plotWindow3
        self.InterestingnessPlot = plotWindow3.plot([0,0,0])
        
        plotWindow3.addItem(self.InterestingnessPlot)
        
        
        if 'InterestingThreshold' in oldGuiState:
            self.InterestingnessThresholdLine = pg.InfiniteLine(pos=oldGuiState['InterestingThreshold'], angle=0, movable=True, pen=(0,0,255))
        else:
            self.InterestingnessThresholdLine = pg.InfiniteLine(pos=40, angle=0, movable=True, pen=(0,0,255)) 
            
        
        plotWindow3.addItem(self.InterestingnessThresholdLine)
        self.InterestingnessArray = []

#        self.LaplacianSharpnessSlider = QSlider()
#        self.LaplacianSharpnessSlider.setRange(0, 100)
#        self.LaplacianSharpnessSlider.setValue(0)
#        grid_layout.addWidget(self.LaplacianSharpnessSlider, 1, 12, 3, 1)
        
        
        #--------------------------------------------------------------------------------------------------------
        # Positionlist Groupbox
        #--------------------------------------------------------------------------------------------------------
        
        
        # self.PositionListGroupBox = QGroupBox("Saved Positions")
        # layout = QGridLayout()
        PositionList = pg.LayoutWidget()
      
        self.SavePositionList = QListWidget()
        if 'Positions' in oldGuiState:
            for i in range(len(oldGuiState['Positions'])):
                self.SavePositionList.addItem(oldGuiState['Positions'][i])
        
        self.SavePositionList.itemDoubleClicked.connect(self.goToPositionInList)
        PositionList.addWidget(self.SavePositionList, 0, 0, 1, 2)
        
        
        btn = QPushButton("Save current Position")
        btn.clicked.connect(self.saveCurrentPosition)
        PositionList.addWidget(btn, 1, 0)
        
        btn = QPushButton("Delete current item")
        btn.clicked.connect(self.deleteCurrentItem)
        PositionList.addWidget(btn, 1, 1)
        
        btn = QPushButton('Open folder in List')
        btn.clicked.connect(self.loadPositionsFromFolder)
        PositionList.addWidget(btn, 2, 0, 1, 2)
        
        btn = QPushButton('Flake Tinder')
        btn.clicked.connect(self.flakeTinder)
        PositionList.addWidget(btn, 3, 0, 1, 1)
        
        btn = QPushButton('Import Likes')
        btn.clicked.connect(self.importFlakeTinderLikes)
        PositionList.addWidget(btn, 3, 1, 1, 1)
        
        
        btn = QPushButton('Clear list')
        btn.clicked.connect(self.clearList)
        PositionList.addWidget(btn, 4, 0, 1, 2)
        
        # self.PositionListGroupBox.setLayout(layout)

        # grid_layout.addWidget(self.PositionListGroupBox,  1, 2, 4, 1)
        self.PositionListGroupBox.addWidget(PositionList)
        
        
        #--------------------------------------------------------------------------------------------------------
        # Spectrometer Settings groupbox
        #--------------------------------------------------------------------------------------------------------
        self.SpectrometerWidget = AdvancedSpectrometerWidget.CloseableSpectrometerWidget(lambda _ : self.SpecPlot.setData(self.SpectrometerWidget.SpectrometerWidget.wl_calibration, self.SpectrometerWidget.SpectrometerWidget.takeSpectrum(), pen=(0,0,255)))
        # grid_layout.addWidget(self.SpectrometerWidget,  0, 2, 1, 1)
        
        self.SpectrometerWidgetGroupBox.addWidget(self.SpectrometerWidget)
        
        
        #--------------------------------------------------------------------------------------------------------
        # PL Map groupbox
        #--------------------------------------------------------------------------------------------------------
        PLMap = pg.LayoutWidget()
        
        PLMap.addWidget(QLabel('Height (y):'), 0, 0, 1, 1)
        self.MapHeight = QDoubleSpinBox()
        self.MapHeight.setRange(0.001, 100)
        PLMap.addWidget(self.MapHeight, 0, 1, 1, 1)
        
        PLMap.addWidget(QLabel('Pixel:'), 0, 2, 1, 1)
        self.MapHeightPixel = QSpinBox()
        self.MapHeightPixel.setRange(1, 5000)
        PLMap.addWidget(self.MapHeightPixel, 0, 3, 1, 1)
        
        PLMap.addWidget(QLabel('Width (x):'), 1, 0, 1, 1)
        self.MapWidth = QDoubleSpinBox()
        self.MapWidth.setRange(0.001, 100)
        PLMap.addWidget(self.MapWidth, 1, 1, 1, 1)
        
        PLMap.addWidget(QLabel('Pixel:'), 1, 2, 1, 1)
        self.MapWidthPixel = QSpinBox()
        self.MapWidthPixel.setRange(1, 5000)
        PLMap.addWidget(self.MapWidthPixel, 1, 3, 1, 1)
        
        self.startPLMapBtn = QPushButton('Start PL Map')
        self.startPLMapBtn.clicked.connect(self.startPLMapScan)
        PLMap.addWidget(self.startPLMapBtn, 2, 0, 1, 4)
        
        self.stopPLScan = QCheckBox('Stop scan in next iteration! (Give it time after clicking!)')
        PLMap.addWidget(self.stopPLScan, 3, 0, 1, 2)
        self.stopPLScan.setChecked(False)
        self.stopPLScan.hide()
        
        self.PLMapGroupBox.addWidget(PLMap)
        
        #--------------------------------------------------------------------------------------------------------
        # Camera Settings groupbox
        #--------------------------------------------------------------------------------------------------------
        
        
        # self.CameraSettingsGroupBox = QGroupBox("Camera Settings")
        # layout = QGridLayout()
        
        CameraSetting = pg.LayoutWidget()
        
        CameraSetting.addWidget(QLabel('Exposure Times'), 0, 0,1,2)
        
        self.WLExposureSpinbox = QDoubleSpinBox()
        self.WLExposureSpinbox.setRange(0.1, 5000)
        self.WLExposureSpinbox.setValue(self.WhiteLightCamera.getExposureTime())
        CameraSetting.addWidget(self.WLExposureSpinbox, 1, 0)
        btn = QPushButton("set WL Exposure (ms)")
        btn.clicked.connect(lambda : self.WhiteLightCamera.setExposureTime(self.WLExposureSpinbox.value()))
        CameraSetting.addWidget(btn, 1, 1)
        
        self.PLExposureSpinbox = QDoubleSpinBox()
        self.PLExposureSpinbox.setRange(0.1, 5000)
        self.PLExposureSpinbox.setValue(self.Camera.getExposureTime())
        CameraSetting.addWidget(self.PLExposureSpinbox, 2, 0)
        btn = QPushButton("set PL Exposure (ms)")
        btn.clicked.connect(lambda : self.Camera.setExposureTime(self.PLExposureSpinbox.value()))
        CameraSetting.addWidget(btn, 2, 1)
        
        CameraSetting.addWidget(QLabel('WL Scaling (Min,Max)'), 3, 0,1,2)
        
        self.ColorScaleMin = QDoubleSpinBox()
        self.ColorScaleMin.setRange(-5000, 5000)
        self.ColorScaleMin.setValue(0)
        CameraSetting.addWidget(self.ColorScaleMin, 4, 0)
        
        self.ColorScaleMax = QDoubleSpinBox()
        self.ColorScaleMax.setRange(-5000, 5000)
        self.ColorScaleMax.setValue(300)
        CameraSetting.addWidget(self.ColorScaleMax, 4, 1)
        
        CameraSetting.addWidget(QLabel('PL Scaling (Min,Max)'), 5, 0,1,2)
        
        self.MonoScaleMin = QDoubleSpinBox()
        self.MonoScaleMin.setRange(-5000, 5000)
        self.MonoScaleMin.setValue(0)
        CameraSetting.addWidget(self.MonoScaleMin, 6, 0)
        
        self.MonoScaleMax = QDoubleSpinBox()
        self.MonoScaleMax.setRange(-5000, 5000)
        self.MonoScaleMax.setValue(100)
        CameraSetting.addWidget(self.MonoScaleMax, 6, 1)
        
        CameraSetting.addWidget(QLabel('PL Filters'), 7, 0, 1, 1)
        
        self.MedianEnableBlur = QCheckBox('Blur')
        CameraSetting.addWidget(self.MedianEnableBlur, 7, 1, 1, 1)
        
        self.GaussianEnableBlur = QCheckBox('Gaussian')
        CameraSetting.addWidget(self.GaussianEnableBlur, 7, 2, 1, 1)
        
        # layout.addWidget(QLabel('Measure for '), 9, 0,1,1)
        
        self.MeasurementLengthLabel = QLabel("Line length: ?")
        CameraSetting.addWidget(self.MeasurementLengthLabel, 12, 0, 1, 1)
        
        self.ObjectiveComboBox = QComboBox()
        self.ObjectiveComboBox.addItem("10x")
        self.ObjectiveComboBox.addItem("20x")
        self.ObjectiveComboBox.addItem("50x")
        self.ObjectiveComboBox.addItem("50xIR")
        self.ObjectiveComboBox.currentIndexChanged.connect(self.ChangeObjective)
        CameraSetting.addWidget(self.ObjectiveComboBox, 8, 1, 1, 2)
        
        self.ObjectiveLabel = QLabel('Current Objective:')
        CameraSetting.addWidget(self.ObjectiveLabel, 8, 0, 1, 1)
        
        self.WhiteLightBlueLightSliderComboBox = QComboBox()
        self.WhiteLightBlueLightSliderComboBox.addItem("White light")
        self.WhiteLightBlueLightSliderComboBox.addItem("Empty")
        self.WhiteLightBlueLightSliderComboBox.addItem("Blue light")
        self.WhiteLightBlueLightSliderComboBox.currentIndexChanged.connect(lambda idx: self.SelectSlider(idx))
        CameraSetting.addWidget(self.WhiteLightBlueLightSliderComboBox, 9, 1, 1, 2)
        
        self.SliderLabel = QLabel('Current Slider:')
        CameraSetting.addWidget(self.SliderLabel, 9, 0, 1, 1)
        
        self.FilterComboBox = QComboBox()
        self.FilterComboBox.addItem('Long Pass')
        self.FilterComboBox.addItem('F2')
        self.FilterComboBox.addItem('F3')
        self.FilterComboBox.currentIndexChanged.connect(lambda idx: self.SelectFilter(idx))
        CameraSetting.addWidget(self.FilterComboBox, 10, 1, 1, 2)
        
        self.FilterLabel = QLabel('Current Filter:')
        CameraSetting.addWidget(self.FilterLabel, 10, 0, 1, 1)
        
        btn = QPushButton('Open image externally')
        btn.clicked.connect(self.openImageExternally)
        CameraSetting.addWidget(btn, 13, 0, 1, 4)
        
        self.ShutterLabel = QLabel('Laser Shutter:')
        CameraSetting.addWidget(self.ShutterLabel, 11, 0, 1, 1)
        
        # btn = QPushButton('Shutter')
        # btn.clicked.connect(self.ChangeShutter)
        # layout.addWidget(btn, 13, 1, 1, 1)
        self.ShutterComboBox = QComboBox()
        self.ShutterComboBox.addItem("Open")
        self.ShutterComboBox.addItem("Closed")
        self.ShutterComboBox.setCurrentIndex(1)
        self.ShutterComboBox.currentIndexChanged.connect(self.ChangeShutter) 
        CameraSetting.addWidget(self.ShutterComboBox, 11, 1, 1, 2)
        
        
        CameraSetting.addWidget(QLabel('Smoothness'), 14, 0, 1, 1)
        self.ResolutionReductionComboBox = QComboBox()
        self.ResolutionReductionComboBox.addItem('Full Resolution')
        self.ResolutionReductionComboBox.addItem('Half resolution')
        
        self.ResolutionReductionComboBox.currentIndexChanged.connect(self.setCameraDivision)
        self.ResolutionReductionComboBox.setCurrentIndex(1)
        CameraSetting.addWidget(self.ResolutionReductionComboBox, 14, 1, 1, 2)
        
        # self.CameraSettingsGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.CameraSettingsGroupBox, 2, 1)
        
        self.CameraSettingsGroupBox.addWidget(CameraSetting)
        
        #--------------------------------------------------------------------------------------------------------
        # Misc Groupbox
        #--------------------------------------------------------------------------------------------------------
        
        # self.MiscGroupBox = QGroupBox("Misc")
        # layout = QGridLayout()
        Misc = pg.LayoutWidget()

        btn = QPushButton('Show/Hide Position list')
        btn.clicked.connect(self.showHidePositionList)
        Misc.addWidget(btn, 0, 0)
        self.PositionListHidden = False
        
        btn = QPushButton('Hide everything')
        btn.clicked.connect(self.hideEverything)
        Misc.addWidget(btn, 0, 1)
        
        btn = QPushButton('RCB')
        btn.clicked.connect(self.RCBFunc)
        Misc.addWidget(btn, 0, 2)
  
        # self.MiscGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.MiscGroupBox, 3, 1)
        
        self.MiscGroupBox.addWidget(Misc)
        
        
        #--------------------------------------------------------------------------------------------------------
        # Minibutton when everything is closed
        #--------------------------------------------------------------------------------------------------------
        self.MiniButtonToShowEverything = QPushButton('<')
        self.MiniButtonToShowEverything.clicked.connect(self.showEverything)
       # grid_layout.addWidget(self.MiniButtonToShowEverything, 0, 3)
        
        self.MiniButtonGroupBox.addWidget(self.MiniButtonToShowEverything)
        self.MiniButtonGroupBox.hide()
        
        
        self.showMaximized()
        
        self.ThreadRunning = True
        self.Thread = threading.Thread(target=self.threadingFunction)
        self.Thread.start()
        self.ThreadLock = threading.Lock()
        
        #TEst 2
        #self.ControllerThread = threading.Thread(target =  self.threadingFunctionController)
        #self.ControllerThread.start()
    
    def RCBFunc(self):
        self.RCBModeOn = not self.RCBModeOn
    
    def setCameraDivision(self):
        self.WhiteLightCamera.CameraResolutionDivider = self.ResolutionReductionComboBox.currentIndex() + 1
     
    def imageProcessingEnabledBoxChanged(self):
        if self.imageProcessingEnabled.isChecked():
            self.ImageProcessingGroupBox.show()
        else:
            self.ImageProcessingGroupBox.hide()
    
    def setMCMWithButton(self):
        self.MCMStage.setPositionInMM(self.MCMMoveToSpinBox.value())
        time.sleep(1)
        self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.getPositionInMM(),4)))
    
    def reduceStepSize(self):
        if self.fineSteps.isChecked():
            self.fineSpeedModifier = 0.01
        else:
            self.fineSpeedModifier = 1
    
    # Helen's edit
    def sprintMode(self):
        if self.sprintCheckbox.isChecked():
            self.originalSpeed = self.SpeedModifier
            self.SpeedModifier = 100
        else:
            self.SpeedModifier = self.originalSpeed
    
    def updateBoxesFromHistogram(self, histogram):
        Levels = histogram.getLevels() 
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: #PL
            self.MonoScaleMin.setValue(Levels[0])
            self.MonoScaleMax.setValue(Levels[1])
        else:
            self.ColorScaleMin.setValue(Levels[0])
            self.ColorScaleMax.setValue(Levels[1])
        
    def showEverything(self):
        self.MiniButtonGroupBox.hide()
        self.CameraSettingsGroupBox.show()
        if not self.PositionListHidden:
            self.PositionListGroupBox.show()
        self.ScanGroupBox.show()
        self.StageControlGroupBox.show()
        self.MiscGroupBox.show()
        self.SpectrometerWidgetGroupBox.show()
        self.PLMapGroupBox.show()
    
    def hideEverything(self):
        self.MiniButtonGroupBox.show()
        self.CameraSettingsGroupBox.hide()
        self.PositionListGroupBox.hide()
        self.ScanGroupBox.hide()
        self.StageControlGroupBox.hide()
        self.MiscGroupBox.hide()
        self.SpectrometerWidgetGroupBox.hide()
        self.PLMapGroupBox.hide()
    
    def showHidePositionList(self):
        if self.PositionListHidden:
            self.PositionListGroupBox.show()
            self.SpectrometerWidgetGroupBox.show()
            # self.PLMapGroupBox.show()
        else:
            self.PositionListGroupBox.hide()
            self.SpectrometerWidgetGroupBox.hide()
            # self.PLMapGroupBox.hide()
        self.PositionListHidden = not self.PositionListHidden
    
    def clearList(self):
        qm = QMessageBox
        reply = qm.question(self,'', "Are you sure to reset all the values?", qm.Yes | qm.No)
        
        if reply == qm.Yes:
            self.SavePositionList.clear()
    
    def setPoint0(self):
        self.setPointOnPlane(0, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
        
    def setPoint1(self):
        self.setPointOnPlane(1, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
        
    def setPoint2(self):
        self.setPointOnPlane(2, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
    

    def openImageExternally(self):
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)      
            else:
                image = self.Camera.getImageAsNumpyArray().T         
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)
        else:
            image = np.flip(self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2), 0)
        
        win = pg.image(image)
        self.text = pg.TextItem(text='Estimated length: ? \u03bcm', color = (255, 255, 255), border = 'w')
        self.MeasurementLine2 = pg.LineSegmentROI([[10, 10], [120,10]], pen = (255, 0, 0))
        self.MeasurementLine2.sigRegionChanged.connect(self.updateMeasurementLine2)
        win.addItem(self.MeasurementLine2)
        win.addItem(self.text)
        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:  
            win.setLevels(self.MonoScaleMin.value(), self.MonoScaleMax.value())
        else:
            win.setLevels(self.ColorScaleMin.value(), self.ColorScaleMax.value())
      
    def saveCurrentPosition(self):
        nr = self.SavePositionList.count()
        self.SavePositionList.addItem("Position "+str(nr)+"\n  X: " + str(self.Stage.getXPosition()) + "\n  Y: " + str(self.Stage.getYPosition()) + "\n  Z: " + str(self.ZStage.getVoltage()))
        return nr
        
    def saveCurrentPositionAsCorner(self, Identifier):
        self.SavePositionList.addItem("Corner: "+Identifier+"\n  X: " + str(self.Stage.getXPosition()) + "\n  Y: " + str(self.Stage.getYPosition()) + "\n  Z: " + str(self.ZStage.getVoltage()))
    
    def goToPositionInList(self, item):
        ItemText = item.text()
        Elements = ItemText.split("\n")
        XString = Elements[1]
        YString = Elements[2]
        ZString = Elements[3]
        XPosition = float(XString.split(": ")[1])
        YPosition = float(YString.split(": ")[1])
        ZPosition = float(ZString.split(": ")[1])
        self.Stage.moveXTo(XPosition)
        self.Stage.moveYTo(YPosition)
        self.ZStage.setVoltage(ZPosition)
        
    def loadSample(self):
        self.ObjectiveComboBox.setCurrentIndex(0)
        currentx = self.Stage.getXPosition()
        currenty = self.Stage.getYPosition()
        if abs(currentx) > 10:
            self.prealignmentxpos = currentx
            self.Stage.moveXTo(0)
        else:
            self.Stage.moveXTo(self.prealignmentxpos)
            
        if abs(currenty - 75) > 5:
            self.prealignmentypos = currenty
            self.Stage.moveYTo(75)
        else:
            self.Stage.moveYTo(self.prealignmentypos)    
        
    def SpecAlignment(self):
        currentx = self.Stage.getXPosition()
        currenty = self.Stage.getYPosition()
        if abs(currentx - 2.328) > 10:
            self.prealignmentxpos = currentx
            self.Stage.moveXTo(2.328)
        else:
            self.Stage.moveXTo(self.prealignmentxpos)
            
        if abs(currenty - 74.941) > 5:
            self.prealignmentypos = currenty
            self.Stage.moveYTo(74.941)
        else:
            self.Stage.moveYTo(self.prealignmentypos)    

        
        
    def deleteCurrentItem(self):
        self.SavePositionList.takeItem(self.SavePositionList.currentRow())
        
    def IncreaseObjective(self):
        if '50xIR' not in self.ObjectiveComboBox.currentText():
            # if self.BacklashCheckbox.isChecked() == True:
            self.Arduino.moveRelativemm('Z', 1.03)
            self.ObjectiveComboBox.setCurrentIndex(self.ObjectiveComboBox.currentIndex()+1)
            time.sleep(0.5)
        else:
            print('cannot increase further')  
        
    def DecreaseObjective(self):
        if '10x' not in self.ObjectiveComboBox.currentText():
            self.ObjectiveComboBox.setCurrentIndex(self.ObjectiveComboBox.currentIndex()-1)
            time.sleep(0.5)
        else:
            print('cannot deacrease further')   
        
    def ChangeObjective(self):
        self.Arduino.moveAbsolutemm('Z', self.Arduino.Zpresetpositions[str(self.ObjectiveComboBox.currentText())])
        self.updateMeasurementLine()
        
    def SwapWLBL(self):
        yoffset = -0.0578
        xoffset = 0.0982
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() != 2:
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(2)
            self.Stage.moveXTo(self.Stage.getXPosition() + xoffset) 
            self.Stage.moveYTo(self.Stage.getYPosition() + yoffset) 
        else:
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(0)
            self.Stage.moveXTo(self.Stage.getXPosition() - xoffset) 
            self.Stage.moveYTo(self.Stage.getYPosition() - yoffset) 

    def SelectSlider(self, idx):
        target = self.WhiteLightBlueLightSliderComboBox.currentText()
        print(target)
        self.Arduino.moveAbsolutemm('X', self.Arduino.Xpresetpositions[str(target)])
        if idx == 0: 
             self.Camera.endImageAcquisition()#
             self.WhiteLightCamera.startImageAcquisition()         
        if idx == 2:
            self.WhiteLightCamera.endImageAcquisition()
            self.Camera.startImageAcquisition()#
        self.updateMeasurementLine()
        QApplication.processEvents()
        time.sleep(0.02)
        QApplication.processEvents()   
        
    def SelectFilter(self, idx):
        if idx == 0:
            self.Arduino.moveAbsolutemm('Y', self.Arduino.Ypresetpositions['F1'])
        elif idx ==1:
            self.Arduino.moveAbsolutemm('Y', self.Arduino.Ypresetpositions['F2'])
        elif idx ==2:
            self.Arduino.moveAbsolutemm('Y', self.Arduino.Ypresetpositions['F3'])
            
    def SwapFilter(self):
        if self.FilterComboBox.currentIndex() == 0:
            self.FilterComboBox.setCurrentIndex(1)
        else:
            self.FilterComboBox.setCurrentIndex(0)
        # elif self.FilterComboBox.currentIndex() ==1:
        #     self.FilterComboBox.setCurrentIndex(2)
        # elif self.FilterComboBox.currentIndex() ==2:
        #     self.FilterComboBox.setCurrentIndex(0)
            
    def inactive(self):
        print("button inactive")
        
    def SwapShutter(self):
        if self.ShutterComboBox.currentIndex() == 0:
            self.ShutterComboBox.setCurrentIndex(1)
        else:
            self.ShutterComboBox.setCurrentIndex(0)
            
    def ChangeShutter(self):
        if self.ShutterComboBox.currentIndex() == 0:
            self.Shutter.flipperOn()
        if self.ShutterComboBox.currentIndex() == 1:
            self.Shutter.flipperOff()
             
    def capture(self):
        path = r"D:\Data\GloveBox_Images"
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

## These seem unused
    # def modifySpeed(self,AxisValue):
    #     self.SpeedModifier
    #     self.SpeedModifier -= AxisValue
    #     if self.SpeedModifier > 100:
    #         self.SpeedModifier = 100
    #     if self.SpeedModifier < 1:
    #         self.SpeedModifier = 1
            
    # def setSpeed(self, value):
    #     if  self.fineSteps.isChecked():
    #         self.SpeedModifier = value
    #         if self.SpeedModifier > 100:
    #             self.SpeedModifier = 100
    #         if self.SpeedModifier < 1:
    #             self.SpeedModifier = 1

    def changeSpeedWithHatButtons(self, hat):
        self.SpeedModifier += hat[0]*1
        if self.SpeedModifier > 100:
            self.SpeedModifier = 100
        if self.SpeedModifier < 1:
            self.SpeedModifier = 1
        self.SpeedModifierFocus += hat[1]*1
        if self.SpeedModifierFocus > 100:
            self.SpeedModifierFocus = 100
        if self.SpeedModifierFocus < 1:
            self.SpeedModifierFocus = 1
       
    def saveStateOnClosing(self):
        data_obj = {}
        data_obj['Positions'] = []
        for i in range(self.SavePositionList.count()):
            data_obj['Positions'].append(self.SavePositionList.item(i).text())
        
        data_obj['xStep'] = self.XStepSize.value()
        data_obj['yStep'] = self.YStepSize.value()
        
        data_obj['ROI_pos'] = self.ROI.pos()
        data_obj['ROI_size'] = self.ROI.size()
        
        data_obj['GrayThreshold'] = self.GrayScaleThresholdLine.pos()
        data_obj['InterestingThreshold'] = self.InterestingnessThresholdLine.pos()
        with open(r'C:\Users\GloveBox\Documents\Python Scripts\GloveboxSetupGUI\GUIState.pickle', 'wb') as f:
            pickle.dump(data_obj, f)       
        print("Successfully exported GUI data")
      
    def loadPositionsFromFolder(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory to load"))
        if os.path.exists(folder + "/CornerInfo.pickle"):
            print("Loading Corners")
            SavedCorners = {}
            with open(folder + "/CornerInfo.pickle", 'rb') as f:
                SavedCorners = pickle.load(f)
            if 'PointsOnPlane' in SavedCorners:
#                self.PointsOnPlane = SavedCorners['PointsOnPlane']
                print(SavedCorners['PointsOnPlane'])
                for i in range(3):
                    if type(SavedCorners['PointsOnPlane'][i]) == QVector3D:
                        self.SavePositionList.addItem("Corner: "+str(i)+"\n  X: " + str(SavedCorners['PointsOnPlane'][i].x()) + "\n  Y: " + str(SavedCorners['PointsOnPlane'][i].y()) + "\n  Z: " + str(SavedCorners['PointsOnPlane'][i].z()))        
        path = folder + "/*.jpg"
        files = glob.glob(path)   
        for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
            stripPath = name[(len(folder)+1):] 
            NameParts = stripPath.split('_')
            self.SavePositionList.addItem(NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
        
    def updateMeasurementLine(self):
        pts = self.MeasurementLine.listPoints()
#        print(pts)
        delta = pts[1] - pts[0]
#        print(delta)
        L = np.sqrt(delta.x()**2 + delta.y()**2)
#        print(L)
        
#        CALIBRATION      
#        INITIAL IDEA - MEASURE ALL OF THEM
#        calibrationMatrix = np.zeros( (4,3) ) # 4 Slider Positions, 3 Objective Selections
#        # Whitelight Cam
#        calibrationMatrix[0,0] = 600/1485.9738 # 10x
#        calibrationMatrix[0,1] = 300/1492.7232 # 20x
#        calibrationMatrix[0,2] = 130/1611241 # 50x
#        # Thorlabs Cam
#        calibrationMatrix[2,0] = 800/1159.6324 # 10x
#        calibrationMatrix[2,1] = 400/1156.5857 # 20x
#        calibrationMatrix[2,2] = 150/1083.1395 # 50x
#        calibrationFactor = calibrationMatrix[self.WhiteLightBlueLightSliderComboBox.currentIndex(), self.ObjectiveComboBox.currentIndex()]
#        self.MeasurementLengthLabel.setText("Estimated length: "+str(np.round(L*calibrationFactor,4)))
        #However it seems to scale almos perfectly!! Therefore only use the highest magnification and calculate the others form this one
        calibrationNormalized = 0
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 0:
            calibrationNormalized = 130/1611.2541*50.0*100/97.8 * self.WhiteLightCamera.CameraResolutionDivider
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            calibrationNormalized = 150/1083.1395*50.0*100/96
        calibrationFactor = calibrationNormalized / float(self.ObjectiveComboBox.currentText()[0:2])
        self.MeasurementLengthLabel.setText("Estimated length: "+str(np.round(L*calibrationFactor,4)) + u" \u03bcm")
    
    #Helen's ugly edit
    def updateMeasurementLine2(self):
        pts = self.MeasurementLine2.listPoints()
        delta = pts[1] - pts[0]
        L = np.sqrt(delta.x()**2 + delta.y()**2)
        calibrationNormalized = 0
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 0:
            calibrationNormalized = 130/1611.2541*50.0*100/97.8 * self.WhiteLightCamera.CameraResolutionDivider
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            calibrationNormalized = 150/1083.1395*50.0*100/96
        calibrationFactor = calibrationNormalized / float(self.ObjectiveComboBox.currentText()[0:2])
        self.text.setText('Estimated length: ' + str(np.round(L*calibrationFactor,4)) + u" \u03bcm")
        
    def resetSliderandComboboxes(self):
        self.Arduino.reset()
        self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(0)

    def startPLMapScan(self):
        if self.SpectrometerWidget.SpectrometerWidget != None:        
            if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                print("Spectrometer is in continous mode! Does not work!!")
                self.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
                self.SpectrometerWidget.SpectrometerWidget.ContinousMode = False
                print("Disabled continous mode")
            
            self.Controller.disableAxes()
            self.stopPLScan.show()
            self.startPLMapBtn.setText('Mapping')
            self.startPLMapBtn.setEnabled(False)
            
            H = float(self.MapHeight.value())
            H_px = self.MapHeightPixel.value()
                
            W = float(self.MapWidth.value())
            W_px = self.MapWidthPixel.value()
                
            wl = self.SpectrometerWidget.SpectrometerWidget.wl_calibration
                
            offset_x = np.linspace(-float(W*0.5),float(W*0.5),W_px) 
            offset_y = np.linspace(-float(H*0.5),float(H*0.5),H_px)
                
            InitialPosition_x = self.Stage.getXPosition()
            InitialPosition_y = self.Stage.getYPosition()
            print('initial x,y', InitialPosition_x, InitialPosition_y)    
            data = np.zeros( (  (H_px*W_px)+1, (len(wl))+2 ) )
            data[0,2:] = wl
                
            
            self.update()
            QApplication.processEvents()  
            PLMapSubprocess = Process(target=Subprocess_Function, args=(PLMapSubprocessQueue,))
            PLMapSubprocess.start()
            self.update()
            QApplication.processEvents()  
            
            #send sizes to the subprocess
            PLMapSubprocessQueue.put(['SxSy', (H_px*W_px), (len(wl)) ])
            PLMapSubprocessQueue.put(['wl', wl ])
            PLMapSubprocessQueue.put(['Ux', InitialPosition_x + offset_x ])
            PLMapSubprocessQueue.put(['Uy', InitialPosition_y + offset_y ])
            
            counter = 0
            for current_offset_y in offset_y:
                curr_y = np.round(InitialPosition_y + current_offset_y,5)
                self.Stage.moveYTo(float(curr_y))
                for current_offset_x in offset_x:
                    
                    if self.stopPLScan.isChecked():
                        break
                
                    curr_x = np.round(InitialPosition_x + current_offset_x, 5)
                    # print(curr_x)
                    self.Stage.moveXTo(float(curr_x))
                    # time.sleep(1)
                    
                    print(curr_x, self.Stage.getXPosition())
                    # self.eventLoop()
                    
                    
                    data[counter,0] = curr_x
                    data[counter,1] = curr_y
                        
                    counter = counter + 1 
                    # add wait time ???
                    
                    
                    spec = self.SpectrometerWidget.SpectrometerWidget.takeSpectrum() #np.random.randint(1000,size=len(wl))#
                        
                    data[counter,2:] = spec
                    PLMapSubprocessQueue.put(['spec', curr_x, curr_y, counter-1, spec])
                    
                    time.sleep(1)
                    
                    self.update()
                    QApplication.processEvents()
            
            self.startPLMapBtn.setEnabled(True)
            self.stopPLScan.setChecked(False)
            self.stopPLScan.hide()
            
            self.Stage.moveXTo(InitialPosition_x)
            self.Stage.moveYTo(InitialPosition_y)
            self.Controller.enableAxes() 
                
        else:
            print("Spectrometer not connected! Abort scan!")
        
        











    
    # This function is really not well written. There shouldn't be so many global variables... however, it gets the job done.
    global CurrentTinderFiles 
    global CurrentTinderFolder
    global ListOfLikes
    def flakeTinder(self):
        global CurrentTinderFolder
        #folder = str(QFileDialog.getExistingDirectory(None, "Select Directory to load"))
        #item, ok = QInputDialog.getText(None, "Enter path of folder with correct slashes", 
        #                                  "Folder path (pay attention to slashes):")
        path = r"C:\Users\GloveBox\Documents\Python Scripts\ScanImages"
        dirs = [x[0] for x in os.walk(path)]
        item, ok = QInputDialog.getItem(None, "Select Folder", "Accessible Folders", dirs[1:], 0, False)
        
        
        
        if ok == False:
            return
        folder = item
        CurrentTinderFolder = folder
        path = folder + "/*.jpg"
        files = glob.glob(path)  
        global CurrentTinderFiles
        CurrentTinderFiles = files
        global ImageView
        ImageView = pg.ImageView()
        global ImageCounter
        ImageCounter = 0    
        name = files[ImageCounter]
        ImageView.setImage(imread(name))
        global ListOfLikes
        ListOfLikes = []
        
        def myKeyPressEvent(event):
            key = event.key()
            global ImageCounter
            global ImageView
            global ListOfLikes
            
            if key == QtCore.Qt.Key_Left:
                ImageCounter = ImageCounter - 1
                if ImageCounter < 0:
                    ImageCounter = 0
                if ImageCounter > len(files)-1:
                    ImageCounter = len(files)-1
                name = files[ImageCounter]
                stripPath = name[(len(folder)+1):] 
                NameParts = stripPath.split('_')
                
            if key == QtCore.Qt.Key_Right:
                ImageCounter = ImageCounter + 1
                if ImageCounter < 0:
                    ImageCounter = 0
                if ImageCounter > len(files)-1:
                    ImageCounter = len(files)-1
                name = files[ImageCounter]
                stripPath = name[(len(folder)+1):] 
                NameParts = stripPath.split('_')
                
        
            if key == QtCore.Qt.Key_Up:
                if not ImageCounter in ListOfLikes:
                    ListOfLikes.append(ImageCounter)
                name = files[ImageCounter]
                stripPath = name[(len(folder)+1):] 
                NameParts = stripPath.split('_')
                print(NameParts[0] + ' ' + NameParts[1])
            
            if key == QtCore.Qt.Key_Down:
                if ImageCounter in ListOfLikes:
                    print(ListOfLikes)
                    ListOfLikes.remove(ImageCounter)
                name = files[ImageCounter]
            Current = imread(name)    
            if ImageCounter in ListOfLikes:
                Current = Current.T       
            ImageView.setImage(Current, autoRange=False, autoLevels=False, autoHistogramRange=False)          
        ImageView.keyPressEvent = myKeyPressEvent
        ImageView.show()

    def importFlakeTinderLikes(self):
        global CurrentTinderFiles
        global ListOfLikes
        global CurrentTinderFolder
        for LikedIndex in ListOfLikes: 
            name = CurrentTinderFiles[LikedIndex]
            stripPath = name[(len(CurrentTinderFolder)+1):] 
            NameParts = stripPath.split('_')
            self.SavePositionList.addItem("Liked " + NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
        
     
# %%      
if __name__ == '__main__':
    print("Import the cameramodules")
    #-------------------------
    #Aidans ugly fix of the problem
    sys.path.append(r'C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Python Compact Scientific Camera Toolkit\examples')
    print("Start a small helper script to enable Thorlabs Camera")
    from polling_example import *
    print("Helper script done. Start loading components")
    #-------------------------    
    import ThorlabsCamera
    # ----------------------------------
    # really nasty workaround / I don't like it but I found no other easz fix

    directory = os.getcwd()
    os.chdir(r'C:\Users\GloveBox\Documents\Python Scripts\ICMeasureCamera')
    import ICMeasureCamera
    os.chdir(directory)
    # ----------------------------------
    
    print("Start GUI")
    
    app = QApplication([])
    app.setStyle('Fusion')
    MainWindow = GloveBoxSetupWindow()
    MainWindow.showMaximized()
    # MainWindow.showNormal()
    # MainWindow.showFullScreen()
    # MainWindow.setWindowFlags(MainWindow.windowFlags() |
    #                 QtCore.Qt.WindowSystemMenuHint |
    #                 QtCore.Qt.WindowMinMaxButtonsHint)
    sys.exit(app.exec_())