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
from PyQt5.QtWidgets import QFileDialog, QSplitter, QInputDialog, QLineEdit, QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QApplication, QPushButton, QListView, QAbstractItemView, QProgressBar, QDialog, QComboBox, QPlainTextEdit, QCheckBox, QTableWidget, QTableWidgetItem, QDoubleSpinBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QPointF
from PyQt5 import QtWidgets


class HWPscanGUI(QtGui.QMainWindow):

    def __init__(self, subprocessqueue=[]):      
        super().__init__()
  
        #data
        self.En = []
        self.x = []
        self.y = []
        self.data = []
        area=DockArea()
        self.setCentralWidget(area)
        self.setWindowTitle('Polarization scan')

        ###MapDock
        mapWin = pg.LayoutWidget()
        DockDock = Dock("Map", size=(500,400))
        mapDock = QSplitter(Qt.Vertical)
        area.addDock(DockDock, 'left')
        DockDock.addWidget(mapDock)
        mapDock.addWidget(mapWin)
        

        self.ExampleFig = pg.GraphicsWindow(title="Example Spectrum (move circle in map to change)")
        self.ExamplePlot1 = self.ExampleFig.addPlot(title="Example Spectrum (move circle in summed intensity map to change)")
        self.ExampleSpectrumPlot = self.ExamplePlot1.plot([0,0,0], pen=pg.mkPen('k', width=1, style=QtCore.Qt.SolidLine))
        mapWin.addWidget(self.ExampleFig)

        self.start = QDoubleSpinBox()
        self.stop = QDoubleSpinBox()
        self.step = QDoubleSpinBox()
        self.startscan = QPushButton('Start')
        self.cancel = QCheckBox('Cancel')
        # self.startscan.clicked.connect(self.HWPscan)
        


        mapWin.addWidget(QLabel("HWP Start: "))
        mapWin.addWidget(self.start)
        mapWin.addWidget(QLabel("HWP Stop: "))
        mapWin.addWidget(self.stop)
        mapWin.addWidget(QLabel("HWP Step: "))
        mapWin.addWidget(self.step)
        mapWin.addWidget(self.startscan)
        mapWin.addWidget(self.cancel)
    

    
        def HWPscan(self):
            print('scan')
            angles = np.arange(self.hwpscandialog.start.value(), self.hwpscandialog.stop.value(), self.hwpscandialog.step.value())
            print(angles)
            dat = []
            for angle in angles:
                if self.hwpscandialog.cancel.isChecked() == False:
                    self.HalfWavePlate.moveToDeg(angle)
                    print('moving to angle')
                    while abs(self.HalfWavePlate.getRotation() - angle) > 0.05:
                        time.sleep(0.05)
                    print('taking spec')
                    spec = self.SpectrometerWidget.SpectrometerWidget.takeSpectrum()
                    path = r"C:\Users\GloveBox\Desktop\HWP_scan/"
                    dat.append(spec)
                    
                    # self.ExampleSpectrumPlot.setData(self.En, self.data[int(len(self.data)/2), :])
                    # np.savez(path + str(angle).replace('.','_') , spec = spec, wls = self.SpectrometerWidget.SpectrometerWidget.wl_calibration, angle = angle )
                else:
                    pass

        
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


# Override closeEvent! thereby problems running the script from spyder versions 3.3.6 and upwards should be amended    
    def closeEvent(self, event):
        if self.GUIisSubprocessed:
            self.UpdateTimer.stop()
        print("Program exited!")
        event.accept()
        if __name__ == '__main__': 
            app2.quit()
       
    

        
#%%
if __name__ == '__main__':
    
    if not QApplication.instance():
        app2 = QApplication(sys.argv)
    else:
        app2 = QApplication.instance()
    app2.setStyle('Fusion')
    MainWindow = HWPscanGUI()
    MainWindow.showMaximized()
    sys.exit(app2.exec_())