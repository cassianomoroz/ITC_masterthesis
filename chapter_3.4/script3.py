import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime
from osgeo import gdal, gdal_array
from PIL import Image

#Set directory where the input files
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")

#Open the rainfall files for all products (GSMaP, IMERG and gauge)
GSMaP_monthly=np.load("prec_GSMaP_monthly.npy",allow_pickle=True).item()
GSMaP_3daily=np.load("prec_GSMaP_3daily.npy",allow_pickle=True).item()
GSMaP_daily=np.load("prec_GSMaP_daily.npy",allow_pickle=True).item()
IMERG_monthly=np.load("prec_IMERG_monthly.npy",allow_pickle=True).item()
IMERG_3daily=np.load("prec_IMERG_3daily.npy",allow_pickle=True).item()
IMERG_daily=np.load("prec_IMERG_daily.npy",allow_pickle=True).item()
gauge_daily=np.load("prec_gauge_daily_all.npy",allow_pickle=True).item()
gauge_3daily=np.load("prec_gauge_3daily_all.npy",allow_pickle=True).item()
gauge_monthly=np.load("prec_gauge_monthly_all.npy",allow_pickle=True).item()

#Import the target locations (pixel centers) for IMERG and GSMaP
targetloc=[]
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SGMerged\Input\Targetloc.csv', newline='') as f:
    reader = csv.reader(f)
    loc_extend = list(reader)   
    targetloc.extend(loc_extend)
#Fix the first text
targetloc[0][0]=targetloc[0][0][3:]

#Import the coordinates from gauge centers
gauge_coord=[]
with open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\GaugeCoordinates.csv', newline='') as f:
    reader = csv.reader(f)
    coord_extend = list(reader)   
    gauge_coord.extend(coord_extend)
#Fix the first text
gauge_coord[0][0]=gauge_coord[0][0][3:]

#Import the adopted codes from Group 1
codes1=np.load("codes_adp.npy",allow_pickle=True).tolist()
codes1=[row[1] for row in codes1]
#Import the adopted codes from Group 2
codes2=np.load(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\GaugeIDW\InputData\codes_group2.npy",allow_pickle=True).tolist()

#Add X and Y coordinates do the codes_adp list:
for i in range(len(codes1)):
    for j in range(len(gauge_coord)):
        if codes1[i]==gauge_coord[j][0]:
            codes1[i]=gauge_coord[j]
            
#Create a function for the mean bias correction merging technique
def merge(sat_daily,sat_interval,gauge_daily,gauge_interval,targetloc,codes1,codes2,datelabel,satlabel):

    #Extract the stations from Group 1 to be adopted to calibrate satellite products
    codes_adp=[row[0] for row in codes1]

    #Calculate the multiplicative and differential correction factors and save the values.
    cor_factor_MBC=[] #list to store MBC correction factors
    cor_factor_RIDW=[] #list to store RIDW correction factors
    sat=sat_interval['Rainfall_02649002'] #for first interaction
    #The correction factors for both cases
    for i in range(len(sat)):
        cor_RIDW_append=[sat[i][0]]
        mean_sat=0
        mean_gauge=0
        for j in sat_interval.keys():
            if j in codes_adp:
                sat=sat_interval[j]    
                gauge=gauge_interval[j]
                mean_sat=mean_sat+sat[i][1]
                mean_gauge=mean_gauge+gauge[i][1]
                dif=gauge[i][1]-sat[i][1]
                cor_RIDW_append.append(dif)
        cor_factor_RIDW.append(cor_RIDW_append)
        if mean_sat<1: ##Adopting a mean satellite estimate equals or higher than 1 to avoid extreme corrections factors (e.g. divided by 0.0001 in satellites).
            cor=1
        else:
            cor=mean_gauge/mean_sat
        cor_append_MBC=[sat[i][0],cor]
        cor_factor_MBC.append(cor_append_MBC)

    #Store the cor factor values from MBC for the boxplot
    boxplot=[row[1] for row in cor_factor_MBC]

    #Interpolate the RIDW correction factors to the target locations (pixel centers - different for GSMaP and IMERG products)
    #Create a dictionary to store the interpolated differences
    diff={}
    #Iterate over the list targetloc, containing the location of the pixel centers
    for i in range(len(targetloc)):
        if targetloc[i][0] in codes2:
            rainfall_list=[]
            for j in cor_factor_RIDW:
                vidi=0
                onedi=0
                for k in range(len(j)-1):
                    source_rainfall=j[k+1]
                    di=((((int(targetloc[i][1])-int(codes1[k][1]))**2)+((int(targetloc[i][2])-int(codes1[k][2]))**2))**0.5)
                    vidi=vidi+(source_rainfall/di)
                    onedi=onedi+(1/di)
                v0=vidi/onedi
                rainfall_list.append([j[0],v0])
            diff[targetloc[i][0]]=rainfall_list
    
    #Apply the correction factors to the daily satellite estimates.
    #Create a date_list countaining all the days from 01-07-2000 to 01-07-2020
    date_list=[]
    for day in range(0,7305): #Increase days 1 by 1 until the present date
        date = (datetime.date(2000,7,1) + datetime.timedelta(days=day))
        date_list.append(date)

    #Calculate the daily correction factors for MBC
    cor_factor_daily_MBC=[]
    for i in range(len(date_list)):
        for j in range(len(cor_factor_MBC)):
            if datelabel=="3daily":
                if j==len(cor_factor_MBC)-1:
                    if date_list[i]>=cor_factor_MBC[j][0]:
                        cor_append=[date_list[i],cor_factor_MBC[j][1]]
                        cor_factor_daily_MBC.append(cor_append)
                else:
                    if cor_factor_MBC[j][0]<=date_list[i]<cor_factor_MBC[j+1][0]:
                        cor_append=[date_list[i],cor_factor_MBC[j][1]]
                        cor_factor_daily_MBC.append(cor_append)
            elif datelabel=="monthly":
                if (date_list[i].month==cor_factor_MBC[j][0].month) and (date_list[i].year==cor_factor_MBC[j][0].year):
                    cor_append=[date_list[i],cor_factor_MBC[j][1]]
                    cor_factor_daily_MBC.append(cor_append)

    #Calculate the daily correction factors for RIDW
    cor_factor_daily_RIDW={}
    for i in diff.keys():
        rain_daily=sat_daily[i]
        rain_interval=sat_interval[i]
        diff_px=diff[i]
        cor_daily_RIDW=[]
        for j in range(len(date_list)):
            for k in range(len(diff_px)):
                if datelabel=="3daily":                    
                    if k==len(diff_px)-1:
                        if date_list[j]>=diff_px[k][0]:
                            if rain_interval[k][1]==0:
                                cor=0
                            else:
                                cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1])
                            cor_append=[date_list[j],cor]
                            cor_daily_RIDW.append(cor_append)
                    else:
                        if diff_px[k][0]<=date_list[j]<diff_px[k+1][0]:
                            if rain_interval[k][1]==0:
                                cor=0
                            else:
                                cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1])
                            cor_append=[date_list[j],cor]
                            cor_daily_RIDW.append(cor_append)
                elif datelabel=="monthly":                    
                    if (date_list[j].month==diff_px[k][0].month) and (date_list[j].year==diff_px[k][0].year):
                        if rain_interval[k][1]==0:
                            cor=0
                        else:
                            cor=diff_px[k][1]*(rain_daily[j][1]/rain_interval[k][1])
                        cor_append=[date_list[j],cor]
                        cor_daily_RIDW.append(cor_append)
        cor_factor_daily_RIDW[i]=cor_daily_RIDW

    #Apply the correction factor of MBC and RIDW to the daily satellite estimates
    prec_sat_daily_MBC={}
    prec_sat_daily_RIDW={}
    for i in sat_daily.keys():
        if i in codes2:
            cor_daily_RIDW=cor_factor_daily_RIDW[i]
            sat=sat_daily[i]
            sat_list_MBC=[]
            sat_list_RIDW=[]            
            for j in range(len(sat)):
                sat_prec_MBC=sat[j][1]*cor_factor_daily_MBC[j][1]
                sat_prec_RIDW=sat[j][1]+cor_daily_RIDW[j][1]
                if sat_prec_RIDW<0:#Cannot have negative values. In case of negatives, assume 0.
                    sat_prec_RIDW=0
                sat_append_MBC=[sat[j][0],sat_prec_MBC]
                sat_append_RIDW=[sat[j][0],sat_prec_RIDW]
                sat_list_MBC.append(sat_append_MBC)
                sat_list_RIDW.append(sat_append_RIDW)
            prec_sat_daily_MBC[i]=sat_list_MBC
            prec_sat_daily_RIDW[i]=sat_list_RIDW

    #Aggregate the daily estimates into 3-daily and monthly estimates.
    prec_sat_3daily_MBC={}
    prec_sat_3daily_RIDW={}
    for i in prec_sat_daily_MBC.keys():
        sat_MBC=prec_sat_daily_MBC[i]
        sat_RIDW=prec_sat_daily_RIDW[i]
        prec_3daily_MBC=[]
        prec_3daily_RIDW=[]
        k=1
        for j in range(len(sat_MBC)):
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
        prec_sat_3daily_MBC[i]=prec_3daily_MBC
        prec_sat_3daily_RIDW[i]=prec_3daily_RIDW

    #Aggregate into monthly
    prec_sat_monthly_MBC={}
    prec_sat_monthly_RIDW={}
    for i in prec_sat_daily_MBC.keys():
        sat_MBC=prec_sat_daily_MBC[i]
        sat_RIDW=prec_sat_daily_RIDW[i]
        prec_monthly_MBC=[]
        prec_monthly_RIDW=[]
        for j in range(len(sat_MBC)):
            if j==0:
                prec_MBC=sat_MBC[j][1]
                prec_RIDW=sat_RIDW[j][1]
            elif sat_MBC[j][0].month==sat_MBC[j-1][0].month and j!=len(sat_MBC)-1:
                prec_MBC=prec_MBC+sat_MBC[j][1]
                prec_RIDW=prec_RIDW+sat_RIDW[j][1]
            elif j==len(sat_MBC)-1:
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

    #Save the corrected satellite estimates (v1).
    #os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SGMerged\Output")
    #np.save("prec_"+satlabel+"_daily_MBC"+datelabel+".npy", prec_sat_daily_MBC)
    #np.save("prec_"+satlabel+"_3daily_MBC"+datelabel+".npy", prec_sat_3daily_MBC)
    #np.save("prec_"+satlabel+"_monthly_MBC"+datelabel+".npy", prec_sat_monthly_MBC)
    #np.save("prec_"+satlabel+"_daily_RIDW"+datelabel+".npy", prec_sat_daily_RIDW)
    #np.save("prec_"+satlabel+"_3daily_RIDW"+datelabel+".npy", prec_sat_3daily_RIDW)
    #np.save("prec_"+satlabel+"_monthly_RIDW"+datelabel+".npy", prec_sat_monthly_RIDW)
             
    #ENABLE THE NEXT LINES OF THE SCRIPT TO APPLY THE MERGING TECHNIQUE TO .TIF FILES.
    #If the validation presented better results than the results demonstrated before, apply these
    #correction factors to each hourly rainfall map.
    #Import the names of the files in the directory
    directory=r'C:\Users\cassi\Desktop\Personal\Applications\PhD\Potsdam\Interview\Data\GSMaP'#Path with the satellite data to be corrected
    sat_maps_names=[] #Create a list to store the codes of the stations and associate these codes with the dictionary
    for entry in os.scandir(directory):
        sat_maps_names.append(entry.name)

    #Create a list with the dates related to each rainfall maps.
    sat_maps_dates=[]
    for i in sat_maps_names:
        date=datetime.date(int(i[:4]),int(i[4:6]),int(i[6:8]))
        sat_maps_dates.append(date)

    #Import each tiff file as a np.array into a np.dictionary
    os.chdir(r'C:\Users\cassi\Desktop\Personal\Applications\PhD\Potsdam\Interview\Data\GSMaP')
    for i in range(len(sat_maps_names)):
        rainfall_map_tif=gdal.Open(sat_maps_names[i])
        proj=rainfall_map_tif.GetProjection()
        geotr=rainfall_map_tif.GetGeoTransform()
        cols=rainfall_map_tif.RasterXSize
        rows=rainfall_map_tif.RasterYSize
        driver=gdal.GetDriverByName("GTiff")
        rainfall_map_array=np.array(rainfall_map_tif.GetRasterBand(1).ReadAsArray())
        for j in range(len(cor_factor_daily_MBC)):
            if cor_factor_daily_MBC[j][0]==sat_maps_dates[i]:
                factor=cor_factor_daily_MBC[j][1]
        rainfall_map_array_v1=rainfall_map_array*factor
        rainfall_map_tif_v1=driver.Create(r"C:\Users\cassi\Desktop\Personal\Applications\PhD\Potsdam\Interview\Data\GSMaP_MBC\_"+sat_maps_names[i],cols,rows,1,gdal.GDT_Float32)
        rainfall_map_tif_v1.GetRasterBand(1).WriteArray(rainfall_map_array_v1)    
        rainfall_map_tif_v1.SetGeoTransform(geotr)
        rainfall_map_tif_v1.SetProjection(proj)

#Run the function to create output data and graphs for the merging techniques
#merge(GSMaP_daily,GSMaP_monthly,gauge_daily,gauge_monthly,targetloc,codes1,codes2,"monthly","GSMaP")
merge(GSMaP_daily,GSMaP_3daily,gauge_daily,gauge_3daily,targetloc,codes1,codes2,"3daily","GSMaP")
#merge(IMERG_daily,IMERG_monthly,gauge_daily,gauge_monthly,targetloc,codes1,codes2,"monthly","IMERG")
#merge(IMERG_daily,IMERG_3daily,gauge_daily,gauge_3daily,targetloc,codes1,codes2,"3daily","IMERG")

#Plot the boxplot for the correction factors
#font = {'size': 10}
#plt.rc('font', **font)
#fig,(ax1,ax2)=plt.subplots(1,2)
#boxprops=dict(linewidth=1, color='black')
#flierprops=dict(markersize=4,markeredgewidth=0.5)
#medianprops=dict(linewidth=1.2, color='blue')
#ax1.boxplot(boxplot,flierprops=flierprops,medianprops=medianprops,boxprops=boxprops)
#ax2.boxplot(boxplot,showfliers=False,medianprops=medianprops,boxprops=boxprops)
#ax1.tick_params(axis='both', which='major', labelsize=8)
#ax1.set_xlabel("Rainfall products",fontsize=10)
#ax1.set_ylabel("Bias correction factor",fontsize=10)
#ax2.tick_params(axis='both', which='major', labelsize=8)
#ax2.set_xlabel("Rainfall products",fontsize=10)
#ax2.set_ylabel("Bias correction factor",fontsize=10)
#ax1.set_yscale('log')
#ax2.set_ylim(0,5)
#ax1.set_xticklabels(['GSMaP\n3-daily','GSMaP\nmonthly','IMERG\n3-daily','IMERG\nmonthly'])
#ax2.set_xticklabels(['GSMaP\n3-daily','GSMaP\nmonthly','IMERG\n3-daily','IMERG\nmonthly'])
#fig.set_size_inches(6,2.5)
#fig.subplots_adjust(bottom=0.21,left=0.10,right=0.97,top=0.96,wspace=0.24,hspace=0.43)
#fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SGMerged\Graphs\MBC_Boxplot.jpg')
#plt.close()
