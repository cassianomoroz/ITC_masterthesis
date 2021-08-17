#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to merge satellite and gauge rainfall estimates through mean bias correction (MBC) and residual inverse distance weighting (RIDW).

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime
from osgeo import gdal, gdal_array
from PIL import Image

#Set directory where the input files are located.
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")

#Open the rainfall files for all products (GSMaP, IMERG and gauge) and time scales (daily, 3-daily, monthly).
GSMaP_monthly=np.load("prec_GSMaP_monthly.npy",allow_pickle=True).item()
GSMaP_3daily=np.load("prec_GSMaP_3daily.npy",allow_pickle=True).item()
GSMaP_daily=np.load("prec_GSMaP_daily.npy",allow_pickle=True).item()
IMERG_monthly=np.load("prec_IMERG_monthly.npy",allow_pickle=True).item()
IMERG_3daily=np.load("prec_IMERG_3daily.npy",allow_pickle=True).item()
IMERG_daily=np.load("prec_IMERG_daily.npy",allow_pickle=True).item()
gauge_daily=np.load("prec_gauge_daily_all.npy",allow_pickle=True).item()
gauge_3daily=np.load("prec_gauge_3daily_all.npy",allow_pickle=True).item()
gauge_monthly=np.load("prec_gauge_monthly_all.npy",allow_pickle=True).item()

#Import the target locations (pixel centers) for IMERG and GSMaP.
targetloc=[] #Create a list to store the locations.
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SGMerged\Input\Targetloc.csv', newline='') as f: #Open the file.
    reader = csv.reader(f)
    loc_extend = list(reader)   
    targetloc.extend(loc_extend)
targetloc[0][0]=targetloc[0][0][3:] #Eliminate the rows and columns that are not relevant.

#Import the coordinates from the pixels where the rain gauges are located.
gauge_coord=[] #Create a list to store the locations.
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\GaugeCoordinates.csv', newline='') as f: #Open the file.
    reader = csv.reader(f)
    coord_extend = list(reader)   
    gauge_coord.extend(coord_extend)
gauge_coord[0][0]=gauge_coord[0][0][3:] #Eliminate the rows and columns that are not relevant.

#Import the adopted codes from the rain gauges from Group 1.
codes1=np.load("codes_adp.npy",allow_pickle=True).tolist() #Create a list.
codes1=[row[1] for row in codes1]
#Import the adopted codes from the rain gauges from Group 2.
codes2=np.load(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\codes_group2.npy",allow_pickle=True).tolist() #Create a list.

#Add the X and Y coordinates of the gauges to the codes list:
for i in range(len(codes1)): #Iterate over gauges.
    for j in range(len(gauge_coord)): #Iterave over coordinates.
        if codes1[i]==gauge_coord[j][0]: #If codes match.
            codes1[i]=gauge_coord[j] #Add X and Y coordinates.
            
#Create a function to perform both MBC and RIDW merging techniques.
def merge(sat_daily,sat_interval,gauge_daily,gauge_interval,targetloc,codes1,codes2,datelabel,satlabel):

    #Extract the codes of the stations from Group 1 to be adopted to calibrate satellite products.
    codes_adp=[row[0] for row in codes1]

    #Calculate the multiplicative and differential correction factors and save the values.
    cor_factor_MBC=[] #Create a list to store MBC correction factors
    cor_factor_RIDW=[] #Create a list to store RIDW correction factors
    sat=sat_interval['Rainfall_02649002'] #For first interaction
    for i in range(len(sat)): #Iterate over time series.
        cor_RIDW_append=[sat[i][0]] #Add date to cor_RIDW_append.
        mean_sat=0 #Mean satellite measurement.
        mean_gauge=0 #Mean gauge measurement.
        for j in sat_interval.keys(): #Iterate over gauge stations.
            if j in codes_adp: #Only consider the station if it is included in Group 1.
                sat=sat_interval[j] #Get satellite time series.
                gauge=gauge_interval[j] #Get gauge time series.
                mean_sat=mean_sat+sat[i][1] #Add satellite estimate to mean_sat (for MBC).
                mean_gauge=mean_gauge+gauge[i][1] #Add gauge estimate to mean_gauge (for MBC).
                dif=gauge[i][1]-sat[i][1] #Calculate the difference between satellite and gauge estimates (for RIDW).
                cor_RIDW_append.append(dif) #Append the difference to the cor_RIDW_append list.
        cor_factor_RIDW.append(cor_RIDW_append) #Append cor_RIDW_append to cor_factor_RIDW.
        if mean_sat<1:
            cor=1 #Adopt correction factor as 1 (no correction) when satellite measurements are much lower than 1. This avoids the estimation of unrealistic multiplicative
                  #bias correction factors.
        else: #In any other case.
            cor=mean_gauge/mean_sat #Calculate correction factor for MBC.
        cor_append_MBC=[sat[i][0],cor] #Add date and correction factor to cor_append_MBC.
        cor_factor_MBC.append(cor_append_MBC) #Append cor_append_MBC to cor_factor_MBC.

    #Interpolate the RIDW correction factors to the target locations (pixel centers from Group 2 gauges).
    #Create a dictionary to store the interpolated differences
    diff={}
    for i in range(len(targetloc)): #Iterate over the list targetloc, containing the location of the pixel centers.
        if targetloc[i][0] in codes2: #Only consider the target locations that contains the gauge stations from Group 2. Eliminate the ones from Group 1.
            rainfall_list=[] #Create a list to store the interpolated correction factors.
            for j in cor_factor_RIDW: #Iterate over the time series of correction factors.
                vidi=0 #Reset vidi.
                onedi=0 #Reset onedi.
                for k in range(len(j)-1): #Iterate over the list of  corrections factors for each date. The list refers to all correction factors associated with the gauges
                    #from Group 1.
                    source_rainfall=j[k+1] #Extract differential correction factor at the location of the gauge from Group 1.
                    di=((((int(targetloc[i][1])-int(codes1[k][1]))**2)+((int(targetloc[i][2])-int(codes1[k][2]))**2))**0.5) #Calculate the distance between the gauge from
                    #Group 1 and the target location at the gauge from Group 2.
                    vidi=vidi+(source_rainfall/di) #Update vidi based on the distance and correction factor at Group 1.
                    onedi=onedi+(1/di) #Update onedi based on the distance.
                v0=vidi/onedi #Calculate the differential correction factor at the target location (gauge from Group 2).
                rainfall_list.append([j[0],v0]) #Append the date and the interpolated correction factor to the rainfall_list, which corresponds to a specific gauge from Group 2.
            diff[targetloc[i][0]]=rainfall_list #Add the rainfall_list to the dictionary and move to the next target location.
    
    #Apply the correction factors to the daily satellite estimates.
    #Create a date_list containing all the days from 01-07-2000 to 01-07-2020
    date_list=[]
    for day in range(0,7305): #Increase days 1 by 1 until the present date, starting with 01-07-2000.
        date = (datetime.date(2000,7,1) + datetime.timedelta(days=day))
        date_list.append(date)

    #Extract the correction factor corresponding to each day of the time series, for MBC.
    cor_factor_daily_MBC=[] #Create a list to store the daily correction factors.
    for i in range(len(date_list)): #Iterate over the date_list.
        for j in range(len(cor_factor_MBC)): #Iterate over the correction factors time series.
            if datelabel=="3daily": #For 3-daily timesteps.
                if j==len(cor_factor_MBC)-1: #Last date in the correction factors time series.
                    if date_list[i]>=cor_factor_MBC[j][0]: #If date in date_list is more recent than date in cor_factor_MBC.
                        cor_append=[date_list[i],cor_factor_MBC[j][1]] #Adopt the corresponding correction factor to the date of date_list.
                        cor_factor_daily_MBC.append(cor_append)
                else: #In any other case.
                    if cor_factor_MBC[j][0]<=date_list[i]<cor_factor_MBC[j+1][0]: #If date in date_list is between the date in the cor_factor_MBC and the following date in
                        #the cor_factor_MBC.
                        cor_append=[date_list[i],cor_factor_MBC[j][1]] #Adopt the corresponding correction factor to the date of date_list.
                        cor_factor_daily_MBC.append(cor_append)
            elif datelabel=="monthly": #For monthly timesteps.
                if (date_list[i].month==cor_factor_MBC[j][0].month) and (date_list[i].year==cor_factor_MBC[j][0].year): #If month and year of the date_list is equal to month
                    #and year of cor_factor_MBC.
                    cor_append=[date_list[i],cor_factor_MBC[j][1]] #Adopt the corresponding correction factor to the date of date_list.
                    cor_factor_daily_MBC.append(cor_append)

    #Extract the correction factor corresponding to each day of the time series, for RIDW.
    cor_factor_daily_RIDW={} #Create a dictionary to store the correction factors at the location of each gauge from Group 2.
    for i in diff.keys(): #Iterate over rain gauges from Group 2.
        rain_daily=sat_daily[i] #Get daily rainfall of the satellite product (for the temporal disggregation of the correction factors).
        rain_interval=sat_interval[i] #Get rainfall of the satellite product at the temporal scale of the merging technique timestep (for the temporal disaggregation).
        diff_px=diff[i] #Get the list of correction factors at the location of each gauge from Group 2.
        cor_daily_RIDW=[] #Create a list to store the daily correction factors.
        for j in range(len(date_list)): #Iterate over the daily time series.
            for k in range(len(diff_px)): #Iterate over the list of correction factors.
                if datelabel=="3daily": #If timestep is 3-daily.
                    if k==len(diff_px)-1: #For the last correction factor of the time series.
                        if date_list[j]>=diff_px[k][0]: #If date in date_list is more recent than date in correction factor list.
                            if rain_interval[k][1]==0: #If satellite rainfall in the timestep of the merging technique is 0.
                                cor=0 #Adopt a correction factor of 0.
                            else: #In any other case.
                                cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1]) #Perform the temporal disaggregation of the differential correction factor.
                            cor_append=[date_list[j],cor] #Add the correction factor to the corresponding date of date_list.
                            cor_daily_RIDW.append(cor_append)
                    else: #In any other case.
                        if diff_px[k][0]<=date_list[j]<diff_px[k+1][0]: #If date in date_list is between the date in the correction factor list and the following date in
                            #the correction factor list.
                            if rain_interval[k][1]==0: #If satellite rainfall in the timestep of the merging technique is 0.
                                cor=0 #Adopt a correction factor of 0.
                            else: #In any other case.
                                cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1]) #Perform the temporal disaggregation of the differential correction factor.
                            cor_append=[date_list[j],cor] #Add the correction factor to the corresponding date of date_list.
                            cor_daily_RIDW.append(cor_append)
                elif datelabel=="monthly": #If timestep is monthly.                
                    if (date_list[j].month==diff_px[k][0].month) and (date_list[j].year==diff_px[k][0].year): #If month and year of the date_list is equal to the month
                        #and year of the correction factor list.
                        if rain_interval[k][1]==0: #If satellite rainfall in the timestep of the merging technique is 0.
                            cor=0 #Adopt a correction factor of 0.
                        else: #In any other case.
                            cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1]) #Perform the temporal disaggregation of the differential correction factor.
                        cor_append=[date_list[j],cor] #Add the correction factor to the corresponding date of date_list.
                        cor_daily_RIDW.append(cor_append)
        cor_factor_daily_RIDW[i]=cor_daily_RIDW #Add the correction factors at the target location to the dictionary, and move to the next target location.

    #Apply the correction factor of MBC and RIDW to the daily satellite estimates.
    prec_sat_daily_MBC={} #Create dictionary to store MBC.
    prec_sat_daily_RIDW={} #Create dictionary to store RIDW.
    for i in sat_daily.keys(): #Iterate over raing gauges.
        if i in codes2: #Only adopt rain gauges from Group 2.
            cor_daily_RIDW=cor_factor_daily_RIDW[i] #Get the RIDW correction factors for the analyzed target location.
            sat=sat_daily[i] #Get satellite time series.
            sat_list_MBC=[] #Create list to store corrected estimates for MBC.
            sat_list_RIDW=[] #Create list to store corrected estimated for RIDW.
            for j in range(len(sat)): #Iterate over time series.
                sat_prec_MBC=sat[j][1]*cor_factor_daily_MBC[j][1] #Correct satellite estimates with MBC (multiplication).
                sat_prec_RIDW=sat[j][1]+cor_daily_RIDW[j][1] #Correct satellite estimated with RIDW (difference).
                if sat_prec_RIDW<0: #Check if RIDW resuted in negative values, which are physically impossible.
                    sat_prec_RIDW=0 #In case values are negative, adopt estimate as 0.
                sat_append_MBC=[sat[j][0],sat_prec_MBC] #Add date and corrected rainfall estimates for MBC.
                sat_append_RIDW=[sat[j][0],sat_prec_RIDW] #Add date and corrected rainfall estimates for RIDW.
                sat_list_MBC.append(sat_append_MBC) #Append sat_append_MBC to sat_list_MBC.
                sat_list_RIDW.append(sat_append_RIDW) #Append sat_append_RIDW to sat_list_RIDW.
            prec_sat_daily_MBC[i]=sat_list_MBC #Add the MBC corrected estimates from a gauge from Group 2 to the dictionary, and move to the next gauge.
            prec_sat_daily_RIDW[i]=sat_list_RIDW #Add the RIDW corrected estimates from a gauge from Group 2 to the dictionary, and move to the next gauge.

    #Aggregate the daily estimates into 3-daily and monthly estimates.
    prec_sat_3daily_MBC={} #Create dictionary for 3-daily (MBC).
    prec_sat_3daily_RIDW={} #Create dictionary for 3-daily (RIDW).
    for i in prec_sat_daily_MBC.keys(): #Iterate over rain gauges.
        sat_MBC=prec_sat_daily_MBC[i] #Get daily satellite data (MBC).
        sat_RIDW=prec_sat_daily_RIDW[i] #Get daily satellite data (RIDW).
        prec_3daily_MBC=[] #Create a list to store 3-daily values (MBC).
        prec_3daily_RIDW=[] #Create a list to store 3-daily values (RIDW).
        k=1 #Create count.
        for j in range(len(sat_MBC)): #Iterate over time series.
            if k==1:
                prec_append_MBC=[sat_MBC[j][0]]
                prec_append_RIDW=[sat_RIDW[j][0]]
                prec_MBC=sat_MBC[j][1]
                prec_RIDW=sat_RIDW[j][1]
                k=k+1
            elif k==2:
                prec_MBC=prec_MBC+sat_MBC[j][1]
                prec_RIDW=prec_RIDW+sat_RIDW[j][1]
                k=k+1
            else:
                prec_MBC=prec_MBC+sat_MBC[j][1]
                prec_RIDW=prec_RIDW+sat_RIDW[j][1]
                prec_append_MBC.append(prec_MBC)
                prec_append_RIDW.append(prec_RIDW)
                prec_3daily_MBC.append(prec_append_MBC)
                prec_3daily_RIDW.append(prec_append_RIDW)
                k=1
        prec_sat_3daily_MBC[i]=prec_3daily_MBC #Add the time series of the gauge to the dictionary (MBC).
        prec_sat_3daily_RIDW[i]=prec_3daily_RIDW #Add the time series of the gauge to the dictionary (RIDW).

    #Aggregate into monthly
    prec_sat_monthly_MBC={} #Create dictionary for monthly estimates (MBC).
    prec_sat_monthly_RIDW={} #Create dictionary for monthly estimates (RIDW).
    for i in prec_sat_daily_MBC.keys(): #Iterate over rain gauges.
        sat_MBC=prec_sat_daily_MBC[i] #Get daily satellite data (MBC).
        sat_RIDW=prec_sat_daily_RIDW[i] #Get daily satellite data (RIDW).
        prec_monthly_MBC=[] #Create list to store monthly values (MBC).
        prec_monthly_RIDW=[] #Create list to store monthly values (RIDW).
        for j in range(len(sat_MBC)): #Iterate over time series.
            if j==0: #For the first date of the time series.
                prec_MBC=sat_MBC[j][1]
                prec_RIDW=sat_RIDW[j][1]
            elif sat_MBC[j][0].month==sat_MBC[j-1][0].month and j!=len(sat_MBC)-1: #If month of the estimate is equal to the month of the previous estimate.
                prec_MBC=prec_MBC+sat_MBC[j][1] #Accumulate rainfall values.
                prec_RIDW=prec_RIDW+sat_RIDW[j][1] #Accumulate rainfall values.
            elif j==len(sat_MBC)-1: #For the last date of the time series.
                date=datetime.date(int(sat_MBC[j][0].year),int(sat_MBC[j][0].month),1)
                prec_append_MBC=[date,prec_MBC]
                prec_append_RIDW=[date,prec_RIDW]
                prec_monthly_MBC.append(prec_append_MBC)
                prec_monthly_RIDW.append(prec_append_RIDW)   
            else:
                date=datetime.date(int(sat_MBC[j-1][0].year),int(sat_MBC[j-1][0].month),1) #Get the date of the previous day and relate it with the accumulated precipitation.
                prec_append_MBC=[date,prec_MBC]
                prec_append_RIDW=[date,prec_RIDW]
                prec_monthly_MBC.append(prec_append_MBC)
                prec_monthly_RIDW.append(prec_append_RIDW)
                prec_MBC=sat_MBC[j][1]
                prec_RIDW=sat_RIDW[j][1]
        prec_sat_monthly_MBC[i]=prec_monthly_MBC
        prec_sat_monthly_RIDW[i]=prec_monthly_RIDW

    #Save the corrected satellite estimates for both MBC and RIDW merging techniques.
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SGMerged\Output")
    np.save("prec_"+satlabel+"_daily_MBC"+datelabel+".npy", prec_sat_daily_MBC)
    np.save("prec_"+satlabel+"_3daily_MBC"+datelabel+".npy", prec_sat_3daily_MBC)
    np.save("prec_"+satlabel+"_monthly_MBC"+datelabel+".npy", prec_sat_monthly_MBC)
    np.save("prec_"+satlabel+"_daily_RIDW"+datelabel+".npy", prec_sat_daily_RIDW)
    np.save("prec_"+satlabel+"_3daily_RIDW"+datelabel+".npy", prec_sat_3daily_RIDW)
    np.save("prec_"+satlabel+"_monthly_RIDW"+datelabel+".npy", prec_sat_monthly_RIDW)

#Run the function for both satellite products (GSMaP and IMERG) and timesteps (daily and 3-daily)
merge(GSMaP_daily,GSMaP_monthly,gauge_daily,gauge_monthly,targetloc,codes1,codes2,"monthly","GSMaP")
merge(GSMaP_daily,GSMaP_3daily,gauge_daily,gauge_3daily,targetloc,codes1,codes2,"3daily","GSMaP")
merge(IMERG_daily,IMERG_monthly,gauge_daily,gauge_monthly,targetloc,codes1,codes2,"monthly","IMERG")
merge(IMERG_daily,IMERG_3daily,gauge_daily,gauge_3daily,targetloc,codes1,codes2,"3daily","IMERG")
