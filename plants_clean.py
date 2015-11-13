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

#functions to use

#fill in data for similar groups with some missing data
def fill_in_group(data):
	data=data.ffill()
	data=data.bfill()
	return(data)

#add zero to front of zip codes
def zip0(code):
	code = str(code)
	if len(code)==4:
		return(str(0) + code)
	else:
		return(code)

#data file with many covariates, but limited sample
power_plants=pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/master_ro_1990_2013.csv", dtype={"zip":str})

generators2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/3_1_Generator_Y2014_Data_Early_Release.xlsx", header=2)
plants2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/2___Plant_Y2014_Data_Early_Release.xlsx", header=2)
wind_turbines =  pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/3_2_Wind_Y2014_Data_Early_Release.xlsx", header=2)
solar_plants = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/3_3_Solar_Y2014_Data_Early_Release.xlsx", header=2)

power_plants = power_plants.sort(["ucode", "pcode","gcode", "year"])

power_plants["pcode"] = [str(i) for i in power_plants.pcode]

power_plants["gen_id"] = power_plants.pcode + "-" + power_plants.gcode

#add variable for year uprate happened
generators2014["gen_id"] = generators2014[["Plant Code" ,"Generator ID"]].apply(lambda x: str(x[0]) + "-" + str(x[1]), axis=1)

generators2014 = generators2014.merge(plants2014[["Plant Code", "Zip", "Latitude", "Longitude", "Balancing Authority Code"]], on="Plant Code", how="left")

hydro2014 = generators2014[generators2014["Energy Source 1"]=="WAT"]

hy_include = ['Utility ID', 
	   'Utility Name', 
	   'Plant Code', 
	   'Plant Name',
       'State',
       'County', 
       'Generator ID',
       'Prime Mover', 
       'Unit Code',
       'Ownership', 
       'Nameplate Capacity (MW)',
       'Nameplate Power Factor',
       'Summer Capacity (MW)', 
       'Winter Capacity (MW)', 
       'Minimum Load (MW)',
       'Uprate or Derate Completed During Year',
       'Year Uprate or Derate Completed',
       'Status', 
       'Operating Month',
       'Operating Year', 
       'Planned Retirement Month', 
       'Planned Retirement Year',
       'Sector Name',
       'Sector',  
       'Energy Source 1', 
       'Turbines, Inverters, or Hydrokinetic Buoys',
       'Planned Net Summer Capacity Uprate (MW)',
       'Planned Net Winter Capacity Uprate (MW)', 
       'Planned Uprate Month',
       'Planned Uprate Year',
       'Planned New Nameplate Capacity (MW)',
       'Planned Repower Month',
       'Planned Repower Year',
       'Other Planned Modifications?', 
       'Other Modifications Year', 
       'gen_id',
       'Zip',
       'Latitude',
       'Longitude',
       'Balancing Authority Code']

hydro2014 = hydro2014[hy_include]

hy_names = hy_include
hy_names = [i.lower() for i in hy_names]

hy_names = ['utility_id',
 'utility_name',
 'plant_code',
 'plant_name',
 'state',
 'county',
 'generator_id',
 'prime_mover',
 'unit_code',
 'ownership',
 'nameplate',
 'power_factor',
 'summer_cap',
 'winter_cap',
 'min_load',
 'uprate_completed',
 'year_uprate_completed',
 'status',
 'op_month',
 'op_year',
 'plan_ret_month',
 'plan_ret_year',
 'sector_name',
 'sector',
 'energy_source',
 'turbines',
 'plan_uprate_sum',
 'plan_uprate_win',
 'plan_uprate_month',
 'plan_uprate_year',
 'plan_new_nameplate',
 'plan_repower_month',
 'plan_repower_year',
 'other_plan_mod',
 'other_mod_year',
 'gen_id',
 'zip',
 'lat',
 'long',
 'bal_auth_code']

hydro2014.columns = hy_names
hydro2014.to_csv("/Users/johannesmauritzen/research/power_plants_data/hydro2014.csv")

complete_year = generators2014[["gen_id", "Year Uprate or Derate Completed", "Latitude", "Longitude"]]
complete_year.columns = ["gen_id", "year_uprate_complete", "lat", "lon"]
power_plants = power_plants.merge(complete_year, on="gen_id", how="left")


include = ['gen_id', 'year','inyr','ucode', 'status', 'rtyr', 'prtyr' , 'nerc', 
'iso', 'node', 'naics', 'nplate','scap', 'wcap', 'state',
 'zip', 'county', 'cogen', 'nrg1', 'puyr', 
 'puscap', 'pm', 'pmod', 'omod', 'omodyr', 'pstatus', 'prpyr', 
 'pdscap', 'pdyr', 'efyr', 'cuyr', 'year_uprate_complete', 'lon', 'lat']


hydro = ["WAT", "CUR"]
#limit to hydro power

hydro_plants = power_plants[power_plants.nrg1.isin(hydro)]

hydro_plants = hydro_plants[include]
# wind_turbines = wind_turbines[include]
# solar_plants = solar_plants[include]

#replace 'HC' with 'HY'
hydro_plants["pm"][hydro_plants.pm=="HC"]="HY"
#replace 'HR' with 'PS'
hydro_plants["pm"][hydro_plants.pm=="HR"]='PS'

hydro_plants.to_csv("/Users/johannesmauritzen/research/power_plants_data/hydro_plants.csv")

wind_turb2014 = generators2014[generators2014["Energy Source 1"]=="WND"]
solar_plants2014 = generators2014[generators2014["Energy Source 1"]=="SUN"]

#energy_sources = generators2014.groupby("Energy Source 1")["gen_id"].aggregate(len)

wind_include = ["Utility ID", "Utility Name", "Plant Code", 
"State", "County", "Generator ID", "Nameplate Capacity (MW)",
 "Minimum Load (MW)", "Operating Month", "Operating Year",
  "Turbines, Inverters, or Hydrokinetic Buoys", "gen_id"]

wind_turb2014 = wind_turb2014[wind_include]
solar_plants2014 = solar_plants2014[wind_include]

wind_data = wind_turb2014.merge(plants2014[["Plant Code", "Zip", "Latitude", "Longitude",
       "Balancing Authority Code",
       "Balancing Authority Name",
       "Transmission or Distribution System Owner ID",
  "Transmission or Distribution System Owner"]], 
  on = ["Plant Code"], how= "left")

solar_data = solar_plants2014.merge(plants2014[["Plant Code", "Zip", "Latitude", "Longitude",  
 "Balancing Authority Code",
 "Balancing Authority Name",
 "Transmission or Distribution System Owner ID",
  "Transmission or Distribution System Owner"]], 
  on = ["Plant Code"], how = "left")

wind_data.columns = ["utility_id", "utility_name", "plant_code", 
"state", "county", "generator_id", "nplate", "min_load", 
"op_month", "op_year",  "num_turbs","gen_id","zip", "lat", "lon",
 "bal_auth_code", "bal_auth_name", "trans_owner_id", "trans_owner"]

solar_data.columns = ["utility_id", "utility_name", "plant_code", 
"state", "county", "generator_id","nplate", "min_load", 
"op_month", "op_year",  "num_turbs","gen_id","zip", "lat", "lon",
 "bal_auth_code", "bal_auth_name", "trans_owner_id", "trans_owner"]

wind_data["zip"] = wind_data.zip.apply(zip0)
solar_data["zip"] = wind_data.zip.apply(zip0)
hydro_plants["zip"] = hydro_plants.zip.apply(zip0)

def short_zip(z):
	try:
		return(z[0:2])
	except TypeError as e:
		return(np.nan)

wind_data["short_zip"] = wind_data.zip.apply(lambda x: x[0:2])
solar_data["short_zip"] = solar_data.zip.apply(short_zip)
hydro_plants["short_zip"]  = hydro_plants.zip.apply(lambda x: x[0:2])

wind_data.to_csv("/Users/johannesmauritzen/research/power_plants_data/wind_data.csv")
solar_data.to_csv("/Users/johannesmauritzen/research/power_plants_data/solar_data.csv")

wind_by_county = wind_data.groupby("county")["nplate"].aggregate(sum)
wind_by_zip = wind_data.groupby("short_zip")["nplate"].aggregate(sum)

wind_zip_year = wind_data.groupby(["short_zip", "op_year"])["nplate"].aggregate(sum)
wind_zip_year = wind_zip_year.reset_index()
wind_zip_year["cum_wind"] = wind_zip_year.groupby(["short_zip"])["nplate"].cumsum()
wind_zip_year.columns = ["short_zip", "year", "year_wind", "cum_wind"]

solar_zip_year = solar_data.groupby(["short_zip", "op_year"])["nplate"].aggregate(sum)
solar_zip_year = solar_zip_year.reset_index()
solar_zip_year["cum_solar"] = solar_zip_year.groupby(["short_zip"])["nplate"].cumsum()
solar_zip_year.columns = ["short_zip", "year", "year_solar", "cum_solar"]

hydro_plants = hydro_plants[hydro_plants.county.notnull()]
hydro_plants["county"] = hydro_plants.county.apply(lambda x:x.lower())

hydro_data = hydro_plants.merge(wind_zip_year, how = "left", on=["short_zip", "year"])
hydro_data = hydro_data.merge(solar_zip_year, how = "left", on = ["short_zip", "year"])

# hydro_data = hydro_plants.merge(wind_county_year, how = "left", on=["county", "year"])

hydro_data[["short_zip", "cum_wind", "cum_solar"]]

hydro_data["cum_wind"][np.isnan(hydro_data.cum_wind)] = 0
hydro_data["cum_solar"][np.isnan(hydro_data.cum_solar)] = 0
hydro_data["year_wind"][np.isnan(hydro_data.year_wind)] = 0
hydro_data["year_solar"][np.isnan(hydro_data.year_solar)] = 0
hydro_data["cum_intmtnt"] = hydro_data["cum_wind"] + hydro_data["cum_solar"]

hydro_data.to_csv("hydro_data.csv")





