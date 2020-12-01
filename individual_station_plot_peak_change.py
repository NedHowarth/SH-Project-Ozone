# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 18:17:44 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import dct, idct
from scipy import stats,optimize

#plottin parametrers
SAMPLING = "daily"
N = 1
YEAR_START = 1970
NO_YEARS = 48
#base URL and series id
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"
SERIES_ID = 21887

#for ploting
data_years = []
peaks = []
no_data_years = 0

#looping over yearis in data series
for i in range(0,NO_YEARS):
        #formating year date for URL
        DATE_START = str(YEAR_START+i) +"-01-01"
        DATE_END = str(YEAR_START+i) +"-12-31"
        DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d" 
        #URL
        URL2 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE
        URL = BASEURL + URL2

        #retreivin yearly data
        response = urlopen(URL).read().decode('utf-8')
        metadata = json.loads(response)
     
        try:
            #day date and mean
            x_data = metadata['datetime']
            y_data = metadata['mean']

            #only years with lots of daily dates
            if len(y_data) > 250:
                #year for plotting
                data_years.append(YEAR_START+i)
                #deleting nan values
                check_nan= np.isnan(y_data)
                x_number = np.linspace(1,len(x_data),len(x_data))
                delete = []
                for j in range(0,len(x_data)):
                    if check_nan[j] == True:
                        delete.append(j)
                x_data = np.delete(x_data,delete)
                x_number = np.delete(x_number,delete)
                y_data = np.delete(y_data,delete)
                
                #for fitting
                t = x_number
                y_o3 = y_data
                
                #rolling average
                if N != 1:
                    x = []
                    y = []
        
                    j = 0
                    o3_smooth = 0
                    smooth_stdv = 0
                    for i in range(0,len(y_data)):
                        if j < N: 
                            o3_smooth += y_data[i]/N
                            j += 1
                        else:
                            y.append(o3_smooth)
                            x.append(t[i] - N/2)
                            j = 1
                            o3_smooth = y_data[i]/N
                    #fitting for rolling average
                    t = x
                    y_o3 = y
                
                try:
                    #descrete cosine transform
                    y = dct(y_o3, norm='ortho')
                    window = np.zeros(len(t))
                    window[:5] = 1
                    yr = idct(y*window, norm='ortho')
                    
                    #peak day for plotting
                    if t[np.argmax(yr)] != t[len(t)-1] and t[np.argmax(yr)] != t[0]:
                        peaks.append(t[np.argmax(yr)])
                        no_data_years +=1
                    
                    #for plotting individual years
                    """
                    ax1 = plt.subplot()
                    ax1.plot(t,y_o3,color="blue")
                    ax1.plot(t, yr,color="red")
                    plt.show()
                    """
                except ValueError:
                    #not enough data for this year
                     pass
        except KeyError:
            #no data for this year
            pass

#years for plotting
data_years = np.array(data_years)              
year = np.linspace (data_years[0],data_years[no_data_years-1],no_data_years)

#only plots with more than 7 peaks are considered
if len(peaks) > 7:
    #correlation
    print(stats.pearsonr(year, peaks)[0])
    
    #fitting linear trendline
    def test_func(x, m, c):
        return (m * x)+c
    
    params, params_covariance = optimize.curve_fit(test_func,year,peaks)
    
    #grad
    print('grad is :'+str(params[0]))
    #error on grad
    print(params_covariance[0][0])
    print(params_covariance[0][0]**(1/2))
    
    #plotting
    plt.figure(figsize=(16,12))
    plt.scatter(year,peaks,s=150)
    plt.plot(year, test_func(year, params[0], params[1]),color = 'red',linewidth = 4)
    label = []
    print(len(year)/2)
    for i in range (0,int((len(year)/2))):
        label.append(year[i*2])
    print(label)
    plt.xticks(label,fontsize=25)
    plt.yticks(fontsize=25)
    plt.title('Yearly Ozone Peaks, Mace Head Surface Station, Ireland',fontsize=35,pad = 15)
    plt.ylabel('Days past start of the year',fontsize=30)
    plt.xlabel('Year',fontsize=30)
    plt.show()
    
    