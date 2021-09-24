# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 16:35:52 2017

@author: lutz
"""

import numpy as np
from scipy.special import kn, erf

def gaussian(x, a, x0, w):      # w is HWHM
    return a*np.exp(-np.log(2)*(x-x0)**2/(w**2))

def skew_gaussian(x, a, x0, w, s):
    return a*np.exp(-np.log(2)*(x-x0)**2/(w**2))*(1+erf(s*(x-x0)/np.sqrt(2)))

def lorentzian(x, a, x0, w):    # w is HWHM
    return a/(1+(x-x0)**2/w**2)

def pseudovoigt(x, a, x0, w, eta): # eta = 0: gaussian, eta=1: lorentzian; w is approximately HWHM
    return eta*lorentzian(x, a, x0, w) + (1-eta)*gaussian(x, a, x0, w)

def lorentzian_asym(x, a, x0, w, s):    # w is HWHM. lineshape from A. Stanick, E. Brauns: A simple asymmetric lineshape for fitting infrared absorption spectra
    wn = 2*w/(1+np.exp(s*(x-x0)))
    return a/(1+(x-x0)**2/wn**2)

def multiple_lorentzians(x,*params):
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 3):
            y = y + lorentzian(x,params[0][i],params[0][i+1],params[0][i+2])
    else:
        for i in range(0, len(params), 3):
            y = y + lorentzian(x,params[i],params[i+1],params[i+2])
    return y

def multiple_lorentzians_v(x,vector):
    y = np.zeros_like(x)
    for i in range(0, len(vector), 3):
        y = y + lorentzian(x,vector[i],vector[i+1],vector[i+2])
    return y

def multiple_gaussians(x,*params):
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 3):
            y = y + gaussian(x,params[0][i],params[0][i+1],params[0][i+2])
    else:
        for i in range(0, len(params), 3):
            y = y + gaussian(x,params[i],params[i+1],params[i+2])
    return y


def multiple_gaussians_withOffset(x,*params): # Attention, every guassian has to have offset, however only the first oneisused asaglobal background for all
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 4):
            y = y + gaussian(x,params[0][i],params[0][i+1],params[0][i+2])
        y = y + params[0][3]
    else:
        for i in range(0, len(params), 4):
            y = y + gaussian(x,params[i],params[i+1],params[i+2])
        y = y + params[3]
    return y


def two_peaks(x, ag, x0g, wg, al, x0l, wl):
   return ag*np.exp(-np.log(2)*(x-x0g)**2/(wg**2))+al/(1+(x-x0l)**2/wl**2)

def m_peaks_vector(x, vectorG, vectorL):
    y=np.zeros_like(y)
    for i in range(0, len(paramsG), 3):
        for j in range(0, len(paramsL), 3):
            y= y + gaussian(x,vectorG[i],vectorG[i+1],vectorG[i+2])+lorentzian(x,vectorL[j],vectorL[j+1],vectorL[j+2])
    return y
#            

def multiple_lorentzians(x,*params):
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 3):
            y = y + lorentzian(x,params[0][i],params[0][i+1],params[0][i+2])
    else:
        for i in range(0, len(params), 3):
            y = y + lorentzian(x,params[i],params[i+1],params[i+2])
    return y

def multiple_sgaussians(x,*params):
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 4):
            y = y + skew_gaussian(x,params[0][i],params[0][i+1],params[0][i+2],params[0][i+3])
    else:
        for i in range(0, len(params), 4):
            y = y + skew_gaussian(x,params[i],params[i+1],params[i+2],params[i+3])
    return y
        

def multiple_pvs(x,*params):        
    y = np.zeros_like(x)
    if len(params)==1:
        for i in range(0, len(params[0]), 4):
            y = y + pseudovoigt(x,params[0][i],params[0][i+1],params[0][i+2],params[0][i+3])
    else:
        for i in range(0, len(params), 4):
            y = y + pseudovoigt(x,params[i],params[i+1],params[i+2],params[i+3])
    return y

def multiple_pvs_v(x,vector):
    y = np.zeros_like(x)
    for i in range(0, len(params), 4):
        y = y + pseudovoigt(x,params[i],params[i+1],params[i+2],params[i+3])
    return y

def multiple_pvs_lbg(x,*params):        
    y = np.zeros_like(x)
    if len(params)==1:
        y = x*1e3*params[0][-2]+params[0][-1]*1e3
        for i in range(0, len(params[0])-2, 4):
            y = y + pseudovoigt(x,params[0][i],params[0][i+1],params[0][i+2],params[0][i+3])
    else:
        y = x*1e3*params[-2]+params[-1]*1e3
        for i in range(0, len(params)-2, 4):
            y = y + pseudovoigt(x,params[i],params[i+1],params[i+2],params[i+3])
    return y

def multiple_lorentzians_conv(x,*params):
    y = np.zeros_like(x)
    for i in range(0, len(params)-1, 3):
        y = y + lorentzian(x,params[i],params[i+1],params[i+2])
    sig = params[-1]/2.355
    cg = 1/np.sqrt(2*np.pi*sig**2) * np.exp(-(x - x[np.round(len(x)/2)])**2/(2*sig**2))
    cg = cg/np.sum(cg)
    y = np.convolve(y, cg, 'same')    
    return y

def multiple_lorentzians_conv_v(x,vector):
    y = np.zeros_like(x)
    for i in range(0, len(vector)-1, 3):
        y = y + lorentzian(x,vector[i],vector[i+1],vector[i+2])
    sig = vector[-1]/2.355
    cg = 1/np.sqrt(2*np.pi*sig**2) * np.exp(-(x - x[np.round(len(x)/2)])**2/(2*sig**2))
    cg = cg/np.sum(cg)
    yc = np.convolve(y, cg, 'same') 
    return yc

def powerf(x,a,n):
    y = a*x**n
    return y

def linf(x,a,b):
    y = a*x+b
    return y

def diffusion_2D(x,x0,LX,omega):    
    dx = max(x)-min(x)
    xn = np.linspace(min(x)-dx/2, max(x)+dx/2, np.size(x)*2-1)
    bess = np.nan_to_num(kn(0,(x-x0)/LX))+np.nan_to_num(kn(0,-(x-x0)/LX))
    gauss = gaussian(x,1/omega,x0,omega)
    n = np.convolve(bess,gauss, 'same')   
#    plt.figure()
#    plt.plot(x,bess/max(bess))
#    plt.plot(x,gauss/max(gauss))
#    plt.plot(x,n/max(n))
    return n

def diffusion_2Df(x,x0,LX,a):
    omega = 4.77    
    dx = max(x)-min(x)
    xn = np.linspace(min(x)-dx/2, max(x)+dx/2, np.size(x)*2-1)
    bess = np.nan_to_num(kn(0,(x-x0)/LX))+np.nan_to_num(kn(0,-(x-x0)/LX))
    gauss = gaussian(x,1/omega,x0,omega)
    n = a*np.convolve(bess,gauss, 'same')   
#    plt.figure()
#    plt.plot(x,bess/max(bess))
#    plt.plot(x,gauss/max(gauss))
#    plt.plot(x,n/max(n))
    return n


def line(x, y0, a):      # w is HWHM
    return y0+a*x
#def poly2(x,x0,y0)

#popt, pcov = curve_fit(pseudovoigt2, PL1[:,0], PL1[:,1], p0 = [1000, 10000, 1.94, 1.98, 0.03, 0.5])