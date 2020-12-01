# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 13:40:32 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import numpy as np
from scipy.fftpack import dct, idct
import time

#code time and establishing parameters for fitting
start_time = time.time()
SAMPLING = "daily"
YEAR_START = 1970
NO_YEARS = 48
#base URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"
n = 1

#opening file to write data to
outfile = open('nox_o3_cycles.txt','w')

#reading in nox file and looping over stations
file = open("nox_o3_ids.txt", "r")
f1 = file.readlines()
for x in f1:
    a,b,c,d,e,f,g,h,blank = x.split(",")
    
    #series ids for nox and o3
    SERIES_ID = a
    SERIES_ID_NOX = b
    print(str(n)+': '+str(SERIES_ID))
    n += 1
    
    #necessary plotting arrays
    t_days = np.linspace(1,365,365)
    o3_ave = np.zeros(len(t_days))
    nox_ave = np.zeros(len(t_days))
    ave_array1 = np.ones(len(t_days))
    ave_array2 = np.ones(len(t_days))
    
    #looping over years for station
    for i in range(0,NO_YEARS):
        
             #formating daterange for URL
            DATE_START = str(YEAR_START+i) +"-01-01"
            DATE_END = str(YEAR_START+i) +"-12-31"
            DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d"
        
            #URLs
            URL1 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
            URL1 = BASEURL + URL1
            URL2 = "stats/?id=" + str(SERIES_ID_NOX) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
            URL2 = BASEURL + URL2

            #retreiving annual data
            response1 = urlopen(URL1).read().decode('utf-8')
            metadata1 = json.loads(response1)
            response2 = urlopen(URL2).read().decode('utf-8')
            metadata2 = json.loads(response2)
    
            #for o3
            try:
                #list of yearly o3 data
                x_data1 = metadata1['datetime']
                y_data1 = metadata1['mean']
                #removing nan values
                
                check_nan1= np.isnan(y_data1)     
                x_number1 = np.linspace(1,len(x_data1),len(x_data1))                
                delete1 = []
                for j in range(0,len(x_data1)):
                    if check_nan1[j] == True:
                        delete1.append(j) 
                y_data1 = np.delete(y_data1,delete1)
                x_data1 = np.delete(x_data1,delete1)
                x_number1 = np.delete(x_number1,delete1)
                
                #summing yearly values
                for j in range(0,len(x_number1)):
                    for k in range(0,len(t_days)):
                        if x_number1[j] == t_days[k]:
                            o3_ave[k] += y_data1[j]
                            ave_array1[k] += 1

            except KeyError:
                #no o3 data this year
                pass
            #same as o3 but for nox
            try:   
                x_data2 = metadata2['datetime']
                y_data2 = metadata2['mean']
                check_nan2= np.isnan(y_data2)
                x_number2 = np.linspace(1,len(x_data2),len(x_data2))
                delete2 = []
                for j in range(0,len(x_data2)):
                    if check_nan2[j] == True:
                        delete2.append(j)
                y_data2 = np.delete(y_data2,delete2)
                x_data2 = np.delete(x_data2,delete2)
                x_number2 = np.delete(x_number2,delete2)
                for j in range(0,len(x_number2)):
                    for k in range(0,len(t_days)):
                        if x_number2[j] == t_days[k]:
                            nox_ave[k] += y_data2[j]
                            ave_array2[k] += 1 
            except KeyError:
                #no nox data this year
                pass
    #mean daily values      
    o3_ave = o3_ave/ave_array1
    nox_ave = nox_ave/ave_array2
    
    #removing any remaining 0 values
    delete1 = []
    delete2 = []

    for i in range(0,len(t_days)):
        if o3_ave[i] == 0:
            delete1.append(i)
        if nox_ave[i] == 0:
            delete2.append(i)

    o3_ave = np.delete(o3_ave,delete1)
    nox_ave = np.delete(nox_ave,delete2)
    t_days1 = np.delete(t_days,delete1)
    t_days2 = np.delete(t_days,delete2)
    
    #plotting quantities
    t1 = t_days1
    t2 = t_days2
    y_o3 = o3_ave
    y_nox = nox_ave
    
    #cosine transform
    y1 = dct(y_o3, norm='ortho')
    y2 = dct(y_nox, norm='ortho')
    window = np.zeros(len(t1))
    window2 = np.zeros(len(t2))
    window[:8] = 1
    window2[:8] = 1
    yr1 = idct(y1*window, norm='ortho')
    yr2 = idct(y2*window2, norm='ortho')
   
    #writing to data file
    outfile.write(str(a)+','+str(b)+','+str(c)+','+str(d)+','+str(e)+','+str(f)+','+str(g)+','+str(h)+','+str(t1[np.argmax(yr1)])+','+str(np.amax(yr1))+','+str(t1[np.argmin(yr1)])+','+str(np.amin(yr1))+','+str(t2[np.argmin(yr2)])+','+str(np.amin(yr2))+','+str(t2[np.argmax(yr2)])+','+str(np.amax(yr2))+',\n')

#closing file printing code time
outfile.close()
end_time = time.time()
code_time = (end_time - start_time)/60
print("code time was: " + str(code_time) + "mins" )