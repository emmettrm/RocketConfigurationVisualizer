'''
fluid properties
h_fg        enthalpy of vaporization
T_sat       saturation temperature
roe_l       density in liquid phase
c_l         specific heat capacity liquid phase
'''
import os

class FluidProperties:
    h_fg = None
    T_sat = None
    roe_l = None
    c_l = None
    cp = None
    def __init__(self, fluidName):
        #print(os.getcwd())
        self.name = fluidName
        try:
            with open(f'src_cea\\fluidProperties\\{fluidName}.csv') as csvfile:
                lines = csvfile.readlines()
                for i in range(len(lines)):
                    lines[i] = lines[i].split(',')
                #print(f'len(lines[0]) = {len(lines[0])}')
                print(lines)
                for i in range(len(lines[0])):
                    self.__setattr__(lines[0][i], float(lines[1][i]))
        except:
            print(f'could not import fluid property file {fluidName}.csv')

    def __repr__(self):
        return f"h_fg: {self.h_fg} " \
            f"T_sat: {self.T_sat} " \
            f"roe_l: {self.roe_l} " \
            f"c_l: {self.c_l} " \
            f"cp: {self.cp} " \

if __name__ == '__main__':
    keroseneProps = FluidProperties('kerosene')
    print(keroseneProps)