# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python ")
        self.setGeometry(100, 100, 600, 400)
        self.UiComponents()
        self.show()


    def UiComponents(self):
        self.spin = QSpinBox(self)
        self.spin.setGeometry(100, 100, 100, 40)
        self.label = QLabel(self)
        self.label.setGeometry(100, 200, 200, 40)

        self.spin.installEventFilter(self)
        # self.spin.setKeyboardTracking(False)
        # self.spin.valueChanged.connect(self.show_result)
        self.spin.editingFinished.connect(self.show_result)


        self.spin2 = QSpinBox(self)
        self.spin2.setGeometry(200, 100, 100, 40)
        self.spin2.installEventFilter(self)
        # self.spin.setKeyboardTracking(False)
        # self.spin.valueChanged.connect(self.show_result2)
        self.spin2.editingFinished.connect(self.show_result2)
        self.label2 = QLabel(self)
        self.label2.setGeometry(200, 200, 200, 40)

    def show_result2(self):
        value = self.spin2.value()
        self.label2.setText("Value : " + str(value))
        print('label 2 updated')

    def show_result(self):
        value = self.spin.value()
        self.label.setText("Value : " + str(value))
        print('label 1 updated')

    def eventFilter(self, object, event):
        if isinstance(object, QSpinBox):
            if event.type() == QtCore.QEvent.FocusIn:
                self.previousObjectValue = object.value()
                self.previousObject = object
                print('Saving previous value as', self.previousObjectValue)
   
            if event.type() ==  QtCore.QEvent.FocusOut and object == self.previousObject: 
                print('Setting to previous value =', self.previousObjectValue)
                print(object.receivers(object.editingFinished()))
                # object.disconnect()
                object.setValue(self.previousObjectValue)
                # object.editingFinished.connect()
            
            if event.type() == QtCore.QEvent.KeyRelease:
                if event.key() == 16777221 or event.key() == 16777220:
                    self.previousObjectValue = object.value()
                    self.previousObject = object
                    print('Return Key pressed')
            return False
                
        else:
            return False
        # self.previousEvent = object
        
        
# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

window.show()

# start the app
sys.exit(App.exec())
