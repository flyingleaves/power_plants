#hyro_plants.py

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

#data file with many covariates, but limited sample
power_plants=pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/master_ro_1990_2013.csv", dtype={"zip":str})

power_plants = power_plants.sort(["ucode", "pcode","gcode", "year"])

power_plants["pcode"] = [str(i) for i in power_plants.pcode]
power_plants["gen_id"] = power_plants.pcode + "-" + power_plants.gcode

hydro = ["WAT", "CUR"]
#limit to hydro power
hydro_plants = power_plants[power_plants.nrg1.isin(hydro)]

wind = ['WT', 'WS']
#WT - onshore wind
#WS - offshore wind

wind_turbines = power_plants[power_plants.pm.isin(wind)]

solar =  ["SUN", "Sun", "sun"]
solar_plants = power_plants[power_plants.nrg1.isin(solar)]

include = ['gen_id', 'year','inyr','ucode', 'status', 'rtyr', 'prtyr' , 'nerc', 
'iso', 'node', 'naics', 'nplate','scap', 'wcap', 'state',
 'zip', 'county', 'cogen', 'nrg1', 'puyr', 
 'puscap', 'pm', 'pmod', 'omod', 'omodyr', 'pstatus', 'prpyr', 
 'pdscap', 'pdyr', 'efyr', 'cuyr']

#pmod - planned modification
#pm - prime mover
#prpyr - planned repower yr
#pstatus - planned status
#pnewpm - planned new prime mover
#pdscap - planned derate summer capacity
#pdyr - planned derate year
#efyr - effective year - planned effective year to be operating
#cuyr - currently planned effective year to be operating

hydro_plants = hydro_plants[include]
wind_turbines = wind_turbines[include]
solar_plants = solar_plants[include]

#replace 'HC' with 'HY'
hydro_plants["pm"][hydro_plants.pm=="HC"]="HY"
#replace 'HR' with 'PS'
hydro_plants["pm"][hydro_plants.pm=="HR"]='PS'

hydro_plants.to_csv("/Users/johannesmauritzen/research/power_plants_data/hydro_plants.csv")
wind_turbines.to_csv("/Users/johannesmauritzen/research/power_plants_data/wind_turbines.csv")

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


#Wind turbines
#wind_turbines = wind_turbines[wind_turbines.inyr.notnull()]
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


#match zip code to county:
# zip_data = pd.read_table("http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt", 
# 	sep=",", header=0, dtype={"ZCTA5":str ,'STATE':str,'COUNTY':str})

# zip_county = zip_data[["ZCTA5", "STATE", "COUNTY", "COPOP", "COAREA"]]
# zip_county.columns = ["zip", "state_id", "county_id", "county_pop", "county_area"]

# county_data = pd.read_table('http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt',
# 	sep=",",header=None, names=["state", "state_id", "county_id", "county", "county_type"], dtype={"county_id":str ,'state_id':str})

# zip_county = zip_county.merge(county_data, how = "left", on = ["state_id", "county_id"])

# new_county = zip_county.county.apply(lambda x:re.sub('\ County', '',x))
# new_county = new_county.apply(lambda x:re.sub('\ Census Area', '',x))
# new_county = new_county.apply(lambda x:re.sub('\ Municipio', '',x))
# new_county = new_county.apply(lambda x:re.sub('\ Municipality', '',x))
# new_county = new_county.apply(lambda x:re.sub('\ Borough', '',x))

# new_county = new_county.apply(lambda x:x.lower())
# zip_county["new_county"] =new_county
# zip_county = zip_county[zip_county.zip.duplicated()]

#look at wind by county
# def rob_lower(x):
# 	try:
# 		return(x.lower())
# 	except AttributeError:
# 		return(np.nan)

# wind_coll["county"] = wind_coll.county.apply(rob_lower)


wind_data = wind_coll

wind_data["zip"] = wind_data.zip.apply(zip0)

wind_data["short_zip"] = wind_data.zip.apply(lambda x: str(x)[0:3])

wind_zip_year = wind_data.groupby(["short_zip", "inyr"])["nplate"].aggregate(sum)
wind_zip_year = wind_zip_year.reset_index()
wind_zip_year["cum_wind"] = wind_zip_year.groupby(["short_zip"])["nplate"].cumsum()
wind_zip_year.columns = ["short_zip", "year", "year_wind", "cum_wind"]

wind_by_county = wind_data.groupby(["state","county"])["nplate"].aggregate(sum)
wind_by_county = wind_by_county.reset_index()
wind_by_county = wind_by_county.sort(["state", "nplate"])

wind_by_county.columns = ["state", "county", "tot_cap"]

wind_county_year = wind_data.groupby(["state", "county", "inyr"])["nplate"].aggregate(sum)

wind_county_year = wind_county_year.reset_index()
wind_county_year["wind_cum"] = wind_county_year.groupby(["state", "county"])["nplate"].cumsum()

kern_county = wind_county_year[wind_county_year.county=="Kern"]

fig, ax = plt.subplots()
ax.plot(kern_county.inyr, kern_county.wind_cum, lw=2)
plt.show()

# wind_by_zip = wind_data.groupby(["short_zip"])["nplate"].aggregate(sum)
# wind_by_zip = wind_by_zip.reset_index()
# wind_by_zip.columns = ["short_zip","zip_wind_cap"]

# top_five = wind_by_state[-5:].index.values


#fig, ax = plt.subplots(2)

county_wind_plot = sns.factorplot(x="county", y="nplate", col = "state",
col_wrap=2, kind="bar", data=wind_by_county, size=2, aspect=1.5)
county_wind_plot.axes.
plt.show()

ggplot(aes(y="nplate"), data=wind_by_county[wind_by_county.state.isin(top_five)]) +\
	geom_bar() +\
	facet_wrap("state", ncol=2, scales="free")

#merge hydro data with wind data
wind_county_year.columns = ["state", "county", "year", "installed_wind", "cum_wind"]


def fill_in_group(data):
	data=data.ffill()
	data=data.bfill()
	return(data)

hydro_plants["county"] = hydro_plants.groupby("gen_id")["county"].transform(fill_in_group)

def zip0(code):
	if len(code)==4:
		return(str(0) + str(code))
	else:
		return(str(code))

hydro_plants["zip"] = hydro_plants.zip.apply(zip0)
hydro_plants["short_zip"] = hydro_plants.zip.apply(lambda x: str(x)[0:3])

hydro_data = hydro_plants.merge(wind_zip_year, how = "left", on=["short_zip", "year"])
hydro_data.to_csv("hydro_data.csv")

with_wind = hydro_data[hydro_data.cum_wind.notnull()]
wind_and_uprate = with_wind[with_wind.puyr.notnull()]

len(with_wind.gen_id)
len(hydro_data.gen_id)



