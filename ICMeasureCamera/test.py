# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 16:15:28 2020

@author: Heinz Group
"""
import numpy as np
import ICMeasureCamera
import matplotlib.pyplot as plt
#a= ICMeasureCamera.ICMeasureCam(name='DFK 33UX265 24910240')
a = ICMeasureCamera.ICMeasureCam(name='DFK 33UX264 43810318')

a.startImageAcquisition()

image = a.getImageAsNumpyArray()

print(a.Camera.GetPropertyValue("WhiteBalance","White Balance Red"))
print(a.Camera.GetPropertyValue("WhiteBalance","White Balance Green"))
print(a.Camera.GetPropertyValue("WhiteBalance","White BalanceB Blue"))
#red = 1.1562
#green = 1.
#blue = 2.17
#a.Camera.SetPropertySwitch("WhiteBalance","Auto",0)
#a.Camera.SetPropertyValue("WhiteBalance","White Balance Red",int(64*red))
#a.Camera.SetPropertyValue("WhiteBalance","White Balance Green",int(64*green))
#a.Camera.SetPropertyValue("WhiteBalance","White Balance Blue",int(64*blue))

from PIL import Image
print(image[:,:,0]- image[:,:,2])
R = image[:,:,0]
G = image[:,:,1]
B = image[:,:,2]
image[:,:,0] = B
image[:,:,1] = G*0.8
image[:,:,2] = R*1.5
#plt.figure()
#im = plt.imshow(R, cmap='gray')
#plt.show()
#plt.figure()
#im = plt.imshow(G, cmap='gray')
#plt.show()
#plt.figure()
#im = plt.imshow(B, cmap='gray')
#plt.show()
#print(R-B)
img = Image.fromarray(image, 'RGB')
img.show()

##imageWL = image.transpose(1,0,2)
#imageWL = np.flip(a.getImageAsNumpyArray().transpose(1,0,2),1)
#print(np.shape(imageWL))
#temp1 = imageWL[:,:,0]
#imageWL[:,:,0] = imageWL[:,:,1]
#imageWL[:,:,0] = temp1
#img2 = Image.fromarray(imageWL, 'RGB')
#img2.show()
a.endImageAcquisition()