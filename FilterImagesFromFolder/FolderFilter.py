# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 10:41:05 2020

@author: Markus A. Huber
"""



# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:07:18 2020

@author: Markus A. Huber
"""

# 12 threshold - 100 cts : WSe2 on SiO2 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import ctypes
myappid = u'HeinzLab.PythonScripts.FilterFolder.v1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

import glob
import sys

from matplotlib.image import imread




import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


from PyQt5.QtWidgets import qApp, QCheckBox, QFileDialog, QSlider, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QGroupBox, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtGui import QIcon

import numpy as np
import cv2

class FilterMonochromImagesWindow(QWidget):
                  
    def closeEvent(self, event):
        self.killAll()  
        self.update()
        QApplication.processEvents()
        self.update()
        print("Program exited!")
        event.accept()
        app.quit()
        
        
      
    # %%
    def __init__(self):      
        super().__init__()
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        self.setWindowTitle('The Filter - It will be beauiful - and Mexico will pay for it!')
        self.setWindowIcon(QIcon(r'C:\Users\Heinz Group\Documents\Python Scripts\FilterImagesFromFolder\Magnifier.ico'))
        
        self.ImageView = pg.ImageView()#levelMode='mono')
        self.ImageView.getHistogramWidget().setHistogramRange(0, 300)
#        grid_layout.setColumnStretch(0,5000)

    
        grid_layout.addWidget(self.ImageView, 0, 0, 5, 1)
 
        #--------------------------------------------------------------------------------------------------------
        # Graphing window
        #--------------------------------------------------------------------------------------------------------
        
        
        self.LaplacianGraph = pg.GraphicsWindow(title="Laplacian")
        grid_layout.addWidget(self.LaplacianGraph, 0, 2)
#        grid_layout.setColumnStretch(2,5000)
        

        plotWindow2 = self.LaplacianGraph.addPlot(title="Color Distribution")
        plotWindow2.setXRange(0, 50, padding=0)
        plotWindow2.setYRange(0,200, padding=0)
        self.DistributionAndThresholdPlot = plotWindow2.plot([0,0,0])
 
        self.GrayScaleThresholdLine = pg.InfiniteLine(pos=20, angle=90, movable=True, pen=(255,0,0)) 
        plotWindow2.addItem(self.GrayScaleThresholdLine)
        self.GrayScaleThresholdLine.sigPositionChangeFinished.connect(self.updateInterestingness)
        
        self.LaplacianGraph.nextRow()
        
        plotWindow3 = self.LaplacianGraph.addPlot(title="Amount of Interestingness")
        self.InterestingnessPlotWindowItem = plotWindow3
        self.InterestingnessPlot = plotWindow3.plot([0,0,0])
        self.InterestingnessThresholdLine = pg.InfiniteLine(pos=180, angle=0, movable=True, pen=(0,0,255)) 
        self.InterestingnessThresholdLine.sigPositionChangeFinished.connect(self.updateFilterlist)
        plotWindow3.addItem(self.InterestingnessPlot)     
        plotWindow3.addItem(self.InterestingnessThresholdLine)

               
        #--------------------------------------------------------------------------------------------------------
        # Positionlist Groupbox
        #--------------------------------------------------------------------------------------------------------
        
        
        self.PositionListGroupBox = QGroupBox("All Files:")
        layout = QGridLayout()
      
        self.SavePositionList = QListWidget()
        self.FullPositionList = []
        
        self.SavePositionList.currentRowChanged.connect(self.goToPositionInList)
        self.SavePositionList.itemClicked.connect(self.goToPositionInList)
        layout.addWidget(self.SavePositionList, 0, 0)
        
        
        btn = QPushButton("Load PL Folder")
        btn.clicked.connect(self.loadFolder)
        layout.addWidget(btn, 1, 0)
        
        btn = QPushButton("Kill All")
        btn.clicked.connect(self.killAll)
        layout.addWidget(btn, 2, 0)
        
        self.PositionListGroupBox.setLayout(layout)
        self.FilteredPathList = []
        grid_layout.addWidget(self.PositionListGroupBox,  0, 1)

        
        #--------------------------------------------------------------------------------------------------------
        # Filtered List Groupbox
        #--------------------------------------------------------------------------------------------------------
        
        self.FilteredListGroupBox = QGroupBox("All Files:")
        layout = QGridLayout()
      
        self.FilteredPositionList = QListWidget()
        
        
        self.FilteredPositionList.currentRowChanged.connect(self.goToPositionInFilteredList)
        self.FilteredPositionList.itemClicked.connect(self.goToPositionInFilteredList)
        layout.addWidget(self.FilteredPositionList, 0, 0, 1, 2)
        
        
        btn = QPushButton("Load WL Folder")
        btn.clicked.connect(self.loadWLFolder)
        layout.addWidget(btn, 1, 0)
        
        btn = QPushButton("+")
        btn.clicked.connect(self.expandLeftSide)
        layout.addWidget(btn, 1, 1)
        
        self.CurrentWLFolder = ""
        
        self.FilteredListGroupBox.setLayout(layout)

        grid_layout.addWidget(self.FilteredListGroupBox,  0, 3)
        self.FilteredListGroupBox.hide()
#        grid_layout.setColumnStretch(3,100)
        
        #--------------------------------------------------------------------------------------------------------
        # Compare whitelight and bluelight images
        #--------------------------------------------------------------------------------------------------------
        
        self.ImageView2 = pg.ImageView()#levelMode='mono')
        
    
        grid_layout.addWidget(self.ImageView2, 0, 4)
        self.ImageView2.hide()
#        grid_layout.setColumnStretch(4,5000)
        
        
        
        self.InterestingnessForCurrentDataSelection = []
        self.CurrentFolder = ''
        
        self.KillOldFilterThread = False
        self.KillOldFilterListUpdateThread = False
        
        self.showMaximized()
        self.Startup = True
        
    def goToPositionInList(self):
        data = imread(self.FullPositionList[self.SavePositionList.currentRow()])
        
        if self.Startup:
            self.ImageView.setImage(data, autoLevels=True, autoHistogramRange=True)
            self.Startup = False
        else:
            self.ImageView.setImage(data, autoLevels=False, autoHistogramRange=False)
        
        hist, pos = np.histogram(data, bins=100)
        self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
     
    def expandLeftSide(self):
        self.PositionListGroupBox.show()
        self.LaplacianGraph.show()
        
    def goToPositionInFilteredList(self):
        
        self.PositionListGroupBox.hide()
        self.LaplacianGraph.hide()
        self.ImageView2.show()
        
        data = imread(self.FilteredPathList[self.FilteredPositionList.currentRow()])
        
        
        self.ImageView.setImage(data, autoLevels=False, autoHistogramRange=False)
        
        hist, pos = np.histogram(data, bins=100)
        self.DistributionAndThresholdPlot.setData(pos, hist, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        
        if self.CurrentWLFolder != "":
            name = self.FilteredPathList[self.FilteredPositionList.currentRow()]
            stripPath = name[(len(self.CurrentFolder)+1):] 
            NameParts = stripPath.split('_')
            
            X = float(NameParts[2].replace("p",".")[1:])
            Y = float(NameParts[3].replace("p",".")[1:])
            
            TargetCoords = (X,Y)
            
            # Euclidean shortes distance to target
            dist_2 = np.sum((np.asarray(self.ListOfWLCoordinates) - TargetCoords)**2, axis=1)
            ClosestIndex = np.argmin(dist_2)
            CenterCoords = self.ListOfWLCoordinates[ClosestIndex] #this will be our new center in the whitelight image
            
            data = np.array(imread(self.ListOfAccordingFileNames[ClosestIndex]))
            data = np.flip(data.transpose(1,0,2),1) 
            OriginalSize = np.shape(data)
            self.StretchFactor = 10
            data = cv2.resize(data, (int(np.round((OriginalSize[1]/self.StretchFactor))), int(np.round(OriginalSize[0]/self.StretchFactor))) )
 
            size = np.shape(data)
            imageWL = np.zeros( (5*size[0],5*size[1],3) )
            
            imageWL[(2*size[0]):(3*size[0]), (2*size[1]):(3*size[1]),:] = data
            
            for yi in [-2,-1,0,1,2]:
                for xi in [-2,-1,0,1,2]:
                    
                    if xi == 0 and yi == 0:
                        continue
                    
                    
                    TargetCoords = np.add(CenterCoords, (xi*self.DeltaX, yi*self.DeltaY))
                    dist_2 = np.sum((np.asarray(self.ListOfWLCoordinates) - TargetCoords)**2, axis=1)
                    ClosestIndex = np.argmin(dist_2)
            
                    data = np.array(imread(self.ListOfAccordingFileNames[ClosestIndex]))
                    data = np.flip(data.transpose(1,0,2),1) 
                    data = cv2.resize(data, (size[1], size[0]) )
        
                    imageWL[((2+xi)*size[0]):((3+xi)*size[0]), ((2-yi)*size[1]):((3-yi)*size[1]),:] = data
        
#        
#        
#            Position_Number = int(NameParts[1])
#            
#            Position_String = str(Position_Number - 1)
#            path = self.CurrentWLFolder + "/Position_" + Position_String + "_*"
#            files = glob.glob(path)
#            data = np.array(imread(files[0]))
#            data = np.flip(data.transpose(1,0,2),1)
#            
#            size = np.shape(data)
#            imageWL = np.zeros( (size[0],3*size[1],3) )
#            
#            
#            imageWL[:, 0:size[1],:] = data
#            
#            
#            Position_String = str(Position_Number )
#            path = self.CurrentWLFolder + "/Position_" + Position_String + "_*"
#            files = glob.glob(path)
#            data = np.array(imread(files[0]))
#            data = np.flip(data.transpose(1,0,2),1)
#       
#            imageWL[:, (size[1]):(2*size[1]),:] = data
#            
#            
#            Position_String = str(Position_Number + 1)
#            path = self.CurrentWLFolder + "/Position_" + Position_String + "_*"
#            files = glob.glob(path)
#            data = np.array(imread(files[0]))
#            data = np.flip(data.transpose(1,0,2),1)
#       
#            imageWL[:, (2*size[1]):(3*size[1]),:] = data
#            
#            
#            imageWL = np.flip(imageWL.transpose(1,0,2),1) 
            temp1 = imageWL[:,:,0]
            imageWL[:,:,0] = imageWL[:,:,1]
            imageWL[:,:,0] = temp1
            self.ImageView2.setImage(imageWL)
        
        
        
                
        
#        AmountOfInterestingPixels = np.sum(self.savedROIData > self.GrayScaleThresholdLine.value())
#        self.InterestingnessArray.append(AmountOfInterestingPixels)
#        
#        if len(self.InterestingnessArray) > 50:
#            self.InterestingnessArray.pop(0)
#            
#        self.InterestingnessPlot.setData(self.InterestingnessArray, pen=(0,0,255))
#        self.InterestingnessPlotWindowItem.setXRange(0,50, padding = 0)
#        
#        
#        AmountOfInterestingPixels = np.sum(data > self.GrayScaleThresholdLine.value())      
#        return AmountOfInterestingPixels > self.InterestingnessThresholdLine.value() 
    
    def updateInterestingness(self):
        self.KillOldFilterThread = True
        self.InterestingnessForCurrentDataSelection = []
        counter = 0
        self.KillOldFilterThread = False
        for name in self.FullPositionList: 
            if self.KillOldFilterThread:
                break
            
            data = imread(name)
            AmountOfInterestingPixels = np.sum(data > self.GrayScaleThresholdLine.value())
            self.InterestingnessForCurrentDataSelection.append(AmountOfInterestingPixels)
            
            
            counter = counter + 1
            
            self.InterestingnessPlot.setData(self.InterestingnessForCurrentDataSelection, brush=(0,0,255))
            self.InterestingnessPlotWindowItem.setXRange(0,counter, padding = 0)
            
            if AmountOfInterestingPixels > self.InterestingnessThresholdLine.value():
                self.updateFilterlist()
            
            self.update()
            QApplication.processEvents()
            self.update()
            

    def updateFilterlist(self):
        self.FilteredListGroupBox.show()
        self.KillOldFilterListUpdateThread = True
        self.FilteredPositionList.clear()
        self.FilteredPathList = []
        self.KillOldFilterListUpdateThread = False
        for i in range(len(self.InterestingnessForCurrentDataSelection)): 
            if self.KillOldFilterListUpdateThread:
                break
            
            if self.InterestingnessForCurrentDataSelection[i] > self.InterestingnessThresholdLine.value() :
                name = self.FullPositionList[i]
                stripPath = name[(len(self.CurrentFolder)+1):] 
                NameParts = stripPath.split('_')
                self.FilteredPositionList.addItem(NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
                self.FilteredPathList.append(name)
                self.update()
                QApplication.processEvents()
                self.update()
          
    
    def loadFolder(self):
        self.FilteredPositionList.clear()
        self.FilteredPathList = []
        self.InterestingnessForCurrentDataSelection = []
        self.SavePositionList.clear()
        self.FullPositionList = []
        self.KillOldFilterThread = True
        self.KillOldFilterListUpdateThread = True
        self.CurrentWLFolder = ""
        
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory to load"))
        self.CurrentFolder = folder
        path = folder + "/*.jpg"
        files = glob.glob(path)   
        self.FullPositionList = files
        
        
        
        for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
            stripPath = name[(len(folder)+1):] 
            NameParts = stripPath.split('_')
            self.SavePositionList.addItem(NameParts[0]+" "+NameParts[1]+"\n  X: " + NameParts[2].replace("p",".")[1:] + "\n  Y: " + NameParts[3].replace("p",".")[1:] + "\n  Z: " + NameParts[4].replace("p",".")[1:-4])
        
    def loadWLFolder(self):
   
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory to load"))
        self.CurrentWLFolder = folder
        
        #do some precharacterization to make it easier later on
        
        path = folder + "/*.jpg"
        files = glob.glob(path) 
        self.ListOfWLCoordinates = []
        self.ListOfAccordingFileNames = []

        
        
        for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
            stripPath = name[(len(folder)+1):] 
            NameParts = stripPath.split('_')
            
            
            
            if NameParts[0] == "Position":
                X = float(NameParts[2].replace("p",".")[1:])
                Y = float(NameParts[3].replace("p",".")[1:])
                
                
                self.ListOfWLCoordinates.append( (X,Y) )
                self.ListOfAccordingFileNames.append(name)
#                Z = NameParts[4].replace("p",".")[1:]
                
        self.DeltaX = np.max( np.diff( np.sort( np.asarray(self.ListOfWLCoordinates)[:,0] )))
        self.DeltaY = np.max( np.diff( np.sort( np.asarray(self.ListOfWLCoordinates)[:,1] )))
       
        print("Deltas: ", self.DeltaX, self.DeltaY)
    
    def killAll(self):
        self.KillOldFilterThread = True
        self.KillOldFilterListUpdateThread = True
   
     
# %%

if __name__ == '__main__':
    
    app = QApplication([])
    MainWindow = FilterMonochromImagesWindow()
    MainWindow.show()
    sys.exit(app.exec_())