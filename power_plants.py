#power_plants.py

#initial data clean and exploration

#master_ro_1990_2013.csv


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

#data file with many covariates, but limited sample
power_plants=pd.read_csv("research/power_plants_data/master_ro_1990_2013.csv")

power_plants = power_plants.sort(["ucode", "pcode","gcode", "year"])

power_plants["pcode"] = [str(i) for i in power_plants.pcode]
power_plants["gen_id"] = power_plants.pcode + "-" + power_plants.gcode

grouped_plants = power_plants.groupby(["gen_id"])


def has_uprate(plants):
	#test
	#plants = power_plants[power_plants["pcode"]==10867]
	#
	for i in plants.puscap:
		if ( ~ np.isnan(i)):
			return(True)
	return(False)

uprate_plants = grouped_plants.filter(has_uprate)

#uprate_plants.to_csv("research/power_plants_data/uprate_plants.csv")

uprate_plants = pd.read_csv("research/power_plants_data/uprate_plants.csv")
include = ['gen_id', 'year','inyr','ucode', 'status', 'nerc', 
'iso', 'node', 'naics', 'nplate','scap', 'wcap', 'state',
 'zip', 'county', 'cogen', 'nrg1', 'puyr', 
 'puscap', 'pm', ]

uprate_plants = uprate_plants[include]


uprate_plants[["inyr", "year", "gen_id", "puscap", "puyr", "scap", "nplate"]].head(200)


len(uprate_plants.gen_id.unique())

def norm_data(data):
	data = np.array(data)
	if (np.isnan(data[0])):
		return(np.nan)
	else:
		norm_data = np.round(data/(data[0]+.0001), decimals=2)
		return(norm_data)

uprate_plants = uprate_plants[uprate_plants["scap"].notnull()]
uprate_plants["n_scap"] = uprate_plants.groupby("gen_id")["scap"].transform(norm_data)


#planned retirement year
#prtyr
#create function to add to all values
def fill_in_group(data):
	data=data.ffill()
	data=data.bfill()
	return(data)


uprate_plants["cogen"] = uprate_plants.groupby("gen_id")["cogen"].transform(fill_in_group)
uprate_plants["county"] = uprate_plants.groupby("gen_id")["county"].transform(fill_in_group)

collapsed = uprate_plants[uprate_plants.puyr.notnull()]
collapsed = collapsed[collapsed.gen_id.duplicated()]

turb_type = collapsed.groupby("nrg1")["gen_id"].aggregate(len)
turb_type = turb_type.reset_index()
turb_type.columns = ["prim_fuel", "count"]
turb_type = turb_type.sort("count")

#prime fuel
prim_fuel = sns.factorplot(x="prim_fuel", y="count", 
	data=turb_type, kind="bar", size=6, aspect=1.5)
prim_fuel.set_xlabels("Primary Fuel")
plt.show()


#prime driver
prime_mover = collapsed.groupby("pm")["gen_id"].aggregate(len)
prime_mover = prime_mover.reset_index()
prime_mover.columns = ["Prime Mover", "Count"]
prime_mover = prime_mover.sort("Count")

prim_mover = sns.factorplot(x="Prime Mover", y="Count", 
	data=prime_mover, kind="bar", size=6, aspect=1.5)
#prim_mover.set_xlabels("Primary Driver")
plt.show()


#by planned upgrade year
collapsed = collapsed[collapsed.puyr!=0]
upgrade_year = collapsed.groupby("puyr")["gen_id"].aggregate(len)
upgrade_year = upgrade_year.reset_index()
upgrade_year.columns = ["Upgrade Year", "Count"]
upgrade_year = upgrade_year.sort("Upgrade Year")

upgrade_yr_plot = sns.factorplot(x="Upgrade Year", y="Count", 
	data=upgrade_year, kind="bar", size=8, aspect=2, color="blue")
#prim_mover.set_xlabels("Primary Driver")
plt.show()

#state

state = collapsed.groupby("state")["gen_id"].aggregate(len)
state = state.reset_index()
state.columns = ["state", "count"]
state = state.sort("count")

by_state = sns.factorplot(x="state", y="count", 
	data=state, kind="bar", size=6, aspect=2)
by_state.set_xlabels("By State")
plt.show()


uprate = collapsed[["gen_id", "puyr"]]
uprate.columns=["gen_id", "uprate_year"]
uprate["uprate_year"] = uprate.uprate_year.astype(int)
uprate = uprate[uprate.uprate_year>0]
uprate_plants = uprate_plants.merge(uprate, on="gen_id")

gen_id = uprate_plants.gen_id.unique()
gen_id = gen_id.tolist()

grouped_uprate = uprate_plants.set_index(["gen_id", "year"])
selection = grouped_uprate.T[gen_id[0:6]].T

selection.reset_index(inplace=True)

selection["uprate_year"] = selection.uprate_year.astype(int)

ggplot(aes(x="year", y="scap"), data=selection) +\
	geom_line() +\
	facet_wrap("gen_id")

select_long = pd.melt(selection[["gen_id", "nplate", "year", "puyr"]], id_vars=["gen_id", "nplate"])

ggplot(aes(x="value", y="nplate", linetype="variable"), data=select_long) +\
	geom_line() +\
	facet_wrap("gen_id")


ggplot(aes(x="year", y="nplate"), data=selection) +\
	geom_line() +\
	facet_wrap("gen_id")

sel_info = selection[~selection.gen_id.duplicated()]
sel_info.set_index("gen_id", inplace=True)
sel_info[["inyr", "nplate", "scap", "uprate_year", ""]]

#variable about whether upgrade happened. 

#direct data from eia
# eia_gen=pd.read_excel("research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx", header=1, sheetname="Operable")
# eia_gen_prop = pd.read_excel("research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx", header=1, sheetname="Proposed")
# eia_gen_retired = pd.read_excel("research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx", header=1, sheetname="Retired and Canceled")
# eia_plants=pd.read_excel("research/power_plants_data/eia8602013/2___Plant_Y2013.xlsx", header=1)
# eia_utility = pd.read_excel("research/power_plants_data/eia8602013/1___Utility_Y2013.xlsx", header=1)

#planned uprate year
uprate_by_year = uprate_data.groupby(["puyr"], sort=True)["puscap"].sum()
uprate_by_year = uprate_by_year[1:]
uprate_by_year.columns = "yearly_uprate"

fig, ax = plt.subplots()
ax.plot(uprate_by_year.index, uprate_by_year)
ax.set_xlabel("Planned uprate year")
ax.set_ylabel("Total yearly uprate, mw")
plt.show()

#percentage uprate
summer_up = uprate_data["puscap"][(uprate_data["puscap"]!=0) & (uprate_data["puscap"].notnull())].copy()
summer_up = np.array(summer_up)

winter_up = uprate_data["puwcap"][(uprate_data["puwcap"]!=0) & (uprate_data["puwcap"].notnull())].copy()
winter_up = np.array(winter_up)

fig, ax = plt.subplots()
ax.hist(summer_up, bins=30)
ax.set_xlabel("Size of Summer Up-rate, mw")
ax.set_label("frequency")
plt.show()

fig, ax = plt.subplots()
ax.hist(summer_up, bins=30)
ax.set_xlabel("Size of Winter Up-rate, mw")
ax.set_ylabel("frequency")
plt.show()

summer_perc_uprate = uprate_data["puscap"][uprate_data["scap"]!=0]/uprate_data["scap"][uprate_data["scap"]!=0]*100
summer_perc_uprate = summer_perc_uprate[summer_perc_uprate!=0]
summer_perc_uprate = summer_perc_uprate[summer_perc_uprate>0]
summer_perc_uprate = np.array(summer_perc_uprate)

fig, ax = plt.subplots()
ax.hist(summer_perc_uprate, bins=50)
ax.set_xlabel("Size of Summer Up-rate, percent")
ax.set_ylabel("frequency")
plt.show()

orig_capacity = uprate_data["scap"][uprate_data["scap"].notnull()]
orig_capacity = np.array(orig_capacity)

fig, ax = plt.subplots()
ax.hist(orig_capacity, bins=40)
ax.set_xlabel("Original Capacity, mw")
plt.show()

#time to planned uprate

#look at age of plants - or year of first operation
initial_year = [uprate_data["inyr"][uprate_data["inyr"].notnull()]]

fig, ax = plt.subplots()
ax.hist(initial_year, bins=50)
ax.set_xlabel("Initial year of operation")
plt.show()

uprate_data["time_to_uprate"] = uprate_data["puyr"] - uprate_data["inyr"]

time_to_uprate = uprate_data["time_to_uprate"]
time_to_uprate = np.array(time_to_uprate[time_to_uprate>0])

fig, ax = plt.subplots()
ax.hist(time_to_uprate, bins=50)
ax.set_xlabel("Time from initial operation year to planned uprate")
plt.show()

uprate_data.groupby("status").groups

uprate_data = uprate_data.sort(["pcode", "gcode", "year"])
uprate_data.head(50)

gen_grouped = uprate_data.groupby(["ucode", "pcode","gcode"])
groups = gen_grouped.groups

downrate_data = power_plants[["pdscap"].notnull()]

downrate_variables = ["year","state", "pm", "status", "nplate", 
 "scap",  "wcap",  "hr860","inmn", "inyr", "pmod", "pdscap", "pdwcap", "pdmn", "pdyr"]

downrate_data_lim = downrate_data[downrate_variables]

downrate_data = down_rate_data_lim[power_plants.pdscap.notnull()]


