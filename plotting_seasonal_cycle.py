# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 15:09:43 2020

@author: nedho
"""
#relevant imports
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

#reduce plots by bounds
station_area = None
Alt_bounds = (None,None)

#empty lists for file columns
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

#reding in a and looping over file lines
file = open("global_stations_seasonal_cycle.txt", "r")
f1 = file.readlines()
for x in f1:
    #putting relevant data in respective list
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

#new dataframe quantity days from peak to trough
dif_day = []
for i in range(0,len(df)):
    if df['peak_day'].iloc[i] < df['trough_day'].iloc[i]:
        dif = df['trough_day'].iloc[i] - df['peak_day'].iloc[i]
    else:
        dif = (df['trough_day'].iloc[i] + 365) - df['peak_day'].iloc[i] 
    dif_day.append(dif)

df['trough-peak'] = dif_day

#new dataframe quantity flatness
flatness = []
for i in range(0,len(df)):
    dif = df['ozone_max'].iloc[i] - df['ozone_min'].iloc[i]
    flatness.append(dif)

df['max-min'] = flatness

#splitting by area
Eu_df = df
Us_df = df
Jp_df = df
#southern hemisphere
S_df = df

#reducing dataframes by lat/lon bounds
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
        
for i in range(0,len(df)):
    if df['Lat'][i] > 0:
        S_df = S_df.drop([i])

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


#reducing dataframes by altitude bounds
delete = []
delete1 = []
delete2 = []
delete3 = []
a,b = Alt_bounds 
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
        

#plotting/ alter this section for different plots
fig, ax = plt.subplots(figsize = (20,12))
ax.scatter(Eu_df['peak_day'],Eu_df['trough-peak'],s = 25,color='blue',label = 'Europe')
ax.scatter(Us_df['peak_day'],Us_df['trough-peak'],s = 25,color='red',label = 'North America')
ax.scatter(Jp_df['peak_day'],Jp_df['trough-peak'],s = 25,color='black',label = 'Japan-S.Korea')
ax.scatter(S_df['peak_day'],S_df['trough-peak'],s = 25,color='green',label = 'S.Hemisphere')
ax.set_title('Plot of cycle days from cycle peak to trough against peak day',fontsize = 40,pad = 30)
plt.xticks(fontsize = 25)
plt.yticks(fontsize = 25)
ax.set_xlabel('Peak day',fontsize = 30)
ax.set_ylabel('Days from peak to trough',fontsize = 30)
legend = ax.legend(loc='lower right', fontsize=30,prop={'size': 28})

#correlation
r = stats.pearsonr(df['peak_day'],df['ozone_max'])
print(r)

