# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 15:02:56 2020

@author: marku
"""

import numpy as np

import sys
import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

from PyQt5.QtWidgets import QGraphicsProxyWidget, QWidget, QGridLayout, QApplication, QComboBox, QCheckBox
from PyQt5.QtCore import QRect 

class SpecPlotGUIElement(pg.GraphicsWindow):

    def __init__(self):      
        super().__init__()
         
        self.SpecViewLabel = pg.LabelItem(justify = "bottom")
        self.addItem(self.SpecViewLabel,0,2,1,3)#2,2,1,3)
        
        self.SpecPlotWindowItem = self.addPlot(1,0,1,3)#1,0,1,3)
        self.SpecPlot = self.SpecPlotWindowItem.plot([0,0,0])
        self.SpecPlotWindowItem.addItem(self.SpecPlot)
        
        self.SpecViewLabel.setText("x = %0.2f, <span style='color: black'> y = %0.2f" % (0, 0))
        self.SpecPlot.scene().sigMouseMoved.connect(self.mouseMovedInSpecWindow)
        self.SpecPlotWindowItem.setLabel('left', text='Intensity', units='counts')
        self.SpecPlotWindowItem.setLabel('bottom', text='Wavelength', units=None)
        # self.SpecPlotWindowItem.enableAutoSIPrefix(False)
        
        proxy = QGraphicsProxyWidget()
        self.xAxisCalibrationComboBox = QComboBox()
        self.xAxisCalibrationComboBox.addItem('Wavelength (nm)')
        self.xAxisCalibrationComboBox.addItem('Energy (eV)')
        self.xAxisCalibrationComboBox.addItem('Wavenumber (cm^-1)')
        self.xAxisCalibrationComboBox.currentIndexChanged.connect(self.updateXAxisCalibration)
        # self.xAxisCalibrationComboBox.setGeometry(QRect(40, 40, 491, 3100))
        self.previousUnitIndex = 0 
        proxy.setWidget(self.xAxisCalibrationComboBox)
        self.addItem(proxy,0,0,1,1) #2,0,1,1)
        
        proxy = QGraphicsProxyWidget()
        self.SpecPlotLockToPointCheckbox = QCheckBox('Lock cursor to point')
        self.SpecPlotLockToPointCheckbox.setStyleSheet("background-color: rgb(255,255,255);");
        self.SpecPlotLockToPointCheckbox.setChecked(True)
        proxy.setWidget(self.SpecPlotLockToPointCheckbox)
        self.addItem(proxy,0,1,1,1)#2,1,1,1)
        
        self.SpecPlotCursorLineX = pg.InfiniteLine(pos=0, angle=90, movable=False, pen=(150,125,125))
        self.SpecPlotCursorLineY = pg.InfiniteLine(pos=0, angle=0, movable=False, pen=(150,125,125))
        self.SpecPlotWindowItem.addItem(self.SpecPlotCursorLineX)
        self.SpecPlotWindowItem.addItem(self.SpecPlotCursorLineY)

    def setData(self, x, y , pen=(0,0,255)):
        
        if self.xAxisCalibrationComboBox.currentIndex() == 0:
            self.SpecPlot.setData(x , y, pen=pen)
            self.SpecPlotWindowItem.setLabel('bottom', text='Wavelength (nm)', units=None)
            
        elif self.xAxisCalibrationComboBox.currentIndex() == 1:
            self.SpecPlot.setData(np.divide(1240, x) , y, pen=pen)
            self.SpecPlotWindowItem.setLabel('bottom', text='Energy (eV)', units=None)
            
        elif self.xAxisCalibrationComboBox.currentIndex() == 2:
            self.SpecPlot.setData(np.divide(1e7,532) - np.divide(1e7, x) , y, pen=pen)
            self.SpecPlotWindowItem.setLabel('bottom', text='Raman Shift (cm^-1)', units=None)

    def updateXAxisCalibration(self):
        x = self.SpecPlot.xData
        y = self.SpecPlot.yData
        pen=(0,0,255)

        if self.xAxisCalibrationComboBox.currentIndex() == 0: 
            if self.previousUnitIndex == 1:
                self.SpecPlot.setData(np.divide(1240, x) , y)                                                # from eV to nm 
            elif self.previousUnitIndex == 2:
                self.SpecPlot.setData(np.divide(1,(np.divide(1, 532)-1e-7*x)) , y, pen=pen)           # from cm^-1 to nm
            self.SpecPlotWindowItem.setLabel('bottom', text='Wavelength (nm)', units=None)
            
        elif self.xAxisCalibrationComboBox.currentIndex() == 1: 
            if self.previousUnitIndex == 0:
                self.SpecPlot.setData(np.divide(1240, x) , y)                                                # from nm to eV (correct)
            elif self.previousUnitIndex == 2:
                self.SpecPlot.setData(np.divide(1240, np.divide(1,(np.divide(1, 532)-1e-7*x)))  , y, pen=pen)            # from cm^-1 to eV
            self.SpecPlotWindowItem.setLabel('bottom', text='Energy (eV)', units=None)
            
        elif self.xAxisCalibrationComboBox.currentIndex() == 2: 
            if self.previousUnitIndex == 0:
                self.SpecPlot.setData(np.divide(1e7,532) - np.divide(1e7, x)  , y)                                    # from nm to cm^-1       
            elif self.previousUnitIndex ==1:
                self.SpecPlot.setData(np.divide(1e7,532) - np.divide(1e7, np.divide(1240,x))  , y)                  # from eV to cm^-1
            self.SpecPlotWindowItem.setLabel('bottom', text='Raman Shift (cm^-1)', units = None)
            
        self.previousUnitIndex = self.xAxisCalibrationComboBox.currentIndex()

                
    def mouseMovedInSpecWindow(self, evt):
        mousePoint = self.SpecPlotWindowItem.vb.mapSceneToView(evt)
        
        x = self.SpecPlot.xData
        # if self.xAxisCalibrationComboBox.currentIndex() ==0:
        #     x = 1e-9*x
        y = self.SpecPlot.yData
        ind = np.argmin(np.abs(np.subtract(x, mousePoint.x())))
        if self.xAxisCalibrationComboBox.currentIndex() == 0:
            self.SpecViewLabel.setText("Mouse: x = %0.3f, y = %0.3f | Closest data point to X:  x = %0.3f, y = %0.3f " % (mousePoint.x(), mousePoint.y(), x[ind], y[ind]))
        else:
            self.SpecViewLabel.setText("Mouse: x = %0.3f, y = %0.3f | Closest data point to X:  x = %0.3f, y = %0.3f " % (mousePoint.x(), mousePoint.y(), x[ind], y[ind]))
        
        
        if self.SpecPlotLockToPointCheckbox.isChecked():
            self.SpecPlotCursorLineX.setPos(x[ind])   
            self.SpecPlotCursorLineY.setPos(y[ind]) 
        else:
            self.SpecPlotCursorLineX.setPos(mousePoint.x())   
            self.SpecPlotCursorLineY.setPos(mousePoint.y()) 


class TestSpecPlotGUIElement_GUI(QWidget):

    def __init__(self):      
        super().__init__()
        self.basic_layout = QGridLayout()
        
        self.SpecView = SpecPlotGUIElement()
        self.SpecView.setData([650,750,850],[1,5,3])
        self.basic_layout.addWidget(self.SpecView)
        self.setLayout(self.basic_layout)
        
         
        
    def closeEvent(self, event):
        
        event.accept()
        if __name__ == '__main__': 
            app.quit() 
        
        
if __name__ == '__main__':
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    MainWindow = TestSpecPlotGUIElement_GUI()
    MainWindow.show()
    sys.exit(app.exec_())