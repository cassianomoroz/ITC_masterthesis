#Define the working directory and import packages
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
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\ANA\Rainfall")

#Create a function to transform the rain gauges input data into a list with date in the column 0 and rain measurement in the column 1.
def rainfall_input(gauge_data):

    #Open and close the rainfall txt file (Brazilian National Water Agency standard), create a variable to work with it.
    rainfall_input=open(gauge_data,'r')
    rainfall_read=rainfall_input.read()
    rainfall_input.close()

    #Create a list separating the rows and columns.
    rainfall_read = [x.split(';') for x in rainfall_read.split('\n')]

    #Delete elements that are not relevant for the analysis.
    rainfall_read=rainfall_read[13:-1] #Columns: general information about the station.
    for row in rainfall_read: #Rows.
        del row[3:13] #Rainfall statistics.
        del row[44:] #Other rainfall information.
    #Now, column 0 refers to the station ID, column 1 to the consistency level, column 2 to the month/year, and columns 3 to 33 to the measurements from day 1 to 31.

    #Generate rainfall measurements in a single list, with different rows.
    rainfall_list=[] #Create a new list.
    for i in range(len(rainfall_read)):
        date=rainfall_read[i][2].split('/') #Separate day, month and year.
        date1=datetime.date(int(date[2]),int(date[1]),1) #Construct the date in a correct data format, adopting the correct day.
        if date1.month==12:
            days=31#31 days in December.
        else:
            date2=datetime.date(int(date[2]),int(date[1])+1,1)
            days=(date2-date1).days #Calculate the number of days in a specific month (when not in December).
        j=days
        while j>0:#Convert the rainfall measurements from string to float.
            if rainfall_read[i][j+2]=='': 
                rainfall_amount=float('nan')
            else:
                rainfall_amount=float(rainfall_read[i][j+2].replace(',','.'))
            list_append=[rainfall_read[i][0],rainfall_read[i][1],datetime.date(int(date[2]),int(date[1]),j),rainfall_amount] 
            rainfall_list.append(list_append) #Insert the date/measurements into the new list.
            j=j-1

    #The previous list generally has data incompleteness. Generate a continuous time series with the period of interest, from 2000 to 2020.
    days = 7305 #From 01-07-2000 to 01-07-2020.
    date_list = [] #Create a list to add the rainfall measuremnts from all rain gauges.

    for day in range(days): #Increase days 1 by 1 until the present date.
        date = (datetime.date(2000,7,1) + datetime.timedelta(days=day))
        date_list.append(date)

    #Join the time series with rainfall data.
    final_list=[]
    for i in range(len(date_list)):
        list_append=0
        for j in range(len(rainfall_list)):
            if date_list[i]==rainfall_list[j][2]:
                list_append=[date_list[i],rainfall_list[j][3]]
            elif list_append==0:
                list_append=[date_list[i],float('nan')]
        final_list.append(list_append)
        
    #Return the data from the function.
    return final_list

#Create a list station_codes to store the codes of the rain gauges. This enables to call the code in future steps.
i=0
codes_all = [] #Create a list to store the codes of the stations and associate these codes with the dictionary.
directory = r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\ANA\Rainfall'
for entry in os.scandir(directory):
    append_codes=[i,entry.name.replace(".txt","")]
    codes_all.append(append_codes)
    i=i+1

#Create a dictionary to store the data from all stations through interaction with the function rainfall_input. Enable in case rainfall_all is not saved.
#rainfall_all = {}
#for i in range(len(codes_all)):
#    rainfall_all[codes_all[i][1]]=rainfall_input(codes_all[i][1]+".txt")

#Save the file as a .npy to call it again without repeat previous steps (long runtime).
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
#np.save('rainfall_all.npy', rainfall_all)

#Open rainfall_all .npy file.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
rainfall_all=np.load("rainfall_all.npy",allow_pickle=True).item()

#Aggregate all rain gauge time series in 3-daily measurements.
prec_gauge_3daily={}
for i in range(len(rainfall_all)):
    station_list=rainfall_all[codes_all[i][1]]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_3daily=[]
    k=1
    for j in range(len(date_list)):
        if k==1:
            prec_append=[date_list[j]]
            prec=prec_list[j]
            k=k+1
        elif k==2:
            prec=prec+prec_list[j]
            k=k+1
        else:
            prec=prec+prec_list[j]
            prec_append.append(prec)
            prec_3daily.append(prec_append)
            k=1
    prec_gauge_3daily[codes_all[i][1]]=prec_3daily
    
#Aggregate all rain gauge time series in monthly measurements.
prec_gauge_monthly={}
for i in range(len(rainfall_all)):
    station_list=rainfall_all[codes_all[i][1]]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_monthly=[]
    for j in range(len(date_list)):
        if j==0:
            prec=prec_list[j]
        elif date_list[j].month==date_list[j-1].month and j!=(len(date_list)-1):
            prec=prec+prec_list[j]
        elif j==(len(date_list)-1):
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
        else:
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
            prec=prec_list[j]
    prec_gauge_monthly[codes_all[i][1]]=prec_monthly

#Check and plot negative values or values over 150mm/day
for i in range(len(codes_all)):
    station_list=rainfall_all[codes_all[i][1]]
    rainfall_list=[row[1] for row in station_list]
    for j in range(len(rainfall_list)):
        if rainfall_list[j]<0:
            print(str(i)+" "+str(rainfall_list[j]))
        elif rainfall_list[j]>200:
            print(str(codes_all[i][0])+" "+str(codes_all[i][1])+" "+str(station_list[j][0])+" "+str(rainfall_list[j]))

#Manually inspect measurements and eliminate stations with negative rainfall or rainfall over 200mm/day not related to flood events.
#Create a new codes list only with stations without the above-mentioned inconsistencies.
codes_all_1=[]
for i in range(len(codes_all)):
    if codes_all[i][0]!=9 and codes_all[i][0]!=16:#Eliminated stations refer to codes 9 (02649008) and 16 (02649065).
        codes_all_1.append(codes_all[i])

#Generate a new dictionary with rain gauge measurements.
keys=[row[1] for row in codes_all_1]
rainfall_all_1={x:rainfall_all[x] for x in keys}
            
#For the first group of rain gauges, select only the stations with a maximum of two consecutive days with missing data from 2000 to 2020.
for i in range(len(rainfall_all_1)):
    station_list=rainfall_all[codes_all_1[i][1]]
    rainfall_list=[row[1] for row in station_list]
    quality=0
    for j in range(len(rainfall_list)-2):
        if quality==0 or quality=="Yes":
            if math.isnan(rainfall_list[j])==True and math.isnan(rainfall_list[j+1])==True and math.isnan(rainfall_list[j+2])==True:
                quality = "No"
            else:
                quality = "Yes"
    codes_all_1[i].append(quality)

#Create a new dictionary for the stations to be adopted (only the ones with data from 2000 to 2020).
keys=[]
for i in range(len(codes_all_1)):
    if codes_all_1[i][2]=="Yes":
        keys.append(codes_all_1[i][1])
rainfall_adp_0={x:rainfall_all_1[x] for x in keys}

#Create a new codes index, only with the adopted stations.
codes_adp_0=[]
for i in range(len(codes_all_1)):
    if codes_all_1[i][2]=="Yes":
        append_list=[i,codes_all_1[i][1]]
        codes_adp_0.append(append_list)

#Fill the missing measurements with the disaggregation of the measurement right after the missing values.
rainfall_adp_1={}
for i in range(len(rainfall_adp_0)):
    station_list=rainfall_adp_0[codes_adp_0[i][1]]
    rainfall_list=[row[1] for row in station_list]
    for j in range(len(rainfall_list)-2):
        if j>0 and math.isnan(rainfall_list[j])==True:
            if math.isnan(rainfall_list[j+1])==True:#Divide by 3 if the number of missing days is 2.
                station_list[j][1]=rainfall_list[j+2]/3#Add to the missing data.
                station_list[j+1][1]=station_list[j][1]
                station_list[j+2][1]=station_list[j][1]#Replace the measurement after the gap.
            else:#Divide by 2 if the number of missing days is 1.
                station_list[j][1]=rainfall_list[j+1]/2#Add to the missing data.
                station_list[j+1][1]=station_list[j][1]#Replace the measurement after the gap.
    rainfall_adp_1[codes_adp_0[i][1]]=(station_list)

#Create histograms
for i in range(len(rainfall_adp_1)):
    font = {'size': 10}
    plt.rc('font', **font)
    fig,((ax1))=plt.subplots(1,1)
    rainfall_list=rainfall_adp_1[codes_adp_0[i][1]]
    x=[row[0] for row in rainfall_list]
    y=[row[1] for row in rainfall_list]
    ax1.plot(x, y, "b-",linewidth=0.5)
    ax1.set_xlabel("Date",fontsize=10)
    ax1.set_ylabel("Rainfall (mm/day)",fontsize=10)
    ax1.set_xlim(datetime.date(2000,7,1),datetime.date(2020,7,1))
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_title(str(codes_adp_0[i][1]),size=11)
    fig.set_size_inches(6,3)
    fig.subplots_adjust(bottom=0.25,left=0.12,right=0.95,top=0.90,wspace=0.39)
    ##Activate the next line to save the histograms
    #fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Histograms\Group1_v1\All_"+str(codes_adp_0[i][1])+".jpg")
    plt.close()

#Visually inspect the histograms to detect data anomalies (e.g. long period of constant values).
#One unusual measurement was observed in the gauge 2749013, over 150mm/day in between a drough period.
#First, the measurement was located in the time series.
station_list=rainfall_adp_0[codes_adp_0[1][1]]#The gauge with possible anomalies.
for j in range(len(station_list)):
    if station_list[j][1]>150:
        print(station_list[j][0],station_list[j][1])
#As observed, the measurement of 165 mm in 28-05-2009 is probably an anomaly, as it is a period of drought, with no
#flood records and no extreme rainfall in the surrounding stations. Replace this measurement by an interpolation of
#the rainfall measurements right before and after the event.
for j in range(len(station_list)):
    if station_list[j][1]>150:
        station_list[j][1]=(station_list[j-1][1]+station_list[j+1][1])/2
#Add the list back to the dictionary.
rainfall_adp_0[codes_adp_0[1][1]]=station_list

#Plot histograms again to check if the value was fixed.
for i in range(len(rainfall_adp_1)):
    font = {'size': 10}
    plt.rc('font', **font)
    fig,((ax1))=plt.subplots(1,1)
    rainfall_list=rainfall_adp_1[codes_adp_0[i][1]]
    x=[row[0] for row in rainfall_list]
    y=[row[1] for row in rainfall_list]
    ax1.plot(x, y, "b-",linewidth=0.5)
    ax1.set_xlabel("Date",fontsize=10)
    ax1.set_ylabel("Rainfall (mm/day)",fontsize=10)
    ax1.set_xlim(datetime.date(2000,7,1),datetime.date(2020,7,1))
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_title(str(codes_adp_0[i][1]),size=11)
    fig.set_size_inches(6,3)
    fig.subplots_adjust(bottom=0.25,left=0.12,right=0.95,top=0.90,wspace=0.39)
    ##Activate the next line to save the histograms
    #fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Histograms\Group1_v2\All_"+str(codes_adp_0[i][1])+".jpg")
    plt.close()

#Save the adopted station codes
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
#np.save('codes_group1.npy', codes_adp_0)

#Aggregate the adopted rain gauge time series in 3-daily measurements.
prec_gauge_3daily_1={}
for i in range(len(rainfall_adp_1)):
    station_list=rainfall_adp_1[codes_adp_0[i][1]]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_3daily=[]
    k=1
    for j in range(len(date_list)):
        if k==1:
            prec_append=[date_list[j]]
            prec=prec_list[j]
            k=k+1
        elif k==2:
            prec=prec+prec_list[j]
            k=k+1
        else:
            prec=prec+prec_list[j]
            prec_append.append(prec)
            prec_3daily.append(prec_append)
            k=1
    prec_gauge_3daily_1[codes_adp_0[i][1]]=prec_3daily

#Aggregate the adopted rain gauge time series in monthly measurements.
prec_gauge_monthly_1={}
for i in range(len(rainfall_adp_1)):
    station_list=rainfall_adp_1[codes_adp_0[i][1]]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_monthly=[]
    for j in range(len(date_list)):
        if j==0:
            prec=prec_list[j]
        elif date_list[j].month==date_list[j-1].month and j!=(len(date_list)-1):
            prec=prec+prec_list[j]
        elif j==(len(date_list)-1):
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
        else:
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
            prec=prec_list[j]
    prec_gauge_monthly_1[codes_adp_0[i][1]]=prec_monthly
           
#Export the daily, 3-daily and monthly rainfall as a .npy file, to be imported in further analyses.
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
#np.save('prec_gauge_daily_all.npy', rainfall_adp_1)
#np.save('prec_gauge_3daily_all.npy',prec_gauge_3daily_1)
#np.save('prec_gauge_monthly_all.npy', prec_gauge_monthly_1)

#Now, start the analysis of Group 2, the rain gauges for validation.
#Create a dictionary to store the codes adopted for each year.
codes_year={}
codes_all_yr=[]
codes_adp=[row[1] for row in codes_adp_0]

#Analyze data completeness per year from 2000 to 2019, from the pre-selected rain gauges rainfall_all_1.
for year in range(2001,2020):
    #Adopt gauges with no missing values in the year.
    codes_year_list=[]
    for i in rainfall_all_1.keys():
        if i not in codes_adp:
            station_list=rainfall_all_1[i]
            rainfall_list=[row[1] for row in station_list]
            quality="Yes"
            for j in range(len(rainfall_list)):
                if quality=="Yes" and station_list[j][0].year==year:
                    if math.isnan(rainfall_list[j])==True:
                        quality="No"
            if quality=="Yes":
                codes_year_list=codes_year_list+[i]
                if i not in codes_all_yr:
                    codes_all_yr.append(i)
    codes_year[year]=codes_year_list

#Analyze number of intersect per year
years_list=[]
for i in codes_year.keys():
    years_list=years_list+[i]

#Create all possible combinations
combination={}
for i in range(1,21):
    combination[i]=list(it.combinations(years_list,i))

#Calculate the number of common elements per group of years and export the statistics
years_stats=[]
gauge_stats=[]
for i in range(1,21):
    count_max=0
    iterate=combination[i]
    for j in iterate:
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

#Now, check all the kinds of combinations that give the same number of gauges (different spatial patterns of gauge)
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
        for k in gauge_stats: #Remove duplicates.
            if ([nryears]+lst)==k:
                adopt="No"
        if count==nrgauges and adopt=="Yes":
            lst_max=[nryears]+lst
            gauge_stats.append(lst_max)
            years_stats_1.append(j)

#Import the shapefile of the Itajai-Acu River Basin and extract the X and Y coordinates
basin = shp.Reader(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Thesis\Edit\Figures\Data\ItajaiAcu.shp")
for shape in basin.shapeRecords():
    basinx = [i[0] for i in shape.shape.points[:]]
    basiny = [i[1] for i in shape.shape.points[:]]

#Import the X and Y coordinates from the gauges
gauge_coord=[]
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\GaugeCoordinates.csv', newline='') as f:
    reader = csv.reader(f)
    coord_extend = list(reader)   
    gauge_coord.extend(coord_extend)
#Fix the first text
gauge_coord[0][0]=gauge_coord[0][0][3:]

#Import the central coordinates of the satellites
sat_coord=[]
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\InputData\SatCoordinates.csv', newline='') as f:
    reader = csv.reader(f)
    loc_extend = list(reader)   
    sat_coord.extend(loc_extend)

#Plot, for each number of years, the location of the gauges with common data.
for i in range(len(gauge_stats)):
    font = {'size': 10}
    plt.rc('font', **font)
    fig,((ax1))=plt.subplots(1,1)  
    plot_gauge=gauge_stats[i]
    title=plot_gauge[:1]
    data=plot_gauge[1:]
    gaugex=[]
    gaugey=[]
    for j in data:
        for k in range(len(gauge_coord)):
            if j==gauge_coord[k][0]:
                gaugex=gaugex+[int(gauge_coord[k][1])]
                gaugey=gaugey+[int(gauge_coord[k][2])]
    gaugeadpx=[]
    gaugeadpy=[]
    for j in codes_adp:
        for k in range(len(gauge_coord)):
            if j==gauge_coord[k][0]:
                gaugeadpx=gaugeadpx+[int(gauge_coord[k][1])]
                gaugeadpy=gaugeadpy+[int(gauge_coord[k][2])]
    #Calculate the average and maximum distance from the satellite pixel centers to the nearest gauge
    disavg=0
    dismax=0
    for j in range(len(sat_coord)):
        disfinal=10000000000
        for k in range(len(gaugex)):
            dist=((((int(sat_coord[j][1])-gaugex[k])**2)+((int(sat_coord[j][2])-gaugey[k])**2))**0.5)
            if dist<disfinal:
                disfinal=dist
        disavg=disavg+disfinal
        if disfinal>dismax:
            dismax=disfinal
    disavg=disavg/len(sat_coord)
    fig.text(0.05, 0.95,"Average distance: "+str(disavg)+"m\nMaximum distance: "+str(dismax)+"m",fontsize=8)
    #ax1.scatter(gaugeadpx, gaugeadpy,color="red",s=15,marker="s",label="Group 1 gauges",zorder=1)
    ax1.scatter(gaugex, gaugey,color="blue",s=15,label="Rain gauges",zorder=2)    
    ax1.plot(basinx, basiny, "k--",linewidth=1,label="Study area")
    ax1.set_xlabel("Coordinate X",fontsize=10)
    ax1.set_ylabel("Coordinate Y",fontsize=10)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_title(str(title[0])+" years",size=11)
    fig.set_size_inches(4,4)
    fig.legend(loc="lower center", fontsize=10,ncol=3,columnspacing=1,handletextpad=0.03,frameon=False)
    fig.subplots_adjust(bottom=0.2,left=0.14,right=0.95,top=0.85,wspace=0.39)
    #fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Maps\Year"+str(title[0])+"Combination"+str(i)+".jpg")
    plt.close()

#Selected configuration was i==5 for gauge_stats e years_stats_1.
gauges2_adp=gauge_stats[5][1:]
year2_adp=years_stats_1[5]

#Create a new dictionary for daily rainfall in Group 2.
prec_gauge_daily_yr={}
for i in rainfall_all_1.keys():
    if i in gauges2_adp:
        prec_gauge_daily_yr[i]=rainfall_all_1[i]
   
#Aggregate to 3-daily measurements.
prec_gauge_3daily_yr={}
for i in prec_gauge_3daily.keys():
    if i in gauges2_adp:
        prec_gauge_3daily_yr[i]=prec_gauge_3daily[i]

#Aggregate to monthly measurements.
prec_gauge_monthly_yr={}
for i in prec_gauge_monthly.keys():
    if i in gauges2_adp:
        prec_gauge_monthly_yr[i]=prec_gauge_monthly[i]

#Create histograms for Group 2.
for year in year2_adp:
    for i in gauges2_adp:
        font = {'size': 10}
        plt.rc('font', **font)
        fig,((ax1))=plt.subplots(1,1)
        rainfall_list=prec_gauge_daily_yr[i]
        x=[row[0] for row in rainfall_list]
        y=[row[1] for row in rainfall_list]    
        ax1.plot(x, y, "b-",linewidth=0.5)
        ax1.set_xlabel("Date",fontsize=10)
        ax1.set_ylabel("Rainfall (mm/day)",fontsize=10)
        ax1.set_xlim(datetime.date(year,1,1),datetime.date(year+1,1,1))
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.set_title(i,size=11)
        fig.set_size_inches(6,3)
        fig.subplots_adjust(bottom=0.25,left=0.12,right=0.95,top=0.90,wspace=0.39)
        #fig.savefig(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Histograms\Group2_v1\Year"+str(year)+'_'+str(i)+".jpg")
        plt.close()

#Plot number of gauges vs. number years
font = {'size': 10,'family':'Calibri'}
plt.rc('font', **font)
fig,ax1=plt.subplots(1,1)
x=[row[0] for row in years_stats]
y=[row[1] for row in years_stats]
plt.scatter(x,y,s=12,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),facecolors='white',zorder=2)
ax1.plot(x,y,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),lw=1.5,zorder=1)
plt.scatter(5,12,s=18,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),zorder=3,label='Selected combination')
ax1.tick_params(axis='both', which='major', labelsize=8)
ax1.set_xlabel("Number of years in common with measurements",fontsize=10)
ax1.set_ylabel("Number of rain gauges",fontsize=10)
ax1.set_xlim(0,21)
ax1.set_xticks(np.arange(1, 21, 1))
ax1.yaxis.set_major_locator(MultipleLocator(5))
fig.set_size_inches(4,2.3)
fig.subplots_adjust(bottom=0.29,left=0.11,right=0.97,top=0.96,wspace=0.6,hspace=0.4)
fig.legend(loc="lower center", fontsize=8,frameon=False)
fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\Maps\Stats.jpg',dpi=500)
plt.close()


#Export the Group 2 rainfall measurements.
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DQA\OutputData")
#np.save('codes_group2.npy', gauges2_adp)
#np.save('codes_years2.npy', year2_adp)
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
#np.save('prec_gauge_daily_yr.npy', prec_gauge_daily_yr)
#np.save('prec_gauge_3daily_yr.npy', prec_gauge_3daily_yr)
#np.save('prec_gauge_monthly_yr.npy', prec_gauge_monthly_yr)
