# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 18:59:11 2020

@author: Heinz Group
"""
# %%
import sys
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\PS4Controller')
sys.path.append(r'C:\Users\Heinz Group\Documents\Python Scripts\ThorlabsStages')

import ThorlabsStages
import PS4Controller
import time

Stage = ThorlabsStages.Thorlabs2DStageAPT()
Controller = PS4Controller.PS4Controller()

Controller.FunctionAxis0 = lambda AxisValue : Stage.motorX.move_by(-AxisValue*0.1)
Controller.FunctionAxis1 = lambda AxisValue : Stage.motorY.move_by(-AxisValue*0.1)

while True:
    Controller.doEvents()
    time.sleep(0.1)