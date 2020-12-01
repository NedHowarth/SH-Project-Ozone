# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:31:21 2020

@author: nedho
"""
#relevant imports
from urllib.request import urlopen
import json
import numpy as np
from scipy.fft import dct, idct
import time
from scipy import stats,optimize
#code time and parameters for fitting
start_time = time.time()
SAMPLING = "daily"
N = 1
YEAR_START = 1970
NO_YEARS = 48
#base URL
BASEURL = "https://join.fz-juelich.de/services/rest/surfacedata/"

#opening file
file = open("global_stations_ids.txt", "r")
f1 = file.readlines()
#writing out to file
outfile = open('global_stations_peak_change.txt','w')
n = 1

#looping over lines in file
for x in f1:
    a,b,c,d,e,f,blank = x.split(",")
    SERIES_ID = a
    print(str(n)+': '+str(SERIES_ID))
    n += 1
    #fitting quantities
    data_years = []
    peaks = []
    no_data_years = 0

    #looping over years for station
    for i in range(0,NO_YEARS):
            #formatting dates       
            DATE_START = str(YEAR_START+i) +"-01-01"
            DATE_END = str(YEAR_START+i) +"-12-31"
            DATERANGE = "%5b" + DATE_START + "%2000:00," + DATE_END +"%2023:00%5d" 
            #URL
            URL2 = "stats/?id=" + str(SERIES_ID) + "&sampling=" + SAMPLING + "&daterange=" + DATERANGE
            URL = BASEURL + URL2
            #opening URL getting yearly data
            response = urlopen(URL).read().decode('utf-8')
            metadata = json.loads(response)
         
            try:
                x_data = metadata['datetime']
                y_data = metadata['mean']
                #only years with enough data
                if len(y_data) > 250:
                    #years for fitting
                    data_years.append(YEAR_START+i)
                    #removing nan values in year
                    check_nan= np.isnan(y_data)
                    x_number = np.linspace(1,len(x_data),len(x_data))
                    delete = []
                    for j in range(0,len(x_data)):
                        if check_nan[j] == True:
                            delete.append(j)
                    x_data = np.delete(x_data,delete)
                    x_number = np.delete(x_number,delete)
                    y_data = np.delete(y_data,delete)
                    
                    #fitting quantities
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
                        #rolling average fitting quantities
                        t = x
                        y_o3 = y
                    
                    try:
                        #descrete cosine fit for year
                        y = dct(y_o3, norm='ortho')
                        window = np.zeros(len(t))
                        window[:5] = 1
                        yr = idct(y*window, norm='ortho')
                        #peaks for peak change fit
                        if t[np.argmax(yr)] != t[len(t)-1] and t[np.argmax(yr)] != t[0]:
                            peaks.append(t[np.argmax(yr)])
                            no_data_years += 1
                    except ValueError:
                        #not enough data for this year
                         pass
            except KeyError:
                #no data for this year
                pass
    #years for plotting
    data_years = np.array(data_years)                 
    year = np.linspace (data_years[0],data_years[no_data_years-1],no_data_years)
    
    #only stations with at least 7 peaks
    if len(peaks) > 7:
        
        #fitting linear trend
        def test_func(x, m, c):
            return (m * x)+c
        
        params, params_covariance = optimize.curve_fit(test_func,year,peaks)
        
        mean = np.mean(peaks)
        stdv = np.std(peaks)
        #writing relevand data to text file
        outfile.write(str(a)+','+str(b)+','+str(no_data_years)+','+str(c)+','+str(d)+','+str(e)+','+str(f)+','+str(stats.pearsonr(year, peaks)[0])+','+str(params[0])+','+str(params_covariance[0][0]**(1/2))+','+str(mean)+','+str(stdv)+",\n")
#closing text file and code run time
outfile.close()
end_time = time.time()
code_time = (end_time - start_time)/60
print("code time was: " + str(code_time) + "mins" )
