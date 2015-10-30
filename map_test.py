#map_test.py
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import vincent
import json
from urllib.request import urlopen


#data

wind_data = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/wind_data.csv")
solar_data = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/solar_data.csv")
hydro2014 = pd.read_csv("/Users/johannesmauritzen/research/power_plants_data/hydro2014.csv")

x=wind_data.lon.values
y=wind_data.lat.values

x1=solar_data.lon.values
y1=solar_data.lat.values

# create new figure, axes instances.
fig=plt.figure(figsize=(12,8))
ax=fig.add_axes([0.1,0.1,.9,.9])
# setup mercator map projection.
m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,\
			urcrnrlon=-50.,urcrnrlat=50.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',projection='merc',)
            #lat_0=40.,lon_0=-20.)
# nylat, nylon are lat/lon of New York
m.drawcoastlines()
#m.fillcontinents()
m.drawstates()
m.drawcountries()
m.scatter(x,y,10, marker='x',color='green', latlon=True, label="Wind")
m.scatter(x1,y1,10, marker='o',color='red', latlon=True, label="Solar")
# draw parallels
#m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
#m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
ax.set_title("Wind and Solar power generators")
ax.legend()
plt.show()



#hydropower
x2=hydro2014.long.values
y2=hydro2014.lat.values

fig=plt.figure(figsize=(12,8))
ax=fig.add_axes([0.1,0.1,.9,.9])
# setup mercator map projection.
m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,\
			urcrnrlon=-50.,urcrnrlat=50.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',projection='merc',)
            #lat_0=40.,lon_0=-20.)
# nylat, nylon are lat/lon of New York
m.drawcoastlines()
#m.fillcontinents()
m.drawstates()
m.drawcountries()
m.scatter(x2,y2,10, marker='x',color='blue', latlon=True, label="Hydro Power")
# draw parallels
#m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
#m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
ax.set_title("Hydro power generators")
ax.legend()
plt.show()


#uprate
uprate = hydro2014[hydro2014.plan_uprate_year!= " "]
repower = hydro2014[hydro2014.plan_repower_year!=" "]


x3=uprate.long.values
y3=uprate.lat.values

x4 = repower.long.values
y4 = repower.lat.values

fig=plt.figure(figsize=(12,8))
ax=fig.add_axes([0.1,0.1,.9,.9])
# setup mercator map projection.
m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,\
			urcrnrlon=-50.,urcrnrlat=50.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',projection='merc',)
            #lat_0=40.,lon_0=-20.)
# nylat, nylon are lat/lon of New York
m.drawcoastlines()
#m.fillcontinents()
m.drawstates()
#m.drawcountries()
m.scatter(x3,y3,50, marker='x',color='blue', latlon=True, label="Hydro Power")
m.scatter(x4,y4,50, marker='x',color='blue', latlon=True, label="Repower")
# draw parallels
#m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
#m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
ax.set_title("Uprates and Repowers")
ax.legend()
plt.show()

#from hydro_data
hydro_data = pd.read_csv("hydro_data.csv")

uprate2 = hydro_data[hydro_data.puscap.notnull()]
uprate2 = uprate2[~uprate2.gen_id.duplicated()]

x5=uprate2.lon.values
y5=uprate2.lat.values

repower2 = hydro_data[hydro_data.prpyr.notnull()]
repower2 = repower2[~repower2.gen_id.duplicated()]

x6=repower2.lon.values
x7=repower2.lat.values

fig=plt.figure(figsize=(12,8))
ax=fig.add_axes([0.1,0.1,.9,.9])
# setup mercator map projection.
m = Basemap(llcrnrlon=-130.,llcrnrlat=20.,\
			urcrnrlon=-50.,urcrnrlat=50.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',projection='merc',)
            #lat_0=40.,lon_0=-20.)
# nylat, nylon are lat/lon of New York
m.drawcoastlines()
#m.fillcontinents()
m.drawstates()
#m.drawcountries()
m.scatter(x5,y5,50, marker='x',color='brown', latlon=True, label="Uprate")
m.scatter(x6,y6,50, marker='x',color='purple', latlon=True, label="Repower")

# draw parallels
#m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
#m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
ax.set_title("Uprates and Repowers")
ax.legend()
plt.show()

