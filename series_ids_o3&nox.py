# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 19:13:24 2020

@author: nedho
"""
#relevant
from urllib.request import urlopen
import json
import numpy as np
import time
import urllib

#measuring code time and opening output file 
start = time.time()
outfile = open('nox_o3_ids.txt','w')

#lists of station ids
station_o3 = []
station_nox = []
station_both = []

#lists of series ids
series_ids_o3 = []
series_ids_o3_keep = []
series_ids_nox = []
series_ids_nox_keep = []

#other station data
station_lons,station_lats = [],[]
station_alts = []
station_area = []

#error counter
Error = 0

#URLs
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"
URL1 ="search/?station_country=Japan&parameter_name=o3&columns=id,station_id,station_lon,station_lat,station_alt,station_type_of_area"
URL2 ="search/?station_country=Japan&parameter_name=nox&columns=id,station_id,station_lon,station_lat,station_alt,station_type_of_area"
URL1 = BASEURL + URL1
URL2 = BASEURL + URL2

#opening URLs
response1 = urlopen(URL1).read().decode('utf-8')
response2 = urlopen(URL2).read().decode('utf-8')

#getting data from URls
metadata1 = json.loads(response1)
metadata2 = json.loads(response2)

#putting data into empty lists for both o3 and nox stations
for s in metadata1:
    station_o3.append(s[1])
    series_ids_o3.append((s[0][0]))
    station_lons.append(s[2])
    station_lats.append(s[3])
    station_alts.append(s[4])
    station_area.append(s[5])
for s in metadata2:
    station_nox.append(s[1])
    series_ids_nox.append((s[0][0]))

#finding stations that have both nox and o3 series
for i in range(0,len(station_o3)):
    for j in range(0,len(station_nox)):
        if station_o3[i] == station_nox[j]:
            #filtering out double o3 ids for a single station
            double = 0
            for l in range(0,len(station_both)):
                if  station_o3[i] == station_both[l]:
                    double += 1
            if double == 0 : 
                #relevant staion ids and corresponding series ids
                station_both.append(station_o3[i])
                series_ids_o3_keep.append(series_ids_o3[i])
                series_ids_nox_keep.append(series_ids_nox[j])
                

#looping over station series ids to find valid data
for i0 in range(0,len(station_both)):
    
    #URLs to get data series
    URL1 = "stats/?id=" + str(series_ids_o3_keep[i0]) + "&sampling=daily"
    URL2 = "stats/?id=" + str(series_ids_nox_keep[i0]) + "&sampling=daily"
    URL1 = BASEURL + URL1
    URL2 = BASEURL + URL2
    print(str(i0) + ":" + URL1)
    
    #opening URL and getting datasreies
    try:
        response1 = urlopen(URL1).read().decode('utf-8')
        o3_data = json.loads(response1)
        response2 = urlopen(URL2).read().decode('utf-8')
        nox_data = json.loads(response2)
    
    #error - wrong format
    except urllib.error.HTTPError:
        Error += 1
    try:
        #filtering out data series that are too short
        days = 3650
        if len(o3_data['datetime']) > days and len(nox_data['datetime']) > days/4:
            #counters for missing data
            j1 = 0
            j2 = 0
            #if enough data in series then keep the station
            check_nan1 = np.isnan(o3_data['mean'])                                           
            check_nan2 = np.isnan(nox_data['mean'])
            for i in range(0,len(o3_data['mean'])):                
                if check_nan1[i] == True:
                    j1 += 1
            for i in range(0,len(nox_data['mean'])):
                if check_nan1[i] == True:
                    j2 += 1
            missing_data1 = j1/len(o3_data['mean'])
            missing_data2 = j2/len(nox_data['mean'])
            
            if missing_data1 < 0.2 and missing_data2 < 0.2:
                
                #writing out valid data series for stations with both nox and o3 series
                            
                outfile.write(str(series_ids_o3_keep[i0])+','+str(series_ids_nox_keep[i0])+','+str(station_both[i0])+','+str(np.nanmean(nox_data['mean']))+','+str(station_lons[i0])+','+str(station_lats[i0])+','+str(station_alts[i0])+','+str(station_area[i0])+ ",\n")
     
    #errors        
    except TypeError:
        #data embargo?
        Error += 1
    except KeyError:
        #no data in series
        Error += 1 
    except NameError:
        #wrong labeling
        Error += 1
    except IndexError:
        #wrong shape
        Error += 1

#closing file and printing No.errors and code time
outfile.close()
end = time.time()
t = (end - start)/60                
print(str(t) + 'mins')
print(Error)