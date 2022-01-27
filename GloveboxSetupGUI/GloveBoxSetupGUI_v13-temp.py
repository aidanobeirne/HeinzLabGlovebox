# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:07:18 2020

@author: Markus A. Huber
"""

#objective 4.8 mm for a roundtrip
# --> 4.8/5 = 0.96 mm between objectives ( G21G91G1X0.96F25 )

# 12 threshold - 100 cts : WSe2 on SiO2 

import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
import ctypes
myappid = u'HeinzLab.PythonScripts.GloveBoxSetup.v1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
import datetime
import time
import sys
import os
import copy
import os.path
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PS4Controller')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
#sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrasshoperCamera3')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsCamera')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ICMeasureCamera')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\MCMStage')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrblRotationStation')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ElliptecMotor')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Andor')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\SpecPlotGUIElement')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\StageLocationGUIelement')
sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Thorlabs Filter Wheel')
sys.path.append(r'C:\Users\GloveBox')

try:
    from FWxC_COMMAND_LIB import *
except OSError as ex:
    print("Filter Wheel Warning: ",ex)

import pickle
import glob
import ThorlabsStages
import MCMStage
import PS4Controller
from matplotlib.image import imread
import matplotlib
from PIL import ImageTk, Image

import ArduinoRotationStage
import PA_arduino
import AdvancedSpectrometerWidget
import PLMapGUI
import SpecPlotGUIElement
import StageLocationGUIElement
import FilterWheel
import Aidan_quickplot

import ElliptecMotor
import time
import pyqtgraph as pg
from pyqtgraph.dockarea import *
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
import threading
from PyQt5.QtWidgets import qApp, QCheckBox, QSpinBox, QFileDialog, QSplitter, QSlider, QProgressBar, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit, QInputDialog
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QVector3D, QMessageBox, QIcon, QMainWindow, QGraphicsProxyWidget, QPushButton
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QRect, QPoint,QPointF
from PyQt5 import QtCore
import cv2
from skimage import draw
from scipy.ndimage.filters import median_filter
from scipy import stats
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
        if self.RCBModeOn:
            self.counter += 2
            self.ImageView.setImage(self.RCBImg)
            self.ImageView.imageItem.setTransform(self.ImageView.imageItem.dataTransform().rotate(self.counter))
            self.ImageView.autoRange()
            return
          
        self.Controller.doEvents()
        
        if self.Scanning == True:
            pass
        else:
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
        
        if not self.XYSpeed.isSliderDown():
            self.XYSpeed.setValue(self.SpeedModifier)
        if not self.ZSpeed.isSliderDown():
            self.ZSpeed.setValue(self.SpeedModifierFocus)
        XPos = self.Stage.getXPosition()
        YPos = self.Stage.getYPosition()
        self.XPositionLabel.setText(str(np.round(XPos,4)))
        self.YPositionLabel.setText(str(np.round(YPos,4)))
        
        self.StageLocationPlot.updateStagePos(abs(XPos), abs(YPos))

        self.ZPositionLabel.setText(str(np.round(self.ZStage.getVoltage() ,4)))
        
        self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.lastCorrectPosition* 0.2116667 /1000.0,4)))
        # self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.getPositionInMM(),4)))
        self.LinPolLabel.setText(str(np.round(self.LinearPolarizer.getRotation(), 4)))
        
        HWPvalue = np.round(2*self.HalfWavePlate.getRotation(), 4)
        if HWPvalue > 360:
            HWPvalue = HWPvalue-360
        self.HWPLabel.setText(str(HWPvalue))

        calibrationNormalized = 0
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 0:
            calibrationNormalized = 130/1611.2541*50.0*100/97.8 * self.WhiteLightCamera.CameraResolutionDivider
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            calibrationNormalized = 150/1083.1395*50.0*100/96
        self.calibrationFactor = 1e-6*calibrationNormalized / float(self.ObjectiveComboBox.currentText()[0:2]) 

        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex():
            if len(image) > 0:
                
                #self.ImageView.setImage(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoRange = False, autoHistogramRange=False)
                self.ImageView.setImage(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoRange = False, autoHistogramRange=False, pos = (0*XPos*1e-3, 0*YPos*1e-3), scale=(self.calibrationFactor, self.calibrationFactor))

                if self.ROIColorCheckEnabled.isChecked():
                    if self.isImageInteresting(image, enableSelectedFilters=True):
                        self.ROI.setPen((0,255,0))
                    else:
                        self.ROI.setPen((255,0,0))
                else:
                    self.ROI.setPen((125,125,125))
        else:
            self.ROI.setPen((125,125,125))
            if len(imageWL) > 0:
                
                #self.ImageView.setImage(imageWL, autoLevels=False, levels=(self.ColorScaleMin.value(), self.ColorScaleMax.value()), autoRange = False, autoHistogramRange=False)
                self.ImageView.setImage(imageWL, autoLevels=False, levels=(self.ColorScaleMin.value(), self.ColorScaleMax.value()), autoRange = False, autoHistogramRange=False, pos = (0*XPos*1e-3, 0*YPos*1e-3), scale=(self.calibrationFactor, self.calibrationFactor))
        
        if self.NeedsAutoRange:
            self.NeedsAutoRange = False
            self.ImageView.autoRange()
            self.ImageView.autoRange()
            self.ImageView.autoRange()
        # self.ImageView.view.setLabel('left', text='y', units='m')
        # self.ImageView.view.setLabel('bottom', text='x', units='m')
        
        
        if self.SpectrometerWidget.SpectrometerWidget != None:        
            if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                self.SpecPlot.setData(self.SpectrometerWidget.SpectrometerWidget.wl_calibration , self.SpectrometerWidget.SpectrometerWidget.LatestContinousSpectrum, pen=(0,0,255))
                
        if self.Controller.KeyboardModeEnabled:
            dx, dy = self.OnScreenJoystick1.getState()
            self.Stage.moveXTo(self.Stage.getXPosition() + dx*1*self.SpeedModifier/10*self.fineSpeedModifier)
            self.Stage.moveYTo(self.Stage.getYPosition() + dy*1*self.SpeedModifier/10*self.fineSpeedModifier)
            
            _, dz = self.OnScreenJoystick2.getState()
            if self.focusStageJoystickComboBox.currentIndex() == 0:
                self.ZStage.setVoltage(self.ZStage.getVoltage() + dz*1)
            elif self.focusStageJoystickComboBox.currentIndex() == 1:
                self.MCMStage.setPositionInMM(self.MCMStage.getPositionInMM() + dz*0.05)
        
        ##### In the first event we initialize all of the QDoubleSpinboxes 
        if self.XMoveToSpinBox.value() ==0 and self.YMoveToSpinBox.value() ==0 and self.ZMoveToSpinBox.value()==0 and self.HWPMoveToSpinBox.value()==0:

            
            self.XMoveToSpinBox.setValue(self.Stage.getXPosition())
            self.YMoveToSpinBox.setValue(self.Stage.getYPosition())
            self.ZMoveToSpinBox.setValue(self.ZStage.getVoltage())
            self.MCMMoveToSpinBox.setValue(np.round(self.MCMStage.lastCorrectPosition* 0.2116667 /1000.0,4))
            self.LinPolMoveToSpinBox.setValue(self.LinearPolarizer.getRotation())
            self.HWPMoveToSpinBox.setValue(2*self.HalfWavePlate.getRotation())
            # self.WLExposureSpinbox.editingFinished.setValue()
            # self.PLExposureSpinbox.editingFinished.setValue()
                
            # self.YMoveToSpinBox.editingFinished.connect(lambda : self.Stage.moveYTo(self.YMoveToSpinBox.value()))
            # self.XMoveToSpinBox.editingFinished.connect(lambda : self.Stage.moveXTo(self.XMoveToSpinBox.value()))
            # self.ZMoveToSpinBox.editingFinished.connect(lambda : self.ZStage.setVoltage(self.ZMoveToSpinBox.value()))
            # self.MCMMoveToSpinBox.editingFinished.connect(self.setMCMWithButton)
            # self.LinPolMoveToSpinBox.editingFinished.connect(lambda : self.RotateAnalyzer(self.LinPolMoveToSpinBox.value()))
            # self.HWPMoveToSpinBox.editingFinished.connect(lambda : self.RotateHWP(self.HWPMoveToSpinBox.value()))
            # # self.WLExposureSpinbox.editingFinished.connect(lambda : self.WhiteLightCamera.setExposureTime(self.WLExposureSpinbox.value()))
            # # self.PLExposureSpinbox.editingFinished.connect(lambda : self.Camera.setExposureTime(self.PLExposureSpinbox.value()))
        


    def set_blank_image(self):
        image = self.Camera.getImageAsNumpyArray().T
        if self.MedianEnableBlur.isChecked():
            image = cv2.medianBlur(image,5)         
        if self.GaussianEnableBlur.isChecked():
            image = cv2.GaussianBlur(image,(5,5),0) 
            
        p = self.ROI.pos()
        s = self.ROI.size()
        S = np.shape(image)
        ImageSize = (S[0]*self.calibrationFactor, S[0]*self.calibrationFactor)
        for i in (0,1):
            if p[i] < 0:
                p[i] = 0
            if p[i]+s[i] > ImageSize[i]:
                s[i] = ImageSize[i] - p[i]
        temp = s
        s = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 
        temp = p
        p = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 

        ROIData = image[int(p[0]):int(p[0]+s[0]),int(p[1]):int(p[1]+s[1])]
        self.blank = ROIData 
        #lower_bound =(int(2*np.median(ROIData))
        # lower_bound = 20
        lower_bound  = self.GrayScaleThresholdLine.value()
        blank_mask = cv2.inRange(self.blank, (lower_bound), (256))
        self.blank_hist = cv2.calcHist([self.blank], [0], blank_mask, [256], [0, 256])
        
        plt.figure()
        plt.imshow(self.blank)
        plt.title('Blank Image')
        
        try:
            interestingness = np.round(cv2.compareHist(self.flake_hist, self.blank_hist, cv2.HISTCMP_CHISQR) , 2)
            self.flakebutton.setText('Flake = ' + str(interestingness))
            self.blankbutton.setText('Blank [SET]' )
        except AttributeError:
            self.blankbutton.setText('Blank [SET]' )
            print('still need to set a flake image')
        
        cv2.imwrite(r'C:\Users\GloveBox\Documents\Python Scripts\autoscan\blank.jpg', self.blank)
   
    def set_flake_image(self):
        image = self.Camera.getImageAsNumpyArray().T
        
        if self.MedianEnableBlur.isChecked():
            image = cv2.medianBlur(image,5)         
        if self.GaussianEnableBlur.isChecked():
            image = cv2.GaussianBlur(image,(5,5),0) 
        ########## Markus's code for the ROI
        p = self.ROI.pos()
        s = self.ROI.size()
        S = np.shape(image)
        ImageSize = (S[0]*self.calibrationFactor, S[0]*self.calibrationFactor)
        for i in (0,1):
            if p[i] < 0:
                p[i] = 0
            if p[i]+s[i] > ImageSize[i]:
                s[i] = ImageSize[i] - p[i]
        temp = s
        s = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 
        temp = p
        p = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 
        ROIData = image[int(p[0]):int(p[0]+s[0]),int(p[1]):int(p[1]+s[1])]
        ################## Save flake image and histogram
        self.flake = ROIData
        # try:
        #     self.flake[self.flake < self.blank] = self.blank[self.flake < self.blank]
        # except AttributeError:
        #     pass
        #lower_bound =(int(2*np.median(ROIData))
        # lower_bound = 20
        lower_bound  = self.GrayScaleThresholdLine.value()
        flake_mask = cv2.inRange(self.flake, (lower_bound), (256))

        self.flake_hist = cv2.calcHist([self.flake], [0], flake_mask, [256], [0, 256])
        

        plt.figure()
        plt.imshow(self.flake)
        plt.title('Flake Image')
        
        try:
            interestingness = np.round(cv2.compareHist(self.flake_hist, self.blank_hist, cv2.HISTCMP_CHISQR) , 2)
            self.flakebutton.setText('Flake = ' + str(interestingness))
        except AttributeError:
            self.flakebutton.setText('Flake [SET]' )
            print('still need to set blank image')
        cv2.imwrite(r'C:\Users\GloveBox\Documents\Python Scripts\autoscan\flake.jpg', self.flake)
            
    def isImageInteresting(self, CurrentImage, enableSelectedFilters=True):
        image = CurrentImage
        if enableSelectedFilters:
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(image,5)         
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)  
        p = self.ROI.pos()
        s = self.ROI.size()
        
        S = np.shape(image)
        ImageSize = (S[0]*self.calibrationFactor, S[0]*self.calibrationFactor)
        for i in (0,1):
            if p[i] < 0:
                p[i] = 0
            if p[i]+s[i] > ImageSize[i]:
                s[i] = ImageSize[i] - p[i]
        temp = s
        s = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 
        temp = p
        p = (temp[0]/self.calibrationFactor,temp[1]/self.calibrationFactor) 
        ROIData = image[int(p[0]):int(p[0]+s[0]),int(p[1]):int(p[1]+s[1])]
        
        try:
            ### An attempt to remove darker regions (bulk) from the chi square calculation
            # print(len([ROIData < self.blank]))
            # ROIData[ROIData < self.blank] = self.blank[ROIData < self.blank]
            #lower_bound =(int(2*np.median(ROIData))
            # lower_bound = 20
            lower_bound  = self.GrayScaleThresholdLine.value()
            mask = cv2.inRange(ROIData, (lower_bound), (256))
            hist = cv2.calcHist([ROIData], [0], mask, [256], [0, 256])
            interestingness = cv2.compareHist(hist, self.blank_hist, cv2.HISTCMP_CHISQR)
            self.ThreadLock.acquire()
            self.savedROIData = ROIData
            self.savedChisquared = interestingness
            self.ThreadLock.release()
            
        except AttributeError:
            self.ThreadLock.acquire()
            self.savedROIData = ROIData
            self.savedChisquared = 0
            self.ThreadLock.release()
            interestingness = 0

        return interestingness >  self.InterestingnessThresholdLine.value()
    
####################################################################
    def threadingFunction(self):
        while self.ThreadRunning:
            time.sleep(0.05)  
            if self.imageProcessingEnabled.isChecked():
                if not self.ROIColorCheckEnabled.isChecked():
                    self.ROIColorCheckEnabled.setChecked(True)
                
                self.ThreadLock.acquire()
                hist, pos = np.histogram(self.savedROIData, bins=100)
                chisquared = self.savedChisquared
                self.ThreadLock.release() 
                
                self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
                self.InterestingnessArray.append(chisquared)
                
                if len(self.InterestingnessArray) > 100:
                    self.InterestingnessArray.pop(0)
                    
                self.InterestingnessPlot.setData(self.InterestingnessArray, pen=(0,0,255))
                self.InterestingnessPlotWindowItem.setXRange(0,100, padding = 0)
                           
        
    def closeEvent(self, event):

        self.ImageView.setImage(self.lazyeggImg)
        self.ImageView.imageItem.setTransform(self.ImageView.imageItem.dataTransform().rotate(90))
        self.ImageView.autoRange()
        
        StopGUI = StartAndCloseProgressWidget()
        StopGUI.show()

        self.closeButton.setText("Closing...Please wait")
        self.closeButton.setEnabled(False)
        print("User has clicked the red x on the main window")
        print("Stopping event loop")
        self.timer.stop()
        
        # Test 1
        # self.timerController.stop()
        
        StopGUI.Progress.setValue(5)
        StopGUI.update()
        QApplication.processEvents()
        
        self.ThreadRunning = False
        print("stopping Thread")
        self.Thread.join()    
        
        StopGUI.Progress.setValue(10)
        StopGUI.update()
        QApplication.processEvents()
        #Test 2
        #self.ControllerThread.join()
            
        print("Stopped Thread")
        print("Closing Controller")
        self.Controller.closeController()
        
        StopGUI.Progress.setValue(15)
        StopGUI.update()
        QApplication.processEvents()
        print('Closing Arduino Rotation Stage')
        self.resetSliderandComboboxes()
        self.Arduino.close()
        
        StopGUI.Progress.setValue(20)
        StopGUI.update()
        QApplication.processEvents()
        print("Closing peripheral devices")   
        print("Closing Monochrom Camera")
        self.Camera.endImageAcquisition()
        self.Camera.close()
        
        plt.close('all')
        
        StopGUI.Progress.setValue(25)
        StopGUI.update()
        QApplication.processEvents()
        print("Closing Color Camera")
        self.WhiteLightCamera.endImageAcquisition()
        self.WhiteLightCamera.close()
        
        StopGUI.Progress.setValue(30)
        StopGUI.update()
        QApplication.processEvents()
        print('Closing Slider Whitelight-Bluelight')

        print("Closing XYStage")
        self.Stage.close()
        

        
        print('Closing Filter Wheel')
        self.filterwheel.SetPosition(1)
        self.filterwheel.close()
        time.sleep(0.5)
        
        StopGUI.Progress.setValue(35)
        StopGUI.update()
        QApplication.processEvents()
        print("Closing Coarse Position Stage")
        # self.MCMStage.setPositionInMM(15)
        self.MCMStage.close()
        
        StopGUI.Progress.setValue(40)
        StopGUI.update()
        QApplication.processEvents()
        print("Closed Coarse Position Stage")
        
        self.Shutter.flipperOff()
        self.Shutter.close()
        
        StopGUI.Progress.setValue(45)
        StopGUI.update()
        QApplication.processEvents()
        print("Shutter disconnected")
        
        self.LinearPolarizer.close()
        
        StopGUI.Progress.setValue(50)
        StopGUI.update()
        QApplication.processEvents()
        print("Linear polarizer closed")
        
        self.HalfWavePlate.close()
        
        StopGUI.Progress.setValue(55)
        StopGUI.update()
        QApplication.processEvents()
        print("HWP closed")
    
        print("Closing ZStage")
        self.ZStage.close()
        
        StopGUI.Progress.setValue(60)
        StopGUI.update()
        QApplication.processEvents()
        print("Closing Andor")
        self.SpectrometerWidget.close()
        print("Andor closed")
        
        StopGUI.Progress.setValue(80)
        StopGUI.update()
        QApplication.processEvents()
        time.sleep(0.2)
        print("Save GUI state")
        self.saveStateOnClosing()
        time.sleep(0.2)
        
        StopGUI.Progress.setValue(90)
        StopGUI.update()
        QApplication.processEvents()
        print("Closing finished successfully")
        
        StopGUI.Progress.setValue(100)
        StopGUI.update()
        QApplication.processEvents()
        time.sleep(1)
        print('Stopping GUI')
        StopGUI.close()
        print("Program exited!")
        # event.accept()
        app.quit()
        
                    
        
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
            n = QVector3D.crossProduct(self.PointsOnPlane[1]-self.PointsOnPlane[0], self.PointsOnPlane[2]-self.PointsOnPlane[0])
            s = self.PointsOnPlane[0]
            self.PlaneEquationGetZFromXandY = lambda x,y : (-n.x()*(x - s.x()) - n.y()*(y - s.y()) )/n.z() + s.z() 
            self.EdgePoints2DScan[0] = QVector3D(np.min([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.min([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.EdgePoints2DScan[1] = QVector3D(np.max([self.PointsOnPlane[0].x(), self.PointsOnPlane[1].x(),self.PointsOnPlane[2].x()]), np.max([self.PointsOnPlane[0].y(), self.PointsOnPlane[1].y(),self.PointsOnPlane[2].y()]),0)
            self.currentPosition = self.EdgePoints2DScan[0]
            self.currentPosition.setZ(self.PlaneEquationGetZFromXandY(self.currentPosition.x(), self.currentPosition.y()))
            self.TopLeft.setText('Top left [SET]')
            self.BottomRight.setText('Bottom right [SET]')
            self.Additional.setText('Additional [SET]')
        
            # self.StageLocationPlot.drawRect(self.PointsOnPlane[0].x(), self.PointsOnPlane[1].y(), abs(self.PointsOnPlane[1].x() - self.PointsOnPlane[0].x()), abs(self.PointsOnPlane[0].y()-self.PointsOnPlane[1].y()))
            
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
        self.Scanning = True
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
        
        # print('setting trigger mode to single frame...')
        # self.Camera.endImageAcquisition()
        # self.Camera.camera.frames_per_trigger_zero_for_unlimited=1   # Testing...
        # self.Camera.startImageAcquisition()
        # print('trigger mode set')
        
        while self.Scanning:
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
                    self.Scanning = False
                    break
                self.update()
                
            # Move to current position
            self.Stage.moveXTo(self.currentPosition.x())
            self.Stage.moveYTo(self.currentPosition.y())
            self.ZStage.setVoltage(self.currentPosition.z())
            self.StageLocationPlot.updateStagePos(abs(self.currentPosition.x()), abs(self.currentPosition.y()))
            
            # Wait for 1/3 of exposure time and capture image from camera        
            time.sleep(0.3*wait/1000.0)
            # start = time.time()
            # print('triggering')
            # self.Camera.camera.issue_software_trigger()
            image = self.Camera.getImageAsNumpyArray().T
            time.sleep(0.1*wait/1000.0)
            
            if self.isImageInteresting(image, enableSelectedFilters=True): 
                nr = self.saveCurrentPosition()
                _filename = path + 'Position_'+str(nr)+'_X' + str(self.Stage.getXPosition()).replace('.','p')+ '_Y' + str(self.Stage.getYPosition()).replace('.','p')+ '_Z' + str(self.ZStage.getVoltage()).replace('.','p') + '.jpg'
#                print(_filename)
                cv2.imwrite(_filename, image)
                if self.MedianEnableBlur.isChecked():
                    image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)   
                self.ImageView.setImage(image, autoRange = True, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoHistogramRange=False)
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
                print('triggering')
                #self.Camera.camera.issue_software_trigger()
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
                self.Scanning = False
                    
            # QApplication.processEvents()
        
        # self.Camera.endImageAcquisition()
        # self.Camera.camera.frames_per_trigger_zero_for_unlimited = 0   # Testing...
        # self.Camera.startImageAcquisition()
        
        print('Scan complete')
        self.stopRunningScan.hide()
        self.stopRunningScan.setChecked(False)
        self.RunScanButton.setText('Run scan')
        self.RunScanButton.setEnabled(True)
        self.RasterAndSaveAllScanButton.setEnabled(True)
        self.TimingLabel.setText("[Currently no scan running]")
        self.currentPosition = saveCurrentPositionFromBeforeScanToResetAfterwards
        self.Controller.enableAxes() 
        
        from playsound import playsound
        playsound(r'C:\Users\GloveBox\Documents\Python Scripts\GloveboxSetupGUI\angriness.mp3')
        
        
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
        self.pauseRunningScan.setChecked(False)
        self.pauseRunningScan.show()
        
        self.Scanning = True
        
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
        
        while self.Scanning:
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
                an
                if self.stopRunningScan.isChecked():
                    self.Scanning = False
                    break
                self.update()

                while self.pauseRunningScan.isChecked():
                    time.sleep(0.5)
                    # self.update()

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
                self.Scanning = False

        print('Scan complete')
        self.stopRunningScan.hide()
        self.stopRunningScan.setChecked(False)
        self.pauseRunningScan.hide()
        self.pauseRunningScan.setChecked(False)
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
            self.ROI = pg.ROI(oldGuiState['ROI_pos'] ,oldGuiState['ROI_size']) ##UNCOMMENT AFTER CORRECTING ROI
            # self.ROI = pg.ROI((0,0),(0.0008, 0.0008))
            print('ROI RESET')
        else:
            self.ROI = pg.ROI((20,20),(100,100))
        self.ROI.hide()
        self.ImageView.view.autoBtn.disconnect()
        self.ImageView.view.autoBtn.clicked.connect(lambda : self.ImageView.autoRange())
        
        self.ROI.addScaleHandle((1,1),(0,0))
        self.ImageView.addItem(self.ROI)
        self.ROI.sigRegionChanged.connect(lambda: print(self.ROI.pos(), self.ROI.size()))
        hist = self.ImageView.getHistogramWidget()
        hist.sigLevelChangeFinished.connect(self.updateBoxesFromHistogram)
        self.MeasurementLine = pg.LineSegmentROI([[10e-6, 10e-6], [50e-6,10e-6]], pen = (255, 0, 0))
        self.MeasurementLine.sigRegionChanged.connect(self.updateMeasurementLine)
        self.ImageView.addItem(self.MeasurementLine)
        _ViewBox = self.ImageView.getView().getViewBox()
        _ViewBox.disableAutoRange(_ViewBox.XYAxes)
        self.savedROIData = []
        #self.ImageView.setFixedWidth(1500)
        self.calibrationFactor = 1
        self.RCBModeOn = False
        self.counter= 0
        self.RCBImg = np.asarray(Image.open(r'C:\Users\GloveBox\Documents\Python Scripts\RCB\RCB.png'))
        self.RCBImg = self.RCBImg[::7,::7,:]
        self.Scanning = False
        
        self.NeedsAutoRange = True
        self.outlier_n = 7
        self.minimum_counts = 0
        
        self.lazyeggImg = np.asarray(Image.open(r'C:\Users\GloveBox\Documents\Python Scripts\RCB\lazyegg.png'))
        
 
        self.SpecPlot = SpecPlotGUIElement.SpecPlotGUIElement()
        self.SpecPlot.setData([650,750,850],[1,1,1]) #set initial values to prefent a division by zero exception when changing wavelenght to eV without any data.

########################################### Aidan adding click-to-move functionality ############################################
        self.StageLocationPlot = StageLocationGUIElement.StageLocationGUIElement()
        self.StageLocationPlot.StageScatterPlot.scene().sigMouseClicked.connect(self.click_to_move)
##################################################################################################   
        StartGUI =  StartAndCloseProgressWidget()
        StartGUI.show()
        QApplication.processEvents()
       
        
        self.PointsOnPlane = [object,object,object]
        self.EdgePoints2DScan = [object,object]
        self.PlaneEquationGetZFromXandY = lambda x,y : None
        
        self.Stage = ThorlabsStages.Thorlabs2DStageKinesis(SN_motor = '73126054')
        print('2D Stage initialized, Starting up Z piezo')
        
        StartGUI.Progress.setValue(10)
        StartGUI.update()
        QApplication.processEvents()
        self.ZStage = ThorlabsStages.Thorlabs1DPiezoKinesis(SN_piezo = '41106464')
        StartGUI.Progress.setValue(20)
        StartGUI.update()
        QApplication.processEvents()
        self.Shutter = ThorlabsStages.LaserShutter()
        StartGUI.Progress.setValue(30)
        StartGUI.update()
        QApplication.processEvents()
        print('Piezo initialized')
        self.Arduino = ArduinoRotationStage.ArduinoRotationStage()
        self.PA_Arduino = PA_arduino.PA_Arduino()
        time.sleep(0.5)
        StartGUI.Progress.setValue(40)
        StartGUI.update()
        QApplication.processEvents()
        print('Arduino Started')
        
        self.filterwheel = FilterWheel.ThorlabsFilterWheel(SN_wheel = 'TP02394482-18585')
        

        
        print("Initializing Linear Polarizer")
        self.LinearPolarizer = ThorlabsStages.ThorlabsCageRotator(SN_motor = '55203454') #In this version this is the analyzer 
        if self.LinearPolarizer.motor.Status.IsHomed == False:
            self.LinearPolarizer.home()
        print("Linear polarizer initialized, start HWP")
        StartGUI.Progress.setValue(50)
        StartGUI.update()
        QApplication.processEvents()
        # self.HalfWavePlate = ThorlabsStages.ThorlabsCageRotator(SN_motor = '55164594') Old HWP
        self.HalfWavePlate = ThorlabsStages.ThorlabsCageRotator(SN_motor = '55164244')
        if self.HalfWavePlate.motor.Status.IsHomed == False:
            self.HalfWavePlate.home()

        print("Halfwaveplate initialized, start MCM stage")
        StartGUI.Progress.setValue(60)
        StartGUI.update()
        QApplication.processEvents()
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
        self.GraphingWindowGroupBox = Dock('Image', size=(1000, 1500))
        self.SpecPlotWindowGroupBox = Dock('Spectrum', size=(1000, 1500))
        self.StageLocationWindowGroupBox = Dock('Stage Location', size=(1000, 1500))
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
        
        area.addDock(self.PositionListGroupBox, 'bottom', self.SpectrometerWidgetGroupBox)
        area.addDock(self.MiscGroupBox, 'bottom', self.PositionListGroupBox)
        # area.addDock(self.StageLocationWindowGroupBox, 'bottom', self.GraphingWindowGroupBox)
        # area.addDock(self.SpecPlotWindowGroupBox, 'below', self.StageLocationWindowGroupBox)
        
        area.addDock(self.SpecPlotWindowGroupBox, 'bottom', self.GraphingWindowGroupBox)
        area.addDock(self.StageLocationWindowGroupBox, 'above', self.SpecPlotWindowGroupBox)

        area.addDock(self.MiniButtonGroupBox, 'bottom', self.GraphingWindowGroupBox)
        
        
        # self.StageControlGroupBox.setOrientation(o="vertical")
        # self.ScanGroupBox.setOrientation(o="vertical")
        # self.PositionListGroupBox.setOrientation(o="vertical")
        # self.CameraSettingsGroupBox.setOrientation(o="horizontal")
        # self.SpectrometerWidgetGroupBox.setOrientation(o="vertical")
        # self.MiscGroupBox.setOrientation(o="vertical")
        # self.GraphingWindowGroupBox.setOrientation(o="vertical")
        # self.MiniButtonGroupBox.setOrientation(o="vertical")
        # self.ImageProcessingGroupBox.setOrientation(o="vertical")
        # self.PLMapGroupBox.setOrientation(o="vertical")
        
        self.GraphingWindowGroupBox.addWidget(self.ImageView)
        self.StageLocationWindowGroupBox.addWidget(self.StageLocationPlot)
        self.SpecPlotWindowGroupBox.addWidget(self.SpecPlot)


        #--------------------------------------------------------------------------------------------------------
        # Stage Control groupbox
        #--------------------------------------------------------------------------------------------------------
        
        # self.horizontalGroupBox = QGroupBox("Stage Control")
        StageControl = pg.LayoutWidget()
        # layout = QGridLayout()
        self.originalSpeed = 10.0
        self.SpeedModifier = 10.0
        self.fineSpeedModifier = 1.0
        self.XYSpeed = QSlider(Qt.Horizontal)#QProgressBar(self)
        self.XYSpeed.setMaximum( 100)
        self.XYSpeed.setTickPosition(QSlider.TicksAbove)
        self.XYSpeed.setValue( self.SpeedModifier)
        self.XYSpeed.sliderReleased.connect(self.changeXYSpeedSlider)
        
        
        self.XYSpeed.setValue(self.SpeedModifier)
        
        #self.progress.setGeometry(200, 80, 250, 20)
        StageControl.addWidget(self.XYSpeed, 0, 1, 1, 3)
        StageControl.addWidget(QLabel("XY Speed: "), 0, 0)
        StageControl.addWidget(QLabel("Z Speed: "), 1, 0)
        self.SpeedModifierFocus = 10.0
        self.ZSpeed = QSlider(Qt.Horizontal)#QProgressBar(self)
        self.ZSpeed.setTickPosition(QSlider.TicksAbove)
        self.ZSpeed.setMaximum( 100)
        self.ZSpeed.setValue( self.SpeedModifierFocus)
        self.ZSpeed.sliderReleased.connect(self.changeZSpeedSlider)
        
        StageControl.addWidget(self.ZSpeed, 1, 1, 1, 3)
        self.XPositionLabel = QLabel("--")
        self.YPositionLabel = QLabel("--")
        self.ZPositionLabel = QLabel("--")
        self.ObjectivePositionLabel = QLabel("--")
        self.LinPolLabel = QLabel("--")
        self.HWPLabel = QLabel("--")
        
        self.XMoveToSpinBox = QDoubleSpinBox()
        self.XMoveToSpinBox.setRange(0, 110)
        # self.XMoveToSpinBox.setKeyboardTracking(False)
        # self.XMoveToSpinBox.valueChanged.connect(lambda : self.Stage.moveXTo(self.XMoveToSpinBox.value()))
        self.XMoveToSpinBox.editingFinished.connect(lambda : self.Stage.moveXTo(self.XMoveToSpinBox.value()))
        self.XMoveToSpinBox.installEventFilter(self)
        StageControl.addWidget(self.XMoveToSpinBox, 2, 2)

        
        self.YMoveToSpinBox = QDoubleSpinBox()
        self.YMoveToSpinBox.setRange(0, 75)
        # self.YMoveToSpinBox.setKeyboardTracking(False)
        # self.YMoveToSpinBox.valueChanged.connect(lambda : self.Stage.moveYTo(self.YMoveToSpinBox.value()))
        self.YMoveToSpinBox.editingFinished.connect(lambda : self.Stage.moveYTo(self.YMoveToSpinBox.value()))
        self.YMoveToSpinBox.installEventFilter(self)
        StageControl.addWidget(self.YMoveToSpinBox, 3, 2)
        self.ZMoveToSpinBox = QDoubleSpinBox()
        self.ZMoveToSpinBox.setRange(0, 150)
        # self.ZMoveToSpinBox.setKeyboardTracking(False)
        # self.ZMoveToSpinBox.valueChanged.connect(lambda : self.ZStage.setVoltage(self.ZMoveToSpinBox.value()))
        self.ZMoveToSpinBox.editingFinished.connect(lambda : self.ZStage.setVoltage(self.ZMoveToSpinBox.value()))
        self.ZMoveToSpinBox.installEventFilter(self)
        StageControl.addWidget(self.ZMoveToSpinBox, 4, 2)
        self.MCMMoveToSpinBox = QDoubleSpinBox()
        self.MCMMoveToSpinBox.setRange(-50, 50)
        self.MCMMoveToSpinBox.setDecimals(4)
        # self.MCMMoveToSpinBox.setKeyboardTracking(False)
        # self.MCMMoveToSpinBox.valueChanged.connect(self.setMCMWithButton)
        self.MCMMoveToSpinBox.editingFinished.connect(self.setMCMWithButton)
        self.MCMMoveToSpinBox.installEventFilter(self)
        StageControl.addWidget(self.MCMMoveToSpinBox, 5, 2)
        self.LinPolMoveToSpinBox = QDoubleSpinBox()
        self.LinPolMoveToSpinBox.setRange(0, 360)
        # self.LinPolMoveToSpinBox.setKeyboardTracking(False)
        # self.LinPolMoveToSpinBox.valueChanged.connect(lambda : self.RotateAnalyzer(self.LinPolMoveToSpinBox.value()))
        self.LinPolMoveToSpinBox.editingFinished.connect(lambda : self.RotateAnalyzer(self.LinPolMoveToSpinBox.value()))
        self.LinPolMoveToSpinBox.installEventFilter(self)
        StageControl.addWidget(self.LinPolMoveToSpinBox, 6, 2)
        self.HWPMoveToSpinBox = QDoubleSpinBox()
        self.HWPMoveToSpinBox.setRange(0, 360)
        # self.HWPMoveToSpinBox.setKeyboardTracking(False)
        # self.HWPMoveToSpinBox.valueChanged.connect(lambda : self.RotateHWP(self.HWPMoveToSpinBox.value()))
        self.HWPMoveToSpinBox.editingFinished.connect(lambda : self.RotateHWP(self.HWPMoveToSpinBox.value()))
        self.HWPMoveToSpinBox.installEventFilter(self)
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
        btn = QPushButton("Set Analyzer")
        btn.clicked.connect(lambda : self.RotateAnalyzer(self.LinPolMoveToSpinBox.value()))
        StageControl.addWidget(btn, 6, 3)
        btn = QPushButton("Set HWP")
        btn.clicked.connect(lambda : self.RotateHWP(self.HWPMoveToSpinBox.value()))
        StageControl.addWidget(btn, 7, 3)
        
        self.analyzerlock = QCheckBox('Lock Analyzer')
        if 'analyzer_Lock' in oldGuiState:
            self.analyzerlock.setChecked(oldGuiState['analyzer_Lock'])
        if 'RotationOffset' in oldGuiState:
            self.RotationOffset = oldGuiState['RotationOffset']
        self.analyzerlock.stateChanged.connect(self.ChangeRotationOffset)
        StageControl.addWidget(self.analyzerlock, 10, 2, 1, 2)
        
        self.HWPButton = QPushButton('HWP Scan')
        self.HWPButton.clicked.connect(self.HWPscanpopup)
        
        StageControl.addWidget(self.HWPButton, 11, 0, 1, 3)
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
        
        # if 'MCMPosition' in oldGuiState:
        #     self.MCMStage.setPositionInMM(oldGuiState['MCMPosition'])
        #     self.ObjectivePositionLabel.setText(str(np.round(oldGuiState['MCMPosition'], 4)))
        # else:
        #     self.MCMStage.setPositionInMM(17.0)
        #     self.ObjectivePositionLabel.setText(str(np.round(self.MCMStage.getPositionInMM(), 4)))
        
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
        self.fineSteps = QCheckBox()#'Slow Mode')
        self.fineSteps.stateChanged.connect(self.reduceStepSize)
        self.fineSteps.setIcon(turtle)
        StageControl.addWidget(self.fineSteps, 10, 1, 1, 1)
        
        # checkbox = QCheckBox('invert X')
        # checkbox.stateChanged.connect(self.checkboxchanged)
        # layout.addWidget(checkbox, 9, 3, 1, 2)
        
        # self.BacklashCheckbox = QCheckBox('Backlash Correction')
        # layout.addWidget(self.BacklashCheckbox, 9, 0, 1, 2)
        bunny = QIcon(r"rabbit.png") 
        self.sprintCheckbox = QCheckBox()#'Fast Mode')
        self.sprintCheckbox.stateChanged.connect(self.sprintMode)
        self.sprintCheckbox.setIcon(bunny)
        StageControl.addWidget(self.sprintCheckbox, 10, 0, 1, 1)
        
        # self.HWPButton = QPushButton('HWP Scan')
        # self.HWPButton.clicked.connect(self.HWPscanpopup)
        # Misc.addWidget(self.HWPButton, 7, 0, 1, 2)
        
        # self.horizontalGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.horizontalGroupBox, 0, 1)
        # grid_layout.setRowStretch(1,0)
        

        
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
        Scan.addWidget(self.TopLeft, 2, 0, 1, 1)
        self.TopLeft.clicked.connect(self.setPoint0)
        
        self.BottomRight = QPushButton('Set bottom right corner')
        Scan.addWidget(self.BottomRight, 3, 0, 1, 1)
        self.BottomRight.clicked.connect(self.setPoint1)
        
        self.Additional = QPushButton('Set additional point on plane')
        Scan.addWidget(self.Additional, 4, 0, 1, 1)
        self.Additional.clicked.connect(self.setPoint2)
        
        self.flakebutton = QPushButton('Set Flake Image')
        Scan.addWidget(self.flakebutton, 2, 1,1, 1)
        self.flakebutton.clicked.connect(self.set_flake_image)
        
        self.blankbutton = QPushButton('Set Blank Image')
        Scan.addWidget(self.blankbutton, 3, 1, 1, 1)
        self.blankbutton.clicked.connect(self.set_blank_image)
        
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
        
        self.stopRunningScan = QCheckBox('Stop scan (be patient)')
        Scan.addWidget(self.stopRunningScan, 8, 0, 1, 1)
        self.stopRunningScan.setChecked(False)
        self.stopRunningScan.hide()

        self.pauseRunningScan = QCheckBox('Pause Scan')
        Scan.addWidget(self.pauseRunningScan, 8, 1, 1, 1)
        self.pauseRunningScan.setChecked(False)
        self.pauseRunningScan.hide()
        
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
        StartGUI.Progress.setValue(70)
        StartGUI.update()
        QApplication.processEvents()
#        self.Camera = Grasshopper3Cam.Grasshopper3Cam()
        self.Camera = ThorlabsCamera.ThorlabsCam() #[]
        StartGUI.Progress.setValue(85)
        StartGUI.update()
        QApplication.processEvents()
        print("Thorlabs Cam online, start ICMeasure cam")
        self.WhiteLightCamera = ICMeasureCamera.ICMeasureCam(name='DFK 33UX265 24910240',  videoFormat="RGB32 (2048x1536)") # 1600x1200 , 2048x1536, 1280x720
        print("ICMeasure Cam online")
        StartGUI.Progress.setValue(99)
        StartGUI.update()
        QApplication.processEvents()

        StartGUI.close()

    
        self.Controller.AxisFunctions[0] = lambda AxisValue :  self.Stage.moveXTo(self.Stage.getXPosition() - AxisValue*0.1*self.SpeedModifier/10*self.fineSpeedModifier)
        self.Controller.AxisFunctions[1] = lambda AxisValue :  self.Stage.moveYTo(self.Stage.getYPosition() + AxisValue*0.1*self.SpeedModifier/10*self.fineSpeedModifier)
        self.Controller.AxisFunctions[3] = lambda AxisValue : self.ZStage.setVoltage(self.ZStage.getVoltage() - AxisValue*0.3*self.SpeedModifierFocus/10)
        self.Controller.ButtonFunctions[0] = self.capture
        self.Controller.ButtonFunctions[1] = self.SwapWLBL
        self.Controller.ButtonFunctions[2] = self.SwapFilter
        self.Controller.ButtonFunctions[3] = self.SwapShutter
        self.Controller.ButtonFunctions[4] = self.DecreaseObjective
        self.Controller.ButtonFunctions[5] = self.IncreaseObjective
        self.Controller.ButtonFunctions[6] = lambda: self.MCMStage.setPositionInMM(self.MCMStage.getPositionInMM() - 0.05 )
        self.Controller.ButtonFunctions[7] = lambda: self.MCMStage.setPositionInMM(self.MCMStage.getPositionInMM() + 0.05 )
        self.Controller.ButtonFunctions[9] = self.snapToGrid
        self.Controller.ButtonFunctions[10] = self.sprintCheckbox.toggle
        self.Controller.ButtonFunctions[11] = self.fineSteps.toggle


        
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
        
        plotWindow3 = self.LaplacianGraph.addPlot(title="Reduced Chi Squared With Blank Image")
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
        spots =[]
        for i in range(self.SavePositionList.count()):    
            ItemText = self.SavePositionList.item(i).text()
            Elements = ItemText.split("\n")
            XString = Elements[1]
            YString = Elements[2]
            XPosition = float(XString.split(": ")[1])
            YPosition = float(YString.split(": ")[1])
            spots.append((XPosition, YPosition))
        self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)
        
        self.SavePositionList.itemDoubleClicked.connect(self.goToPositionInList)
        # self.SavePositionList.itemClicked.connect(self.highlightpoint)
        PositionList.addWidget(self.SavePositionList, 0, 0, 1, 2)
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
        btn.clicked.connect(self.AddDataToFlakeFinderDatasetpopup)
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
        
        PLMap.addWidget(QLabel('Map Height ('+ u"\u03bcm" + '):'), 1, 0, 1, 1)
        self.MapHeight = QDoubleSpinBox()
        self.MapHeight.setRange(0.001, 100)
        PLMap.addWidget(self.MapHeight, 0, 1, 1, 1)
        
        # PLMap.addWidget(QLabel('Pixel:'), 0, 2, 1, 1)
        # self.MapHeightPixel = QSpinBox()
        # self.MapHeightPixel.setRange(1, 5000)
        # PLMap.addWidget(self.MapHeightPixel, 0, 3, 1, 1)
        
        PLMap.addWidget(QLabel('Map Width ('+ u"\u03bcm" + '):'), 0, 0, 1, 1)
        self.MapWidth = QDoubleSpinBox()
        self.MapWidth.setRange(0.001, 100)
        PLMap.addWidget(self.MapWidth, 1, 1, 1, 1)
        
        # PLMap.addWidget(QLabel('Pixel:'), 1, 2, 1, 1)
        # self.MapWidthPixel = QSpinBox()
        # self.MapWidthPixel.setRange(1, 5000)
        # PLMap.addWidget(self.MapWidthPixel, 1, 3, 1, 1)
        
        self.startPLMapBtn = QPushButton('Start PL Map')
        self.startPLMapBtn.clicked.connect(self.startPLMapScan)
        PLMap.addWidget(self.startPLMapBtn, 2, 0, 1, 4)
        
        self.stopPLScan = QCheckBox('Stop scan in next iteration! (Give it time after clicking!)')
        PLMap.addWidget(self.stopPLScan, 3, 0, 1, 2)
        self.stopPLScan.setChecked(False)
        self.stopPLScan.hide()
        
        self.LaserCircleROI = pg.CircleROI( (10e-6, 10e-6), radius=10e-6 )
        
        self.ImageView.addItem(self.LaserCircleROI)
        # self.LaserCircleROI.hide()
        self.PLMapPolyline = pg.PolyLineROI([(10e-6,10e-6), (90e-6,10e-6), (90e-6,90e-6), (10e-6,90e-6)], closed=True)
        self.PLMapPolyline.sigRegionChangeFinished.connect(self.PLMapPolylineChanged)
        
        self.ImageView.addItem(self.PLMapPolyline)
        self.PLMapPolyline.hide()
        
        
        self.PLMapShowROIsCheckbox = QCheckBox('Show Helper Tools')
        self.PLMapShowROIsCheckbox.stateChanged.connect(self.togglePLMapROIs)
        PLMap.addWidget(self.PLMapShowROIsCheckbox, 4, 0, 1, 2)
        
        PLMap.addWidget(QLabel('Step Width ('+ u"\u03bcm" + '):'), 5, 0, 1, 2)
        self.PLMapStepWidth = QDoubleSpinBox()
        self.PLMapStepWidth.setRange(0.1, 5)
        self.PLMapStepWidth.setValue(0.5)
        PLMap.addWidget(self.PLMapStepWidth, 5, 3, 1, 2)
        
        self.stopPLScan.setChecked(False)
        
        
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
        # self.WLExposureSpinbox.setKeyboardTracking(False)
        # self.WLExposureSpinbox.valueChanged.connect(lambda : self.WhiteLightCamera.setExposureTime(self.WLExposureSpinbox.value()))
        self.WLExposureSpinbox.editingFinished.connect(lambda : self.WhiteLightCamera.setExposureTime(self.WLExposureSpinbox.value()))
        self.WLExposureSpinbox.installEventFilter(self)
        btn.clicked.connect(lambda : self.WhiteLightCamera.setExposureTime(self.WLExposureSpinbox.value()))
        CameraSetting.addWidget(btn, 1, 1)
        
        self.PLExposureSpinbox = QDoubleSpinBox()
        self.PLExposureSpinbox.setRange(0.1, 5000)
        self.PLExposureSpinbox.setValue(self.Camera.getExposureTime())
        # self.PLExposureSpinbox.setKeyboardTracking(False)
        # self.PLExposureSpinbox.valueChanged.connect(lambda : self.Camera.setExposureTime(self.PLExposureSpinbox.value()))
        self.PLExposureSpinbox.editingFinished.connect(lambda : self.Camera.setExposureTime(self.PLExposureSpinbox.value()))
        self.PLExposureSpinbox.installEventFilter(self)
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
        
        # CameraSetting.addWidget(QLabel('PL Filters'), 7, 0, 1, 1)
        
        self.MedianEnableBlur = QCheckBox('Blur')
        CameraSetting.addWidget(self.MedianEnableBlur, 7, 0, 1, 1)
        
        self.GaussianEnableBlur = QCheckBox('Gaussian')
        CameraSetting.addWidget(self.GaussianEnableBlur, 7, 1, 1, 1)
        
        # layout.addWidget(QLabel('Measure for '), 9, 0,1,1)
        
        self.MeasurementLengthLabel = QLabel("Line length: ?")
        CameraSetting.addWidget(self.MeasurementLengthLabel, 12, 0, 1, 1)
        
        self.ObjectiveComboBox = QComboBox()
        self.ObjectiveComboBox.addItem("10x")
        self.ObjectiveComboBox.addItem("20x")
        self.ObjectiveComboBox.addItem("50x")
        self.ObjectiveComboBox.addItem("50xIR")
        self.oldObjectiveFactor = 10
        self.ObjectiveComboBox.currentIndexChanged.connect(self.ChangeObjective)
        CameraSetting.addWidget(self.ObjectiveComboBox, 8, 1, 1, 1)
        
        self.ObjectiveLabel = QLabel('Current Objective:')
        CameraSetting.addWidget(self.ObjectiveLabel, 8, 0, 1, 1)
        
        self.WhiteLightBlueLightSliderComboBox = QComboBox()
        self.WhiteLightBlueLightSliderComboBox.addItem("White light")
        self.WhiteLightBlueLightSliderComboBox.addItem("Empty")
        self.WhiteLightBlueLightSliderComboBox.addItem("Blue light")
        self.WhiteLightBlueLightSliderComboBox.currentIndexChanged.connect(lambda idx: self.SelectSlider(idx))
        CameraSetting.addWidget(self.WhiteLightBlueLightSliderComboBox, 9, 1, 1, 1)
        
        self.SliderLabel = QLabel('Current Slider:')
        CameraSetting.addWidget(self.SliderLabel, 9, 0, 1, 1)
        
        self.FilterComboBox = QComboBox()
        self.FilterComboBox.addItem('LP 600 nm')
        self.FilterComboBox.addItem('BP 750 ± 20 nm')
        self.FilterComboBox.addItem('BP 790 ± 5 nm')
        self.FilterComboBox.addItem('BP 800 ± 5 nm')
        self.FilterComboBox.addItem('empty') #keep this one the fourth (start indexing at 0)
        self.FilterComboBox.addItem('BP 800 ± 5 nm')
        
        self.FilterComboBox.currentIndexChanged.connect(lambda idx: self.SelectFilter(idx))
        CameraSetting.addWidget(self.FilterComboBox, 10, 1, 1, 1)
        
        self.FilterLabel = QLabel('Current Filter:')
        CameraSetting.addWidget(self.FilterLabel, 10, 0, 1, 1)
        
        btn = QPushButton('Open image externally')
        btn.clicked.connect(self.openImageExternally)
        CameraSetting.addWidget(btn, 13, 0, 1, 2)
        
        btn = QPushButton('Analyze Optical Contrast')
        btn.clicked.connect(self.opticalContrastPopup)
        CameraSetting.addWidget(btn, 14, 0, 1, 2)
        
        self.ShutterLabel = QLabel('Laser Shutter:')
        CameraSetting.addWidget(self.ShutterLabel, 11, 0, 1, 1)
        
        btn = QPushButton('Shutter')
        btn.clicked.connect(self.ChangeShutter)
  #      layout.addWidget(btn, 13, 1, 1, 1)
        self.ShutterComboBox = QComboBox()
        self.ShutterComboBox.addItem("Open")
        self.ShutterComboBox.addItem("Closed")
        self.ShutterComboBox.setCurrentIndex(1)
        self.ShutterComboBox.currentIndexChanged.connect(self.ChangeShutter) 
        CameraSetting.addWidget(self.ShutterComboBox, 11, 1, 1, 1)
        
        
        CameraSetting.addWidget(QLabel('Smoothness'), 15, 0, 1, 1)
        self.ResolutionReductionComboBox = QComboBox()
        self.ResolutionReductionComboBox.addItem('Full Resolution')
        self.ResolutionReductionComboBox.addItem('Half resolution')
        
        self.ResolutionReductionComboBox.currentIndexChanged.connect(self.setCameraDivision)
        self.ResolutionReductionComboBox.setCurrentIndex(1)
        CameraSetting.addWidget(self.ResolutionReductionComboBox, 15, 1, 1, 1)
        
        # self.CameraSettingsGroupBox.setLayout(layout)
        # grid_layout.addWidget(self.CameraSettingsGroupBox, 2, 1)
        
        self.CameraSettingsGroupBox.addWidget(CameraSetting)
        
        #--------------------------------------------------------------------------------------------------------
        # Misc Groupbox
        #--------------------------------------------------------------------------------------------------------
        
 #       self.MiscGroupBox = QGroupBox("Misc")
#        layout = QGridLayout()
        Misc = pg.LayoutWidget()

        btn = QPushButton('Show/Hide Position list')
        btn.clicked.connect(self.showHidePositionList)
        Misc.addWidget(btn, 0, 0)
        self.PositionListHidden = False
        
        btn = QPushButton('Hide everything')
        btn.clicked.connect(self.hideEverything)
        Misc.addWidget(btn, 0, 1)
        
        Misc.addWidget(QLabel('Joystick for XY stage'), 1, 0)
        self.focusStageJoystickComboBox = QComboBox()
        self.focusStageJoystickComboBox.addItem('Joystick for Z Stage')
        self.focusStageJoystickComboBox.addItem('Joystick for MCM Stage')
        Misc.addWidget(self.focusStageJoystickComboBox, 1, 1) 
        
        self.OnScreenJoystick1 = pg.JoystickButton()
        self.OnScreenJoystick1.setFixedWidth(30)
        self.OnScreenJoystick1.setFixedHeight(30)
        Misc.addWidget(self.OnScreenJoystick1, 2, 0)
        
        self.OnScreenJoystick2 = pg.JoystickButton()
        self.OnScreenJoystick2.setFixedWidth(30)
        self.OnScreenJoystick2.setFixedHeight(30)
        Misc.addWidget(self.OnScreenJoystick2, 2, 1)
        
        btn = QPushButton('RCB')
        btn.clicked.connect(self.RCBFunc)
        Misc.addWidget(btn, 4, 0, 1, 2)
        
        self.closeButton = QPushButton('Close Program')
        self.closeButton.clicked.connect(self.close)
        Misc.addWidget(self.closeButton, 6, 0, 1, 2)
        
        # self.HWPButton = QPushButton('HWP Scan')
        # self.HWPButton.clicked.connect(self.HWPscanpopup)
        # Misc.addWidget(self.HWPButton, 7, 0, 1, 2)
        
        # self.ffbuttton = QPushButton('Flat Field Image')
        # self.ffbutton.clicked.connect(self.flatfield)
        # Misc.addwidget(self.ffbutton, 7, 0, 1, 1)
        
        # self.darkbuttton = QPushButton('Dark Image')
        # self.darkbutton.clicked.connect(self.darkimage)
        # Misc.addwidget(self.darkbutton, 7, 1, 1, 1)
        
        self.KeyboardControlBox = QCheckBox('Keyboard')
        self.KeyboardControlBox.stateChanged.connect(self.toggleKeyboardControl)
        Misc.addWidget(self.KeyboardControlBox, 3, 0)
        
        self.JoystickCheckBox = QCheckBox('Controller Enabled')
        self.JoystickCheckBox.setChecked(True)
        self.JoystickCheckBox.stateChanged.connect(self.toggleJoystickControl)
        Misc.addWidget(self.JoystickCheckBox, 3, 1)
  
        Misc.addWidget(QLabel("Savepath:"), 5, 0, 1, 1)
        self.ImageFolderSavePath = QLineEdit()
        self.ImageFolderSavePath.setText("")
        Misc.addWidget(self.ImageFolderSavePath, 5, 1, 1, 1)
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
        # self.showFullScreen()
        
        self.ThreadRunning = True
        self.Thread = threading.Thread(target=self.threadingFunction)
        self.Thread.start()
        self.ThreadLock = threading.Lock()
        
############################# Aidan edits ##########################################
    def eventFilter(self, object, event): # If the spinbox was just defocused then we ignore the event (return True)
        if isinstance(object, QDoubleSpinBox):
            if event.type() == QtCore.QEvent.FocusOut: 
                # event.ignore()
                # print('Enter key not pressed')
                return True
            else:
                return False
        else:
            return False
        
    
        # This function returns the QDoubleSpinBox back to its previous value... the problem is that it will move the axis to the previous value and not the label value...
    # def eventFilter(self, object, event):
    #     if isinstance(object, QDoubleSpinBox):
    #         if event.type() == QtCore.QEvent.FocusIn:
    #             self.previousObjectValue = object.value()
    #             self.previousObject = object
    #             print('Saving previous value as', self.previousObjectValue)
   
    #         if event.type() ==  QtCore.QEvent.FocusOut and object == self.previousObject: 
    #             print('Setting to previous value =', self.previousObjectValue)
    #             object.setValue(self.previousObjectValue)
            
    #         if event.type() == QtCore.QEvent.KeyRelease:
    #             if event.key() == 16777221 or event.key() == 16777220:
    #                 self.previousObjectValue = object.value()
    #                 self.previousObject = object
    #                 print('Return Key pressed')
    #         return False
                
    #     else:
    #         return False
##################################################
    
    
    def findPLMapPolylineBoundingBox(self):
        Handles = self.PLMapPolyline.getHandles()
        minX = Handles[0].pos().x()
        maxX = Handles[0].pos().x()
        minY = Handles[0].pos().y()
        maxY = Handles[0].pos().y()
        for i in range(len(Handles)):
            p = Handles[i].pos()
            x = p.x()
            y = p.y()
            if x < minX:
                minX = x
            if x > maxX:
                maxX = x
            if y < minY:
                minY = y
            if y > maxY:
                maxY = y
        
        offset = self.PLMapPolyline.pos()        
        return minX+offset.x(), maxX+offset.x(), minY+offset.y(), maxY+offset.y()
    
    def PLMapPolylineChanged(self):
       
        minX, maxX, minY, maxY = self.findPLMapPolylineBoundingBox()
                
        self.MapWidth.setValue( (maxX-minX)/1e-6 )
        self.MapHeight.setValue( (maxY-minY)/1e-6 )
        
        # LaserDiameter = self.LaserCircleROI.size().x()
        # StepWidth = self.PLMapStepWidth.value()
        # self.MapWidthPixel.setValue( int( (maxX-minX) / StepWidth))
        # self.MapHeightPixel.setValue(  int( (maxY-minY) / StepWidth))
        
    
    def togglePLMapROIs(self):
        if self.PLMapShowROIsCheckbox.isChecked():
            self.PLMapPolyline.show()
            # self.LaserCircleROI.show()
        else:
            self.PLMapPolyline.hide()
            # self.LaserCircleROI.hide()
        
    
    def changeXYSpeedSlider(self):
        self.SpeedModifier = self.XYSpeed.value()
            
    def changeZSpeedSlider(self):
        self.SpeedModifierFocus = self.ZSpeed.value()
    
    def toggleKeyboardControl(self):
        print('toggle Keyboard Controls')
        self.Controller.KeyboardModeEnabled = self.KeyboardControlBox.isChecked()
        
    def toggleJoystickControl(self):
        print('toggle Joystick Controls')
        if self.JoystickCheckBox.isChecked():
            self.Controller.enableAxes()
        else:
            self.Controller.disableAxes()
    
    def RCBFunc(self):
        if self.RCBModeOn:
            self.Camera.startImageAcquisition()
            self.WhiteLightCamera.startImageAcquisition()
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(self.saveSliderPos)
            self.ShutterComboBox.setCurrentIndex(0)
            if self.SpectrometerWidget.SpectrometerWidget != None:        
                self.SpectrometerWidget.SpectrometerWidget.coolerCheckbox.setChecked(True)
        else:
            self.Camera.endImageAcquisition()
            self.WhiteLightCamera.endImageAcquisition()
            self.saveSliderPos = self.WhiteLightBlueLightSliderComboBox.currentIndex()
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(1)
            self.ShutterComboBox.setCurrentIndex(1)
            if self.SpectrometerWidget.SpectrometerWidget != None:        
                if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                    self.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
                self.SpectrometerWidget.SpectrometerWidget.coolerCheckbox.setChecked(False)
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
            self.sprintCheckbox.setChecked(False)
            self.fineSpeedModifier = 0.01
        else:
            self.fineSpeedModifier = 1
            
        time.sleep(0.1)
    
    # Helen's edit
    def sprintMode(self):
        if self.sprintCheckbox.isChecked():
            self.fineSteps.setChecked(False)
            self.originalSpeed = self.SpeedModifier
            self.SpeedModifier = 100
        else:
            self.SpeedModifier = self.originalSpeed
            
        time.sleep(0.1)
    
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
            spots =[]
            for i in range(self.SavePositionList.count()):    
                ItemText = self.SavePositionList.item(i).text()
                Elements = ItemText.split("\n")
                XString = Elements[1]
                YString = Elements[2]
                XPosition = float(XString.split(": ")[1])
                YPosition = float(YString.split(": ")[1])
                spots.append((XPosition, YPosition))
            # print(spots)
            self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)

            
    def setPoint0(self):
        self.setPointOnPlane(0, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
        
    def setPoint1(self):
        self.setPointOnPlane(1, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
        
    def setPoint2(self):
        self.setPointOnPlane(2, self.Stage.getXPosition(), self.Stage.getYPosition(), self.ZStage.getVoltage())
    

    def openImageExternally(self):
        # XPos = self.Stage.getXPosition()
        # YPos = self.Stage.getYPosition()
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)      
            else:
                image = self.Camera.getImageAsNumpyArray().T         
            if self.GaussianEnableBlur.isChecked():
                image = cv2.GaussianBlur(image,(5,5),0)
                
            win = pg.image(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoRange = True, autoHistogramRange=False, pos = (0, 0), scale=(self.calibrationFactor, self.calibrationFactor))
            win.view=pg.PlotItem()
        else:
            image = np.flip(self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2), 0)
            win = pg.image(image, autoLevels=False, levels=(self.ColorScaleMin.value(), self.ColorScaleMax.value()), autoRange = True, autoHistogramRange=False, pos = (0, 0), scale=(self.calibrationFactor, self.calibrationFactor))
            win.view=pg.PlotItem()
        
        whiteLightBlueLightFactor = self.WhiteLightBlueLightSliderComboBox.currentIndex()
        # objectiveFactor = float(self.ObjectiveComboBox.currentText()[0:2])
        text = pg.TextItem(text='Estimated length: ? \u03bcm', color = (255, 255, 255), border = 'w')
        MeasurementLine2 = pg.LineSegmentROI([[10e-6, 10e-6], [30e-6,10e-6]], pen = (255, 0, 0))
        MeasurementLine2.sigRegionChanged.connect(lambda: self.updateMeasurementLine2(MeasurementLine2, text, whiteLightBlueLightFactor))
        win.addItem(MeasurementLine2)
        win.addItem(text)
        
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:  
            win.setLevels(self.MonoScaleMin.value(), self.MonoScaleMax.value())
        else:
            win.setLevels(self.ColorScaleMin.value(), self.ColorScaleMax.value())
      
    def saveCurrentPosition(self):
        nr = self.SavePositionList.count()
        self.SavePositionList.addItem("Position "+str(nr)+"\n  X: " + str(self.Stage.getXPosition()) + "\n  Y: " + str(self.Stage.getYPosition()) + "\n  Z: " + str(self.ZStage.getVoltage()))
        
        spots =[]
        for i in range(self.SavePositionList.count()):    
            ItemText = self.SavePositionList.item(i).text()
            Elements = ItemText.split("\n")
            XString = Elements[1]
            YString = Elements[2]
            XPosition = float(XString.split(": ")[1])
            YPosition = float(YString.split(": ")[1])
            spots.append((XPosition, YPosition))
        print(spots)
        self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)
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
        
    def highlightpoint(self):
        self.SavePositionList.currentRow()
        
    def click_to_move(self, evt):
        if evt.button() == 1 and evt.double() == True:
            mousePoint =  self.StageLocationPlot.StagePlotWindowItem.vb.mapSceneToView(evt.scenePos())
            self.Stage.moveXTo(mousePoint.x())
            self.Stage.moveYTo(mousePoint.y())
            self.StageLocationPlot.updateStagePos(mousePoint.x(), mousePoint.y())
            
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
        # GaAs - 870 nm - (x,y) = (5.22, 71.02)
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
        
        spots =[]
        for i in range(self.SavePositionList.count()):    
            ItemText = self.SavePositionList.item(i).text()
            Elements = ItemText.split("\n")
            XString = Elements[1]
            YString = Elements[2]
            XPosition = float(XString.split(": ")[1])
            YPosition = float(YString.split(": ")[1])
            spots.append((XPosition, YPosition))
        print(spots)
        self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)
        
        
    def snapToGrid(self):
        try:
            height = self.PlaneEquationGetZFromXandY(self.Stage.getXPosition(), self.Stage.getYPosition())
            self.ZStage.setVoltage(height)
        except AttributeError:
            print('Corners not set')
            pass
            
    def IncreaseObjective(self):
        if '50xIR' not in self.ObjectiveComboBox.currentText():
            self.ObjectiveComboBox.setCurrentIndex(self.ObjectiveComboBox.currentIndex()+1)
            time.sleep(0.5)
            print('Increasing Objective')
        else:
            print('cannot increase further')  
        
        
    def DecreaseObjective(self):
        if '10x' not in self.ObjectiveComboBox.currentText():
            print('Decreasing Objective (overshooting for backlash)')
            self.ObjectiveComboBox.setCurrentIndex(self.ObjectiveComboBox.currentIndex()-1)
            time.sleep(0.5)
        else:
            print('cannot deacrease further') 
        
        
    def ChangeObjective(self):
        objectiveBeforeRotating = self.oldObjectiveFactor
        
        self.NewObjectivePosition = self.Arduino.Ypresetpositions[str(self.ObjectiveComboBox.currentText())]
        try:
            if self.NewObjectivePosition < self.OldObjectivePosition:
                self.Arduino.moveRelativemm('Y', -1.03)
        except AttributeError:
            pass
        self.Arduino.moveAbsolutemm('Y', self.Arduino.Ypresetpositions[str(self.ObjectiveComboBox.currentText())])
        objectiveFactor = float(self.ObjectiveComboBox.currentText()[0:2])    
        scaling = objectiveBeforeRotating/objectiveFactor
        
        self.OldObjectivePosition = self.Arduino.Ypresetpositions[str(self.ObjectiveComboBox.currentText())]
        
        self.oldObjectiveFactor = objectiveFactor
        
        sc = self.MeasurementLine.getState()
        sc['pos'] = [self.MeasurementLine.pos().x()*scaling, self.MeasurementLine.pos().y()*scaling]
        sc['size'] = [self.MeasurementLine.size().x()*scaling, self.MeasurementLine.size().y()*scaling] #[10/objectiveFactor, 0]
        self.MeasurementLine.setState(sc)
        
        sc = self.LaserCircleROI.getState()
        sc['pos'] = [self.LaserCircleROI.pos().x()*scaling, self.LaserCircleROI.pos().y()*scaling]
        sc['size'] = [self.LaserCircleROI.size().x()*scaling, self.LaserCircleROI.size().y()*scaling] #[10/objectiveFactor, 0]
        self.LaserCircleROI.setState(sc)
        
        

        # if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            # self.ROI.setPos(pg.Point(self.ROI.pos().x()*objectiveFactor/objectiveBeforeRotating, self.ROI.pos().y()*objectiveFactor/objectiveBeforeRotating))
            # self.ROI.setSize(pg.Point(self.ROI.size().x()*objectiveFactor/objectiveBeforeRotating, self.ROI.size().y()*objectiveFactor/objectiveBeforeRotating))

        sc2 = self.ROI.getState()
        # print(sc2)
        
        sc2['pos'] =[ self.ROI.pos().x()*scaling, self.ROI.pos().y()*scaling]
        sc2['size'] = [self.ROI.size().x()*scaling, self.ROI.size().y()*scaling]
        # print(sc2)
        self.ROI.setState(sc2, update=True)
        self.ROI.update()
            
        self.updateMeasurementLine()
        self.NeedsAutoRange = True
        
    def SwapWLBL(self):
        yoffset = -0.0578
        xoffset = 0.0982
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() != 0:
            if self.WhiteLightBlueLightSliderComboBox.currentIndex() ==2:
                self.Stage.moveXTo(self.Stage.getXPosition() - xoffset) 
                self.Stage.moveYTo(self.Stage.getYPosition() - yoffset) 
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(0)

        else:
            self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(2)
            self.Stage.moveXTo(self.Stage.getXPosition() + xoffset) 
            self.Stage.moveYTo(self.Stage.getYPosition() + yoffset) 


    def SelectSlider(self, idx):
        # target = self.WhiteLightBlueLightSliderComboBox.currentText()
        # self.Arduino.moveAbsolutemm('X', self.Arduino.Xpresetpositions[str(target)])
        ###
        # INSERT PA motor code here
        if idx==0:
            new_pos = 'WL'
        elif idx==1:
            new_pos = 'Empty'
        elif idx==2:
            new_pos = 'BL'
        self.PA_Arduino.moveTo(new_pos)
        ###
        
        if idx == 0: 
             self.Camera.endImageAcquisition()#
             self.WhiteLightCamera.startImageAcquisition()   
             self.ROI.hide()
        if idx == 2:
            self.WhiteLightCamera.endImageAcquisition()
            self.Camera.startImageAcquisition()#
            self.ROI.show()
        QApplication.processEvents()
        time.sleep(0.02)
        QApplication.processEvents()
        
        objectiveFactor = float(self.ObjectiveComboBox.currentText()[0:1])
        sc = self.MeasurementLine.getState()
        sc['pos'] = [10e-6/objectiveFactor, 10e-6/objectiveFactor]
        sc['points'] = [[0, 0], [40e-6/objectiveFactor, 0]]
        sc['size'] = [1/objectiveFactor, 0]
        self.MeasurementLine.setState(sc)
        self.updateMeasurementLine()
        self.NeedsAutoRange = True
        
    def SelectFilter(self, idx):
        if idx == 4:                                # If the selected value is the empty position
            self.PLExposureSpinbox.setValue(1)
            self.Camera.setExposureTime(1)
            self.MonoScaleMax.setValue(220)
        else:
            self.PLExposureSpinbox.setValue(300)
            self.Camera.setExposureTime(300)
            self.MonoScaleMax.setValue(15)    
        self.filterwheel.SetPosition(idx+1)
            
        
    def SwapFilter(self):
        currentidx = int(self.filterwheel.GetPosition()) - 1
        if currentidx == 4: # If the current position is in the empty position then go to 750 +/- 40 nm
            self.FilterComboBox.setCurrentIndex(1)
        else: # Otherwise go to the empty position
            self.FilterComboBox.setCurrentIndex(4)
            
    def RotateHWP(self, angle): 
        angle = float(angle)           ##################### All HWP commands are in units of the polarization of light, i.e."angle" = light angle
        HWPangle = angle/2
        if self.analyzerlock.isChecked():
            print('moving Analyzer to angle ' + str((angle + self.RotationOffset)))
            self.LinearPolarizer.moveToDeg((angle + self.RotationOffset))
            print('moving HWP to angle ' + str(HWPangle) + ', HWPunits = '+ str(HWPangle))
            self.HalfWavePlate.moveToDeg(HWPangle)
        else:
            print('moving HWP to angle ' +str(HWPangle) + ', HWPunits = '+ str(HWPangle))
            self.HalfWavePlate.moveToDeg(HWPangle)

    def RotateAnalyzer(self, angle): 
        angle = float(angle)
        if self.analyzerlock.isChecked():
            HWPangle = angle - self.RotationOffset/2
            print('moving Analyzer to angle ' + str(angle))
            self.LinearPolarizer.moveToDeg(angle)
            print('moving HWP to angle ' + str(HWPangle))
            self.HalfWavePlate.moveToDeg(HWPangle)
        else:
            print('moving Analyzer to angle ' +str(angle))
            self.LinearPolarizer.moveToDeg(angle)

    def ChangeRotationOffset(self):
        if self.analyzerlock.isChecked():
            self.RotationOffset = self.LinearPolarizer.getRotation() - 2*self.HalfWavePlate.getRotation()
            print('Rotation offset = ', self.RotationOffset)
        else:
            pass
        
    def HWPscanpopup(self):
        self.hwpscandialog = QDialog()
        self.hwpscandialog.start = QDoubleSpinBox()
        self.hwpscandialog.start.setValue(0)
        self.hwpscandialog.start.setRange(0,360)
        self.hwpscandialog.stop = QDoubleSpinBox()
        self.hwpscandialog.stop.setValue(359)
        self.hwpscandialog.stop.setRange(0, 360)
        self.hwpscandialog.step = QDoubleSpinBox()
        self.hwpscandialog.step.setValue(1)
        self.hwpscandialog.startscan = QPushButton('Start')
        self.hwpscandialog.cancel = QCheckBox('Cancel')
        self.hwpscandialog.startscan.clicked.connect(self.HWPscan)
        self.HWPscanprogress = QProgressBar()
        
        layout = QGridLayout()
        layout.addWidget(QLabel("HWP Start: ") , 1,0)
        layout.addWidget(self.hwpscandialog.start, 1,1)
        layout.addWidget(self.hwpscandialog.stop, 2,1)
        layout.addWidget(QLabel("HWP Stop: "), 2,0)
        layout.addWidget(self.hwpscandialog.step, 3,1)
        layout.addWidget(QLabel("HWP Step: "), 3,0)
        layout.addWidget(self.hwpscandialog.cancel, 4,0 )
        layout.addWidget(self.hwpscandialog.startscan, 4,1 )
        layout.addWidget(self.HWPscanprogress, 5, 0, 1, 2)
        self.hwpscandialog.setLayout(layout)
        self.hwpscandialog.show()


    def opticalContrastPopup(self):
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            image = self.Camera.getImageAsNumpyArray().T
            sendImage = self.Camera.getImageAsNumpyArray()
            if self.MedianEnableBlur.isChecked():
                image = cv2.medianBlur(self.Camera.getImageAsNumpyArray().T,5)
                sendImage = cv2.medianBlur(self.Camera.getImageAsNumpyArray(),5)
            win = pg.image(image, autoLevels=False, levels=(self.MonoScaleMin.value(), self.MonoScaleMax.value()), autoRange = True, autoHistogramRange=False, pos = (0, 0))
            win.view=pg.PlotItem()
            win.setLevels(self.MonoScaleMin.value(), self.MonoScaleMax.value())
        else:
            image = np.flip(self.WhiteLightCamera.getImageAsNumpyArray().transpose(1,0,2), 0)
            sendImage = self.WhiteLightCamera.getImageAsNumpyArray()
            win = pg.image(image, autoLevels=False, levels=(self.ColorScaleMin.value(), self.ColorScaleMax.value()), autoRange = True, autoHistogramRange=False, pos = (0, 0))
            win.view=pg.PlotItem()
            win.setLevels(self.ColorScaleMin.value(), self.ColorScaleMax.value())
        
        drawLine = pg.LineSegmentROI([[10, 0], [100,10]], pen = (255, 0, 0))
        win.addItem(drawLine)
        
        try:
            if self.opticalContrastGraph:
                del self.opticalContrastGraph
                self.opticalContrastGraph = pg.GraphicsWindow(title='Optical Contrast')
        except:
                self.opticalContrastGraph = pg.GraphicsWindow(title='Optical Contrast')
                
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 0:
            plotWindow = self.opticalContrastGraph.addPlot(title='Green Channel Optical Contrast', row=0, col=0)
            try:
                if self.opticalContrastPlot:
                    del self.opticalContrastPlot
                    self.opticalContrastPlot = plotWindow.plot([0,0,0])
            except:
                self.opticalContrastPlot = plotWindow.plot([0,0,0])
                plotWindow.addItem(self.opticalContrastPlot)
            
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
            plotWindow = self.opticalContrastGraph.addPlot(title='Mono Optical Contrast', row=0, col=0)
            try:
                if self.opticalContrastPlot:
                    del self.opticalContrastPlot
                    self.opticalContrastPlot = plotWindow.plot([0,0,0])
            except:
                self.opticalContrastPlot = plotWindow.plot([0,0,0])
                plotWindow.addItem(self.opticalContrastPlot)
        else:
            pass
        
        #Add button to Graphics Window
        proxy = QGraphicsProxyWidget()
        btn = QPushButton('Load saved image')
        proxy.setWidget(btn)
        
        button = self.opticalContrastGraph.addLayout(row=1, col=0)
        button.addItem(proxy, row=1, col=1)
        btn.clicked.connect(self.readImage)

        self.opticalContrastGraph.move(200, 200)
        self.opticalContrastGraph.show()
        
        drawLine.sigRegionChanged.connect(lambda: self.plotContrast(sendImage, drawLine))
    
    def plotContrast(self, image, drawLine):
        # pts = drawLine.listPoints()
        print(drawLine.listPoints())
        pos = drawLine.pos()
        xstart = int(drawLine.listPoints()[0].x() + pos.x())
        ystart = int(drawLine.listPoints()[0].y() + pos.y())
        xend = int(drawLine.listPoints()[1].x() + pos.x())
        yend = int(drawLine.listPoints()[1].y() + pos.y())
        line = np.transpose(np.array(draw.line(xstart, ystart, xend, yend)))
        data = image.copy()[line[:, 1], line[:, 0], :]
        
        if image.ndim == 2:
            data = image.copy()[line[:, 1], line[:, 0]]
            self.opticalContrastPlot.setData(data, pen=(255, 0, 0))
        if np.array_equal(image[:, :, 0], image[:, :, 1]):
            self.opticalContrastPlot.setData(data[:, 1], pen=(255, 0, 0))
            # self.plotWindow.plot(data)
        else:
            self.opticalContrastPlot.setData(data[:, 1], pen=(0,255,0))
            # self.plotWindow.plot(data[:, 1])
    
    def readImage(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open Image', '', "Image Files (*.png *.jpg *.bmp)")
        # print(fileName[0])
        image = cv2.imread(str(fileName[0]))
        sendImage = image
        
        try:
            if np.array_equal(image[:, :, 0], image[:, :, 1]):
                image=cv2.rotate(np.flip(image, 0), cv2.ROTATE_90_CLOCKWISE)
                print(image.shape)
                win = pg.image(image, autoLevels=False, autoRange = True, autoHistogramRange=False, pos = (0, 0))
                win.view=pg.PlotItem()
                win.setLevels(self.MonoScaleMin.value(), self.MonoScaleMax.value())
            else:
                image[:, :, [2, 0]] = image[:, :, [0, 2]]
                image=cv2.rotate(np.flip(image, 0), cv2.ROTATE_90_CLOCKWISE)
                print(image.shape)
                win = pg.image(image, autoLevels=False, autoRange = True, autoHistogramRange=False, pos = (0, 0))
                win.view=pg.PlotItem()
                win.setLevels(self.ColorScaleMin.value(), self.ColorScaleMax.value())
            
            drawLine = pg.LineSegmentROI([[10, 10], [100 ,10]], pen = (255, 0, 0))
            win.addItem(drawLine)
            
            try:
                if self.opticalContrastGraph:
                    del self.opticalContrastGraph
                    self.opticalContrastGraph = pg.GraphicsWindow(title='Optical Contrast')
            except:
                self.opticalContrastGraph = pg.GraphicsWindow(title='Optical Contrast')
            
            if np.array_equal(image[:, :, 0], image[:, :, 1]):
                plotWindow = self.opticalContrastGraph.addPlot(title='Mono Optical Contrast', row=0, col=0)
            else:
                 plotWindow = self.opticalContrastGraph.addPlot(title='Green Channel Optical Contrast', row=0, col=0)               
            
            try:
                if self.opticalContrastPlot:
                    del self.opticalContrastPlot
                    self.opticalContrastPlot = plotWindow.plot([0,0,0])
            except:
                self.opticalContrastPlot = plotWindow.plot([0,0,0])
                plotWindow.addItem(self.opticalContrastPlot)
            
            self.opticalContrastGraph.move(200, 200)
            self.opticalContrastGraph.show()
            
            drawLine.sigRegionChanged.connect(lambda: self.plotContrast(sendImage, drawLine))
        
        except:
            print('Oops! Something went wrong')
    
    def HWPscan(self):
        self.hwpscandialog.startscan.setEnabled(False)
        self.hwpscandialog.start.setEnabled(False)
        self.hwpscandialog.stop.setEnabled(False)
        self.hwpscandialog.step.setEnabled(False)
        if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                print("Spectrometer is in continous mode! Does not work!!")
                self.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
                self.SpectrometerWidget.SpectrometerWidget.ContinousMode = False
                print("Disabled continous mode")
            
        self.Controller.disableAxes()
        
        StartTimeFull = datetime.datetime.now()
        path = r"D:\Data\HWP_scan/"
        path = path + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S')
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of directory %s failed" % path)
            return
        else:
            print ("Successfully created directory %s " % path)
        path = path + "/"
        
        angles =np.arange(self.hwpscandialog.start.value(), self.hwpscandialog.stop.value(), self.hwpscandialog.step.value(), dtype = float)
        print(angles)
        
        if self.ShutterComboBox.currentIndex() == 1:
            print("opening shutter")
            self.SwapShutter()
        
        i=0
        for angle in angles:
            # self.update()
            self.HWPscanprogress.setValue(100*i/len(angles))
            i+=1
            QApplication.processEvents()
            angle = float(angle)
            HWPangle = angle/2

            if self.hwpscandialog.cancel.isChecked():
                print('Scan Cancelled')
                break
            else:
                if self.analyzerlock.isChecked():
                    print('moving Analyzer to angle ' + str((angle + self.RotationOffset)))
                    self.LinearPolarizer.moveToDeg(angle + self.RotationOffset)
                    print('moving HWP to angle ' + str(angle) + ', HWPunits = '+ str(HWPangle))
                    self.HalfWavePlate.moveToDeg(HWPangle)
                else:
                    self.HalfWavePlate.moveToDeg(HWPangle)
                    print('moving HWP to angle ' + str(angle) + ', HWPunits = '+ str(HWPangle))

                print('taking spec')
                spec = self.SpectrometerWidget.SpectrometerWidget.takeSpectrum()
                self.SpecPlot.setData(self.SpectrometerWidget.SpectrometerWidget.wl_calibration , spec, pen=(0,0,255))
                np.savez(path + str(angle).replace('.','_') , spec = spec, wls = self.SpectrometerWidget.SpectrometerWidget.wl_calibration, angle = angle )

        self.hwpscandialog.close()
        print("closing shutter")
        self.SwapShutter()
        plot_func = Aidan_quickplot.plot()
        plot_func.plotAndFit(path)
        self.Controller.enableAxes() 
        # self.HWPscanpopup.close()
        
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
        if self.ImageFolderSavePath.text() == "":
            folder = str(QFileDialog.getExistingDirectory(self, "Select Directory to save"))
            self.ImageFolderSavePath.setText(folder)
        else:
            folder = self.ImageFolderSavePath.text()
        path = folder +"/"
        path = path + str(datetime.datetime.now()).replace(':','-').replace('.','-').replace(' ','_')
        path = path + "_X" + str(self.XPositionLabel.text()).replace('.','p') + "_Y" + str(self.YPositionLabel.text()).replace('.','p')
        path = path + "_" + str(self.ObjectiveComboBox.currentText())
        if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2: 
            if self.FilterComboBox.currentIndex() == 0:
                _filename = path + '_bl_LP.jpg'
            elif self.FilterComboBox.currentIndex() == 1:
                _filename = path + '_bl_F2.jpg'
            elif self.FilterComboBox.currentIndex() == 2:
                _filename = path + '_bl_F3.jpg'
            else:
                _filename = path + '_bl.jpg'
            self.Camera.saveImageAsJpg(filename=_filename)
        else:
            _filename = path + '_wl.jpg'
            tempSave = self.WhiteLightCamera.CameraResolutionDivider
            self.WhiteLightCamera.CameraResolutionDivider = 1 # set to always take fullscreen image
            self.WhiteLightCamera.saveImageAsJpg(filename=_filename)
            self.WhiteLightCamera.CameraResolutionDivider = tempSave
        QMessageBox.about(self, "Image saved", "Saved image:\n\r"+_filename)
    
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
        # data_obj['MCMPosition'] = float(self.ObjectivePositionLabel.text())
        
        data_obj['ROI_pos'] = self.ROI.pos()
        data_obj['ROI_size'] = self.ROI.size()
        
        data_obj['analyzer_Lock'] = self.analyzerlock.isChecked()
        try:
            data_obj['RotationOffset'] = self.RotationOffset
        except AttributeError:
            pass
        
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
            try:
                self.StageLocationPlot.addRect(SavedCorners['PointsOnPlane'][0].x(), SavedCorners['PointsOnPlane'][1].y(), abs(SavedCorners['PointsOnPlane'][0].x() - SavedCorners['PointsOnPlane'][1].y()), abs(SavedCorners['PointsOnPlane'][0].y()-SavedCorners['PointsOnPlane'][1].y()))
            except AttributeError:
                print('StagePlotWindowItem doesnt exist yet')
        path = folder + "/*.jpg"
        files = glob.glob(path)   
        for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
            stripPath = name[(len(folder)+1):] 
            NameParts = stripPath.split('_')
            self.SavePositionList.addItem(NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
        
        spots =[]
        for i in range(self.SavePositionList.count()):    
            ItemText = self.SavePositionList.item(i).text()
            Elements = ItemText.split("\n")
            XString = Elements[1]
            YString = Elements[2]
            XPosition = float(XString.split(": ")[1])
            YPosition = float(YString.split(": ")[1])
            spots.append((XPosition, YPosition))
        print(spots)
        self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)
        
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
        # calibrationNormalized = 0
        # if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 0:
        #     calibrationNormalized = 130/1611.2541*50.0*100/97.8 * self.WhiteLightCamera.CameraResolutionDivider
        # if self.WhiteLightBlueLightSliderComboBox.currentIndex() == 2:
        #     calibrationNormalized = 150/1083.1395*50.0*100/96
        # calibrationFactor = calibrationNormalized / float(self.ObjectiveComboBox.currentText()[0:2])
        
        self.MeasurementLengthLabel.setText("Estimated length: "+str(np.round(L*1e6,4)) + u" \u03bcm")
    
    #Helen's formerly ugly, now very beautiful edit
    def updateMeasurementLine2(self, MeasurementLine2, text, whiteLightBlueLightFactor):
        pts = MeasurementLine2.listPoints()
        delta = pts[1] - pts[0]
        L = np.sqrt(delta.x()**2 + delta.y()**2)
        # calibrationNormalized = 0
        # if whiteLightBlueLightFactor == 0:
        #     calibrationNormalized = 130/1611.2541*50.0*100/97.8 * self.WhiteLightCamera.CameraResolutionDivider
        # if whiteLightBlueLightFactor == 2:
        #     calibrationNormalized = 150/1083.1395*50.0*100/96
        # calibrationFactor = calibrationNormalized / objectiveFactor
        text.setText('Estimated length: ' + str(np.round(L*1e6,4)) + u" \u03bcm")
        
    def resetSliderandComboboxes(self):
        self.Arduino.reset()
        self.ObjectiveComboBox.setCurrentIndex(0)

    def PLMapisPointWithinPolygon(self, point):
        
        Handles = self.PLMapPolyline.getHandles()
        PolyLineOffset = self.PLMapPolyline.pos()
        x0 = (point.x() - PolyLineOffset[0], point.y() - PolyLineOffset[1] )
        
        Angle = 0
        for i in range(len(Handles)):
            if i < len(Handles)-1:
                t = Handles[i].pos()
                x1 = (t.x(), t.y())
                t = Handles[i+1].pos()
                x2 = (t.x(), t.y())
      
            else:
                t = Handles[i].pos()
                x1 = (t.x(), t.y())
                t = Handles[0].pos()
                x2 = (t.x(), t.y())
            
            #print(x0,x1,x2)
            av = np.subtract(x1, x0)
            a = np.linalg.norm(av)
            bv = np.subtract(x2, x0)
            b = np.linalg.norm(bv)
            cv = np.subtract(x2, x1)
            c = np.linalg.norm(cv)
            
            Gamma = np.arccos( (a*a + b*b - c*c) / ( 2*a*b ) )
            CrossProduct = np.cross( (cv[0],cv[1],0), (av[0],av[1],0)  )
            DeltaAngle = Gamma*np.sign(CrossProduct[2])
            # print(i, DeltaAngle/np.pi*180)
            Angle += DeltaAngle
            
                

        if 355 < np.mod(np.abs(Angle/np.pi*180),360.0) < 365 or -5 < np.mod(np.abs(Angle/np.pi*180),360.0) < 5 and np.abs(Angle/np.pi*180) > 300:
            return True
        else:
            return False


    def startPLMapScan(self):
        if self.SpectrometerWidget.SpectrometerWidget != None:        
            if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
                print("Spectrometer is in continous mode! Does not work!!")
                self.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
                self.SpectrometerWidget.SpectrometerWidget.ContinousMode = False
                print("Disabled continous mode")
            
            self.Controller.disableAxes()
            if self.ShutterComboBox.currentIndex() == 1:
                print("opening shutter")
                self.SwapShutter()
            self.stopPLScan.show()
            self.startPLMapBtn.setText('Mapping')
            self.startPLMapBtn.setEnabled(False)
            
            H = float(self.MapHeight.value())*1e-6#*0.001
            # H_px = self.MapHeightPixel.value()
                
            W = float(self.MapWidth.value())*1e-6#*0.001
            # W_px = self.MapWidthPixel.value()
                
            wl = self.SpectrometerWidget.SpectrometerWidget.wl_calibration
                
            offset_x = np.arange(-float(W*0.5), float(W*0.5)+(self.PLMapStepWidth.value()*1e-6), self.PLMapStepWidth.value()*1e-6)#np.linspace(-float(W*0.5),float(W*0.5),W_px) 
            offset_y = np.arange(-float(H*0.5), float(H*0.5)+(self.PLMapStepWidth.value()*1e-6), self.PLMapStepWidth.value()*1e-6)# np.linspace(-float(H*0.5),float(H*0.5),H_px)
            
            H_px = len(offset_y)
            W_px = len(offset_x)
            #-----------
            # move LAser to center of thePolzLineshape
            #-----------
            WrongStartingPosition_x = self.Stage.getXPosition()*0.001
            WrongStartingPosition_y = self.Stage.getYPosition()*0.001
            
            BBox_minX,BBox_maxX,BBox_minY,BBox_maxY = self.findPLMapPolylineBoundingBox()
            
            Shift_x_InMeters = 1* ( ( BBox_minX + W*0.5 ) - ( self.LaserCircleROI.pos().x() + 0.5 * self.LaserCircleROI.size().x() ) )
            Shift_y_InMeters = 1* (( BBox_minY + H*0.5 ) - ( self.LaserCircleROI.pos().y() + 0.5 * self.LaserCircleROI.size().y() ) )
            
            print("Calculating RelevanceMap")
            ShouldPointBeTaken = np.ones( (H_px*W_px)+1 )
            mapcheckCounter = 0
            for current_offset_y in offset_y:
                curr_y = ( BBox_minY + H*0.5 ) + current_offset_y
                for current_offset_x in offset_x:
                    mapcheckCounter = mapcheckCounter + 1
                    curr_x = ( BBox_minX + W*0.5 ) + current_offset_x
                    self.LaserCircleROI.setPos( QPointF(curr_x,curr_y))
                    self.update()
                    # QApplication.processEvents()  
                    
                    if self.PLMapisPointWithinPolygon( QPointF(curr_x, curr_y) ) == True:
                        ShouldPointBeTaken[mapcheckCounter] = 1
                    else:
                        ShouldPointBeTaken[mapcheckCounter] = 0
            print(ShouldPointBeTaken)
            print("Done calculating positions")
            
            if self.ShutterComboBox.currentIndex() == 1:
                print("opening shutter")
                self.SwapShutter()
            
            
            self.Stage.moveXTo(WrongStartingPosition_x*1000.0 + Shift_x_InMeters*1000.0)
            self.Stage.moveYTo(WrongStartingPosition_y*1000.0 - Shift_y_InMeters*1000.0)
            
            
            
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
            PLMapSubprocessQueue.put(['Ux', InitialPosition_x + offset_x*1000 ])
            PLMapSubprocessQueue.put(['Uy', InitialPosition_y + offset_y*1000 ])
            
           
            
            counter = 0
            for current_offset_y in offset_y:
                curr_y = InitialPosition_y - current_offset_y*1000
                self.Stage.moveYTo(float(curr_y))
                for current_offset_x in offset_x:
                    
                    if self.stopPLScan.isChecked():
                        # spec = np.zeros(len(wl))
                            
                        # data[counter,0] = curr_x
                        # data[counter,1] = curr_y
                        # data[counter,2:] = spec
                        # PLMapSubprocessQueue.put(['spec', curr_x, curr_y, counter-1, spec])
                        
                        # # time.sleep(1)
                        
                        # self.update()
                        # QApplication.processEvents()
                        # continue
                        break
                
                    curr_x = InitialPosition_x + current_offset_x*1000
                    counter = counter + 1 # 
                    
                    if ShouldPointBeTaken[counter] == 1:
                        # print(curr_x)
                        self.Stage.moveXTo(float(curr_x))
                        # time.sleep(1)
                        
                        print(curr_x, " take spectrum")
                        # self.eventLoop()
                            
                        
                        time.sleep(0.1)
                        spec = self.SpectrometerWidget.SpectrometerWidget.takeSpectrum() #np.random.randint(1000,size=len(wl))#
                            
                        data[counter,0] = curr_x
                        data[counter,1] = curr_y
                        data[counter,2:] = spec
                        PLMapSubprocessQueue.put(['spec', curr_x, curr_y, counter-1, spec])
                        
                        # time.sleep(1)
                        
                        # self.update()
                        # QApplication.processEvents()
                    else:
                        print(curr_x, " skip point")
                        
                        spec = np.zeros(len(wl))  #np.random.randint(1000,size=len(wl))#
                            
                        data[counter,0] = curr_x
                        data[counter,1] = curr_y
                        data[counter,2:] = spec
                        PLMapSubprocessQueue.put(['spec', curr_x, curr_y, counter-1, spec])
                        
                        # time.sleep(1)
                        
                        # self.update()
                        # QApplication.processEvents()
            
            print('Saving data')
            path = r"C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI\SavedPLMapData/"
            StartTimeFull = datetime.datetime.now()
            path = path + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S')        
            np.savetxt(path, data, delimiter='\t')
            
            self.Stage.moveXTo(WrongStartingPosition_x*1000.0)
            self.Stage.moveYTo(WrongStartingPosition_y*1000.0)
                
            self.startPLMapBtn.setText('Start PL Map')
            self.startPLMapBtn.setEnabled(True)
            self.stopPLScan.setChecked(False)
            self.stopPLScan.hide()
            
            self.SwapShutter()
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

    def AddDataToFlakeFinderDatasetpopup(self, filenames):
        self.adddata_dialog = QDialog()
        self.adddata_dialog.bpflakeimage_checkbox = QCheckBox("Add Flakes to BP labelled data?")
        self.adddata_dialog.bpblankimage_checkbox = QCheckBox("Add Blanks to BP labelled data?")
        self.adddata_dialog.wseflakeimage_checkbox = QCheckBox("Add Flakes to WSe2 labelled data?")
        self.adddata_dialog.wseblankimage_checkbox = QCheckBox("Add Blanks to WSe2 labelled data?")
        self.adddata_dialog.done = QPushButton('Done')
        self.adddata_dialog.done.clicked.connect(self.importFlakeTinderLikes)
        layout = QGridLayout()
        layout.addWidget(self.adddata_dialog.bpflakeimage_checkbox, 0,0)
        layout.addWidget(self.adddata_dialog.bpblankimage_checkbox, 1,0)
        layout.addWidget(self.adddata_dialog.wseflakeimage_checkbox, 2,0)
        layout.addWidget(self.adddata_dialog.wseblankimage_checkbox, 3,0)
        layout.addWidget(self.adddata_dialog.done, 4,0 )
        self.adddata_dialog.setLayout(layout)
        self.adddata_dialog.setMinimumSize(100,100)
        self.adddata_dialog.setWindowTitle("Do you want to add these to the labelled data set?")
        self.adddata_dialog.show()

        
    def importFlakeTinderLikes(self):
        global CurrentTinderFiles
        global ListOfLikes
        global CurrentTinderFolder 
        import shutil

        if self.adddata_dialog.bpflakeimage_checkbox.isChecked():
            for LikedIndex in ListOfLikes:
                oldfile = CurrentTinderFiles[LikedIndex]
                newfilename = r'C:\Users\GloveBox\Documents\Python Scripts\ScanImages\BP labelled data\yes/' + 'yes_' + os.path.basename(os.path.dirname(oldfile)) + os.path.basename(oldfile)
                shutil.copy(oldfile, newfilename)
        if self.adddata_dialog.bpblankimage_checkbox.isChecked():
            notLiked = [i for i in CurrentTinderFiles if i not in CurrentTinderFiles[LikedIndex]]
            for file in notLiked:
                newfilename = r'C:\Users\GloveBox\Documents\Python Scripts\ScanImages\BP labelled data\no/' + 'no_' + os.path.basename(os.path.dirname(file)) + os.path.basename(file)
                shutil.copy(file, newfilename)
                
        if self.adddata_dialog.wseflakeimage_checkbox.isChecked():
            for LikedIndex in ListOfLikes:
                oldfile = CurrentTinderFiles[LikedIndex]
                newfilename = r'C:\Users\GloveBox\Documents\Python Scripts\ScanImages\WSe2 labelled data\yes/' + 'yes_' + os.path.basename(os.path.dirname(oldfile)) + os.path.basename(oldfile)
                shutil.copy(oldfile, newfilename)
        if self.adddata_dialog.wseblankimage_checkbox.isChecked():
            notLiked = [i for i in CurrentTinderFiles if i not in CurrentTinderFiles[LikedIndex]]
            for file in notLiked:
                newfilename = r'C:\Users\GloveBox\Documents\Python Scripts\ScanImages\WSe2 labelled data\no/' + 'no_' + os.path.basename(os.path.dirname(file)) + os.path.basename(file)
                shutil.copy(file, newfilename)
            
        for LikedIndex in ListOfLikes: 
            name = CurrentTinderFiles[LikedIndex]
            stripPath = name[(len(CurrentTinderFolder)+1):] 
            NameParts = stripPath.split('_')
            self.SavePositionList.addItem("Liked " + NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
        self.adddata_dialog.close()
        
        spots =[]
        for i in range(self.SavePositionList.count()):    
            ItemText = self.SavePositionList.item(i).text()
            Elements = ItemText.split("\n")
            XString = Elements[1]
            YString = Elements[2]
            XPosition = float(XString.split(": ")[1])
            YPosition = float(YString.split(": ")[1])
            spots.append((XPosition, YPosition))
        self.StageLocationPlot.StagePositionListPlot.setData(pos = spots)
        
class StartAndCloseProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        self.Progress = QProgressBar()
        self.Progress.setValue(0)
        grid_layout.addWidget(self.Progress)        
     
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
    # MainWindow.showMaximized()
    # MainWindow.showNormal()
    # MainWindow.showFullScreen()
    MainWindow.show()
    sys.exit(app.exec_())
