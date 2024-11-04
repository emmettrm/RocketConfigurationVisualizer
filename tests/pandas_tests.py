import pandas as pd
import numpy as np

d1 = [0, 1, 2, 3, 4]
d2 = [00, 11, 22, 33, 44]
d3 = [000, 111, 222, 333, 444]
d4 = list([0])
d5 = [None]
arrays1 = [d1, d2, d3, d4, d5]
pdDatabase1 = pd.MultiIndex.from_product(arrays1, names=['d1', 'd2', 'd3', 'd4', 'd5']) #https://pandas.pydata.org/docs/user_guide/advanced.html
print(pdDatabase1)
#print(pdDatabase1.names[1])
#print(pdDatabase1.names.index('d1'))
mydataframe = pdDatabase1.to_frame(index=False)
print(mydataframe)

# Create a MultiIndex and convert to dataframe
index = pd.MultiIndex.from_tuples([('A', 1), ('A', 2), ('B', 1), ('B', 2)])
new = index.to_frame(index=True)
print(index)
print(new)
print(d3)
print(list(d3))

inputNames = ['fuel', 'ox', 'nozzle_type', 'Mr', 'pMaxCham', 'mdotMax', 'frozen', 'pAmbient']
outputNames = ['thrust', 'isp', 'inj', 'cham', 'thr', 'exit']
names = inputNames+outputNames
print(names)
print(type([]))