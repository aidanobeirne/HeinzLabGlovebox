# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:57:14 2020

@author: Heinz Group
"""
# %%


import cv2
from scipy.ndimage.filters import median_filter
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread(r'C:\Users\Heinz Group\Desktop\GrasshopperImages\Image_2020-01-17_10-51-11-481223.jpg')

image = image[:,0:,0]

#image[50:150, 50:150]=1

plt.figure(1)
plt.imshow(image)

image = cv2.medianBlur(image,5)
plt.figure(2)
plt.imshow(image)

            
        
image = cv2.GaussianBlur(image,(5,5),0)
plt.figure(3)
plt.imshow(image)


image = median_filter(image, 1)
plt.figure(4)
plt.imshow(image)



## Calculate the Laplacian
lap = cv2.Laplacian(image,cv2.CV_64F, ksize = 15)
plt.figure(5)
plt.imshow(lap)
#

