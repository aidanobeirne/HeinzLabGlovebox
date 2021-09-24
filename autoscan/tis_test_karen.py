# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 16:03:42 2019

@author: Karen
"""

import tisgrabber as IC
import cv2
import matplotlib.pyplot as plt

gain_value=0
contrast=30
brightness=30
saturation=100 # 0-255
red = 1
green = 1.0625
blue = 2.29
exposure_value=[1/3000]

Camera = IC.TIS_CAM()
#Camera.ShowDeviceSelectionDialog()
Camera.open("DFK 33UX264 43810318")

Camera.SetVideoFormat("RGB32 (1024x768)")
Camera.SetFrameRate( 1.0 )

Camera.SetPropertySwitch("Gain","Auto",0) # 0-off; 1-on
Camera.SetPropertyValue("Gain","Value",gain_value)
gain_value=Camera.GetPropertyValue("Gain","Value")
print("gain=",gain_value)

Camera.SetPropertySwitch("Contrast","Auto",0)
#Camera.SetPropertyValue("Contrast","Value",contrast)
contrast=Camera.GetPropertyValue("Contrast","Value")
print("contrast=",contrast)

Camera.SetPropertySwitch("Brightness","Auto",0)
#Camera.SetPropertyValue("Brightness","Value",brightness)
brightness=Camera.GetPropertyValue("Brightness","Value")
print("brightness=",brightness)

Camera.SetPropertySwitch("Saturation","Auto",0)
Camera.SetPropertyValue("Saturation","Value",saturation)
brightness=Camera.GetPropertyValue("Saturation","Value")
print("saturation=",saturation)

Camera.SetPropertySwitch("WhiteBalance","Auto",0)
Camera.SetPropertyValue("WhiteBalance","White Balance Red",int(64*red))
Camera.SetPropertyValue("WhiteBalance","White Balance Green",int(64*green))
Camera.SetPropertyValue("WhiteBalance","White Balance Blue",int(64*blue))
red=Camera.GetPropertyValue("WhiteBalance","White Balance Red")
print("red=",red)
green=Camera.GetPropertyValue("WhiteBalance","White Balance Green")
print("green=",green)
blue=Camera.GetPropertyValue("WhiteBalance","White Balance Blue")
print("blue=",blue)

Camera.SetPropertySwitch("Exposure","Auto",0)
Camera.SetPropertyAbsoluteValue("Exposure","Value",exposure_value[0])
Camera.GetPropertyAbsoluteValue("Exposure","Value",exposure_value)
print("exposure=",exposure_value[0])


Camera.StartLive(1)  

# Get the image  
Camera.SnapImage()
image = Camera.GetImage()
plt.figure()
plt.imshow(image)
#cv2.imshow('Window', image)
#cv2.waitKey(0)
Camera.StopLive()    


#print( 'Press ctrl-c to stop' )
#Camera.StartLive(1)   
#try:
#    while ( True ):
#        # Snap an image
#        Camera.SnapImage()
#        # Get the image
#        image = Camera.GetImage()
#        # Apply some OpenCV function on this image        
##        cv2.imshow('Window', image)
##        cv2.waitKey(10)
#except KeyboardInterrupt:
#    Camera.StopLive()    
#    cv2.destroyWindow('Window')

