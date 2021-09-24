# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 17:10:37 2020

@author: Heinz Group
"""

import pygame
import numpy as np

class PS4Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        #this could be done more elegantly using an arraz and a nice "register(axis, funcion)" method but for now its fine
        self.FunctionAxis0 = lambda _ : None
        self.FunctionAxis1 = lambda _ : None
        self.AxisFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numaxes())]
        self.ButtonFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numbuttons())]
        self.HatFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numhats())]
        self.AxisEnabled = True
        self.MoveThreshold = 0.1
        #use getbuttons getaxes
        #generate arrayz
        
    def closeController(self):
        pygame.quit()
        
    def disableAxes(self):
        self.AxisEnabled = False
        
    def enableAxes(self):
        self.AxisEnabled = True
        
    def doEvents(self):
        for event in pygame.event.get(): # User did something
            pass
        if self.AxisEnabled:
            for i in range(len(self.AxisFunctions)):
                currentAxisFunction = self.AxisFunctions[i]
                currentAxisValue = self.joystick.get_axis(i)
                if np.abs(currentAxisValue) > self.MoveThreshold:
                    currentAxisFunction(currentAxisValue)
            
        for j in range(len(self.ButtonFunctions)):
            if self.joystick.get_button(j) == 1:
                self.ButtonFunctions[j]()
                
        for k in range(len(self.HatFunctions)):
            hat = self.joystick.get_hat( k )
            self.HatFunctions[k](hat)
        
        