#storage.py

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
from ggplot import *
import math

pd.options.display.max_rows = 2000
pd.options.display.max_columns = 100

power_plants=pd.read_csv("research/power_plants_data/master_ro_1990_2013.csv")

power_plants = power_plants.sort(["ucode", "pcode","gcode", "year"])

power_plants["pcode"] = [str(i) for i in power_plants.pcode]
power_plants["gen_id"] = power_plants.pcode + "-" + power_plants.gcode

#replace with the same 
power_plants["pm"][power_plants.pm=="HC"]="HY"

#replace 'HR' with 'PS'
power_plants["pm"][power_plants.pm=="HR"]='PS'

wind = ['WT', 'WS']
#WT - onshore wind
#WS - offshore wind

wind_turbines = power_plants[power_plants.pm.isin(wind)]
storage = ['BA', 'CE', 'CP', 'FW', 'ES', 'PS']

#BA - Battery storage
#CE - compressed air
#CP - Concentrated Solar Power, CP
#FW - flywheel

storage_plants = power_plants[power_plants.pm.isin(storage)]
storage_plants["is_ps"] = storage_plants.pm=="PS"
storage_plants = storage_plants[storage_plants.inyr.notnull()]
storage_plants["inyr"] = storage_plants["inyr"].astype(int).copy()
stor_collapsed = storage_plants[~storage_plants.gen_id.duplicated()]



#capacity by year

storage_by_year = stor_collapsed.groupby(["inyr"])["nplate"].aggregate(sum)
storage_year_plot = storage_by_year.plot(kind="bar")
storage_year_plot.figure.set_size_inches(8,6)
plt.show()

non_ps_by_year = stor_collapsed[~stor_collapsed.is_ps].groupby(["inyr", "pm"])["nplate"].aggregate(sum)
non_ps_by_year.plot(kind="bar")
plt.show()
#now, ex ps

storage_by_year_ex_ps = stor_collapsed[stor_collapsed.pm!="PS"].groupby("inyr")["nplate"]

#descriptives of storage in the US

#what have investments been there?



#relation to wind power / solar power