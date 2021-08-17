#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to generate daily, 3-daily and monthly time series from the downloaded IMERG and GSMaP products.
#This script exemplifies the process of creating a time series for GSMaP estimates.
#This process refers to a time series at the location of a single rain gauge. To add more gauges to the analysis, it is necessary to add
#their coordinates in chapter_3.4/script1.

import csv
import re
import datetime
import numpy as np
import os

#Select the directory where the .csv time series are located (downloaded from Google Earth Engine via Google Drive).
os.chdir(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\SatelliteRainfall\GSMaP_V5_6\2000_2020') #Path.
GSMaP=[] #Create list to store the unprocessed time series.
with open('GSMaP.csv', newline='') as f: #Open GSMaP file.
        reader = csv.reader(f)
        GSMaP_extend = list(reader)
        GSMaP_extend = GSMaP_extend[1:] #For each row, select only the relevant columns (column 0 was eliminated).  
        GSMaP.extend(GSMaP_extend) #Extend the meurement to the GSMaP list.

prec_GSMaP={} #Create dicionary to store the processes results.
prec_new=[] #Create list to store the new time series.
for i in range(len(GSMaP)): #Iterate over the unprocessed time series.
    date=re.split("T|:|-",GSMaP[i][1]) #Split the date to fit the date format in datetime.
    prec=float(GSMaP[i][2]) #Extract and convert the rainfall measurement to float.
    append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),  #Create the new date based on the datetime format. Add it to append_list.
         (int(date[3])+(int(date[4])/60)),prec] #Also add the exact hour and the rainfall measurement to the append_list.
    prec_new.append(append_list) #Append append_list to prec.
   
#To be sure that the dates are in chronological order, order the entire list according to the row referring to the date.
prec_new.sort(key = lambda x: x[0])

#Aggregate the rainfall into daily, 3-daily and monthly measurements.
#Starting with daily, the date/hour in GSMaP are defined at UTC.
#The gauge stations are in (UTC-3). The measuring time of the daily measurement at the gauges is at 7 am .
#Therefore, fixing for both UTC and measuring time, the GSMaP day goes from 10 am until 10 am of the following day.
prec_GSMaP_daily={} #Create dictionary to store the GSMaP measurements.
for i in prec_GSMaP.keys(): #Iterate over gauge stations (if more are added).
    station_list=prec_GSMaP[i] #Get time series.
    date_list=[row[0] for row in station_list] #Get date.
    prec_list=[row[2] for row in station_list] #Get rainfall esimate.
    prec_daily=[] #Create list to store daily measurements.
    for j in range(len(date_list)-10): #Iterate over time series.
        if j==0: #For the first date/time.
            prec=prec_list[j+10] #Get the rainfall estimate 10 hours after midnight.
        elif date_list[j]==date_list[j-1]: #If the date is the same as the date of the previous measurement.
            prec=prec+prec_list[j+10] #Sum the rainfall estimate (10 hours later) to prec.
        elif j==(len(date_list)-10): #If the date is the last in the time series.
            prec_append=[date_list[j],prec] #Create prec_append with the date and the cumulative daily rainfall (prec).
            prec_daily.append(prec_append) #Append prec_append to prec_daily.
            prec=0 #Reset prec to 0.
        else: #Else, or if the date is different from the date of the previous measurement.
            prec_append=[date_list[j-1],prec,dateuse] #Create prec_append with the date of the previous measurement and the cumulative daily rainfall (prec).
            prec_daily.append(prec_append) #Append prec_append to prec_daily.
            prec=0 #Reset prec to 0.
    prec_GSMaP_daily[i]=prec_daily #Add the list prec_daily, corresponding to a specific rain gauge, to the dictionary.

#Aggregate the daily measurements into 3-daily.
prec_GSMaP_3daily={} #Create a dictionary to store 3-daily values.
for i in prec_GSMaP_daily.keys(): #Iterate over rain gauges (if more than 1 is adopted).
    station_list=prec_GSMaP_daily[i] #Get time series.
    date_list=[row[0] for row in station_list] #Get date.
    prec_list=[row[1] for row in station_list] #Get daily rainfall estimates.
    prec_3daily=[] #Create a list to store 3-daily totals.
    k=1 #Create count.
    for j in range(len(date_list)): #Iterate over time series.
        if k==1:
            prec_append=[date_list[j]] #Add the date to the prec_append list.
            prec=prec_list[j] #Start calculating prec with the first rainfall estimate.
            k=k+1 #Add 1 to the count.
        elif k==2:
            prec=prec+prec_list[j] #Add the rainfall estimate to prec.
            k=k+1 #Add 1 to the count.
        else: #If k if higher than 2.
            prec=prec+prec_list[j] #Add the rainfall estimate to prec.
            prec_append.append(prec) #Append the 3-daily total (prec) to prec_append.
            prec_3daily.append(prec_append) #Append prec_append to prec_3daily.
            k=1 #Reset k to 1.
    prec_GSMaP_3daily[i]=prec_3daily #Add the list prec_3daily, corresponding to a specific rain gauge, to the dicionary.

#Aggregate the daily measurements into monthly.
prec_GSMaP_monthly={} #Create a dictionary to store monthly values.
for i in prec_GSMaP_daily.keys(): #Iterate over rain gauges (if more than 1 is adopted).
    station_list=prec_GSMaP_daily[i] #Get time series.
    date_list=[row[0] for row in station_list] #Get dates.
    prec_list=[row[1] for row in station_list] #Get daily rainfall estimates.
    prec_monthly=[] #Create a list to store monthly totals.
    for j in range(len(date_list)): #Iterate over the time series.
        if j==0: #For the first date of the time series.
            prec=prec_list[j] #Start calculating prec with the first rainfall estimate.
        elif j==len(date_list)-1: #For the last date of the time series.
            prec=prec+prec_list[j] #Add the rainfall estimate to prec.
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1) #Create the date (consider day 1 of the month).
            prec_append=[date,prec] #Add date and monthly rainfall to prec_append.
            prec_monthly.append(prec_append) #Append prec_append to prec_monthly.
            prec=0 #Reset prec to 0.
        elif date_list[j].month==date_list[j-1].month and j!=len(date_list)-1: #If the month of the measurement is equal to the month of the previous measurement.
            prec=prec+prec_list[j] #Add the rainfall estimate to prec.
        else: #Else, or if the month of the measurement is different from the month of the previous measurement.
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1) #Create the date (consider day 1 of the month).
            prec_append=[date,prec] #Add date and monthly rainfall to prec_append.
            prec_monthly.append(prec_append) #Append prec_append to prec_monthly.
            prec=0 #Reset prec to 0.
    prec_GSMaP_monthly[i]=prec_monthly #Add the list prec_monthly, corresponding to a specific rain gauges, to the dictionary.

#Save the generated daily, 3-daily, and monthly totals.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
np.save('prec_GSMaP_daily.npy', prec_GSMaP_daily)
np.save('prec_GSMaP_3daily.npy', prec_GSMaP_3daily)
np.save('prec_GSMaP_monthly.npy', prec_GSMaP_monthly)
