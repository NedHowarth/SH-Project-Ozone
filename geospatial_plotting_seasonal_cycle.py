# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 13:41:10 2020

@author: nedho
"""
#relevant imports
import pandas as pd
import geoplot as gplt
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
import seaborn as sns
from scipy import optimize

#geospatial plotting parameters
title = "Days from cycle peak to cycle trough"
Alt_bounds = (None,None)
query = 'peak_day'
station_area = None
min_data_length = 0

#list for columns in text file
series_ids = []
station_ids = []
data_lengths = []
list_lons = []
list_lats = []
list_alts = []
list_areas = []
peak_days = []
peak_ozone = []
trough_days = []
trough_ozone = []

#reading text file
file = open("global_stations_seasonal_cycle.txt", "r")
f1 = file.readlines()
#putting values in lists
for x in f1:
    a,b,c,d,e,f,g,h,i,j,k,blank = x.split(",")
    series_ids.append(a)
    station_ids.append(b)
    data_lengths.append(int(c))
    list_lons.append(float(d))
    list_lats.append(float(e))
    list_alts.append(float(f))
    list_areas.append(g)
    peak_days.append(float(h))
    peak_ozone.append(float(i))
    trough_days.append(float(j))
    trough_ozone.append(float(k))
    
    
#lists into dataframe
df = pd.DataFrame({
     'series_id':series_ids,
     'station_id':station_ids,
     'data_length':data_lengths,
     'Lon':list_lons,
     'Lat':list_lats,
     'alt':list_alts,
     'area':list_areas,
     'peak_day':peak_days,
     "ozone_max":peak_ozone,
     'trough_day':trough_days,
     "ozone_min":trough_ozone
     })

#defining new quantity in dataframe days from peak to trough
dif_day = []
for i in range(0,len(df)):
    if df['peak_day'].iloc[i] < df['trough_day'].iloc[i]:
        dif = df['trough_day'].iloc[i] - df['peak_day'].iloc[i]
    else:
        dif = (df['trough_day'].iloc[i] + 365) - df['peak_day'].iloc[i] 
    dif_day.append(dif)

df['trough-peak'] = dif_day

#defining new quantity in dataframe cycle flatness
flatness = []
for i in range(0,len(df)):
    dif = df['ozone_max'].iloc[i] - df['ozone_min'].iloc[i]
    flatness.append(dif)

df['max-min'] = flatness

#splitting dataframe for locations
Eu_df = df
Us_df = df
Jp_df = df

#reducing dataframes for location by lat/lon bounds
for i in range(0,len(df)):
    if df['Lon'][i] < -25:
        Eu_df = Eu_df.drop([i])
    elif df['Lon'][i] > 28:
        Eu_df = Eu_df.drop([i])
    elif df['Lat'][i] < 35:
        Eu_df = Eu_df.drop([i])
    elif df['Lat'][i] > 85:
        Eu_df = Eu_df.drop([i])
        
for i in range(0,len(df)):
    if df['Lon'][i] < -130:
        Us_df = Us_df.drop([i])
    elif df['Lon'][i] > -75:
        Us_df = Us_df.drop([i])
    elif df['Lat'][i] < 25:
        Us_df = Us_df.drop([i])
    elif df['Lat'][i] > 60:
        Us_df = Us_df.drop([i])
  
for i in range(0,len(df)):
    if df['Lon'][i] < 127:
        Jp_df = Jp_df.drop([i])
    elif df['Lon'][i] > 150:
        Jp_df = Jp_df.drop([i])
    elif df['Lat'][i] < 30:
        Jp_df = Jp_df.drop([i])
    elif df['Lat'][i] > 48:
        Jp_df = df.drop([i])

#reducing dataframes by area type
delete = []
delete1 = []
delete2 = []      
if station_area != None:
    for i in range(0,len(df)):
        if df['area'].iloc[i] != station_area:
            delete.append(df.index[i])
            
if station_area != None:
    for i in range(0,len(Eu_df)):
        if Eu_df['area'].iloc[i] != station_area:
            delete1.append(Eu_df.index[i])
            
if station_area != None:
    for i in range(0,len(Jp_df)):
        if Jp_df['area'].iloc[i] != station_area:
            delete2.append(Jp_df.index[i])
            
df = df.drop(delete)
Eu_df = Eu_df.drop(delete1)
Jp_df = Jp_df.drop(delete2)

#reducing dataframes by alt bounds
delete = []
delete1 = []
delete2 = []
delete3 = []
a,b = Alt_bounds
print(a)   
if Alt_bounds != (None,None):
    for i in range(0,len(df)):
        if df['alt'].iloc[i] < a or df['alt'].iloc[i] > b:
            #print(df['area'].iloc[i])
            delete.append(df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Eu_df)):
        if Eu_df['alt'].iloc[i] < a or Eu_df['alt'].iloc[i] > b:
            #print(df['area'].iloc[i])
            delete1.append(Eu_df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Us_df)):
        if Us_df['alt'].iloc[i] < a or Us_df['alt'].iloc[i] > b:
            #print(df['area'].iloc[i])
            delete2.append(Us_df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Jp_df)):
        if Jp_df['alt'].iloc[i] < a or Jp_df['alt'].iloc[i] > b:
            #print(df['area'].iloc[i])
            delete3.append(Jp_df.index[i])
            
df = df.drop(delete)
Eu_df = Eu_df.drop(delete1)
Us_df = Us_df.drop(delete2)
Jp_df = Jp_df.drop(delete3)

#turning dataframs into geospatial dataframes
geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
geometry1 = [Point(xy) for xy in zip(Eu_df.Lon, Eu_df.Lat)]
geometry2 = [Point(xy) for xy in zip(Us_df.Lon, Us_df.Lat)]
geometry3 = [Point(xy) for xy in zip(Jp_df.Lon, Jp_df.Lat)]
df = df.drop(['Lon', 'Lat'], axis=1)
Eu_df = Eu_df.drop(['Lon', 'Lat'], axis=1)
Us_df = Us_df.drop(['Lon', 'Lat'], axis=1)
Jp_df = Jp_df.drop(['Lon', 'Lat'], axis=1)
gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
Eu_gdf = gpd.GeoDataFrame(Eu_df, crs="EPSG:4326", geometry=geometry1)
Us_gdf = gpd.GeoDataFrame(Us_df, crs="EPSG:4326", geometry=geometry2)
Jp_gdf = gpd.GeoDataFrame(Jp_df, crs="EPSG:4326", geometry=geometry3)


#histogram, relevant quantity needs to be altered here
n_bins = 46
n, bins, patches = plt.hist(Eu_gdf['peak_day'], n_bins, facecolor='blue', alpha=0.5)
plt.title('histogram of peak ozone day, European Stations')
plt.xlabel('day of peak past start of year')
plt.ylabel('No. of stations')

b = []
for i in range(1,len(bins)):
      b.append((bins[i]+bins[i-1])/2) 

#fitting a gaussian/2 gaussians to histogram
def test_func(x, mu, sig, h):
    return h*(np.exp(-0.5*(((x-mu)/sig)**2)))

params, params_covariance = optimize.curve_fit(test_func, b[:29], n[:29],p0 = [bins[np.argmax(n[:29])],1,np.amax(n[:29])])
print(params)
plt.plot(b[:29], test_func(b[:29], params[0], params[1],params[2]))
params, params_covariance = optimize.curve_fit(test_func, b[28:], n[28:],p0 = [bins[np.argmax(n[28:])],20,np.amax(n[28:])])
print(params)
plt.plot(b[28:], test_func(b[28:], params[0], params[1],params[2]),color = 'red')
plt.show()



#histogram and boxplot relevant quantity needs to be altered here
sns.set(style="ticks")
f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, 
                                    gridspec_kw={"height_ratios": (.15, .85)})

sns.boxplot(Eu_gdf['ozone_max'], ax=ax_box,whis='range')
sns.distplot(Eu_gdf['ozone_max'], ax=ax_hist,kde=False)

ax_box.set(yticks=[])
ax_box.set(xlabel = None)
ax_hist.set(xlabel = 'Peak day')
ax_hist.set(ylabel = 'No. stations')
sns.despine(ax=ax_hist)
sns.despine(ax=ax_box, left=True)

#boxplots for each area corresponding to geospatial plot
f, (ax_box, ax_box1,ax_box2) = plt.subplots(3, sharex=True, 
                                    gridspec_kw={"height_ratios": (.15, .15, .15)})
sns.boxplot(Eu_gdf[query], ax=ax_box,whis='range')
sns.boxplot(Us_gdf[query], ax=ax_box1,whis='range')
sns.boxplot(Jp_gdf[query], ax=ax_box2,whis='range')
ax_box.set(yticks=[])
ax_box1.set(yticks=[])
ax_box2.set(yticks=[])
ax_box.set(xlabel = None)
ax_box1.set(xlabel = None)
ax_box2.set(xlabel = 'Ozone concetration at peak/ppb')
ax_box.set(ylabel='Europe')
ax_box1.set(ylabel='N.America')
ax_box2.set(ylabel='Japan-S.Korea')

sns.despine(ax=ax_box)
sns.despine(ax=ax_box1)
sns.despine(ax=ax_box2)

#histograms for each area corresponding to geospatial plot
f, (ax_hist, ax_hist1,ax_hist2) = plt.subplots(3, sharex=True, 
                                    gridspec_kw={"height_ratios": (.15, .15, .15)})
sns.distplot(Eu_gdf[query], ax=ax_hist,bins=46,kde=False)
sns.distplot(Us_gdf[query], ax=ax_hist1,bins=46,kde=False)
sns.distplot(Jp_gdf[query], ax=ax_hist2,bins=46,kde=False)
ax_hist.set(yticks=[])
ax_hist1.set(yticks=[])
ax_hist2.set(yticks=[])
ax_hist.set(xlabel = None)
ax_hist1.set(xlabel = None)
ax_hist2.set(xlabel = 'Peak_day')
ax_hist.set(ylabel='Europe')
ax_hist1.set(ylabel='N.America')
ax_hist2.set(ylabel='Japan-S.Korea')

sns.despine(ax=ax_hist)
sns.despine(ax=ax_hist1)
sns.despine(ax=ax_hist2)


#geospatial locations
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
Europe = (world.loc[world['continent'] == 'Europe'])
USA = (world.loc[world['continent'] == 'North America'])
Japan = (world.loc[world['name'] == 'Japan'])
Korea = (world.loc[world['name'] == 'South Korea'])


#plot of station distribution
ax = gplt.polyplot(world,linewidth=0.7)
gplt.pointplot(gdf,color = 'red',
               ax = ax)

#plt.title('Global Station Distribution For Stations With Valid Data Series')


#geospatial plots (titles are comented out)
Eu_ax = gplt.polyplot(Europe,linewidth=0.7)
gplt.pointplot(Eu_gdf,
               hue = query,
               cmap = 'plasma',
               k = None,
               alpha = 1,
               scale = query,
               limits = (25, 25),
               legend = True,
               
               ax = Eu_ax)

#plt.title(str(title)+', Europe')

Us_ax = gplt.polyplot(USA,linewidth=0.7)
gplt.pointplot(Us_gdf,
               hue = query,
               cmap = 'plasma',
               k = None,
               alpha = 0.8,
               scale = query,
               limits = (25, 25),
               legend = True,
               ax = Us_ax)
#plt.title(str(title)+', USA')

Us_ax1 = gplt.polyplot(USA,linewidth=0.7,
                       figsize = (80,60)
                       )
gplt.voronoi(Us_gdf, figsize = (80,60),
               hue = query,
               cmap = 'plasma',
               clip = USA,
               k = None,
               linewidth = 0.1,
               alpha = 0.9,
               legend = True,ax = Us_ax1)

#plt.title(str(title)+', USA')

Jp_ax =gplt.polyplot(world,linewidth=0.7)
gplt.pointplot(Jp_gdf,
               hue = query,
               cmap = 'plasma',
               k = None,
               alpha = 0.8,
               scale = query,
               limits = (20, 20),
               legend = True,ax = Jp_ax)
#plt.title(str(title)+', Japan')
