# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:22:39 2020

@author: Markus A. Huber
"""
# This is a wrapper around the Thorlabs Cameras

import matplotlib.pyplot as plt
import keyboard
import cv2
import numpy as np

import tisgrabber as IC
 

class ICMeasureCam:
    def __init__(self, name="", videoFormat="RGB32 (1600x1200)", frameRate=30.00003):
    #def __init__(self, name="", videoFormat="RGB32 (1920x1080)", frameRate=30.00003):
        self.Camera = IC.TIS_CAM()
        self.CameraResolutionDivider = 1 #reduces resolution in x and y bz this factor for faster movement!
    
        if name == "" :
            self.Camera.ShowDeviceSelectionDialog()
        else:
            self.Camera.open(name)
            self.Camera.SetVideoFormat(videoFormat)
            self.Camera.SetFrameRate( frameRate)
        
        if self.Camera.IsDevValid() != 1:
            print("Couldn't load camera! Did you write the name correctly? Try instantiation without a name - this will show you the selectable devices.")
            

    def startImageAcquisition(self):
        self.Camera.StartLive(0)
            
    def showCameraProperties(self):
        self.Camera.StopLive() 
        self.Camera.ShowPropertyDialog()
        self.Camera.StartLive(1)
    
    def saveImageAsJpg(self, filename="C:\\Users\\GloveBox\\Desktop\\ICMeasureCamCapture.jpg"):
        data = []
        data = self.getImageAsNumpyArrayForCV2Save()
        if len(data) > 0 :
            dataFlipped = np.flip(data,1)
            cv2.imwrite(filename, dataFlipped)
            
    
    def startContinuosDataStream(self):
        self.startImageAcquisition()
        # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
        fig = plt.figure(0)
        
        # Retrieve and display images
        continue_recording = True
        while(continue_recording):
            image_data = self.getImageAsNumpyArray()

            # Draws an image on the current figure
            plt.imshow(image_data)
            plt.title("DO NOT CLOSE - press ENTER to close")
            # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
            # Interval is in seconds.
            plt.pause(0.001)

            # Clear current reference of a figure. This will improve display speed significantly
            plt.clf()
            
            # If user presses enter, close the program
            if keyboard.is_pressed('ENTER'):
                print('Stream is closing')
                
                # Close figure
                plt.close(fig)             
                continue_recording=False
        self.endImageAcquisition()
    
    def endImageAcquisition(self):
        self.Camera.StopLive() 
    


    def getSerialNumber(self):
        print("Not yet implemented")
        
        
    def getExposureTime(self):
        ExposureTime = [0]
        self.Camera.GetPropertyAbsoluteValue("Exposure","Value", ExposureTime)
        return ExposureTime[0]*1000.0
    
    def setExposureTime(self, setpoint_ms):
        self.Camera.SetPropertyAbsoluteValue("Exposure","Value", setpoint_ms/1000.0)

    
    def getImageAsNumpyArray(self):
        self.Camera.SnapImage()
        imageWrong = self.Camera.GetImage()
        imageCorrected = imageWrong[::self.CameraResolutionDivider,::self.CameraResolutionDivider,:]
        imageCorrected[:,:,::-1] = imageWrong[::self.CameraResolutionDivider,::self.CameraResolutionDivider,:]
        return imageCorrected
    
    
    def getImageAsNumpyArrayForCV2Save(self):
        self.Camera.SnapImage()
        image = self.Camera.GetImage()
        return image
    
    def close(self):    
        self.endImageAcquisition()
        
    #implement garbage collector destructor just in case,  when somebodz does "del GrashopperObject" instead of closing it properly
    def __del__(self): 
        self.close()
    
    
    
