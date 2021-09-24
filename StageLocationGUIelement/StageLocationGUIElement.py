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
from PyQt5.QtWidgets import QGraphicsProxyWidget, QWidget, QGridLayout, QApplication, QComboBox, QCheckBox, QGraphicsRectItem, QGraphicsItem
from PyQt5.QtCore import QRect
from PyQt5 import QtCore

class StageLocationGUIElement(pg.GraphicsLayoutWidget):

    def __init__(self):      
        super().__init__()
         
        # self.StageViewLabel = pg.LabelItem(justify = "bottom")
        # self.addItem(self.StageViewLabel,0,2,1,3)#2,2,1,3)
        # self.StageViewLabel.setText("x = %0.2f, <span style='color: black'> y = %0.2f" % (0, 0))
        

        self.StagePlotWindowItem = self.addPlot(1,0,1,3)
        self.StagePlotWindowItem.setLabel('left', text='Y position', units='m')
        self.StagePlotWindowItem.setLabel('bottom', text='X position', units='m')
        self.StagePlotWindowItem.vb.setAspectLocked(True)
        
        # boundary = QGraphicsRectItem(QtCore.QRectF(-110, -75, 110, 75))
        boundary = QGraphicsRectItem(QtCore.QRectF(0, 0, 110, 75))
        boundary.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.StagePlotWindowItem.addItem(boundary) 
        magnet = QGraphicsRectItem(QtCore.QRectF(49.5, 47.6, 0.8, 0.8))
        magnet.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.StagePlotWindowItem.addItem(magnet)
        glassSlide = QGraphicsRectItem(QtCore.QRectF(2.7, 36.3, 79.42,22.81))
        glassSlide.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.StagePlotWindowItem.addItem(glassSlide)
        

        pos_array = (50, 50)
        symbol_array = ('o')
        brush_array = ('w')
        size_array = (10)
        brush_array = (152,251,152)
        pen_array = (46,139,87)
        self.StageScatterPlot = pg.ScatterPlotItem( pos = [pos_array], symbol = symbol_array, pen = pen_array,brush = brush_array,  size = size_array)
        self.StagePlotWindowItem.addItem(self.StageScatterPlot)
        
        self.StagePositionListPlot = pg.ScatterPlotItem( symbol = 'x', size = '8', pen= (255,0,0))
        self.StagePlotWindowItem.addItem(self.StagePositionListPlot)

        # self.StageScatterPlot.scene().sigMouseMoved.connect(self.mouseMovedInStageWindow)
        # self.StageScatterPlot.scene().sigMouseClicked.connect(self.mouse_clicked)
        
    def drawRect(self, x, y, xlen, ylen):
        # self.StagePlotWindowItem.clear()
        # boundary = QGraphicsRectItem(QtCore.QRectF(0, 0, 110, 75))
        # boundary.setFlag(QGraphicsItem.ItemIsMovable, False)
        # self.StagePlotWindowItem.addItem(boundary) 
        # magnet = QGraphicsRectItem(QtCore.QRectF(49.5, 47.6, 0.8, 0.8))
        # magnet.setFlag(QGraphicsItem.ItemIsMovable, False)
        # self.StagePlotWindowItem.addItem(magnet)
        # glassSlide = QGraphicsRectItem(QtCore.QRectF(2.7, 36.3, 79.42,22.81))
        # glassSlide.setFlag(QGraphicsItem.ItemIsMovable, False)
        # self.StagePlotWindowItem.addItem(glassSlide)
        
        rect = QGraphicsRectItem(QtCore.QRectF(x, y,xlen, ylen))
        rect.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.StagePlotWindowItem.addItem(rect)

    def updateStagePos(self, x, y):
        # stagePos = {'pos': (x,y), 'symbol': 'o', 'pen': (0,0,255) , 'size': 10}
        pos_array = (x, y)
        symbol_array = ('o')
        size_array = (10)
        brush_array = (152,251,152)
        pen_array = (46,139,87)
        self.StageScatterPlot.setData( pos = [pos_array], symbol = symbol_array, pen = pen_array, brush = brush_array,  size = size_array)
    
    # def mouse_clicked(self, evt):
    #     mousePoint = self.StagePlotWindowItem.vb.mapSceneToView(evt.scenePos())
    #     pos_array = (mousePoint.x(), mousePoint.y())
    #     symbol_array = ('x')
    #     brush_array = ('w')
    #     size_array = (8)
    #     pen_array = (255,0, 0)
    #     if evt.button() == 1:
    #         # print(mousePoint.x())
    #         self.StagePositionListPlot.addPoints(pos = [pos_array], symbol = symbol_array, pen = pen_array,  size = size_array)
    #     else:
    #         # self.StagePositionListPlot.clear()
    #         self.StagePositionListPlot.setData(pos = [pos_array], symbol = symbol_array, pen = pen_array,  size = size_array)
    #     # return mousePoint.x(), mousePoint.y()
                
    # def mouseMovedInStageWindow(self, evt):
    #     print(self.StageScatterPlot.data)
    #     mousePoint = self.StagePlotWindowItem.vb.mapSceneToView(evt)
    #     # print(mousePoint.x(), mousePoint.y())
    #     # x = self.StagePlot.xData
    #     # if self.xAxisCalibrationComboBox.currentIndex() ==0:
    #     #     x = 1e-9*x
    #     # y = self.StagePlot.yData
    #     # ind = np.argmin(np.abs(np.subtract(x, mousePoint.x())))

class TestStagePlotGUIElement_GUI(QWidget):

    def __init__(self):      
        super().__init__()
        self.basic_layout = QGridLayout()
        
        self.StageView = StageLocationGUIElement()
        # self.StageView.setData([650,750,850],[1,5,3])
        self.basic_layout.addWidget(self.StageView)
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
    MainWindow = TestStagePlotGUIElement_GUI()
    MainWindow.show()
    sys.exit(app.exec_())