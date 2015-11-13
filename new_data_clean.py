#new_data_clean.py
#open data from eia files and put into 

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

# generators2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/3_1_Generator_Y2014_Data_Early_Release.xlsx", header=2)
# plants2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/2___Plant_Y2014_Data_Early_Release.xlsx", header=2)

# gen_data = generators2012
# plant_data = plants2012
# report_year = 2012


def get_hydro_data(gen_data, plant_data, report_year):

	gen_data["gen_id"] = gen_data[["Plant Code" ,"Generator ID"]].apply(lambda x: str(x[0]) + "-" + str(x[1]), axis=1)

	gen_data.columns = [i.replace(" (MW)", "") for i in gen_data.columns]

	full_data = gen_data.merge(plant_data[["Plant Code", "Zip", "Latitude", "Longitude"]], on="Plant Code", how="left")

	hydro = full_data[full_data["Energy Source 1"]=="WAT"]
	hydro.columns = [i.lower() for i in hydro.columns]


	hy_include = ['Utility ID', 'Utility Name', 'Plant Code', 
		  'Plant Name','State','County', 'Generator ID',
	       'Prime Mover',  'Unit Code',
	       'Ownership', 'Nameplate Capacity',
	       'Summer Capacity', 
	       'Winter Capacity',
	       'Status', 
	       'Operating Month','Operating Year',
	        'Planned Retirement Month', 
	       'Planned Retirement Year', 'Sector Name',
	       'Sector',  'Energy Source 1', 
	       'Planned Net Summer Capacity Uprate',
	        'Planned Net Winter Capacity Uprate', 
	       'Planned Uprate Month','Planned Uprate Year',
	       'Planned Repower Month',
	       'Planned Repower Year',
	       'Other Planned Modifications?', 'Other Modifications Year', 
	       'gen_id','Zip','Latitude','Longitude']

	hy_include2 = ['Utility ID', 'Utility Name', 'Plant Code', 
		  'Plant Name','State','County', 'Generator ID',
	       'Prime Mover',  'Unit Code',
	       'Ownership', 'Nameplate Capacity',
	       'Summer Capacity', 
	       'Winter Capacity',
	       'Status', 
	       'Operating Month','Operating Year',
	       'Planned Retirement Month', 
	       'Planned Retirement Year', 'Sector Name',
	       'Sector',  'Energy Source 1',
	       'Planned Uprates Net Summer Capacity',
       		'Planned Uprates Net Winter Capacity',
	       'Planned Uprate Month','Planned Uprate Year',
	       'Planned Repower Month',
	       'Planned Repower Year',
	       'Other Modifications', 'Other Modifications Year', 
	       'gen_id','Zip','Latitude','Longitude']

	hy_include = [i.lower() for i in hy_include] 
	hy_include2 = [i.lower() for i in hy_include2]

	hy_names = ['utility_id',
			 'utility_name','plant_code','plant_name',
			 'state','county','generator_id','prime_mover',
			 'unit_code','ownership','nameplate',
			 'summer_cap','winter_cap','status','op_month',
			 'op_year','plan_ret_month','plan_ret_year','sector_name',
			 'sector','energy_source','plan_uprate_sum',
			 'plan_uprate_win','plan_uprate_month','plan_uprate_year',
			 'plan_repower_month','plan_repower_year',
			 'other_plan_mod','other_mod_year','gen_id','zip','lat','long']

	try:
		hydro = hydro[hy_include]
	except KeyError as k:
		hydro = hydro[hy_include2]

	hydro.columns = hy_names
	hydro["report_year"] = report_year
	return(hydro)


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


generators2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/3_1_Generator_Y2014_Data_Early_Release.xlsx", header=2)
plants2014 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602014er/2___Plant_Y2014_Data_Early_Release.xlsx", header=2)

generators2013 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx", header=1)
plants2013 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602013/2___Plant_Y2013.xlsx", header=1)

generators2012 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602012/GeneratorY2012.xlsx", header=1)
plants2012 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602012/PlantY2012.xlsx", header=1)

#generators2011 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602011/GeneratorY2011.xlsx", header=1)
#plants2011 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602011/Plant.xlsx", header=1)

#generators2010 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602010/GeneratorY2010.xlsx", header=2)
#plants2010 = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602010/PlantY2010.xlsx", header=2)

hydro2014 = get_hydro_data(generators2014, plants2014, 2014)
hydro2013 = get_hydro_data(generators2013, plants2013, 2013)
hydro2012 = get_hydro_data(generators2012, plants2012, 2012)

hydro_2012_2014 = pd.concat([hydro2014, hydro2013, hydro2012])
hydro_2012_2014 = hydro_2012_2014.sort(["gen_id", "report_year"])

def add_nan_series(series):
	def add_nan(value):
		if value == " ":
			return(np.nan)
		else:
			return(value)
	
	return(series.apply(add_nan))

series_nan = ["plan_repower_year", "plan_ret_month", 
"plan_ret_year", "plan_uprate_sum", "plan_uprate_win", 
"plan_uprate_month", "plan_uprate_year", "plan_repower_month",
"other_mod_year"]

hydro_2012_2014[series_nan] = hydro_2012_2014[series_nan].apply(add_nan_series, axis=0)

#merge in data from 2013/2014 on 
#balancing authority and completed uprate

generators2014["gen_id"] = generators2014[["Plant Code" ,"Generator ID"]].apply(lambda x: str(x[0]) + "-" + str(x[1]), axis=1)

gen_merge_data = generators2014[['gen_id', 'Uprate or Derate Completed During Year',
       'Month Uprate or Derate Completed', 'Year Uprate or Derate Completed']]
gen_merge_data.columns = [['gen_id', 'uprate_this_yr',
       'month_uprate_cmplt', 'yr_uprate_cmplt']]
gen_merge_data["month_uprate_cmplt"] = add_nan_series(gen_merge_data["month_uprate_cmplt"])
gen_merge_data["yr_uprate_cmplt"] = add_nan_series(gen_merge_data["yr_uprate_cmplt"])


plants_merge_data = plants2014[['Plant Code', 'NERC Region', 'Balancing Authority Code',
       'Balancing Authority Name',  'Transmission or Distribution System Owner',
       'Transmission or Distribution System Owner ID']]
plants_merge_data.columns = [['plant_code', 'nerc_region', 'bal_auth_code', 'bal_auth_name',
       'trans_owner','trans_owner_id']]
plants_merge_data["trans_owner_id"] = add_nan_series(plants_merge_data.trans_owner_id)


hydro_2012_2014 = hydro_2012_2014.merge(plants_merge_data, on = "plant_code", how="left")
hydro_2012_2014 = hydro_2012_2014.merge(gen_merge_data, on="gen_id", how="left")
hydro_2012_2014.to_csv("hydro_2012_2014.csv")


##################
new_hydro_data = pd.read_csv("hydro_2012_2014.csv")


#combine with measures of wind and solar data
wind_data = pd.read_csv("wind_data.csv")

solar_data = pd.read_csv("solar_data.csv")


wind_by_trans = wind_data.groupby("trans_owner_id")["nplate"].aggregate(sum)
wind_by_trans = wind_by_trans.reset_index()
wind_by_trans["report_year"]=2014
wind_by_trans.columns = ["trans_owner_id", "wind_cap", "report_year"]

wind_cap_2013 = wind_data[wind_data.op_year!=2014].groupby("trans_owner_id")["nplate"].aggregate(sum)
wind_cap_2013 = wind_cap_2013.reset_index()
wind_cap_2013["report_year"] = 2013
wind_cap_2013.columns = ["trans_owner_id", "wind_cap", "report_year"]

report_years = [2013,2014]
wind_cap_2012 = wind_data[~wind_data.op_year.isin(report_years)].groupby("trans_owner_id")["nplate"].aggregate(sum)
wind_cap_2012 = wind_cap_2012.reset_index()
wind_cap_2012["report_year"] = 2012
wind_cap_2012.columns = ["trans_owner_id", "wind_cap", "report_year"]

wind_by_trans = pd.concat([wind_by_trans, wind_cap_2013, wind_cap_2012])
wind_by_trans = wind_by_trans.sort(["trans_owner_id", "report_year"])

solar_by_trans = solar_data.groupby("trans_owner_id")["nplate"].aggregate(sum)
solar_by_trans = solar_by_trans.reset_index()
solar_by_trans["report_year"]=2014
solar_by_trans.columns = ["trans_owner_id", "solar_cap", "report_year"]

solar_cap_2013 = solar_data[solar_data.op_year!=2014].groupby("trans_owner_id")["nplate"].aggregate(sum)
solar_cap_2013 = solar_cap_2013.reset_index()
solar_cap_2013["report_year"] = 2013
solar_cap_2013.columns = ["trans_owner_id", "solar_cap", "report_year"]

report_years = [2013,2014]
solar_cap_2012 = solar_data[~solar_data.op_year.isin(report_years)].groupby("trans_owner_id")["nplate"].aggregate(sum)
solar_cap_2012 = solar_cap_2012.reset_index()
solar_cap_2012["report_year"] = 2012
solar_cap_2012.columns = ["trans_owner_id", "solar_cap", "report_year"]

solar_by_trans = pd.concat([solar_by_trans, solar_cap_2013, solar_cap_2012])
solar_by_trans = solar_by_trans.sort(["trans_owner_id", "report_year"])

#get rid of missing transmission owner data
solar_by_trans = solar_by_trans[solar_by_trans.trans_owner_id!=" "]
wind_by_trans = wind_by_trans[wind_by_trans.trans_owner_id!=" "]
#change to type float to match hydro data
solar_by_trans["trans_owner_id"] = solar_by_trans["trans_owner_id"].astype(float)
wind_by_trans["trans_owner_id"] = wind_by_trans["trans_owner_id"].astype(float)

new_hydro_data = new_hydro_data.merge(solar_by_trans, on = ["trans_owner_id", "report_year"], how = "left")
new_hydro_data = new_hydro_data.merge(wind_by_trans, on = ["trans_owner_id", "report_year"], how = "left")
new_hydro_data["solar_cap"][new_hydro_data.solar_cap.isnull()] = 0
new_hydro_data["wind_cap"][new_hydro_data.wind_cap.isnull()] = 0

new_hydro_data["intermittent_cap"] = new_hydro_data["solar_cap"] + new_hydro_data["wind_cap"]


#logit with excess zeros
num_uprates_by_trans = new_hydro_data.

new_hydro_data.to_csv("new_hydro_data.csv")

proposed_generators = pd.read_excel("/Users/johannesmauritzen/research/power_plants_data/eia8602013/3_1_Generator_Y2013.xlsx",sheetname = "Proposed",  header=1)

# OP	Operating - 
# SB	Standby/Backup 
# OA	Out of service 
# OS	Out of service 


