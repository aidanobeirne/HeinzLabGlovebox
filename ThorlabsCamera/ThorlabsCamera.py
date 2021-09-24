# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:22:39 2020

@author: Markus A. Huber
"""
# This is a wrapper around the Thorlabs Cameras

import matplotlib.pyplot as plt
import keyboard
import numpy as np
import cv2
import threading
import copy
import time
import sys

sys.path.append(r'C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Python Compact Scientific Camera Toolkit\examples')
from polling_example import *

import os
import sys
ThorlabsCameraDLLPath = r'C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Python Compact Scientific Camera Toolkit\dlls\64_lib'
sys.path.append(ThorlabsCameraDLLPath)
os.environ['PATH'] = ThorlabsCameraDLLPath + os.pathsep + os.environ['PATH']

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

class ThorlabsCam:
    def __init__(self):
        self.sdk = TLCameraSDK()  
        self.available_cameras = self.sdk.discover_available_cameras()
        if len(self.available_cameras) < 1:
            print("no cameras detected")
        self.camera = self.sdk.open_camera(self.available_cameras[0]) 
        self.camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
        self.camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        self.camera.black_level = 0
        self.camera.exposure_time_us = 150000  # set exposure to 150 ms
        self.cameraArmed = False
        self.camera.roi = (0, 0, 1920, 1200)  # set roi to be at origin point (100, 100) with a width & height of 500
        self.cameraInThreadedOperation = False
        self.cameraThreadImageLock = threading.Lock()
        self.currentThreadBufferImage = []

    def startImageAcquisition(self, threadedOperation = False):
        if not self.cameraArmed:
            self.camera.arm(2)
            self.camera.issue_software_trigger()
            self.image_width = self.camera.image_width_pixels
            self.image_height = self.camera.image_height_pixels
            self.cameraArmed = True
            
            if threadedOperation:
                self.cameraInThreadedOperation = True
                self.Thread = threading.Thread(target=self.threadingFunction)
                self.Thread.start()
            
     
    def threadingFunction(self):
        while self.cameraInThreadedOperation:
            time.sleep(self.camera.exposure_time_us/1000000)
            frame = self.camera.get_pending_frame_or_null()
            if frame is not None:
                self.cameraThreadImageLock.acquire()
                self.currentThreadBufferImage = np.copy(frame.image_buffer)
                self.cameraThreadImageLock.release()
    
    def saveImageAsJpg(self, filename="C:\\Users\\Heinz Group\\Desktop\\ThorlabsCameraCapture.jpg"):
        data = self.getImageAsNumpyArray()
        if data != [] :
            cv2.imwrite(filename, data)
            
    
    def startContinuosDataStream(self):
        self.startImageAcquisition()
        # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
        fig = plt.figure(0)
        
        # Retrieve and display images
        continue_recording = True
        while(continue_recording):
            image_data = self.getImageAsNumpyArray()

            # Draws an image on the current figure
            plt.imshow(image_data, cmap='gray')
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
        if self.cameraInThreadedOperation:
            print("Closing Camera background thread")
            self.cameraInThreadedOperation = False
            self.Thread.join()
            print("Camera background thread closed")
        self.camera.disarm()
        self.cameraArmed = False
        print("Camera disarmed")
    
    def showCameraProperties(self):
        print("Not yet implemented!")

    def getSerialNumber(self):
        print("Not yet implemented")
    
    
    def getImageAsNumpyArray(self):
        image_buffer_copy = []
        if self.cameraInThreadedOperation:
                self.cameraThreadImageLock.acquire()
                image_buffer_copy = copy.deepcopy(self.currentThreadBufferImage)
                self.cameraThreadImageLock.release()
                return image_buffer_copy
        else:
            frame = self.camera.get_pending_frame_or_null()
            if frame is not None:
                image_buffer_copy = np.copy(frame.image_buffer)
                return image_buffer_copy
            else:
                print("timeout reached during polling, return empty...")
                return []
    
    def getExposureTime(self):
        return  self.camera.exposure_time_us/1000.0
    
    def setExposureTime(self, setpoint_ms):
        self.camera.disarm()
        saveThreadingState = copy.deepcopy(self.cameraInThreadedOperation)
        if self.cameraInThreadedOperation:
            print("Closing Camera background thread")
            self.cameraInThreadedOperation = False
            self.Thread.join()
            print("Camera background thread closed")
            
        self.camera.exposure_time_us = int(setpoint_ms*1000.0)
        print("Changed exposure")
        self.camera.arm(2)
        self.camera.issue_software_trigger()
        
        if saveThreadingState:
                self.cameraInThreadedOperation = True
                self.Thread = threading.Thread(target=self.threadingFunction)
                self.Thread.start()
                
    def testrun(self):
        start = time.time()
        img = self.getImageAsNumpyArray().T
        stop = time.time()
        print(stop-start)
        
    
    def close(self): 
        self.camera.disarm()
        # self.camera.dispose()
        del self.camera
        del self.sdk
        self.cameraArmed = False
        
    #implement garbage collector destructor just in case,  when somebodz does "del GrashopperObject" instead of closing it properly
    def __del__(self): 
        self.close()
    
    
    
