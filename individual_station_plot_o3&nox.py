# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 15:18:48 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.fftpack import dct, idct

#plotting parametres
SAMPLING = "daily"
N = 1
YEAR_START = 1970
NO_YEARS = 48
#base URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"

#necessary plotting arrays
t_days = np.linspace(1,365,365)
o3_ave = np.zeros(len(t_days))
nox_ave = np.zeros(len(t_days))
ave_array1 = np.ones(len(t_days))
ave_array2 = np.ones(len(t_days))

#series ids
SERIES_ID =24080
SERIES_ID_NOX = 44689

#looping over years
for i in range(0,NO_YEARS):
        
        #formatting date for URL
        DATE_START = str(YEAR_START+i) +"-01-01"
        DATE_END = str(YEAR_START+i) +"-12-31"
        print(i,DATE_START,DATE_END)
        DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d" 
    
        #URLs
        URL1 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
        URL1 = BASEURL + URL1
        URL2 = "stats/?id=" + str(SERIES_ID_NOX) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
        URL2 = BASEURL + URL2
        
        #getting years data from URL
        response1 = urlopen(URL1).read().decode('utf-8')
        metadata1 = json.loads(response1)
        response2 = urlopen(URL2).read().decode('utf-8')
        metadata2 = json.loads(response2)


        try:
            x_data1 = metadata1['datetime']
            y_data1 = metadata1['mean']
            
            #deleting nan values in year
            check_nan1= np.isnan(y_data1)            
            x_number1 = np.linspace(1,len(x_data1),len(x_data1))          
            delete1 = []
            for j in range(0,len(x_data1)):
                if check_nan1[j] == True:
                    delete1.append(j)
                       
            y_data1 = np.delete(y_data1,delete1)
            x_data1 = np.delete(x_data1,delete1)
            x_number1 = np.delete(x_number1,delete1)

            #summing daily values
            for j in range(0,len(x_number1)):
                for k in range(0,len(t_days)):
                    if x_number1[j] == t_days[k]:
                        o3_ave[k] += y_data1[j]
                        ave_array1[k] += 1 

            
        except KeyError:
            #no o3 data for this year
            pass 
        
        #same as above but for nox
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
            #no nox data for this year
            pass
               
#averaging for typical year        
o3_ave = o3_ave/ave_array1
nox_ave = nox_ave/ave_array2
delete1 = []
delete2 = []

#removing any remaining 0 values
for i in range(0,len(t_days)):
    if o3_ave[i] == 0:
        delete1.append(i)
    if nox_ave[i] == 0:
        delete2.append(i)
#defining elements fro plotting       
o3_ave = np.delete(o3_ave,delete1)
nox_ave = np.delete(nox_ave,delete2)
t_days = np.delete(t_days,delete1)
t = t_days
y_o3 = o3_ave
y_nox = nox_ave

#descrete cosine tranform
y1 = dct(y_o3, norm='ortho')
y2 = dct(y_nox, norm='ortho')
window = np.zeros(len(t))
window[:8] = 1
yr1 = idct(y1*window, norm='ortho')
yr2 = idct(y2*window, norm='ortho')

#plotting
plt.figure(figsize=(16,12))
plt.plot(t,y_o3,color="blue",linewidth = 4)
plt.plot(t, yr1,color="red",linewidth = 7)
plt.plot(t,y_nox,color="orange",linewidth = 4)
plt.plot(t, yr2,color="red",linewidth = 7)
plt.title('O3 and NOx cycles for Luneville surface staion, France ',fontsize = 35,pad = 20)
plt.xticks(fontsize = 25)
plt.yticks(fontsize = 25)
plt.xlabel('Day past start of year',fontsize = 30)
plt.ylabel('Ozone & Nox/ppb',fontsize = 30)
blue_patch = mpatches.Patch(color='blue', label='Ozone cycle')
orange_patch = mpatches.Patch(color='orange', label='NOx cycle')
red_patch = mpatches.Patch(color='red', label='Trendlines')
plt.legend(handles=[blue_patch,orange_patch,red_patch],loc = 'upper center',fontsize = 20)
plt.show()
