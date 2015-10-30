#wind_descriptives.py
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
import re

pd.options.display.max_rows = 2000
pd.options.display.max_columns = 100

wind_data = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/wind_data.csv")

wind_over_time = wind_data.groupby(["op_year", "op_month"])["nplate"].aggregate(sum)
wind_over_time.plot(kind="bar")
plt.show()

wind_cum = wind_over_time.cumsum()
wind_cum.plot(kind="bar")
plt.show()


wind_turbines["inyr"]=wind_turbines["inyr"].astype(int)
operating = wind_turbines[wind_turbines.status =="OP"]

wind_coll = operating[operating.year==2013]

wind_by_year = wind_coll.groupby("inyr")["nplate"].aggregate(sum)

wind_year_plot = wind_by_year.plot(kind="bar")
wind_year_plot.axes.set_ylabel("Installed wind capacity by year (nplate)")
plt.show()

wind_by_year = wind_by_year.reset_index()
wind_by_year["cum_cap"]=wind_by_year["nplate"].cumsum()

wind_by_year.set_index("inyr", inplace=True)
cum_sum_wind_plot = wind_by_year.cum_cap.plot(kind="line")
cum_sum_wind_plot.axes.set_ylable("Cumulative wind capacity by year")
plt.show()

wind_by_state = wind_coll.groupby("state")["nplate"].aggregate(sum)
wind_by_state.sort()

wind_by_state.plot(kind="bar")
plt.show()

#state by year

wind_state = wind_coll.groupby(["state", "inyr"])["nplate"].aggregate(sum)
wind_state = wind_state.reset_index()
wind_state["cum_cap"] = wind_state.groupby("state")["nplate"].cumsum()

top_ten = wind_by_state[-10:].index.values

wind_growth_state = ggplot(aes(x="inyr", y="cum_cap"), data=wind_state[wind_state.state.isin(top_ten)]) +\
	geom_line() +\
	facet_wrap("state", ncol=2)

wind_state_plot = wind_growth_state.draw()



