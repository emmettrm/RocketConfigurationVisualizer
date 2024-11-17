import math
from .engine import Engine
import pandas as pd
from rocketcea.cea_obj import CEA_Obj, add_new_fuel
from .fluidProperties.fluidProperties import FluidProperties
import plotly.express as px

class EngineAnalyzer:
    def __init__(self, title, fuel, ox, nozzle_type, Mr, pMaxCham, mdotMax, Lstar, Dcham, wall_temp, r1, r2, r3, conv_angle, fuel_delta_t, pMinExitRatio = [], filmCoolingPercent = [], div_angle = None, contourStep = 5e-3, customFuel = None, frozen = [0], fac_CR = None, pAmbient = [1.01325], doContours = True, eta = 1):
        self.title = title
        self.fuel = FluidProperties(fuel) #CEA
        self.ox = FluidProperties(ox) #CEA
        self.nozzle_type = nozzle_type #in engine
        self.Mr = Mr #CEA
        self.pMaxCham = pMaxCham #CEA
        self.mdotMax = mdotMax #in engine?
        self.Lstar = Lstar #in engine
        self.Dcham = Dcham #in engine
        self.wall_temp = wall_temp #in engine?
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.conv_angle = conv_angle #in engine
        self.div_angle = div_angle #in engine
        self.fuel_delta_t = fuel_delta_t 
        self.frozen = frozen #CEA
        self.pAmbient = pAmbient #CEA
        self.filmCoolingPercent = filmCoolingPercent #in engine
        self.pMinExitRatio = pMinExitRatio #??????
        self.fac_CR = fac_CR
        self.step = contourStep #no
        self.doContours = doContours
        self.eta = eta
        #basic calcs, sizing calcs, contour calcs, heat calcs, cooling calcs
        #varsToSweep = [list(fuel), list(ox), list(nozzle_type), list(Mr), list(pMaxCham), list(mdotMax), list(frozen), list(pAmbient), [0], [0], [0], [0], [0], [0]]
        varsToSweeptemp = [fuel, ox, nozzle_type, Mr, pMaxCham, mdotMax, frozen, pAmbient, eta, [None], [None], [None], [None], [None], [None]]
        varsToSweep = []
        for el in varsToSweeptemp:
            if type(el) != list:
                varsToSweep.append([el])
            else:
                varsToSweep.append(el)

        print(varsToSweep)
        inputNames = ['fuel', 'ox', 'nozzle_type', 'Mr', 'pMaxCham', 'mdotMax', 'frozen', 'pAmbient', 'eta']
        outputNames = ['thrust', 'isp_s', 'inj', 'cham', 'thr', 'exit']
        names = inputNames+outputNames
        enginesDBtemp = pd.MultiIndex.from_product(varsToSweep, names=names)
        enginesDB = enginesDBtemp.to_frame(index=False)
        
        #print(enginesDB)   #prints input db

        for i, row in enginesDB.iterrows():
            tempEng = Engine(title, row['fuel'], row['ox'], row['nozzle_type'], row['Mr'], row['pMaxCham'], row['mdotMax'], Lstar, Dcham, wall_temp, r1, r2, r3, conv_angle, fuel_delta_t, pMinExitRatio = pMinExitRatio, filmCoolingPercent = filmCoolingPercent, contourStep = contourStep, customFuel = customFuel, frozen = row['frozen'], pAmbient = row['pAmbient'], doContours = doContours, eta = row['eta'])
            enginesDB.loc[i,'thrust'] = tempEng.max.thrust
            enginesDB.loc[i,'isp_s'] = tempEng.max.isp_s
            enginesDB.loc[i,'inj'] = tempEng.max.inj
            enginesDB.loc[i,'cham'] = tempEng.max.cham
            enginesDB.loc[i,'thr'] = tempEng.max.thr
            enginesDB.loc[i,'exit'] = tempEng.max.exit

        print(enginesDB)    #prints output db

        # df = px.data.gapminder().query("country=='Canada'")
        # fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
        # fig.show()

