# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 16:34:19 2020

@author: nedho
"""
#relevant imports
import pandas as pd
import geoplot as gplt
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from scipy import optimize

#plotting parameters
title = "Significant gradient Peak change throught data series"
Alt_bounds = (None,None)
query = 'grad'
station_area = None

#lists for dataframe
series_ids = []
station_ids = []
data_lengths = []
list_lons = []
list_lats = []
list_alts = []
list_areas = []
pearsons = []
grad = []
grad_error = []
peak_mean = []
peak_stdv = []

#reading file lines
file = open("world_stations_peak_change.txt", "r")
f1 = file.readlines()
for x in f1:
    #column values into lists
    a,b,c,d,e,f,g,h,i,j,k,l,blank = x.split(",")
    series_ids.append(a)
    station_ids.append(b)
    data_lengths.append(int(c))
    list_lons.append(float(d))
    list_lats.append(float(e))
    list_alts.append(float(f))
    list_areas.append(g)
    pearsons.append(float(h))
    grad.append(float(i))
    grad_error.append(float(j))
    peak_mean.append(float(k))
    peak_stdv.append(abs(float(l)))
    
    
#creating dataframe
df = pd.DataFrame({
     'series_id':series_ids,
     'station_id':station_ids,
     'data_length':data_lengths,
     'Lon':list_lons,
     'Lat':list_lats,
     'alt':list_alts,
     'area':list_areas,
     'corelation':pearsons,
     'grad':grad,
     'grad_error':grad_error,
     'peak_mean':peak_mean,
     'peak_stdv':peak_stdv,
     })

#removing stations with under 20 years of data
for i in range(0,len(df)):
    if df['data_length'][i] < 20:
        df = df.drop([i])

#splitting into areas
Eu_df = df
Us_df = df
Jp_df = df

#reducing by lat/lon bounds
delete = []
for i in range(0,len(df)):
    if df['Lon'].iloc[i] < -25:
        delete.append(df.index[i])
    elif df['Lon'].iloc[i] > 28:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] < 35:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] > 85:
        delete.append(df.index[i])
Eu_df = Eu_df.drop(delete)

delete = []      
for i in range(0,len(df)):
    if df['Lon'].iloc[i] < -130:
        delete.append(df.index[i])
    elif df['Lon'].iloc[i] > -75:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] < 25:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] > 60:
        delete.append(df.index[i])
Us_df = Us_df.drop(delete)      

delete = []       
for i in range(0,len(df)):
    if df['Lon'].iloc[i] < 127:
        delete.append(df.index[i])
    elif df['Lon'].iloc[i] > 150:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] < 30:
        delete.append(df.index[i])
    elif df['Lat'].iloc[i] > 48:
        delete.append(df.index[i])
Jp_df = Jp_df.drop(delete)
 
#reducing by station area
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


#reducing by altitude bounds
delete = []
delete1 = []
delete2 = []
delete3 = []
a,b = Alt_bounds

if Alt_bounds != (None,None):
    for i in range(0,len(df)):
        if df['alt'].iloc[i] < a or df['alt'].iloc[i] > b:
            delete.append(df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Eu_df)):
        if Eu_df['alt'].iloc[i] < a or Eu_df['alt'].iloc[i] > b:
            delete1.append(Eu_df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Us_df)):
        if Us_df['alt'].iloc[i] < a or Us_df['alt'].iloc[i] > b:
            delete2.append(Us_df.index[i])
            
if Alt_bounds != (None,None):
    for i in range(0,len(Jp_df)):
        if Jp_df['alt'].iloc[i] < a or Jp_df['alt'].iloc[i] > b:
            delete3.append(Jp_df.index[i])
          
df = df.drop(delete)
Eu_df = Eu_df.drop(delete1)
Us_df = Us_df.drop(delete2)
Jp_df = Jp_df.drop(delete3)

#dataframe into geodataframe
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

#histograms with fitted gaussians for each area
n_bins = 40
n, bins, patches = plt.hist(Eu_gdf['grad'], n_bins, facecolor='blue',alpha = 0.7)
b = []
for i in range(1,len(bins)):
      b.append((bins[i]+bins[i-1])/2) 

def test_func(x, mu, sig, h):
    return h*(np.exp(-0.5*(((x-mu)/sig)**2)))

params, params_covariance = optimize.curve_fit(test_func, b, n,p0 = [bins[np.argmax(n)],1,np.amax(n)])
plt.plot(b, test_func(b, params[0], params[1],params[2]),color = 'red')
plt.show()

n, bins, patches = plt.hist(Us_gdf['grad'], n_bins, facecolor='blue',alpha = 0.7)
b = []
for i in range(1,len(bins)):
      b.append((bins[i]+bins[i-1])/2) 
params, params_covariance = optimize.curve_fit(test_func, b, n,p0 = [bins[np.argmax(n)],1,np.amax(n)])
plt.plot(b, test_func(b, params[0], params[1],params[2]),color = 'red')
plt.show()

n, bins, patches = plt.hist(Jp_gdf['grad'], n_bins, facecolor='blue',alpha = 0.7)
b = []
for i in range(1,len(bins)):
      b.append((bins[i]+bins[i-1])/2) 
params, params_covariance = optimize.curve_fit(test_func, b, n,p0 = [bins[np.argmax(n)],1,np.amax(n)])
plt.plot(b, test_func(b, params[0], params[1],params[2]),color = 'red')
plt.show()


#Eu_gdf.to_csv('Europe_stations_peak_change.csv')

#error propogation on mean grad for area
sig_Eu = 0
for i in range(0,len(Eu_gdf)):
    if Eu_gdf['grad_error'].iloc[i] != np.inf:
        m = Eu_gdf['grad'].iloc[i]
        dm = Eu_gdf['grad_error'].iloc[i]
        dm = dm
        dm = dm**2
        sig_Eu += dm
sig_Eu = np.sqrt(sig_Eu/len(Eu_gdf))


print(np.mean(Eu_gdf['grad']))
print(sig_Eu)

sig_Us = 0
for i in range(0,len(Us_gdf)):
    if Us_gdf['grad_error'].iloc[i] != np.inf:
        m = Us_gdf['grad'].iloc[i]
        dm = Us_gdf['grad_error'].iloc[i]
        dm = dm
        dm = dm**2
        sig_Us += dm
sig_Us = np.sqrt(sig_Us/len(Us_gdf))


print(np.mean(Us_gdf['grad']))
print(sig_Us)

sig_Jp= 0
for i in range(0,len(Jp_gdf)):
    if Jp_gdf['grad_error'].iloc[i] != np.inf:
        m = Jp_gdf['grad'].iloc[i]
        dm = Jp_gdf['grad_error'].iloc[i]
        dm = dm
        dm = dm**2
        sig_Jp += dm
sig_Jp = np.sqrt(sig_Jp/len(Jp_gdf))


print(np.mean(Jp_gdf['grad']))
print(sig_Jp)


#reducing plots to only statistically significant stations
#hypothosis test
p = 0.95
z = 1.96
delete = []
print(len(Eu_gdf))
print(len(Eu_gdf)*(1-p))
for i in range(0,len(Eu_gdf)):
    if Eu_gdf['grad'].iloc[i] > 0:
        sig = abs(Eu_gdf['grad_error'].iloc[i]*z)
        if Eu_gdf['grad'].iloc[i] - sig < 0:
            delete.append(Eu_gdf.index[i])
            
    else:
        sig = abs(Eu_gdf['grad_error'].iloc[i]*z)
        if Eu_gdf['grad'].iloc[i] + sig > 0:
            
            delete.append(Eu_gdf.index[i])
Eu_gdf = Eu_gdf.drop(delete)
print(len(Eu_gdf))

print(len(Us_gdf))
print(len(Us_gdf)*(1-p))
delete = []
for i in range(0,len(Us_gdf)):
    if Us_gdf['grad'].iloc[i] > 0:
        sig = abs(Us_gdf['grad_error'].iloc[i]*z)
        if Us_gdf['grad'].iloc[i] - sig < 0:
            delete.append(Us_gdf.index[i])
    else:
        sig = abs(Us_gdf['grad_error'].iloc[i]*z)
        if Us_gdf['grad'].iloc[i] + sig > 0:
            
            delete.append(Us_gdf.index[i])
Us_gdf = Us_gdf.drop(delete)
print(len(Us_gdf))

print(len(Jp_gdf))
print(len(Jp_gdf)*(1-p))
delete = []
for i in range(0,len(Jp_gdf)):
    if Jp_gdf['grad'].iloc[i] > 0:
        sig = abs(Jp_gdf['grad_error'].iloc[i]*z)
        if Jp_gdf['grad'].iloc[i] - sig < 0:
            delete.append(Jp_gdf.index[i])
    else:
        sig = abs(Jp_gdf['grad_error'].iloc[i]*z)
        if Jp_gdf['grad'].iloc[i] + sig > 0:
            
            delete.append(Jp_gdf.index[i])
Jp_gdf = Jp_gdf.drop(delete)
print(len(Jp_gdf))

sig_Eu = 0
for i in range(0,len(Eu_gdf)):
    if Eu_gdf['grad_error'].iloc[i] != np.inf:
        m = Eu_gdf['grad'].iloc[i]
        dm = Eu_gdf['grad_error'].iloc[i]
        dm = dm
        dm = dm**2
        sig_Eu += dm
        #print(sig_Eu,dm)
sig_Eu = np.sqrt(sig_Eu/len(Eu_gdf))


print(np.mean(Eu_gdf['grad']))
print(np.std(Eu_gdf['grad']))
print(sig_Eu)


#changing plots to be binary positive or negative grad
pos = 0
neg = 0
for i in range(0,len(gdf)):
    if gdf['grad'].iloc[i] > 0:
        gdf['grad'].iloc[i] = 1
        pos+=1
    else:
        gdf['grad'].iloc[i] = -1
        neg+=1
print(pos)
print(neg)
pos = 0
neg = 0     
for i in range(0,len(Eu_gdf)):
    if Eu_gdf['grad'].iloc[i] > 0:
        Eu_gdf['grad'].iloc[i] = 1
        pos+=1
    else:
        Eu_gdf['grad'].iloc[i] = -1
        neg+=1
print(pos)
print(neg)
pos = 0
neg = 0 
for i in range(0,len(Us_gdf)):
    if Us_gdf['grad'].iloc[i] > 0:
        Us_gdf['grad'].iloc[i] = 1
        pos+=1
    else:
        Us_gdf['grad'].iloc[i] = -1
        neg+=1
print(pos)
print(neg)
pos = 0
neg = 0        
for i in range(0,len(Jp_gdf)):
    if Jp_gdf['grad'].iloc[i] > 0:
        Jp_gdf['grad'].iloc[i] = 1
        pos+=1
    else:
        Jp_gdf['grad'].iloc[i] = -1
        neg+=1
       
print(pos)
print(neg) 


#gdf = gdf[]
#gdf.to_csv('Europe_stations_data.csv')


#geospatial areas
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
Europe = (world.loc[world['continent'] == 'Europe'])
USA = (world.loc[world['continent'] == 'North America'])
Japan = (world.loc[world['name'] == 'Japan'])
Korea = (world.loc[world['name'] == 'South Korea'])

#geospatial pointplots
ax = gplt.polyplot(world,linewidth=0.7)
gplt.pointplot(gdf,
               hue = query,
               cmap = 'rainbow',
               k = 2,
               alpha = 0.8,
               scale = query,
               limits = (20, 20),
               legend = True,
               legend_values = [-1,1],
               legend_labels = ['negative','positive'],
               ax = ax)
plt.title('Global Station Distribution For Stations With Valid Data Series')

Eu_ax = gplt.polyplot(Europe,linewidth=0.7)
gplt.pointplot(Eu_gdf,
               hue = query,
               cmap = 'rainbow',
               k = 2,
               alpha = 0.8,
               scale = query,
               limits = (30,30),
               legend = True,
               #legend_values = [-1,1],
               #legend_labels = ['negative','positive'],
               ax = Eu_ax)
print(Eu_gdf['peak_mean'])

plt.title(str(title)+', Europe')

Us_ax = gplt.polyplot(USA,linewidth=0.7)
gplt.pointplot(Us_gdf,
               hue = query,
               cmap = 'rainbow',
               k = 2,
               alpha = 0.8,
               scale = query,
               limits = (30, 30),
               legend = True,
               #legend_values = [-1,1],
               #legend_labels = ['negative','positive'],
               ax = Us_ax)
plt.title(str(title)+', USA')

Us_ax1 = gplt.polyplot(USA,linewidth=0.7
                       #,figsize = size
                       )
gplt.voronoi(Us_gdf,
               hue = query,
               cmap = 'rainbow',
               clip = USA,
               k = None,
               linewidth = 0.1,
               alpha = 0.9,
               #scale = query,
               #limits = (30, 30),
               legend = True,ax = Us_ax1)

plt.title(str(title)+', USA')

Jp_ax =gplt.polyplot(world,linewidth=0.7)
gplt.pointplot(Jp_gdf,
               hue = query,
               cmap = 'rainbow',
               k = 2,
               alpha = 0.8,
               scale = query,
               limits = (30, 30),
               #legend_values = [-1,1],
               #legend_labels = ['negative','positive'],
               legend = True,
               ax = Jp_ax)
plt.title(str(title)+', Japan')