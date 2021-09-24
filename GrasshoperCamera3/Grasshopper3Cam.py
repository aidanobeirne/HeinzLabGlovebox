# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:22:39 2020

@author: Markus A. Huber
"""
# This is a wrapper around the Spinnaker Grasshopper 3 camera 
# The code is mostly based on the example AcquireAndDisplay.pyfrom the examples library

import matplotlib.pyplot as plt
import keyboard
import PySpin


class Grasshopper3Cam:
    def __init__(self):
        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()
        # Get current library version
        version = self.system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))
        # Retrieve list of cameras from the system
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()
        print('Number of cameras detected: %d' % num_cameras)
        # Finish if there are no cameras
        if num_cameras == 0:
            self.cam = None
            # Clear camera list before releasing system
            self.cam_list.Clear()
            # Release system instance
            self.system.ReleaseInstance()
            print('Not enough cameras!')
            return False
        elif num_cameras == 1:
            self.cam = self.cam_list[0]
            print("Retrieved camera")
        else:
            print("This class works only when a single camera is detected - however there seem to be more!")
            self.cam = None
            self.cam_list.Clear()
            # Release system instance
            self.system.ReleaseInstance()
            return False
        
        try:
            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
            # Initialize camera
            self.cam.Init()
            print("Camera initialized")
            # Retrieve GenICam nodemap
            self.nodemap = self.cam.GetNodeMap()         
    
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

    def startImageAcquisition(self):
        sNodemap = self.cam.GetTLStreamNodeMap()
    
        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
    
        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
        if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
            print('Unable to set stream buffer handling mode.. Aborting...')
            return False
    
        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()
    
        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)
    
        print('*** IMAGE ACQUISITION ***\n')
        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False
    
            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False
    
            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
    
            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
    
            print('Acquisition mode set to continuous...')
    
            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.cam.BeginAcquisition()
    
            print('Acquiring images...')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    
    def showCameraProperties(self):
        print("Not yet implemented! however you can change parameters live by using SpinView - it doesn't block this program")
    
    def saveImageAsJpg(self, filename="C:\\Users\\Heinz Group\\Desktop\\Grasshopper3Image.jpg"):
        #self.startImageAcquisition()
        image_result = self.cam.GetNextImage()

        #  Ensure image completion
        #
        #  *** NOTES ***
        #  Images can easily be checked for completion. This should be
        #  done whenever a complete image is expected or required.
        #  Further, check image status for a little more insight into
        #  why an image is incomplete.
        if image_result.IsIncomplete():
            print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

        else:

            #  Print image information; height and width recorded in pixels
            #
            #  *** NOTES ***
            #  Images have quite a bit of available metadata including
            #  things such as CRC, image status, and offset values, to
            #  name a few.
            #width = image_result.GetWidth()
            #height = image_result.GetHeight()
            
            #  Convert image to mono 8
            #
            #  *** NOTES ***
            #  Images can be converted between pixel formats by using
            #  the appropriate enumeration value. Unlike the original
            #  image, the converted one does not need to be released as
            #  it does not affect the camera buffer.
            #
            #  When converting images, color processing algorithm is an
            #  optional parameter.
            image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

            #  Save image
            #
            #  *** NOTES ***
            #  The standard practice of the examples is to use device
            #  serial numbers to keep images of one device from
            #  overwriting those of another.
            image_converted.Save(filename)
            print('Image saved at %s' % filename)

            #  Release image
            #
            #  *** NOTES ***
            #  Images retrieved directly from the camera (i.e. non-converted
            #  images) need to be released in order to keep from filling the
            #  buffer.
            image_result.Release()
        #self.endImageAcquisition()
    
    def startContinuosDataStream(self):
            self.startImageAcquisition()
            # Close program
            print('Press enter to stop the data stream..')
    
            # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
            fig = plt.figure(0)

            # Retrieve and display images
            continue_recording = True
            while(continue_recording):
                try:
    
                    #  Retrieve next received image
                    #
                    #  *** NOTES ***
                    #  Capturing an image houses images on the camera buffer. Trying
                    #  to capture an image that does not exist will hang the camera.
                    #
                    #  *** LATER ***
                    #  Once an image from the buffer is saved and/or no longer
                    #  needed, the image must be released in order to keep the
                    #  buffer from filling up.
                    
                    image_result = self.cam.GetNextImage()
    
                    #  Ensure image completion
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
    
                    else:                    
    
                        # Getting the image data as a numpy array
                        image_data = image_result.GetNDArray()
    
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
    
                    #  Release image
                    #
                    #  *** NOTES ***
                    #  Images retrieved directly from the camera (i.e. non-converted
                    #  images) need to be released in order to keep from filling the
                    #  buffer.
                    image_result.Release()
    
                except PySpin.SpinnakerException as ex:
                    print('Error: %s' % ex)
                    return False
    
            
            self.endImageAcquisition()
    
    def endImageAcquisition(self):
        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        try:
            self.cam.EndAcquisition()
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
    


    def getSerialNumber(self):
        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(self.nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)
            return device_serial_number
    
    
    def getImageAsNumpyArray(self):
        #self.startImageAcquisition()
        try:

            #  Retrieve next received image
            #
            #  *** NOTES ***
            #  Capturing an image houses images on the camera buffer. Trying
            #  to capture an image that does not exist will hang the camera.
            #
            #  *** LATER ***
            #  Once an image from the buffer is saved and/or no longer
            #  needed, the image must be released in order to keep the
            #  buffer from filling up.
            
            image_result = self.cam.GetNextImage()

            #  Ensure image completion
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                image_data = []
            else:                    

                # Getting the image data as a numpy array
                image_data = image_result.GetNDArray()

            #  Release image
            #
            #  *** NOTES ***
            #  Images retrieved directly from the camera (i.e. non-converted
            #  images) need to be released in order to keep from filling the
            #  buffer.
            image_result.Release()
            return image_data

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return []

        
        #self.endImageAcquisition()
    
    
    def close(self):
        print("Closing camera instance")
        if self.cam != None:
            self.cam.DeInit()
            
        del self.cam
        # Clear camera list before releasing system
        self.cam_list.Clear()
        # Release system instance
        self.system.ReleaseInstance()
        
    #implement garbage collector destructor just in case,  when somebodz does "del GrashopperObject" instead of closing it properly
    def __del__(self): 
        self.close()
    
    
    
