#hydro_descriptives.py

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

solar_plants = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/solar_plants.csv")
hydro_plants = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/hydro_plants.csv")
wind_turbines = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/wind_turbines.csv")

solar_coll = solar_plants[solar_plants.year ==2013]

solar_by_state = solar_coll.groupby("state")["nplate"].aggregate(sum)
solar_by_state.plot(kind="bar")
plt.show()
#hydro_plants = pd.read_csv("research/power_plants_data/hydro_plants.csv")
#by year
#first collapse
collapsed = hydro_plants[~hydro_plants.gen_id.duplicated()]

hydro_by_year = collapsed.groupby("inyr")["gen_id"].aggregate(len)
hydro_by_year = hydro_by_year.reset_index()
hydro_by_year.columns = ["start_year", "count_by_year"]

hydro_by_year = hydro_by_year.sort("start_year")

hydro_by_year = hydro_by_year.sort("start_year")

fig, ax = plt.subplots()
ax.bar(hydro_by_year.start_year, hydro_by_year.count_by_year)
fig.set_size_inches(8,6)
plt.show()

#capacity per year:
nplate_by_year = collapsed.groupby(["inyr", "nrg1"])["nplate"].aggregate(sum)
nplate_by_year = nplate_by_year.reset_index()
nplate_by_year.columns = ["year", "nplate_by_year"]

fig, ax = plt.subplots()
ax.bar(nplate_by_year.year, nplate_by_year.nplate_by_year)
ax.set_xlabel("Initial Year of Operation")
ax.set_ylabel("Installed Capacity, mW")
fig.set_size_inches(13,6)
fig.savefig("research/power_plants/figures/hydro_capacity_year.png")

#histogram of size of plants
fig, ax = plt.subplots()
ax.hist(collapsed.nplate)
plt.show()

#joint with time
fig, ax = plt.subplots()
ax.plot(collapsed.inyr, collapsed.nplate, 'bo', alpha=.4)
plt.show()

hydro_by_state = collapsed.groupby("state")["gen_id"].aggregate(len)
hydro_by_state.sort(inplace=True)
hydro_by_state = hydro_by_state.reset_index()
hydro_by_state.columns = ["state", "count_by_state"]

by_state_plot = sns.factorplot(x="state", y="count_by_state", kind = "bar",
	color = "blue", data = hydro_by_state)
by_state_plot.fig.set_size_inches(15,6)
by_state_plot.ax.set_ylabel("Number of plants by state")
plt.show()

#capacity by state


cap_by_state = collapsed.groupby("state")["nplate"].aggregate(sum)
cap_by_state.sort(inplace=True)
cap_by_state = cap_by_state.reset_index()
cap_by_state.columns=["state", "cap_by_state"]


cap_by_state_plot = sns.factorplot(x="state", y="cap_by_state", 
                                   data=cap_by_state, color="blue", kind="bar")
cap_by_state_plot.ax.set_ylabel("Installed Capacity, mW")
cap_by_state_plot.fig.set_size_inches(13,6)
#plt.show()
cap_by_state_plot.fig.savefig("research/power_plants/figures/hydro_capacity_state.png")

#Look at those that were retired:

retired = collapsed[collapsed.status=="RE"]
retired_by_year = retired.groupby("rtyr")["gen_id"].aggregate(len)
retired_cap_by_year = retired.groupby("rtyr")["nplate"].aggregate(sum)

fig, ax = plt.subplots(2)
ax[0].bar(retired_by_year.index.values, retired_by_year.values)
ax[0].set_ylabel("# of retirements")
ax[1].bar(retired_cap_by_year.index.values, retired_cap_by_year.values)
ax[1].set_xlabel("retirement year")
ax[1].set_ylabel("Capacity of retirement")
fig.set_size_inches(10,6)
plt.show()

#look at uprates:
uprate = hydro_plants[hydro_plants.puscap.notnull()]

uprate_coll = uprate[~uprate.gen_id.duplicated()]



#size of planned uprate to summer cap

fig, ax = plt.subplots(2)
ax[0].plot(uprate_coll.scap, uprate_coll.puscap, "bo")
ax[0].set_xlabel("initial summer capacity")
ax[0].set_ylabel("planned uprate capacity")
ax[1].plot(uprate_coll.puyr, uprate_coll.puscap, "bo")
ax[1].set_xlabel("planned uprate year")
ax[1].set_ylabel("planned uprate capacity")
plt.show()

#uprate by year
uprate_cap_year = uprate_coll.groupby("puyr")["puscap"].aggregate(sum)
uprate_cap_plot = uprate_cap_year.plot(kind="bar")
uprate_cap_plot.axes.set_ylabel("Uprate Capacity, mW")
uprate_cap_plot.axes.set_xlabel("Planned uprate year, mW")
uprate_cap_plot.figure.savefig("research/power_plants/figures/uprate_capacity.png")
plt.show()

uprate_by_type = uprate_coll.groupby("pm")["gen_id"].aggregate(len)

uprate_by_state = uprate_coll.groupby("state")["puscap"].aggregate(sum)
uprate_by_state.sort(inplace=True)

#Is there something else here though? What was it referred to
#uprate

by_pm = collapsed.groupby("pm")['gen_id'].aggregate(len)

#HY - hydrokinetic turbine
#PS - Pumped storage - hydr
#HL - Hydraulic Turbine (pipeline)
#HC - Hydraulic Turbine (conventional)
#HL - Hydraulic Turbine (pipeline)
#HR - Hydraulic Turbine Reversible (pumped storage)

pumped = hydro_plants[hydro_plants.pm=="PS"]
pumped_coll = pumped[pumped.gen_id.duplicated()]

#pumped storage capacity over time
pumped_by_year_cap = pumped_coll.groupby("inyr")["nplate"].aggregate(sum)
pump_cap_plot = pumped_by_year_cap.plot(kind="bar")
plt.show()
#by status
by_status = collapsed.groupby("status")['gen_id'].aggregate(len)
by_status.plot(kind="bar")
plt.show()

by_pstatus = collapsed.groupby("pstatus")['gen_id'].aggregate(len)
by_pstatus.plot(kind="bar")
plt.show()

#look at pmod and prpyr
mod_plants = hydro_plants[hydro_plants.pmod=="Y"]
repower_plants = hydro_plants[hydro_plants.prpyr.notnull()]
repower_plants[["gen_id", "prpyr"]]

#planned derate:
derate = hydro_plants[hydro_plants.pdscap.notnull()]

#pdscap - planned derate summer capacity


