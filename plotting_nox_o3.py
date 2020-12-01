# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 13:06:11 2020

@author: nedho
"""
#reelvant imports
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#lists for plotting
o3_peak = []
o3_trough = []
o3_max = []
o3_min = []
nox_peak = []
nox_trough = []
nox_min = []
nox_max = []
ave_nox = []
dist1 = []
dist2 = []
nox_dif = []
summer_peaks = []
summer_o3 = []
summer_nox = []
spring_peaks = []
spring_o3 = []
spring_nox = []

#reding lines in file
file = open("nox_o3_cycles.txt", "r")
f1 = file.readlines()
for x in f1:
    #appending file columns to lists
    a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,blank = x.split(",")
    
    o3_peak.append(float(i))
    o3_trough.append(float(k))
    o3_max.append(float(j))
    o3_min.append(float(l))
    nox_trough.append(float(m))
    nox_peak.append(float(o))
    nox_min.append(float(n))
    nox_max.append(float(p))
    ave_nox.append(float(d))

# further quantities for plotting
for i in range(0,len(o3_peak)):
    dist1.append(abs(nox_trough[i]-o3_peak[i]))
    
for i in range(0,len(o3_peak)):
    dist2.append(abs(o3_peak[i]-o3_trough[i]))
    
for i in range(0,len(o3_peak)):
    nox_dif.append(abs(nox_max[i]-nox_min[i]))
    
#seasonal splitting of data   
for i in range(0,len(o3_peak)):
    if o3_peak[i] > 150:
        summer_peaks.append(o3_peak[i])
        summer_o3.append(o3_max[i])
        summer_nox.append(ave_nox[i])
    if o3_peak[i] < 150:
        spring_peaks.append(o3_peak[i])
        spring_o3.append(o3_max[i])
        spring_nox.append(ave_nox[i])
        


#plotting    
plt.figure(figsize = (16,10))    
plt.scatter(summer_nox,summer_o3,color = 'red')
plt.scatter(spring_nox,spring_o3,color = 'blue')
plt.title('Plot of mean NOx against peak ozone concentration',fontsize = 30,pad = 30)
plt.xlabel('Mean annual NOx/ppb',fontsize = 25)
plt.ylabel('peak ozone concentration/ppb',fontsize = 25)
plt.xticks(fontsize = 25)
plt.yticks(fontsize = 25)
blue_patch = mpatches.Patch(color='blue', label='Spring stations')
red_patch = mpatches.Patch(color='red', label='Summer stations')
plt.legend(handles=[blue_patch,red_patch],loc = 'upper right',fontsize = 20)
plt.show()

    