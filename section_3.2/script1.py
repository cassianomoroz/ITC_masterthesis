#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to analyze the quality of the rain gauge data through a series of consistency and completeness tests

import os
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy as sp
import itertools as it
import shapefile as shp
from scipy.stats import gaussian_kde
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

#Define the working directory where the .txt rainfall files are located. These are the files downloaded from the HidroWeb portal.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\ANA\Rainfall")

#Create a function to create time series from the data. Column 0 represents the date, column 1 represents the daily measurements.
def rainfall_input(gauge_data):

    #Read the file.
    rainfall_input=open(gauge_data,'r')
    rainfall_read=rainfall_input.read() #Read the data.
    rainfall_input.close() #Close.

    #Split rows and columns.
    rainfall_read = [x.split(';') for x in rainfall_read.split('\n')] #Split the data according to the separator ;

    #Delete the rows and columns that are not part of the data (mostly metadata provided by ANA).
    rainfall_read=rainfall_read[13:-1] #Columns: metadata about the rain gauge.
    for row in rainfall_read: #Rows.
        del row[3:13] #Rainfall statistics.
        del row[44:] #Other rainfall information.
    #Now, column 0 refers to the station ID, column 1 to the consistency level, column 2 to the month/year, and columns 3 to 33 to the measurements from day 1 to 31.
    #Rows refers to the months.

    #Transform the matrix into a nested list with rainfall measurements in a single column.
    rainfall_list=[] #Create a new list.
    for i in range(len(rainfall_read)):
        date=rainfall_read[i][2].split('/') #Separate day, month and year.
        date1=datetime.date(int(date[2]),int(date[1]),1) #Correct the format of the date.
        if date1.month==12:
            days=31#31 days in December.
        else:
            date2=datetime.date(int(date[2]),int(date[1])+1,1)
            days=(date2-date1).days #Calculate the number of days in a specific month (when not in December).
        j=days
        while j>0:#Convert the rainfall measurements from string to float.
            if rainfall_read[i][j+2]=='': #Adopt 'nan' for missing values.
                rainfall_amount=float('nan')
            else:
                rainfall_amount=float(rainfall_read[i][j+2].replace(',','.'))
            list_append=[rainfall_read[i][0],rainfall_read[i][1],datetime.date(int(date[2]),int(date[1]),j),rainfall_amount] 
            rainfall_list.append(list_append) #Insert the date/measurements into the new list.
            j=j-1

    #Generate a continuous time series with the period of interest, from 2000 to 2020.
    days = 7305 #From 01-07-2000 to 01-07-2020.
    date_list = [] #Create a list to add the rainfall measurements from all rain gauges.

    for day in range(days): #Increase days 1 by 1 until the present date.
        date = (datetime.date(2000,7,1) + datetime.timedelta(days=day))
        date_list.append(date)

    #Join the time series with rainfall data. Add the rainfall measurements to the new list in all cases when the date matches.
    final_list=[]
    for i in range(len(date_list)): #Interate over the complete time series.
        list_append=0
        for j in range(len(rainfall_list)): #Iterate over the original time series, with temporal gaps.
            if date_list[i]==rainfall_list[j][2]: #If dates are the same.
                list_append=[date_list[i],rainfall_list[j][3]] #Append date and rainfall to the final list.
            elif list_append==0: #If the first measurement didn't find a match for the date, assume it as 'nan'.
                list_append=[date_list[i],float('nan')]
        final_list.append(list_append) #Append the daily measurement to the final list.
        
    #Return the rainfall time series.
    return final_list

#Create a list station_codes to store the codes of the rain gauges.
i=0
codes_all = []
directory = r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\ANA\Rainfall' #Define the directory where the .txt files from HidroWeb are located.
for entry in os.scandir(directory): #Iterate over the directory.
    append_codes=[i,entry.name.replace(".txt","")] #Add the codes of the rain gauges to the list.
    codes_all.append(append_codes)
    i=i+1

#Create a dictionary to store the rainfall data from all stations through interaction with the function rainfall_input.
rainfall_all = {} #Dictionary with all rain gauge measurements.
for i in range(len(codes_all)): #Iterate over the rain gauge codes.
    rainfall_all[codes_all[i][1]]=rainfall_input(codes_all[i][1]+".txt") #Call the function rainfall_input.

#Aggregate the daily data into 3-daily totals.
prec_gauge_3daily={} #Create a new dictionary to store the 3-daily totals.
for i in range(len(rainfall_all)): #Iterate over all rain gauge stations.
    station_list=rainfall_all[codes_all[i][1]] #Get the rain gauge data.
    date_list=[row[0] for row in station_list] #Get dates.
    prec_list=[row[1] for row in station_list] #Get rainfall measurements.
    prec_3daily=[] #New list to store values.
    k=1 #Create a count to aggregate measurements when it reaches the value 1.
    for j in range(len(date_list)): #Iterate over dates.
        if k==1: #Get the first value of rainfall, add 1 to k.
            prec_append=[date_list[j]]
            prec=prec_list[j]
            k=k+1
        elif k==2: #Sum the rainfall measurement to the prec variable, add 1 to k.
            prec=prec+prec_list[j]
            k=k+1
        else: #If k>2, sum the rainfall measurement to the prec variable and append the value of 3-daily totals. Return to k equals 1.
            prec=prec+prec_list[j]
            prec_append.append(prec)
            prec_3daily.append(prec_append)
            k=1
    prec_gauge_3daily[codes_all[i][1]]=prec_3daily #Add the temporary list to the dictionary.
    
#Aggregate the daily data into monthly totals.
prec_gauge_monthly={} #Create a new dictionary to store the monthly totals.
for i in range(len(rainfall_all)): #Iterate over all rain gauge stations.
    station_list=rainfall_all[codes_all[i][1]] #Get the rain gauge data.
    date_list=[row[0] for row in station_list] #Get dates.
    prec_list=[row[1] for row in station_list] #Get rainfall measurements.
    prec_monthly=[] #New list to store values.
    for j in range(len(date_list)): #Iterate over dates.
        if j==0: #Start with the first rainfall measurement.
            prec=prec_list[j]
        elif date_list[j].month==date_list[j-1].month and j!=(len(date_list)-1): #If month and year remain the same, add rainfall measurement to prec variable.
            prec=prec+prec_list[j]
        elif j==(len(date_list)-1): #For the last value in the list (01-07-2020), adopt prec as the monthly rainfall.
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1)
            prec_append=[date,prec] #Get the date of the previous day to represent the month/year of the monthly total.
            prec_monthly.append(prec_append)
        else: #If month or year change, adopt the pre variable as the monthly rainfall, and start a new prec variable.
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1)
            prec_append=[date,prec] #Get the date of the previous day to represent the month/year of the monthly total.
            prec_monthly.append(prec_append)
            prec=prec_list[j]
    prec_gauge_monthly[codes_all[i][1]]=prec_monthly #Add the temporary list to the dictionary.

#Check and plot negative values or values over 200mm/day
for i in range(len(codes_all)): #Iterate over all rain gauges.
    station_list=rainfall_all[codes_all[i][1]] #Get the rain gauge data.
    rainfall_list=[row[1] for row in station_list] #Get rainfall measurements.
    for j in range(len(rainfall_list)): #Iterate over rainfall.
        if rainfall_list[j]<0: #Check for negative measurements. Print values for manual inspection.
            print(str(i)+" "+str(rainfall_list[j]))
        elif rainfall_list[j]>200: #Check for measurements over 200mm/day. Print values for manual inspection.
            print(str(codes_all[i][0])+" "+str(codes_all[i][1])+" "+str(station_list[j][0])+" "+str(rainfall_list[j]))

#Manually inspect measurements and delete stations with negative rainfall or rainfall over 200mm/day not related to flood events.
#Create a new codes list only with stations without the above-mentioned inconsistencies.
codes_all_1=[] #New list.
for i in range(len(codes_all)): #Iterate over rain gauges.
    if codes_all[i][0]!=9 and codes_all[i][0]!=16: #Manual selection of rain gauges to be eliminated. Eliminated stations refer to codes 9 (02649008) and 16 (02649065).
        codes_all_1.append(codes_all[i])

#Generate a new dictionary with rain gauge measurements.
keys=[row[1] for row in codes_all_1]
rainfall_all_1={x:rainfall_all[x] for x in keys} #New dictionary with stations that were maintained.
            
#Select rain gauges from Group 1. Select only the stations with a maximum of two consecutive days with missing data from 2000 to 2020.
for i in range(len(rainfall_all_1)): #Iterate over rain gauges.
    station_list=rainfall_all[codes_all_1[i][1]] #Get the rain gauge data.
    rainfall_list=[row[1] for row in station_list] #Get rainfall measurements.
    quality=0 #Code to express quality of the rain gauge measurements.
    for j in range(len(rainfall_list)-2): #Iterate over date.
        if quality==0 or quality=="Yes":
            if math.isnan(rainfall_list[j])==True and math.isnan(rainfall_list[j+1])==True and math.isnan(rainfall_list[j+2])==True: #Check for more than 2 days of consecutive missing measurements.
                quality = "No" #Adopt code no is this is the case.
            else:
                quality = "Yes" #Adopt code yes if this is not the case.
    codes_all_1[i].append(quality) #Add the quality variable (Yes or No) to the station codes.

#Create a new dictionary for the stations from Group 1.
keys=[]
for i in range(len(codes_all_1)): #Iterate over rain gauges.
    if codes_all_1[i][2]=="Yes": #Adopt only stations with quality Yes.
        keys.append(codes_all_1[i][1])
rainfall_adp_0={x:rainfall_all_1[x] for x in keys}

#Create a new codes index, only with the adopted stations.
codes_adp_0=[] #New list with codes for Group 1 stations.
for i in range(len(codes_all_1)):
    if codes_all_1[i][2]=="Yes": #Add only stations with quality Yes.
        append_list=[i,codes_all_1[i][1]]
        codes_adp_0.append(append_list)

#Fill the missing measurements with the disaggregation of the measurement right after the missing values.
rainfall_adp_1={} #New dictionary for corrected measurements.
for i in range(len(rainfall_adp_0)): #Iterate over rain gauges.
    station_list=rainfall_adp_0[codes_adp_0[i][1]] #Get the rain gauge data.
    rainfall_list=[row[1] for row in station_list] #Get rain measurements.
    for j in range(len(rainfall_list)-2): #Iterate over the dates.
        if j>0 and math.isnan(rainfall_list[j])==True: #If measurement is missings.
            if math.isnan(rainfall_list[j+1])==True: #Divide the following existing measurement by 3 if the number of missing days is 2.
                station_list[j][1]=rainfall_list[j+2]/3 #Replace the missing measurements.
                station_list[j+1][1]=station_list[j][1] #Replace the missing measurements.
                station_list[j+2][1]=station_list[j][1] #Replace the measurement after the gap.
            else: #Divide the following existing measurement by 2 if the number of missing days is 1.
                station_list[j][1]=rainfall_list[j+1]/2 #Replace the missing measurements.
                station_list[j+1][1]=station_list[j][1] #Replace the measurement after the gap.
    rainfall_adp_1[codes_adp_0[i][1]]=(station_list)

#Create histograms
for i in range(len(rainfall_adp_1)): #Iterate over the rainfall
    font = {'size': 10}
    plt.rc('font', **font)
    fig,((ax1))=plt.subplots(1,1)
    rainfall_list=rainfall_adp_1[codes_adp_0[i][1]] #Get the rain gauge data.
    x=[row[0] for row in rainfall_list] #Get the date.
    y=[row[1] for row in rainfall_list] #Get rainfall measurements.
    ax1.plot(x, y, "b-",linewidth=0.5)
    ax1.set_xlabel("Date",fontsize=10)
    ax1.set_ylabel("Rainfall (mm/day)",fontsize=10)
    ax1.set_xlim(datetime.date(2000,7,1),datetime.date(2020,7,1))
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_title(str(codes_adp_0[i][1]),size=11)
    fig.set_size_inches(6,3)
    fig.subplots_adjust(bottom=0.25,left=0.12,right=0.95,top=0.90,wspace=0.39)
    fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Histograms\Group1_v1\All_"+str(codes_adp_0[i][1])+".jpg")
    plt.close()

#Visually inspect the histograms.

#Save the adopted codes for stations from Group 1.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
np.save('codes_group1.npy', codes_adp_0)

#Aggregate the corrected daily data into 3-daily totals.
prec_gauge_3daily_1={} #Create new dictionary.
for i in range(len(rainfall_adp_1)): #Iterate over rain gauges.
    station_list=rainfall_adp_1[codes_adp_0[i][1]] #Get the rain gauge data.
    date_list=[row[0] for row in station_list] #Get dates.
    prec_list=[row[1] for row in station_list] #Get rainfall measurements.
    prec_3daily=[] #Create temporary list to store 3-daily totals.
    k=1 #Create a count to aggregate measurements when it reaches the value 1.
    for j in range(len(date_list)): #Iterate over dates.
        if k==1: #Get the first value of rainfall, add 1 to k.
            prec_append=[date_list[j]]
            prec=prec_list[j]
            k=k+1
        elif k==2: #Sum the rainfall measurement to the prec variable, add 1 to k.
            prec=prec+prec_list[j]
            k=k+1
        else: #If k>2, sum the rainfall measurement to the prec variable and append the value of 3-daily totals. Return to k equals 1.
            prec=prec+prec_list[j]
            prec_append.append(prec)
            prec_3daily.append(prec_append)
            k=1
    prec_gauge_3daily_1[codes_adp_0[i][1]]=prec_3daily #Add the temporary list to the dictionary.

#Aggregate the corrected daily data into monthly totals.
prec_gauge_monthly_1={} #Create new dictionary.
for i in range(len(rainfall_adp_1)): #Iterate over rain gauges.
    station_list=rainfall_adp_1[codes_adp_0[i][1]] #Get the rain gauge data.
    date_list=[row[0] for row in station_list] #Get dates.
    prec_list=[row[1] for row in station_list] #Get rainfall measurements.
    prec_monthly=[] #Create temporary list to store monthly totals.
    for j in range(len(date_list)): #Iterate over dates.
        if j==0: #Start with the first rainfall measurement.
            prec=prec_list[j]
        elif date_list[j].month==date_list[j-1].month and j!=(len(date_list)-1): #If month and year remain the same, add rainfall measurement to prec variable.
            prec=prec+prec_list[j]
        elif j==(len(date_list)-1): #For the last value in the list (01-07-2020), adopt prec as the monthly rainfall.
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1)
            prec_append=[date,prec] #Get the date of the previous day to represent the month/year of the monthly total.
            prec_monthly.append(prec_append)
        else: #If month or year change, adopt the pre variable as the monthly rainfall, and start a new prec variable.
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1)
            prec_append=[date,prec] #Get the date of the previous day to represent the month/year of the monthly total.
            prec_monthly.append(prec_append)
            prec=prec_list[j]
    prec_gauge_monthly_1[codes_adp_0[i][1]]=prec_monthly #Add the temporary list to the dictionary.
           
#Save the daily, 3-daily and monthly rainfall of gauges from Group 1 as a .npy file, to be imported in further analyses.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
np.save('prec_gauge_daily_all.npy', rainfall_adp_1)
np.save('prec_gauge_3daily_all.npy',prec_gauge_3daily_1)
np.save('prec_gauge_monthly_all.npy', prec_gauge_monthly_1)

#Now, start the analysis of Group 2.
#Create a dictionary to store the codes adopted for each year.
codes_year={}
codes_all_yr=[]
codes_adp=[row[1] for row in codes_adp_0]

#Analyze data completeness per year from 2000 to 2019, from the pre-selected rain gauges rainfall_all_1.
for year in range(2001,2020): #Iterate over years.
    #Adopt gauges with no missing values in the year.
    codes_year_list=[]
    for i in rainfall_all_1.keys(): #Iterate over rain gauges.
        if i not in codes_adp: #Adopt only gauges that were not adopted for Group 1.
            station_list=rainfall_all_1[i] #Get the rain gauge data.
            rainfall_list=[row[1] for row in station_list] #Get rainfall measurements.
            quality="Yes" #Start with quality Yes.
            for j in range(len(rainfall_list)): #Iterate over time series.
                if quality=="Yes" and station_list[j][0].year==year: #For the measurements of the year.
                    if math.isnan(rainfall_list[j])==True: #If there is any missing measurement.
                        quality="No" #Change quality to No.
            if quality=="Yes":
                codes_year_list=codes_year_list+[i] #Adopt code if quality if yes.
                if i not in codes_all_yr:
                    codes_all_yr.append(i) #Adopt rain gauge code to the codes for Group 2.
    codes_year[year]=codes_year_list

#Create a list to store all years with complete data among rain gauges, regardless of the number of gauges.
years_list=[]
for i in codes_year.keys():
    years_list=years_list+[i]

#Create all possible combinations of number of gauges and number of years in common with complete data.
combination={} #Create a dictionary to store combinations.
for i in range(1,21): #Analyze all combinations from 1 to 21 years.
    combination[i]=list(it.combinations(years_list,i)) #Apply the function to generate all combinations of years, adopting 1 to 20 years in the combination.

#Calculate the number of rain gauges with common years of measurements, per number of years.
years_stats=[] #List for statistics of years.
gauge_stats=[] #List for statistics of rain gauges.
for i in range(1,21): #Iterate over number of gauges.
    count_max=0
    iterate=combination[i] #Get the number of combinations for each number of years in common.
    for j in iterate: #Iterate over each combination and check the number of gauges with data for each combination of years.
        a={}
        keys=[]
        for k in range(0,21):
            if i>k:
                keys=keys+[k]
                a[k]=codes_year[j[k]]
        if i==1:
            for k in range(len(keys)):
                count=len(a[keys[k]])
                lst=a[keys[k]]
        else:
            lst=0
            for k in range(len(keys)-1):
                if lst==0:
                    lst1=a[keys[k]]
                    lst2=a[keys[k+1]]
                else:
                    lst1=lst
                    lst2=a[keys[k+1]]
                lst=[value for value in lst1 if value in lst2]
                count=len(lst)
        if count>count_max:
            count_max=count
    years_stats.append([i,count_max])

#Now, check all the kinds of combinations that give the same number of gauges, but with a different selection.
years_stats_1=[]
for i in range(len(years_stats)):
    nryears=years_stats[i][0]
    nrgauges=years_stats[i][1]
    iterate=combination[nryears]
    for j in iterate:
        a={}
        keys=[]
        for k in range(0,21):
            if nryears>k:
                keys=keys+[k]
                a[k]=codes_year[j[k]]        
        if nryears==1:
            for k in range(len(keys)):
                count=len(a[keys[k]])
                lst=a[keys[k]]
        else:
            lst=0
            for k in range(len(keys)-1):
                if lst==0:
                    lst1=a[keys[k]]
                    lst2=a[keys[k+1]]
                else:
                    lst1=lst
                    lst2=a[keys[k+1]]
                lst=[value for value in lst1 if value in lst2]
                count=len(lst)
        adopt="Yes"
        for k in gauge_stats:
            if ([nryears]+lst)==k:
                adopt="No"
        if count==nrgauges and adopt=="Yes":
            lst_max=[nryears]+lst
            gauge_stats.append(lst_max)
            years_stats_1.append(j)

#Import the shapefile of the Itajai-Acu River Basin and extract the X and Y coordinates
basin = shp.Reader(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Thesis\Edit\Figures\Data\ItajaiAcu.shp") #Import the shapefile.
for shape in basin.shapeRecords():
    basinx = [i[0] for i in shape.shape.points[:]] #Extract x coordinate.
    basiny = [i[1] for i in shape.shape.points[:]] #Extract y coordinate.

#Import the X and Y coordinates from the gauges.
gauge_coord=[] #List to store coordinates.
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\GaugeCoordinates.csv', newline='') as f: #Directory with the coordinates.
    reader = csv.reader(f)
    coord_extend = list(reader)   
    gauge_coord.extend(coord_extend)
#Fix the first text
gauge_coord[0][0]=gauge_coord[0][0][3:]

#Plot, for each number of years, the location of the gauges with common data.
for i in range(len(gauge_stats)):
    font = {'size': 10}
    plt.rc('font', **font)
    fig,((ax1))=plt.subplots(1,1)  
    plot_gauge=gauge_stats[i]
    title=plot_gauge[:1]
    data=plot_gauge[1:]
    gaugex=[] #Create a list for the x coordinates of gauges.
    gaugey=[] #Create a list for the y coordinates of gauges.
    for j in data:
        for k in range(len(gauge_coord)): #Iterate over the coordinates and fill the lists.
            if j==gauge_coord[k][0]:
                gaugex=gaugex+[int(gauge_coord[k][1])]
                gaugey=gaugey+[int(gauge_coord[k][2])]
    #Repeat the procedure only for the gauges adopted for Group 2.
    gaugeadpx=[]
    gaugeadpy=[]
    for j in codes_adp:
        for k in range(len(gauge_coord)):
            if j==gauge_coord[k][0]:
                gaugeadpx=gaugeadpx+[int(gauge_coord[k][1])]
                gaugeadpy=gaugeadpy+[int(gauge_coord[k][2])]
    ax1.scatter(gaugeadpx, gaugeadpy,color="red",s=15,marker="s",label="Group 1 gauges",zorder=1) #Plot adopted gauges.
    ax1.scatter(gaugex, gaugey,color="blue",s=15,label="Rain gauges",zorder=2)    #Plot all gauges.
    ax1.plot(basinx, basiny, "k--",linewidth=1,label="Study area") #Plot boundaries of the catchment area.
    ax1.set_xlabel("Coordinate X",fontsize=10)
    ax1.set_ylabel("Coordinate Y",fontsize=10)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_title(str(title[0])+" years",size=11)
    fig.set_size_inches(4,4)
    fig.legend(loc="lower center", fontsize=10,ncol=3,columnspacing=1,handletextpad=0.03,frameon=False)
    fig.subplots_adjust(bottom=0.2,left=0.14,right=0.95,top=0.85,wspace=0.39)
    fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Maps\Year"+str(title[0])+"Combination"+str(i)+".jpg")
    plt.close()

#Visually inspect all combinations and selected the best combination based on an even distribution of the gauges.
#The selected combination was configuration was i==5 for gauge_stats e years_stats_1, which refers to 5 years in common, countaining 12 rain gauges.
gauges2_adp=gauge_stats[5][1:] #Get the codes of the gauges.
year2_adp=years_stats_1[5] #Get the years.

#Create a new dictionary for daily rainfall from Group 2.
prec_gauge_daily_yr={}
for i in rainfall_all_1.keys(): #Iterate over old dictionary.
    if i in gauges2_adp: #Adopt only the gauges included in the previous analysis.
        prec_gauge_daily_yr[i]=rainfall_all_1[i]
   
#Aggregate to 3-daily totals.
prec_gauge_3daily_yr={} #Create a dictionary to store 3-daily aggregates.
for i in prec_gauge_3daily.keys(): #Iterate over the dictionary of 3-daily totals from all gauges.
    if i in gauges2_adp: #Adopt only the gauges included in the previous analysis.
        prec_gauge_3daily_yr[i]=prec_gauge_3daily[i]

#Aggregate to monthly totals.
prec_gauge_monthly_yr={} #Create a dictionary to store monthly aggregates.
for i in prec_gauge_monthly.keys(): #Iterate over the dictionary of monthly totals from all gauges.
    if i in gauges2_adp: #Adopt only the gauges included in the previous analysis.
        prec_gauge_monthly_yr[i]=prec_gauge_monthly[i]

#Create histograms for Group 2, to be visually inspected.
for year in year2_adp: #Plot only the years that are relevant, the common years among the gauges.
    for i in gauges2_adp: #Iterate over the rain gauges.
        font = {'size': 10}
        plt.rc('font', **font)
        fig,((ax1))=plt.subplots(1,1)
        rainfall_list=prec_gauge_daily_yr[i] #Get the gauge data.
        x=[row[0] for row in rainfall_list] #Get dates.
        y=[row[1] for row in rainfall_list] #Get rainfall measurements.
        ax1.plot(x, y, "b-",linewidth=0.5)
        ax1.set_xlabel("Date",fontsize=10)
        ax1.set_ylabel("Rainfall (mm/day)",fontsize=10)
        ax1.set_xlim(datetime.date(year,1,1),datetime.date(year+1,1,1))
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.set_title(i,size=11)
        fig.set_size_inches(6,3)
        fig.subplots_adjust(bottom=0.25,left=0.12,right=0.95,top=0.90,wspace=0.39)
        fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Histograms\Group2_v1\Year"+str(year)+'_'+str(i)+".jpg")
        plt.close()

#Export the Group 2 rainfall measurements.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
np.save('codes_group2.npy', gauges2_adp)
np.save('codes_years2.npy', year2_adp)
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
np.save('prec_gauge_daily_yr.npy', prec_gauge_daily_yr)
np.save('prec_gauge_3daily_yr.npy', prec_gauge_3daily_yr)
np.save('prec_gauge_monthly_yr.npy', prec_gauge_monthly_yr)
