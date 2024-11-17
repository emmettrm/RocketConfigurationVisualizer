import math
import os
import sys
parent_directory = os.path.abspath('..')
sys.path.append(parent_directory)
from RocketConfigurationVisualizer.src_cea.engineAnalyzer import EngineAnalyzer

#test engine 
title = 'APRL Engine mu2 Sizing'
ox = 'LOX'        # full propellant selection is availible at https://rocketcea.readthedocs.io/en/latest/propellants.html
fuel =  'RP1'# 'Isopropanol70''Ethanol''CH4'
customFuel = [
    "Isopropanol70", 
    """fuel C3H8O-2propanol C 3 H 8 O 1    wt%=70.0
h,cal=-65133.0     t(k)=298.15   rho=0.786
fuel water H 2.0 O 1.0  wt%=30.0
h,cal=-68308.0  t(k)=298.15 rho,g/cc = 0.9998"""
]
#print('{}'.format(customFuel[1]))
pMaxCham = [39, 40]    #max thrust chamber pressure in bar
Mr = [1.8, 1.9] # propellant mixture ratio
pAmbient = 1.01325 #bar
#pMaxCham = 25*14.5     #max thrust chamber pressure in bar
#pAmbient = 1.01325*14.5 #bar
pMinExitRatio = [] #trottle exit pressure
#set veriables
mdotMax = [1.48, 1.6]        #max thrust mass flow rate
filmCoolingPercent = 0.0
Lstar = 1.02
Dcham = 3.375 * 0.0254 #in meters
conv_angle = math.pi / 4 # rad, 45deg
div_angle = math.pi / 12  # rad, 15deg
wall_temp = 473 # K
fuel_delta_t = 100 # K
#fuel_cp = 2010 # J/KgK
r1 = 1
r2 = 1
r3 = 0.4
step = 1e-2 #array resolution
nozzle_type = 'conical' #'bell80'
doContours = False
eta = 0.9
test = EngineAnalyzer(title, fuel, ox, nozzle_type, Mr, pMaxCham, mdotMax, Lstar, Dcham, wall_temp, r1, r2, r3, conv_angle, fuel_delta_t, pMinExitRatio = pMinExitRatio, filmCoolingPercent = filmCoolingPercent, div_angle = div_angle, contourStep = step, customFuel = customFuel, frozen = 1, pAmbient = pAmbient, doContours = doContours, eta = eta)