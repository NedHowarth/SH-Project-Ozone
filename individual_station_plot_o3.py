# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 15:25:47 2020

@author: nedho
"""
#relevant improts
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import dct, idct

#plotting parameters
SAMPLING = "daily"
N = 1
YEAR_START = 1970
NO_YEARS = 47
#base URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"

#nescesary plotting arrays
t_days = np.linspace(1,365,365)
o3_ave = np.zeros(len(t_days))
ave_array = np.ones(len(t_days))
o3_stdv = np.zeros(len(t_days))

SERIES_ID = 21887

#looping over years in data series
for i in range(0,NO_YEARS):
        
        #individual year
        DATE_START = str(YEAR_START+i) +"-01-01"
        DATE_END = str(YEAR_START+i) +"-12-31"
        print(i,DATE_START,DATE_END)
        
        #formating daterange for URL
        DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d"
        #URL
        URL2 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE 
        URL = BASEURL + URL2
        
        #getting yearly data
        response = urlopen(URL).read().decode('utf-8')
        metadata = json.loads(response)

        try:
            #if year has data then put data in relevant lists
            x_data = metadata['datetime']            
            y_data = metadata['mean']            
            stdv_y = metadata['stddev']
    
            #removing nan values
            check_nan= np.isnan(y_data)
            check_nan2 = np.isnan(stdv_y)
            x_number = np.linspace(1,len(x_data),len(x_data))
            delete = []
            for j in range(0,len(x_data)):
                if check_nan[j] == True:
                    delete.append(j)
            
            y_data = np.delete(y_data,delete)
            x_data = np.delete(x_data,delete)
            x_number = np.delete(x_number,delete)
            stdv_y = np.delete(stdv_y,delete)

            #summing data over days
            for j in range(0,len(x_number)):
                for k in range(0,len(t_days)):
                    if x_number[j] == t_days[k]:                        
                        o3_ave[k] += y_data[j]
                        ave_array[k] += 1                        
                        o3_stdv[k] += (((stdv_y[j]/y_data[j])**2))**(1/2)




        except KeyError:
            #no data for this year
            pass              

#daily average             
o3_ave = o3_ave/ave_array
#dleeting any daily value that remain at 0
delete = []
for i in range(0,len(t_days)):
    if o3_ave[i] == 0:
        delete.append(i)
o3_ave = np.delete(o3_ave,delete)
t_days = np.delete(t_days,delete)

#defining ploting quantities
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
    #new quantities for plotting
    t = x_data
    y_o3 = y_data

#descrete cosine transform
y = dct(y_o3, norm='ortho')
window1 = np.zeros(len(t))
window1[:8] = 1
yr = idct(y*window1, norm='ortho')

#plotting typical cycle
plt.figure(figsize=(16,12))
plt.plot(t,y_o3,color="blue",linewidth = 4)
plt.plot(t, yr,color="red",linewidth = 7)
plt.title('Typical seasonal cycle for Mac Head surface staion, Ireland ',fontsize = 35,pad = 20)
plt.xticks(fontsize = 25)
plt.yticks(fontsize = 25)
plt.xlabel('Day past start of year',fontsize = 30)
plt.ylabel('Ozone/ppb',fontsize = 30)
plt.show()

#plotting residuals
plt.figure(figsize=(20,8))
plt.scatter(t,(y_o3-yr))
plt.errorbar(t,(y_o3-yr),yerr=o3_stdv,color = 'black',alpha = 0.6)
plt.axhline(y=0, color='k')
plt.xticks(fontsize = 25)
plt.yticks(fontsize = 25)
plt.xlabel('Day past start of year',fontsize = 30)
plt.ylabel('Residuals',fontsize = 30)
plt.show()

#% of residuals crossing origin
res=0
for i in range(0,len(y_o3)):
    if y_o3[i]-yr[i] > 0:
        if y_o3[i]-yr[i] - o3_stdv[i] < 0 :
            res+=1
    if y_o3[i]-yr[i] < 0:
        if y_o3[i]-yr[i] + o3_stdv[i] > 0 :
            res+=1
print(res/len(y_o3))

        