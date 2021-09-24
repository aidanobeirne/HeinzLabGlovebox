# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 17:10:37 2020

@author: Heinz Group
"""

import pygame
import numpy as np
import time
import keyboard

class PS4Controller:
    def __init__(self):
        
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.FunctionAxis0 = lambda _ : None
            self.FunctionAxis1 = lambda _ : None
            self.AxisFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numaxes())]
            self.ButtonFunctions = [ (lambda  : None) for x in range(self.joystick.get_numbuttons())]
            self.HatFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numhats())]
            self.AxisEnabled = True
            self.MoveThreshold = 0.1
            self.NoJoystickConnected = False
            self.KeyboardModeEnabled = False
    
        #-----------------------------------------------------------
        #CHANGE`S HERE
            self.speedModeButtonNumber = 8
            self.SpeedModeAxisFunctions = [ (lambda _ : None) for x in range(self.joystick.get_numaxes())]
    
    	#------------------------------------------------------------
            
        else:
            print('No controller detected. Switch to keyboard mode!')
            self.KeyboardModeEnabled = True
            self.FunctionAxis0 = lambda _ : None
            self.FunctionAxis1 = lambda _ : None
            self.AxisFunctions = [ (lambda _ : None) for x in range(10)]
            self.ButtonFunctions = [ (lambda _ : None) for x in range(10)]
            self.HatFunctions = [ (lambda _ : None) for x in range(10)]
            self.AxisEnabled = True
            self.MoveThreshold = 0.1
            self.speedModeButtonNumber = 8
            self.SpeedModeAxisFunctions = [ (lambda _ : None) for x in range(10)]
            self.NoJoystickConnected = True
            self.KeyboardModeEnabled = True
            
            
            
        
        

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
        if self.KeyboardModeEnabled:
            print('received keyboard input')
            shiftPressed = keyboard.is_pressed('shift')
            if keyboard.is_pressed('a'):
                if shiftPressed:
                    self.HatFunctions[0]([-1,0])
                else:
                    self.AxisFunctions[0](-1)
            if keyboard.is_pressed('d'):
                if shiftPressed:
                    self.HatFunctions[0]([1,0])
                else:
                    self.AxisFunctions[0](1)
            if keyboard.is_pressed('w'):
                if shiftPressed:
                    self.HatFunctions[0]([0,1])
                else:
                    self.AxisFunctions[1](-1)
            if keyboard.is_pressed('s'):
                if shiftPressed:
                    self.HatFunctions[0]([0,-1])
                else:
                    self.AxisFunctions[1](1)
            if keyboard.is_pressed('q'):
                if shiftPressed:
                    self.ButtonFunctions[7]()
                else:
                    self.AxisFunctions[3](-1)
            if keyboard.is_pressed('e'):
                if shiftPressed:
                    self.ButtonFunctions[6]()
                else:
                    self.AxisFunctions[3](1)
            if keyboard.is_pressed('r'):
                if shiftPressed:
                    self.ButtonFunctions[4]()
                else:
                    self.ButtonFunctions[5]()
            if keyboard.is_pressed('f'):
                if shiftPressed:
                    self.ButtonFunctions[2]()
                else:
                    self.ButtonFunctions[1]()
            if keyboard.is_pressed('l'):
                    self.ButtonFunctions[3]()
            if keyboard.is_pressed('c'):
                    self.ButtonFunctions[10]()
                
             
            
            
        
        if self.NoJoystickConnected:
            return
        
        if self.AxisEnabled:
            for i in range(len(self.AxisFunctions)):
                
                #-----------------------------------------------------------
    			#CHANGE`S HERE
                currentAxisValue = self.joystick.get_axis(i)
                if np.abs(currentAxisValue) > self.MoveThreshold:
                    if self.joystick.get_button(self.speedModeButtonNumber) == 1:
                        currentAxisFunction = self.SpeedModeAxisFunctions[i]
                    else:
                        currentAxisFunction = self.AxisFunctions[i]
                        currentAxisFunction(currentAxisValue)

                #------------------------------------------------------------
            
        for j in range(len(self.ButtonFunctions)):
            if j != self.speedModeButtonNumber and self.joystick.get_button(j) == 1:
                self.ButtonFunctions[j]() 
                time.sleep(0.005)
                    
        for k in range(len(self.HatFunctions)):
            hat = self.joystick.get_hat( k )
            self.HatFunctions[k](hat)
            time.sleep(0.005)
            

    

if __name__ == '__main__':
    import time
    
    c = PS4Controller()
    while True:
        c.doEvents()
        time.sleep(0.2)

        
        