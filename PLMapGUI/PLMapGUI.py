# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 20:28:53 2020

@author: marku
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 20:17:21 2020

@author: marku
"""


import numpy as np

import sys
import datetime



import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
import pyqtgraph.console
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
from fitfunctions import *
from scipy.optimize import curve_fit
from PyQt5.QtWidgets import QFileDialog, QSplitter, QInputDialog, QLineEdit, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QPlainTextEdit, QCheckBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QPointF
from PyQt5 import QtWidgets

class PLMapGUI(QtGui.QMainWindow):

    def __init__(self, subprocessqueue=[]):      
        super().__init__()
#        grid_layout = QGridLayout()
#        self.setLayout(grid_layout)
        
        
        
        #data
        self.En = []
        self.x = []
        self.y = []
        self.data = []
        
        self.num_points = 0
        
        #initial guess
        self.pposE = [250] 
        self.skew = [0]     
        self.amps = [4000]
        self.widths = [10]
        
        self.CurrentlySelectedIndex = 0
        
        self.num_peaks = len(self.pposE)
        
        #initial fitting parameters
        self.p0 = np.zeros(4*self.num_peaks)      
        self.upper_bound = np.zeros(4*self.num_peaks)
        self.lower_bound = np.zeros(4*self.num_peaks) 
        self.xpx = np.zeros(self.num_peaks)
        
        #fitting results
        self.opt_param = []
        self.opt_param_err = []
        self.param_map = []
        self.ind_map = []
        self.ExampleFigure = {}
        
        area=DockArea()
        self.setCentralWidget(area)
        self.setWindowTitle('Raman and PL Map Evaluation')
       
        #
        # grid_layout = QGridLayout()
        # self.setLayout(grid_layout)
        
        
        
        #
        DockDock = Dock("Map", size=(500,400))
        
        mapDock = QSplitter(Qt.Vertical)#Dock("Map", size=(500,400))
        
            
        area.addDock(DockDock, 'left')
        DockDock.addWidget(mapDock)
        
        mapWin = QSplitter(Qt.Horizontal)#pg.LayoutWidget()
        
        self.OverviewFig1 = pg.ImageView(view=pg.PlotItem())
        self.OverviewFig1.setColorMap(pg.ColorMap([0,1],[[255,255,255],[255,0,0]]))
        
        self.OverviewFig2 = pg.ImageView(view=pg.PlotItem())
        self.OverviewFig2.setColorMap(pg.ColorMap([0,1],[[255,255,255],[0,0,255]]))
        
        
        
        mapWin.addWidget(self.OverviewFig1)

        mapWin.addWidget(self.OverviewFig2)
        
        mapDock.addWidget(mapWin)
        
        self.CricleROI = pg.CircleROI( [0,0],  size=1, pen='k')
        self.OverviewFig1.addItem(self.CricleROI)
        self.CricleROI.hide()
        
        self.CricleROI2 = pg.CircleROI( [0,0],  size=1, pen='k')
        self.OverviewFig2.addItem(self.CricleROI2)
        self.CricleROI2.hide()

        mapWin = QSplitter(Qt.Horizontal)#pg.LayoutWidget()

        self.ExampleFig = pg.GraphicsWindow(title="Example Spectrum (move circle in map to change)")
        
        self.ExamplePlot1 = self.ExampleFig.addPlot(title="Example Spectrum (move circle in summed intensity map to change)")
        self.ExampleSpectrumPlot = self.ExamplePlot1.plot([0,0,0], pen=pg.mkPen('k', width=1, style=QtCore.Qt.SolidLine))
        self.FitInitialGuessPlot = self.ExamplePlot1.plot([0,0,0], pen=pg.mkPen('r', width=0.5, style=QtCore.Qt.DashLine))
        
        mapWin.addWidget(self.ExampleFig)
        
        self.ExampleFig2 = pg.GraphicsWindow(title="Example Spectrum")
        
        self.ExamplePlot2 = self.ExampleFig2.addPlot(title="Example Spectrum")
        self.ExampleSpectrumPlot2 = self.ExamplePlot2.plot([0,0,0])
        self.FitResultPlot = self.ExamplePlot2.plot([0,0,0], pen=pg.mkPen('r', width=0.5, style=QtCore.Qt.DashLine))
        mapWin.addWidget(self.ExampleFig2)

        mapDock.addWidget(mapWin)

        ###MapDock
        mapWin = pg.LayoutWidget()

        # self.mapCanvas =pg.LayoutWidget()
        # mapWin.addWidget(self.mapCanvas)

        button = QPushButton('Load map')
        mapWin.addWidget(button)
        button.clicked.connect(self.loadMap)
        
        button = QPushButton('Save data')
        mapWin.addWidget(button)
        button.clicked.connect(self.saveData)
        
        self.WhatToPlotCombobox = QComboBox()
        self.WhatToPlotCombobox.addItem('Summed')
        self.WhatToPlotCombobox.addItem('Maximum')
        mapWin.addWidget(self.WhatToPlotCombobox)
        
        self.RamanMapComboBoxWhichFitParameter = QComboBox()
        self.RamanMapComboBoxWhichFitParameter.addItem('1. Gaussian')
        self.RamanMapComboBoxWhichFitParameter.currentIndexChanged.connect(self.getParameter)
        mapWin.addWidget(self.RamanMapComboBoxWhichFitParameter)
        
        button = QPushButton('+')
        mapWin.addWidget(button)
        button.clicked.connect(lambda : self.RamanMapComboBoxWhichFitParameter.addItem(str(self.addGaussian())+'. Gaussian'))
        
        button = QPushButton('-')
        mapWin.addWidget(button)
        button.clicked.connect(self.removeGaussianFromRamanMap)
        
        
        mapWin.addWidget( QLabel('Center:'))
        self.centerEdit = QLineEdit()
        self.centerEdit.setText('250')
        self.centerEdit.returnPressed.connect(self.renewMapParameter)
        mapWin.addWidget(self.centerEdit)
        
        mapWin.addWidget( QLabel('Amplitude:'))
        self.amplEdit = QLineEdit()
        self.amplEdit.setText('4000')
        self.amplEdit.returnPressed.connect(self.renewMapParameter)
        mapWin.addWidget(self.amplEdit)
        
        mapWin.addWidget( QLabel('Width:'))
        self.widthEdit = QLineEdit()
        self.widthEdit.setText('10')
        self.widthEdit.returnPressed.connect(self.renewMapParameter)
        mapWin.addWidget(self.widthEdit)
        
        mapWin.addWidget( QLabel('Offset:'))
        self.skewEdit = QLineEdit()
        self.skewEdit.setText('0')
        self.skewEdit.returnPressed.connect(self.renewMapParameter)
        mapWin.addWidget(self.skewEdit)
        
        button = QPushButton('Calculate')
        mapWin.addWidget(button)
        button.clicked.connect(lambda : self.calculate(self.RamanMapComboBoxWhichFitParameter.currentIndex()))
        
        mapDock.addWidget(mapWin)
        
        mapWin = QSplitter(Qt.Horizontal)#pg.LayoutWidget()
        
        self.subfig1 = pg.ImageView(view=pg.PlotItem())
        self.subfig1.setColorMap(pg.ColorMap([0,1],[[255,255,255],[255,0,0]]))
        
        self.subfig2 = pg.ImageView(view=pg.PlotItem())
        self.subfig2.setColorMap(pg.ColorMap([0,1],[[255,255,255],[0,0,255]]))
        
        self.subfig3 = pg.ImageView(view=pg.PlotItem())
        self.subfig3.setColorMap(pg.ColorMap([0,1],[[255,255,255],[0,0,255]]))
        
        # mapWin.nextRow()
        
        mapWin.addWidget(self.subfig1)
        mapWin.addWidget(self.subfig2)
        mapWin.addWidget(self.subfig3)
        
        self.CricleROI3 = pg.CircleROI( [0,0],  size=1, pen='k')
        self.subfig1.addItem(self.CricleROI3)
        self.CricleROI3.hide()
        
        self.CricleROI4 = pg.CircleROI( [0,0],  size=1, pen='k')
        self.subfig2.addItem(self.CricleROI4)
        self.CricleROI4.hide()
        
        self.CricleROI5 = pg.CircleROI( [0,0],  size=1, pen='k')
        self.subfig3.addItem(self.CricleROI5)
        self.CricleROI5.hide()
        
        mapDock.addWidget(mapWin)
        
        self.Title = 's'
        
        self.UpdateTimer = {}
        self.GUIisSubprocessed = False
        if subprocessqueue != []:
            self.GUIisSubprocessed = True
            self.SubprocessQueue = subprocessqueue
            
            self.UpdateTimer = QTimer()
            self.UpdateTimer.timeout.connect(self.updateGUI)
            self.UpdateTimer.start(10)
        
        
        
    def updateGUI(self):
        try:
            QueueResult = self.SubprocessQueue.get(block=False)
            
        except:
            return
        
        self.updateMapFromSubprocess(QueueResult)
        # if QueueResult[0] == "SxSy":
        #     self.Title = self.Title + 'sz:' + str(QueueResult[1]) + 'x' + str(QueueResult[2])
            
        # if QueueResult[0] == "spec":
        #     self.Title = self.Title + 'spc:x' + str(QueueResult[1]) + ',y ' + str(QueueResult[2]) + 'dat:' + str(QueueResult[3])
            
        # self.setWindowTitle(self.Title)
        
        
        

    def renewMapParameter(self):
        self.renewParameter(self.centerEdit.text(), self.amplEdit.text(), self.widthEdit.text(), self.skewEdit.text(), self.RamanMapComboBoxWhichFitParameter.currentIndex())
        # self.centerEdit.setText(str(center))
        # self.amplEdit.setText(str(ampl))
        # self.widthEdit.setText(str(width))
        
    def getParameter(self):
        (center, ampl, width) = self.getParameterForIndex(self.RamanMapComboBoxWhichFitParameter.currentIndex())
        self.centerEdit.setText(str(center))
        self.amplEdit.setText(str(ampl))
        self.widthEdit.setText(str(width))
        
    def removeGaussianFromRamanMap(self):
        
        self.removeGaussian(self.RamanMapComboBoxWhichFitParameter.currentIndex())
        self.RamanMapComboBoxWhichFitParameter.removeItem(self.RamanMapComboBoxWhichFitParameter.count()-1)
        self.getParameter()
    
    
        
# Override closeEvent! thereby problems running the script from spyder versions 3.3.6 and upwards should be amended    
    def closeEvent(self, event):
        if self.GUIisSubprocessed:
            self.UpdateTimer.stop()
        print("Program exited!")
        event.accept()
        if __name__ == '__main__': 
            app2.quit()
       
        
    def drawImage(self, WindowNumber, x, y, Z, autoscale=True):
        if WindowNumber == 0:
            win = self.subfig1
        elif WindowNumber == 1:
            win = self.subfig2
        elif WindowNumber == 2:
            win = self.OverviewFig1
        elif WindowNumber == 3:
            win = self.OverviewFig2
        else:
            win = self.subfig3 # = drawImage(4,...) .. not consistent with the rest, because it was added later
        S = np.shape(Z)
        win.imageItem.resetTransform()
        win.setImage(np.flip(Z.T,1), autoRange=autoscale, autoLevels=autoscale, autoHistogramRange=autoscale)
        
        win.imageItem.translate(x[0], y[0])
        win.imageItem.scale( (y[-1]-y[0])/S[0], (x[-1]-x[0])/S[1]) # this is stragne. I removed the transposte above on setImage(Z.T) and flipped x and y and it seems a little better
        
        if autoscale:
            win.autoRange()
            win.autoLevels()
        win.view.invertY(False)

            
        win.view.setLabel('left', text='y', units='mm')
        win.view.setLabel('bottom', text='x', units='mm')
        
    
    def updateMapFromSubprocess(self, command):
        
        if command[0] == "SxSy":
            self.data = np.zeros( (  command[1], command[2] ) )
            self.En = np.zeros(command[2])
            self.x = np.zeros(command[1])
            self.y = np.zeros(command[1])
            return
        
        if command[0] == "wl":
            # print(command[1])
            self.En = np.array(command[1])
            return
        
        if command[0] == "Ux":
            # print("xu transfer", command[1])
            self.xu = command[1]
            return
        
        if command[0] == "Uy":
            # print("yu transfer", command[1])
            self.yu = command[1]
            return
            
        if command[0] == "spec":
            self.x[command[3]] = command[1]
            self.y[command[3]] = command[2]
            self.data[command[3],:] = command[4]
            
        
         
        
        self.num_points = len(self.x)
        self.opt_param = np.zeros([self.num_points, 4*self.num_peaks])
        
        #do fitting and ploting after loading the file
#        print('x', self.x, 'y', self.y, 'data', self.data, 'En', self.En)
        self.setFittingParameter()
        # self.startFitting()
        # self.plotMap()
        
       
        self.OverviewFig1.imageItem.resetTransform()
        #Think about this....
        
        # print("xu",self.xu)
        # print("yu",self.yu)
        if command[0] == "spec" and command[3] == 0:
            self.drawImage(2,[np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)],np.reshape(np.sum(self.data,axis=1), [len(self.yu), len(self.xu)]), autoscale=True)
        else:
            self.drawImage(2,[np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)],np.reshape(np.sum(self.data,axis=1), [len(self.yu), len(self.xu)]), autoscale=False)
       
        
        self.OverviewFig1.view.setTitle('Summed intensity')
        
        # self.subfig1.imshow(np.reshape(np.sum(self.data,axis=1), [np.size(xu), np.size(yu)]), cmap='Reds') # extent=[np.min(self.x),np.max(self.x),np.min(self.y),np.max(self.y)]
        # self.subfig1.set_title('Summed image (px not micrometer)')
        
        if command[0] == "spec" and command[3] == 0:
            self.ExampleSpectrumPlot.setData(self.En, self.data[int(len(self.data)/2), :])
            self.ExampleSpectrumPlot2.setData(self.En, self.data[int(len(self.data)/2), :])
            
            
            self.CenterLine = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex], angle=90, movable=True, pen=(125,0,0))
            self.Width1 = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex]+ self.widths[self.CurrentlySelectedIndex]/2, angle=90, movable=True, pen=(0,0,255))
            self.Width2 = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex]- self.widths[self.CurrentlySelectedIndex]/2, angle=90, movable=True, pen=(0,0,255))
            self.AmplLine = pg.InfiniteLine(self.amps[self.CurrentlySelectedIndex], angle=0, movable=True, pen=(125,0,0))
            self.OffsetLine = pg.InfiniteLine(self.skew[0], angle=0, movable=True, pen=(125,125,125))
               
            self.CenterLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.CenterLine.value(), self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            self.Width1.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], 2.0*np.abs(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()]-self.Width1.value()), self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            self.Width2.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], 2.0*np.abs(self.Width2.value()-self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()]), self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            self.AmplLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.abs(self.AmplLine.value()-self.skew[0]), self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            self.OffsetLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.abs(self.AmplLine.value()-self.OffsetLine.value()), self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.min([self.OffsetLine.value(), self.AmplLine.value()]), self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            
            self.ExamplePlot1.addItem(self.CenterLine)
            self.ExamplePlot1.addItem(self.Width1)
            self.ExamplePlot1.addItem(self.Width2)
            self.ExamplePlot1.addItem(self.AmplLine)
            self.ExamplePlot1.addItem(self.OffsetLine)
            
            
            self.SumSpecLine1 = pg.InfiniteLine(self.En[0], angle=90, movable=True, pen=(0,0,255))
            self.SumSpecLine2 = pg.InfiniteLine(self.En[-1], angle=90, movable=True, pen=(0,0,255))
            self.SumSpecLine1.sigPositionChangeFinished.connect(self.updateSummedAreaPlot)
            self.SumSpecLine2.sigPositionChangeFinished.connect(self.updateSummedAreaPlot)
            self.ExamplePlot2.addItem(self.SumSpecLine1)
            self.ExamplePlot2.addItem(self.SumSpecLine2)
            
            # self.AxisClicker = self.Fig.canvas.mpl_connect('button_press_event', self.onclick_event)# self.subfig2.plot( self.data[:, event.xdata*event.ydata] ))
            
            # self.subfig2.plot(self.En, self.data[int(len(self.data)/2), :] )
            # self.subfig2.set_title('Example spectrum (click in map left to change)')
            self.CricleROI.show()
            self.CricleROI.setPos( (command[1],command[2]) )
            self.CricleROI.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
            self.CricleROI.sigRegionChangeFinished.connect(self.onclick_event)
            
            self.CricleROI2.show()
            self.CricleROI2.setPos( (command[1],command[2]) )
            self.CricleROI2.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
            self.CricleROI2.sigRegionChangeFinished.connect(self.onclick_event)
            
            self.CricleROI3.show()
            self.CricleROI3.setPos( (command[1],command[2]) )
            self.CricleROI3.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
            self.CricleROI3.sigRegionChangeFinished.connect(self.onclick_event)
            
            self.CricleROI4.show()
            self.CricleROI4.setPos( (command[1],command[2]) )
            self.CricleROI4.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
            self.CricleROI4.sigRegionChangeFinished.connect(self.onclick_event)
            
            self.CricleROI5.show()
            self.CricleROI5.setPos( (command[1],command[2]) )
            self.CricleROI5.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
            self.CricleROI5.sigRegionChangeFinished.connect(self.onclick_event)
            
            
            # self.draw()


    def saveData(self):
        if self.En == []:
            print('No data! Check acquisition!')
        else:
            # sizeXY = len(self.x)
            # valuesWithoutEn = np.hstack((self.x.reshape(sizeXY, 1), self.y.reshape(sizeXY, 1), self.data))
            # output = np.vstack(([' ', ' '] + self.En, valuesWithoutEn))
            
            S = np.shape(self.data)
            dataToExport = np.zeros( ( S[0]+1, S[1]+2) )
            dataToExport[0,2:] = self.En
            dataToExport[1:,0] = self.x
            dataToExport[1:,1] = self.y
            dataToExport[1:,2:] = self.data
            
            path = r"C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI\SavedPLMapData/"
            StartTimeFull = datetime.datetime.now()
            pathRawData = path  + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S') + '_rawData'        
            np.savetxt(pathRawData, dataToExport, delimiter='\t')
            pathFitParam = path + StartTimeFull.strftime('%Y-%m-%d_%H-%M-%S')  + '_FitParam'
            np.savetxt(pathFitParam, self.opt_param, delimiter= '\t')
            
    
    def loadMap(self):
        temp = []
        mapFileName = QFileDialog.getOpenFileName()[0]
        temp = np.loadtxt(mapFileName, encoding='latin1', dtype='str', comments='#', delimiter='\t')
        self.En = temp[0,2:].astype(np.float)
        self.x = temp[1:,0].astype(np.float)
        self.y = temp[1:,1].astype(np.float)
        self.data = temp[1:, 2:].astype(np.float) 
        
        self.xu = np.unique(np.trim_zeros(self.x, trim='b'))
        self.yu = (np.unique(np.trim_zeros(self.y, trim='b')))
        # self.yu = self.yu[::-1]
        # self.yu = self.yu[0:-1]
        
        # self.xu = np.unique((self.x))
        # self.yu = np.unique((self.y))
        
        
        # print(self.x, self.xu, self.y, self.yu)
        print(self.xu, self.yu)
        self.num_points = len(self.xu)*len(self.yu)
        print(len(self.xu), len(self.yu))
        temp = self.data[0:(self.num_points),:]
        self.data = temp
        self.opt_param = np.zeros([self.num_points, 4*self.num_peaks])
        self.FittedDataAvailable = False
        #do fitting and ploting after loading the file
#        print('x', self.x, 'y', self.y, 'data', self.data, 'En', self.En)
        self.setFittingParameter()
        # self.startFitting()
        # self.plotMap()
        
        
        
        # self.drawImage(0, xu, yu,np.reshape(np.sum(self.data,axis=1), [np.size(xu), np.size(yu)]))
        self.OverviewFig1.imageItem.resetTransform()
        # self.OverviewFig1.setImage(np.reshape(np.sum(self.data,axis=1), [np.size(self.xu), np.size(self.yu)]).T)
        self.drawImage(2,[np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)],np.reshape(np.sum(self.data,axis=1), [len(self.yu), len(self.xu)]))
       
        
        self.OverviewFig1.view.setTitle('Summed intensity')
        
        # self.subfig1.imshow(np.reshape(np.sum(self.data,axis=1), [np.size(xu), np.size(yu)]), cmap='Reds') # extent=[np.min(self.x),np.max(self.x),np.min(self.y),np.max(self.y)]
        # self.subfig1.set_title('Summed image (px not micrometer)')
        
        
        
        self.ExampleSpectrumPlot.setData(self.En, self.data[int(len(self.data)/2), :])
        self.ExampleSpectrumPlot2.setData(self.En, self.data[int(len(self.data)/2), :])
        
        self.CenterLine = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex], angle=90, movable=True, pen=(125,0,0))
        self.Width1 = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex]+ self.widths[self.CurrentlySelectedIndex]/2, angle=90, movable=True, pen=(0,0,255))
        self.Width2 = pg.InfiniteLine(self.pposE[self.CurrentlySelectedIndex]- self.widths[self.CurrentlySelectedIndex]/2, angle=90, movable=True, pen=(0,0,255))
        self.AmplLine = pg.InfiniteLine(self.amps[self.CurrentlySelectedIndex], angle=0, movable=True, pen=(125,0,0))
        self.OffsetLine = pg.InfiniteLine(self.skew[0], angle=0, movable=True, pen=(125,125,125))
        
        self.CenterLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.CenterLine.value(), self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
        self.Width1.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], 2.0*np.abs(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()]-self.Width1.value()), self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
        self.Width2.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.amps[self.RamanMapComboBoxWhichFitParameter.currentIndex()], 2.0*np.abs(self.Width2.value()-self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()]), self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
        self.AmplLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.abs(self.AmplLine.value()-self.skew[0]), self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], self.skew[0], self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
        self.OffsetLine.sigPositionChangeFinished.connect( lambda _ : self.renewParameter(self.pposE[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.abs(self.AmplLine.value()-self.OffsetLine.value()), self.widths[self.RamanMapComboBoxWhichFitParameter.currentIndex()], np.min([self.OffsetLine.value(), self.AmplLine.value()]), self.RamanMapComboBoxWhichFitParameter.currentIndex() ))
            
        
        self.ExamplePlot1.addItem(self.CenterLine)
        self.ExamplePlot1.addItem(self.Width1)
        self.ExamplePlot1.addItem(self.Width2)
        self.ExamplePlot1.addItem(self.AmplLine)
        self.ExamplePlot1.addItem(self.OffsetLine)
        
        
        self.SumSpecLine1 = pg.InfiniteLine(self.En[0], angle=90, movable=True, pen=(0,0,255))
        self.SumSpecLine2 = pg.InfiniteLine(self.En[-1], angle=90, movable=True, pen=(0,0,255))
        self.SumSpecLine1.sigPositionChangeFinished.connect(self.updateSummedAreaPlot)
        self.SumSpecLine2.sigPositionChangeFinished.connect(self.updateSummedAreaPlot)
        self.ExamplePlot2.addItem(self.SumSpecLine1)
        self.ExamplePlot2.addItem(self.SumSpecLine2)
        
        # self.AxisClicker = self.Fig.canvas.mpl_connect('button_press_event', self.onclick_event)# self.subfig2.plot( self.data[:, event.xdata*event.ydata] ))
        
        # self.subfig2.plot(self.En, self.data[int(len(self.data)/2), :] )
        # self.subfig2.set_title('Example spectrum (click in map left to change)')
        self.CricleROI.show()
        self.CricleROI.setPos( (self.xu[0],self.yu[0]) )
        self.CricleROI.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
        self.CricleROI.sigRegionChangeFinished.connect(self.onclick_event)

        self.CricleROI2.show()
        self.CricleROI2.setPos( (self.xu[0],self.yu[0]) )
        self.CricleROI2.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
        self.CricleROI2.sigRegionChangeFinished.connect(self.onclick_event)
        
        self.CricleROI3.show()
        self.CricleROI3.setPos( (self.xu[0],self.yu[0]) )
        self.CricleROI3.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
        self.CricleROI3.sigRegionChangeFinished.connect(self.onclick_event)
        
        self.CricleROI4.show()
        self.CricleROI4.setPos( (self.xu[0],self.yu[0]) )
        self.CricleROI4.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
        self.CricleROI4.sigRegionChangeFinished.connect(self.onclick_event)
        
        self.CricleROI5.show()
        self.CricleROI5.setPos( (self.xu[0],self.yu[0]) )
        self.CricleROI5.setSize( QPointF(self.xu[1]-self.xu[0], self.xu[1]-self.xu[0])  )
        self.CricleROI5.sigRegionChangeFinished.connect(self.onclick_event)
                
        

            
        
        # self.draw()

    def updateSummedAreaPlot(self):
        E1 =  self.SumSpecLine1.value() 
        E2 =  self.SumSpecLine2.value() 
        
        id1 = (np.abs(self.En - E1)).argmin()
        id2 = (np.abs(self.En - E2)).argmin()
        
        id_min = np.min([id1, id2])
        id_max = np.max([id1, id2])
        # print(np.shape(self.data[id_min:id_max,:]))
        
        if self.WhatToPlotCombobox.currentIndex() == 0:
            self.drawImage(3, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], np.reshape(np.sum(self.data[:,id_min:id_max],axis=1), [len(self.yu), len(self.xu)]))
        else:
            self.drawImage(3, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], np.reshape(self.En[id_min+np.argmax(self.data[:,id_min:id_max],axis=1)], [len(self.yu), len(self.xu)]))
        
        
        
    def onclick_event(self, obj):
        
        
        # self.xu = np.unique(self.x)
        # self.yu = np.unique(self.y)
        # print(int(event.ydata*len(xu)+event.xdata))
        
        # self.subfig2.clear()
        # self.subfig2.plot(self.En, self.data[int(event.ydata*len(xu)+event.xdata), :]  ) #
        # self.draw()
        
        ExactCircleLocation = obj.pos()+0.5*obj.size()
        self.updateAllCircles(ExactCircleLocation)
        IndexOfSpectrum = ((self.x-ExactCircleLocation[0])**2 + (self.y-ExactCircleLocation[1])**2).argmin() 
        print(ExactCircleLocation.x() - self.x[IndexOfSpectrum],ExactCircleLocation.y() - self.y[IndexOfSpectrum])
        
        self.ExampleSpectrumPlot.setData(self.En, self.data[IndexOfSpectrum, :])
        self.ExampleSpectrumPlot2.setData(self.En, self.data[IndexOfSpectrum, :])
        if self.FittedDataAvailable:
            self.FitResultPlot.setData(self.En, multiple_gaussians_withOffset(self.En, self.opt_param[IndexOfSpectrum,:] ) )
        
        self.CenterLine.setValue(self.pposE[self.CurrentlySelectedIndex])
        self.Width1.setValue(self.pposE[self.CurrentlySelectedIndex]+ self.widths[self.CurrentlySelectedIndex]/2)
        self.Width2.setValue(self.pposE[self.CurrentlySelectedIndex]- self.widths[self.CurrentlySelectedIndex]/2)
        self.AmplLine.setValue(self.skew[0] + self.amps[self.CurrentlySelectedIndex])
        self.OffsetLine.setValue(self.skew[0])
        self.update()
        
        QApplication.processEvents()

    
    def updateAllCircles(self, newPosition):
            self.CricleROI.sigRegionChangeFinished.disconnect()    
            self.CricleROI2.sigRegionChangeFinished.disconnect()
            self.CricleROI3.sigRegionChangeFinished.disconnect() 
            self.CricleROI4.sigRegionChangeFinished.disconnect() 
            self.CricleROI5.sigRegionChangeFinished.disconnect()
        
            self.CricleROI.setPos(newPosition-0.5*self.CricleROI.size())  
            self.CricleROI2.setPos(newPosition-0.5*self.CricleROI2.size())
            self.CricleROI3.setPos(newPosition-0.5*self.CricleROI3.size()) 
            self.CricleROI4.setPos(newPosition-0.5*self.CricleROI4.size()) 
            self.CricleROI5.setPos(newPosition-0.5*self.CricleROI5.size())
        
            self.CricleROI.sigRegionChangeFinished.connect(self.onclick_event)    
            self.CricleROI2.sigRegionChangeFinished.connect(self.onclick_event)
            self.CricleROI3.sigRegionChangeFinished.connect(self.onclick_event) 
            self.CricleROI4.sigRegionChangeFinished.connect(self.onclick_event) 
            self.CricleROI5.sigRegionChangeFinished.connect(self.onclick_event)
    
    def setFittingParameter(self):
        # Lower and upper bounds for fit
        for i in range(self.num_peaks):
            self.p0[4*i] = self.amps[i]
            self.p0[4*i+1] = self.pposE[i]
            self.p0[4*i+2] = self.widths[i]
            self.p0[4*i+3] = self.skew[i]
            self.lower_bound[4*i] = 0
            self.lower_bound[4*i+1] = self.pposE[i]*0.5
            self.lower_bound[4*i+2] = self.widths[i]*0.5
            self.lower_bound[4*i+3] = 0
            self.upper_bound[4*i] = self.amps[i]*5
            self.upper_bound[4*i+1] = self.pposE[i]*1.5 
            self.upper_bound[4*i+2] = self.widths[i]*1.5
            self.upper_bound[4*i+3] = self.skew[i]*5+0.05
            # pixels closest to the peak positions
            self.xpx[i] = np.argmin(np.abs(self.En - self.pposE[i]))
    
    def startFitting(self):
        # self.Fig.canvas.mpl_disconnect(self.AxisClicker)
        # self.CricleROI.hide()
        # self.xu = np.unique(self.x)
        # self.yu = np.unique(self.y)
        
        for ind in range(self.num_points):                          
            if self.data[ind,0] == 0:
                continue
            else:
                # self.data[ind,:] = self.data[ind,:] - np.average(self.data[ind,0:20], axis=0)
                if self.num_peaks == 1:
                    self.p0[0] = self.data[ind, self.xpx[0].astype(int)]
                    if self.p0[0] < 10:
                        self.p0[0] = 10
                elif self.num_peaks == 2:
                    self.p0[0] = self.data[ind, self.xpx[0].astype(int)] - self.data[ind, self.xpx[1].astype(int)]/5
                    self.p0[4] = self.data[ind, self.xpx[1].astype(int)] - self.data[ind, self.xpx[0].astype(int)]/5
                    if self.p0[0] < 10:
                        self.p0[0] = 10
                    if self.p0[4] < 10:
                        self.p0[4] = 10   
                else:
                    print('Too many peaks xD')
                # fit and error
                try:
                    popt, pcov = curve_fit(multiple_gaussians_withOffset, self.En, self.data[ind,:], self.p0, bounds=(self.lower_bound, self.upper_bound))
                    perr = np.sqrt(np.diag(pcov)) # standard deviation of parameters
                    self.opt_param[ind,:] = popt      
                except RuntimeError:
                    print("Error - curve_fit failed at image " + str(ind))
                    self.opt_param[ind,:] = 1e-5 
            
            self.FittedDataAvailable = True
                    
            if ind%20 == 0:
                self.param_map = np.reshape(self.opt_param, [np.size(self.xu), np.size(self.yu), 4*self.num_peaks])
                self.ind_map = np.reshape(np.linspace(0, np.size(self.data, axis=0)-1, np.size(self.data, axis=0)), [np.size(self.xu), np.size(self.yu)])
                self.plotMap(self.CurrentlySelectedIndex)
                self.update()
                QApplication.processEvents()
        
        # Reshape data into 2D array
        
        self.param_map = np.reshape(self.opt_param, [np.size(self.xu), np.size(self.yu), 4*self.num_peaks])
        self.ind_map = np.reshape(np.linspace(0, np.size(self.data, axis=0)-1, np.size(self.data, axis=0)), [np.size(self.xu), np.size(self.yu)])
       
    def plotMap(self, index):
        try:
            self.drawImage(0, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], self.param_map[:,:,index*4])
            self.subfig1.view.setTitle('Amplitude Gaussian '+str(index+1))
            # self.subfig1.imshow(self.param_map[:,:,index*4], extent=[np.min(self.x),np.max(self.x),np.min(self.y),np.max(self.y)], cmap='Reds')
            # self.subfig1.set_title('Amplitude Gaussian '+str(index+1))
            
            self.drawImage(1, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], self.param_map[:,:,index*4+1])
            self.subfig2.view.setTitle('Position Gaussian '+str(index+1))
            # self.subfig2.imshow(self.param_map[:,:,index*4+1], extent=[np.min(self.x),np.max(self.x),np.min(self.y),np.max(self.y)], cmap='Blues')
            # self.subfig2.set_title('Position Gaussian '+str(index+1))
            self.drawImage(4, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], self.param_map[:,:,index*4+2])
            self.subfig3.view.setTitle('Width Gaussian '+str(index+1))
    
            # self.draw()
        except:
            self.drawImage(0, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)],np.zeros( (3,3)))
            self.subfig1.view.setTitle('Amplitude (not yet calculated)')
            # self.subfig1.imshow([[0,0],[0,0]], cmap='Reds')
            # self.subfig1.set_title('Amplitude (not yet calculated)')
            
            self.drawImage(1, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], np.zeros( (3,3)))
            self.subfig2.view.setTitle('Position (not yet calculated)')
            # self.subfig2.imshow([[0,0],[0,0]], cmap='Blues')
            # self.subfig2.set_title('Position (not yet calculated)')
            self.drawImage(4, [np.min(self.xu),np.max(self.xu)],[np.min(self.yu),np.max(self.yu)], np.zeros( (3,3)))
            self.subfig3.view.setTitle('Width (not yet calculated)')
    
            # self.draw()
        
    def renewParameter(self, center, ampl, width, skew, index):
        self.pposE[index] = float(center)#[float(i) for i in center.split(',')]   
        self.amps[index] = float(ampl)#[float(i) for i in ampl.split(',')]
        self.widths[index] = float(width)#[float(i) for i in width.split(',')]  
        self.skew[0] = float(skew)
        self.num_peaks = len(self.pposE)
        
        self.CurrentlySelectedIndex = index
        
        self.setFittingParameter()
        # self.startFitting()
        self.plotMap(index)
        if self.ExampleSpectrumPlot:
            self.CenterLine.setValue(self.pposE[self.CurrentlySelectedIndex])
            self.Width1.setValue(self.pposE[self.CurrentlySelectedIndex]+ self.widths[self.CurrentlySelectedIndex]/2)
            self.Width2.setValue(self.pposE[self.CurrentlySelectedIndex]- self.widths[self.CurrentlySelectedIndex]/2)
            self.AmplLine.setValue(self.skew[0] + self.amps[self.CurrentlySelectedIndex])
            self.OffsetLine.setValue(self.skew[0])
        
        self.centerEdit.setText(str(self.pposE[index]))
        self.amplEdit.setText(str(self.amps[index]))
        self.widthEdit.setText(str(self.widths[index]))
        self.skewEdit.setText(str(self.skew[0]))
        
        
        self.FitInitialGuessPlot.setData(self.En, np.add(gaussian(self.En, float(ampl), float(center), float(width)), float(skew)) )
        
        self.update()
        
        return (self.pposE[index], self.amps[index], self.widths[index])
    
    def getParameterForIndex(self,index):
        self.CurrentlySelectedIndex = index
        self.plotMap(index)
        if self.ExampleSpectrumPlot:
            self.CenterLine.setValue(self.pposE[self.CurrentlySelectedIndex])
            self.Width1.setValue(self.pposE[self.CurrentlySelectedIndex]+ self.widths[self.CurrentlySelectedIndex]/2)
            self.Width2.setValue(self.pposE[self.CurrentlySelectedIndex]- self.widths[self.CurrentlySelectedIndex]/2)
            self.AmplLine.setValue(self.skew[0] + self.amps[self.CurrentlySelectedIndex])
            self.OffsetLine.setValue(self.skew[0])
        return (self.pposE[index], self.amps[index], self.widths[index])
        
    
    def addGaussian(self):
        
        self.pposE.append(250)  
        self.amps.append(4000)
        self.widths.append(10) 
        self.skew.append(0)
        self.num_peaks = len(self.pposE)
        self.p0 = np.zeros(4*self.num_peaks)      
        self.upper_bound = np.zeros(4*self.num_peaks)
        self.lower_bound = np.zeros(4*self.num_peaks) 
        self.xpx = np.zeros(self.num_peaks)
        self.opt_param = np.zeros([self.num_points, 4*self.num_peaks])
        
        self.setFittingParameter()
        
        return self.num_peaks
    
    def removeGaussian(self, index):
        self.pposE.pop(index)  
        self.amps.pop(index)
        self.widths.pop(index)
        self.skew.pop(index)
        
        self.num_peaks = len(self.pposE)
        self.p0 = np.zeros(4*self.num_peaks)      
        self.upper_bound = np.zeros(4*self.num_peaks)
        self.lower_bound = np.zeros(4*self.num_peaks) 
        self.xpx = np.zeros(self.num_peaks)
        self.opt_param = np.zeros([self.num_points, 4*self.num_peaks])
        
        self.setFittingParameter()
        
        return self.num_peaks
    
    def calculate(self, index):
        self.startFitting()
        self.plotMap(index)
        
#%%
if __name__ == '__main__':
    
    if not QApplication.instance():
        app2 = QApplication(sys.argv)
    else:
        app2 = QApplication.instance()
    app2.setStyle('Fusion')
    MainWindow = PLMapGUI()
    MainWindow.showMaximized()
    sys.exit(app2.exec_())