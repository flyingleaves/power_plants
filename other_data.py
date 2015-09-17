#other_data.py


import pandas as pd
import numpy as np
import matplotlib as mpt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import statsmodels.formula.api as smf
import statsmodels.api as sm
import sys
import pystan
import scipy

pd.options.display.max_rows = 999
pd.options.display.max_columns = 100
eia_generator=pd.read_excel("research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx", header=1)

eia_plants=pd.read_excel("research/power_plants_data/eia8602013/2___Plant_Y2013.xlsx", header=1)
eia_utility = pd.read_excel("research/power_plants_data/eia8602013/1___Utility_Y2013.xlsx", header=1)

