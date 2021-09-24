from andor import *
import time
import sys
import signal

import matplotlib.pyplot as plt


#####################
# Initial settings  #
#####################

#please set these values accordingly!! I have no idea what is used for our cameras!! especially Tset
Tset = -75# -70
EMCCDGain = 1
PreAmpGain = 0

def signal_handler(signal, frame):
    print('Shutting down the camera...')
    cam.ShutDown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initialising the Camera
cam = Andor()
cam.SetSingleScan()
cam.SetSingleScanFullyBinned()
cam.SetTriggerMode(7)
cam.SetShutter(1,1,0,0)
cam.SetPreAmpGain(PreAmpGain)
cam.SetEMCCDGain(EMCCDGain)
cam.SetExposureTime(0.01)
cam.SetCoolerMode(1)

cam.SetTemperature(Tset)
cam.CoolerON()

while cam.GetTemperature() is not 'DRV_TEMP_STABILIZED':
    print( "Temperature is:" + str(cam.temperature))
    time.sleep(10)

i = 0

while True:
        i += 1
        print(cam.GetTemperature())
        print(cam.temperature)
        print("Ready for Acquisition")
        cam.StartAcquisition()
        data = []
        cam.GetAcquiredData(data)
        
        plt.figure(10101)
        plt.clf()
        plt.plot(data)
        plt.show()
        plt.pause(0.1)
        
        time.sleep(10)
        #cam.SaveAsBmpNormalised("%03g.bmp" %i)
        #cam.SaveAsBmp("%03g.bmp" %i)
        #cam.SaveAsTxt("%03g.txt" %i)
