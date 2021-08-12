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

#Open the daily rainfall files from group 1 of gauges.
gauge_daily=np.load("prec_gauge_daily_all.npy",allow_pickle=True).item()

#Import the adopted gauge codes from group 2.
codes_g1=np.load("codes_group1.npy",allow_pickle=True).tolist()
codes_g1=[row[1] for row in codes_g1]
codes_g2=np.load("codes_group2.npy",allow_pickle=True).tolist()

#Import the coordinates X and Y from groups 1 and 2 of rain gauges.
coord=[]
with open('GaugeCoordinates.csv', newline='') as f:
    reader = csv.reader(f)
    coord_extend = list(reader)   
    coord.extend(coord_extend)
#Fix the first text
coord[0][0]=coord[0][0][3:]

#Use KDE interpolator to calculate daily rainfall in the location of group 2 gauges from
#measurements of group 1 gauges.
#Add X and Y coordinates do codes_g2 and codes_g1 lists
for i in range(len(codes_g1)):
    for j in range(len(coord)):
        if codes_g1[i]==coord[j][0]:
            codes_g1[i]=coord[j]
for i in range(len(codes_g2)):
    for j in range(len(coord)):
        if codes_g2[i]==coord[j][0]:
            codes_g2[i]=coord[j]

#Create a dictionary to store daily values.
prec_gaugeIDW_daily={}
#Iterate over the list codes_g2.
for i in range(len(codes_g2)):
    rainfall_list=[]
    date=[row[0] for row in gauge_daily['Rainfall_02649002']]
    for j in range(len(gauge_daily['Rainfall_02649002'])):
        vidi=0
        onedi=0
        for k in range(len(codes_g1)):
            source_rainfall=gauge_daily[codes_g1[k][0]]
            di=((((codes_g2[i][1]-codes_g1[k][1])**2)+((codes_g2[i][2]-codes_g1[k][2])**2))**0.5)
            vidi=vidi+(source_rainfall[j][1]/di)
            onedi=onedi+(1/di)
        v0=vidi/onedi
        rainfall_list.append([date[j],v0])
    prec_gaugeIDW_daily[codes_g2[i][0]]=rainfall_list

#Aggregate the daily estimates into 3-daily and monthly estimates.
prec_gaugeIDW_3daily={}
for i in prec_gaugeIDW_daily.keys():
        prec_daily=prec_gaugeIDW_daily[i]
        prec_3daily=[]
        k=1
        for j in range(len(prec_daily)):
            if k==1:
                prec_append=[prec_daily[j][0]]
                prec=prec_daily[j][1]
                k=k+1
            elif k==2:
                prec=prec+prec_daily[j][1]
                k=k+1
            else:
                prec=prec+prec_daily[j][1]
                prec_append.append(prec)
                prec_3daily.append(prec_append)
                k=1
        prec_gaugeIDW_3daily[i]=prec_3daily

prec_gaugeIDW_monthly={}
for i in prec_gaugeIDW_daily.keys():
        prec_daily=prec_gaugeIDW_daily[i]
        prec_monthly=[]
        for j in range(len(prec_daily)):
            if j==0:
                prec=prec_daily[j][1]
            elif prec_daily[j][0].month==prec_daily[j-1][0].month and j!=len(prec_daily)-1:
                prec=prec+prec_daily[j][1]
            elif j==len(prec_daily)-1:
                date=datetime.date(int(prec_daily[j][0].year),int(prec_daily[j][0].month),1)
                prec_append=[date,prec]
                prec_monthly.append(prec_append)           
            else:
                date=datetime.date(int(prec_daily[j-1][0].year),int(prec_daily[j-1][0].month),1)
                prec_append=[date,prec]
                prec_monthly.append(prec_append)
                prec=prec_daily[j][1]
        prec_gaugeIDW_monthly[i]=prec_monthly

#Save the estimated rainfall as .npy files.
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\OutputData")
#np.save('prec_gaugeIDW_daily.npy', prec_gaugeIDW_daily)
#np.save('prec_gaugeIDW_3daily.npy', prec_gaugeIDW_3daily)
#np.save('prec_gaugeIDW_monthly.npy', prec_gaugeIDW_monthly)
