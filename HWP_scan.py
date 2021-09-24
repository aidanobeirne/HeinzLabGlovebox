import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QLineEdit, QPushButton, QGridLayout, QDoubleSpinBox, QLabel)
import pyqtgraph as pg
from pyqtgraph.dockarea import *
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class Form(QDialog):
    def __init__(self):
        super().__init__()

        self.start = QDoubleSpinBox()
        self.stop = QDoubleSpinBox()
        self.step = QDoubleSpinBox()
        # self.edit.selectAll()
        		
        self.startscan = QPushButton('Start')
        self.cancel = QPushButton('Cancel')
        
        self.startscan.clicked.connect(lambda :print('Hello {0}'.format(self.edit.text())))
        
        layout = QGridLayout()
        layout.addWidget(QLabel("HWP Start: ") , 1,0)
        layout.addWidget(self.start, 1,1)
        
        layout.addWidget(self.stop, 2,1)
        layout.addWidget(QLabel("HWP Stop: "), 2,0)
        layout.addWidget(self.step, 3,1)
        layout.addWidget(QLabel("HWP Step: "), 3,0)
        
        layout.addWidget(self.cancel, 4,0 )
        layout.addWidget(self.startscan, 4,1 )
        self.setLayout(layout)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	demo = Form()
	demo.show()
	sys.exit(app.exec_())