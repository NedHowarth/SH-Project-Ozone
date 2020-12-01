# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:37:05 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import numpy as np
from scipy.fftpack import dct, idct
import time

#measuring code time
start_time = time.time()
#sampling type
SAMPLING = "daily"
#rolling avarage if N=1 then no average is taken
N = 1
#daterange
YEAR_START = 1970
NO_YEARS = 47
#base URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"
#writing data to file
outfile = open('global_stations_seasonal_cycle.txt','w')
#counter for stations
n = 1

#reading in text file for series ids
file = open("global_stations_ids.txt", "r")
f1 = file.readlines()
#looping over stations
for x in f1:
    #seperating coloumns in text file
    a,b,c,d,e,f,blank = x.split(",")
    SERIES_ID = a
    print(str(n)+': '+str(SERIES_ID))
    n += 1
    
    #defining necessary quantities for plotting and averaging
    t_days = np.linspace(1,365,365)
    o3_ave = np.zeros(len(t_days))
    ave_array = np.ones(len(t_days))
    #length of data series in years counter
    data_years = 0
    #looping over dataseries for station
    for i in range(0,NO_YEARS):
        #formatting dates for URL
        DATE_START = str(YEAR_START+i) +"-01-01"
        DATE_END = str(YEAR_START+i) +"-12-31"
        DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d"
        #constructing URL
        URL2 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
        URL = BASEURL + URL2
        
        #retreiving data for 1 year
        response = urlopen(URL).read().decode('utf-8')
        metadata = json.loads(response)

        try:
            #making lists of ozone data
            x_data = metadata['datetime']
            y_data = metadata['mean']
            
            #removing non values in data series
            check_nan= np.isnan(y_data)
            #defining days of year in number of days as opposed to actual dates - easier for plotting
            x_number = np.linspace(1,len(x_data),len(x_data))
            delete = []
            for j in range(0,len(x_data)):
                if check_nan[j] == True:
                    delete.append(j)            
            y_data = np.delete(y_data,delete)
            x_data = np.delete(x_data,delete)
            x_number = np.delete(x_number,delete)
          
            #adding ozone concentrations for the year at each day there is data
            for j in range(0,len(x_number)):
                for k in range(0,len(t_days)):
                    if x_number[j] == t_days[k]:
                        o3_ave[k] += y_data[j]
                        #if there is data at that day the averging counter is increased by 1
                        ave_array[k] += 1
            data_years +=1
        except KeyError:
            #no data for this year
            pass
                 
    #mean daily ozone count for each day in data series              
    o3_ave = o3_ave/ave_array
    
    #removing any data that happens to remain at 0 - very unlikely
    #only necessary if no count was taken for the same day each year in the datta series
    delete = []
    for i in range(0,len(t_days)):
        if o3_ave[i] == 0:
            delete.append(i)
    o3_ave = np.delete(o3_ave,delete)
    t_days = np.delete(t_days,delete)
    
    #quantities for plotting
    t = t_days
    y_o3 = o3_ave
    
    #rolling average
    if N != 1:
        x_data = []
        y_data = []

        j = 0
        o3_smooth = 0
        smooth_stdv = 0
        for i in range(0,len(o3_ave)):
            if j < N: 
                o3_smooth += o3_ave[i]/N
                j += 1
            else:
                y_data.append(o3_smooth)
                x_data.append(t_days[i] - N/2)
                j = 1
                o3_smooth = o3_ave[i]/N
        
        #new averaged quantities for plotting
        t = x_data
        y_o3 = y_data
    
    #descrete cosine transform for data
    y = dct(y_o3, norm='ortho')
    window = np.zeros(len(t))
    #number of fourier coefficients
    window[:4] = 1
    yr = idct(y*window, norm='ortho')

    #quantities relating cycle peaks and troughs
    cycle_peak = t[np.argmax(yr)]
    cycle_trough = t[np.argmin(yr)]
    peak_ozone = np.amax(yr)
    trough_ozone = np.amin(yr)
    #writting all data to text file
    outfile.write(str(a)+','+str(b)+','+str(data_years)+','+str(c)+','+str(d)+','+str(e)+','+str(f)+','+str(cycle_peak)+','+str(peak_ozone)+','+str(cycle_trough)+','+str(trough_ozone)+",\n")

#closing file and printing code time
outfile.close()
end_time = time.time()
code_time = (end_time - start_time)/(60*60)
print("code time was: " + str(code_time) + "hours" )
