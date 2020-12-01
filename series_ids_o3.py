# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 13:25:57 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import numpy as np
import time
import urllib
#measurments of code time and number of errors
start = time.time()
Error = 0

#text file data is writen to
outfile = open('global_stations_ids.txt','w')

#URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"
URL1 ="search/?parameter_name=o3&columns=id,station_id,station_lon,station_lat,station_alt,station_type_of_area"
URL = BASEURL + URL1

#retrieving data from URL and appending data to lists
response = urlopen(URL).read().decode('utf-8')
metadata = json.loads(response)
series_ids = []
station_ids = []
station_lons,station_lats = [],[]
station_alts = []
station_area = []
for s in metadata:
    series_ids.append((s[0][0]))
    station_ids.append(s[1])
    station_lons.append(s[2])
    station_lats.append(s[3])
    station_alts.append(s[4])
    station_area.append(s[5])

#looping over series ids
#lists for exsisting station locations
existing_lons,existing_lats = [],[]

for i0 in range(0,len(series_ids)):
    
    #URL for data series
    URL2 = "stats/?id=" + str(series_ids[i0]) + "&sampling=daily"
    URL = BASEURL + URL2
    print(str(i0) + ":" + URL)
    
    #retrieving station data
    try:
        response = urlopen(URL).read().decode('utf-8')
        station_data = json.loads(response)
    except urllib.error.HTTPError:
        print('wrong formatting')
        Error += 1
    try:
        #keeping stations over minimum data series length in days
        if len(station_data['datetime']) > 3650:
            #counters for data population and more than one series id at a location
            j = 0
            double = 0
            #finding proportion of missing data
            check_nan = np.isnan(station_data['mean'])
            for i in range(0,len(station_data['mean'])):
                if check_nan[i] == True:
                    j += 1
            missing_data = j/len(station_data['mean'])
            #keeping stations with enough data
            if missing_data < 0.2:
                #checking for double data series
                for k in range(0,len(existing_lons)):
                    if station_lons[i0] == existing_lons[k] and station_lats[i0] == existing_lats[k]:
                        double += 1
                    else:
                        pass    
                if double == 0:
                    #writing out data to text file
                    existing_lons.append(station_lons[i0])
                    existing_lats.append(station_lats[i0])
                    outfile.write(str(series_ids[i0])+','+str(station_ids[i0])+','+str(station_lons[i0])+','+str(station_lats[i0])+','+str(station_alts[i0])+','+str(station_area[i0])+ ",\n")
    #errors
    except TypeError:
        print("data embargo?")
        Error += 1
    except KeyError:
        print('no data in series')
        Error += 1  
    except NameError:
        print('wrong labeling')
        Error += 1

#closing file and printing code time and errors         
outfile.close()
end = time.time()
t = (end - start)/60                
print(str(t) + 'mins')      
print('errors:' +str(Error))