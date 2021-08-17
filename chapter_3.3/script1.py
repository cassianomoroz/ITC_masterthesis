#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to estimate rainfall at the location of the rain gauges from Group 2 through the inverse distance weighting (IDW) interpolation of
#the measurements of the rain gauges from Group 1.

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime
from osgeo import gdal, gdal_array
from PIL import Image

#Set the directory where the input files are located.
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData")

#Open the daily measurements from rain gauges from Group 1.
gauge_daily=np.load("prec_gauge_daily_all.npy",allow_pickle=True).item()

#Open the adopted codes from rain gauges from Groups 1 and 2.
codes_g1=np.load("codes_group1.npy",allow_pickle=True).tolist() #list with codes from Group 1 gauges.
codes_g1=[row[1] for row in codes_g1]
codes_g2=np.load("codes_group2.npy",allow_pickle=True).tolist() #list with codes from Group 2 gauges.

#Import the coordinates (X and Y) of the rain rauges from Groups 1 and 2.
coord=[] #Create a list to store the coordinates.
with open('GaugeCoordinates.csv', newline='') as f: #Open the coordinates file, exported from ArcGIS.
    reader = csv.reader(f)
    coord_extend = list(reader)   
    coord.extend(coord_extend)
coord[0][0]=coord[0][0][3:] #Delete the unwanted rows and columns.

#Use KDE interpolator to calculate daily rainfall in the location of the rain gauges from Group 1.
#Add the X and Y coordinates do the lists with the gauge codes.
for i in range(len(codes_g1)): #Iterate over the list with codes from Group 1 gauges.
    for j in range(len(coord)): #Iterate over the list of coordinates.
        if codes_g1[i]==coord[j][0]: #If codes match.
            codes_g1[i]=coord[j] #Add coordinates.
for i in range(len(codes_g2)): #Iterate over the list with codes from Group 1 gauges.
    for j in range(len(coord)): #Iterate over the list of coordinates.
        if codes_g2[i]==coord[j][0]: #If codes match.
            codes_g2[i]=coord[j] #Add coordinates.

#Create a dictionary to store daily values at the target locations.
prec_gaugeIDW_daily={}
for i in range(len(codes_g2)): #Iterate over gauges from Group 2.
    rainfall_list=[] #Create a list to store the rainfall values.
    date=[row[0] for row in gauge_daily['Rainfall_02649002']] #Extract dates.
    for j in range(len(gauge_daily['Rainfall_02649002'])): #Iterate over dates.
        vidi=0 #Reset vidi (rainfall at gauge 1/distance between gauges).
        onedi=0 #Reset onedi (1/distance between gauges).
        for k in range(len(codes_g1)): #Iterate over gauges from group 1.
            source_rainfall=gauge_daily[codes_g1[k][0]] #Get the rainfall value.
            di=((((codes_g2[i][1]-codes_g1[k][1])**2)+((codes_g2[i][2]-codes_g1[k][2])**2))**0.5) #Calculate distance between gauges from Group 1 and 2.
            vidi=vidi+(source_rainfall[j][1]/di) #Update vidi (rainfall/distance).
            onedi=onedi+(1/di) #Update onedi (1/distance).
        v0=vidi/onedi #Calculate the estimated rainfall from the IDW interpolation (vidi/onedi).
        rainfall_list.append([date[j],v0]) #Append the estimted rainfall to the list, for a corresponding date.
    prec_gaugeIDW_daily[codes_g2[i][0]]=rainfall_list #Add the complete list (all time series) of the corresponding gauge from Group 2 to the dictionary.

#Aggregate the daily estimates into 3-daily and monthly estimates.
prec_gaugeIDW_3daily={} #Create a dictionary for 3-daily estimates.
for i in prec_gaugeIDW_daily.keys(): #Iterate over rain gauges from Group 2.
        prec_daily=prec_gaugeIDW_daily[i] #Get time series.
        prec_3daily=[] #Create list to store 3-daily values.
        k=1 #Create count.
        for j in range(len(prec_daily)): #Iterate over time series.
            if k==1:
                prec_append=[prec_daily[j][0]] #Add the date to the prec_append list.
                prec=prec_daily[j][1] #Add the rainfall to prec.
                k=k+1 #Sum 1 to count.
            elif k==2:
                prec=prec+prec_daily[j][1] #Add the rainfall to prec.
                k=k+1 #Sum 1 to count.
            else: #If count is higher than 2.
                prec=prec+prec_daily[j][1] #Add the rainfall to prec.
                prec_append.append(prec) #Append the cumulative 3-daily rainfall to prec_append.
                prec_3daily.append(prec_append) #Append prec_append to prec_3daily.
                k=1 #Reset count to 1.
        prec_gaugeIDW_3daily[i]=prec_3daily #Add the time series prec_3daily of the specific rain gauge to the dictionary.

prec_gaugeIDW_monthly={} #Create a dictionary for monthly values.
for i in prec_gaugeIDW_daily.keys(): #Iterate over rain gauges from Group 2.
        prec_daily=prec_gaugeIDW_daily[i] #Get time series.
        prec_monthly=[] #Create list to store monthly values.
        for j in range(len(prec_daily)): #Iterate over time series.
            if j==0: #For the first date.
                prec=prec_daily[j][1] #Start count of precipitation (prec).
            elif prec_daily[j][0].month==prec_daily[j-1][0].month and j!=len(prec_daily)-1: #If the month of the date is equal from the month of the previous date.
                prec=prec+prec_daily[j][1] #Add the rainfall to prec.
            elif j==len(prec_daily)-1: #If the date is the last date in the time series.
                date=datetime.date(int(prec_daily[j][0].year),int(prec_daily[j][0].month),1) #Extract date.
                prec_append=[date,prec] #Create prec_append with date and cumulative rainfall.
                prec_monthly.append(prec_append) #Append prec_append to prec_monthly.
            else: #Else, or if the month of the date is different from the month of the previous date.
                date=datetime.date(int(prec_daily[j-1][0].year),int(prec_daily[j-1][0].month),1)
                prec_append=[date,prec] #Create prec_append with date and cumulative rainfall.
                prec_monthly.append(prec_append) #Append prec_append to prec_monthly.
                prec=prec_daily[j][1] #Reset prec with the measurement from the date.
        prec_gaugeIDW_monthly[i]=prec_monthly #Add the time series prec_monthly of the specific rain gauge to the dictionary.

#Save the daily, 3-daily, and monthly rainfall as .npy files.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\OutputData")
np.save('prec_gaugeIDW_daily.npy', prec_gaugeIDW_daily)
np.save('prec_gaugeIDW_3daily.npy', prec_gaugeIDW_3daily)
np.save('prec_gaugeIDW_monthly.npy', prec_gaugeIDW_monthly)
