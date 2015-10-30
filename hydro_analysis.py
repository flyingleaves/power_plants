#hydro_analysis.py

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats 
import matplotlib.pyplot as plt
import seaborn as sns
import pystan
from ggplot import *
from mpl_toolkits.basemap import Basemap
import pandas as pd
from __future__ import print_function
from patsy.contrasts import Treatment

pd.options.display.max_rows = 2000
pd.options.display.max_columns = 100

hydro_data = pd.read_csv("hydro_data.csv")
hydro_data["puscap"][np.isnan(hydro_data.puscap)] = 0

hydro_data["uprate"] = hydro_data.puscap
hydro_data["uprate"][hydro_data.uprate!=0]=1

formula = 'uprate ~ cum_intmtnt + inyr + C(state)'

dta = hydro_data[['uprate','cum_intmtnt', 'inyr', 'state']]

endog = hydro_data[['cum_intmtnt', 'inyr']]
exog = hydro_data[['uprate']]

states = sm.tools.tools.categorical(hydro_data["state"])

mod1 = smf.glm(formula=formula, data=dta, family=sm.families.Poisson()).fit()

mod1 = sm.glm(endog=endog, exog=exog, family=sm.families.Poisson()).fit()



from __future__ import print_function
import statsmodels.api as sm
import statsmodels.formula.api as smf
star98 = sm.datasets.star98.load_pandas().data
formula = 'SUCCESS ~ LOWINC + PERASIAN + PERBLACK + PERHISP + PCTCHRT + \
           PCTYRRND + PERMINTE*AVYRSEXP*AVSALK + PERSPENK*PTRATIO*PCTAF'
dta = star98[['NABOVE', 'NBELOW', 'LOWINC', 'PERASIAN', 'PERBLACK', 'PERHISP',
              'PCTCHRT', 'PCTYRRND', 'PERMINTE', 'AVYRSEXP', 'AVSALK',
              'PERSPENK', 'PTRATIO', 'PCTAF']]
endog = dta['NABOVE'] / (dta['NABOVE'] + dta.pop('NBELOW'))
del dta['NABOVE']
dta['SUCCESS'] = endog
