#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to extract the extreme values from the Google Earth Engine time series of the GSMaP product, and to use the extreme values to
#generate spatially distributed design storms from intensity-duration-frequency curves.

import csv
import os
import math
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import copy
from osgeo import gdal
import seaborn as sns
import ee
import datetime
from osgeo import osr
import time

#Inititalize the Google Earth Engine API.
ee.Initialize()

#Create a rectangle over the Itajai-Acu river basin.
rec = ee.Geometry.Rectangle([-50.5, -28, -48.5, -26])

#Iterate over the hydrological years, from July 2000 to July 2020.
for year in range(2000,2020):
    
    #Iterate over the durations, from 1 to 24.
    for hour in [1,2,3,4,5,6,7,8,12,14,20,24]:
        
        #Import the image collection of GSMaP, for the first period in the entire time series.
        if hour in [1,2,3,4,5,6,7,8]:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-01T0'+str(hour)+':00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        elif hour==24:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-02T00:00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        else:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-01T'+str(hour)+':00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        rainfall=collection.reduce(ee.Reducer.mean()) #Apply reducer to calculate the mean of all hourly measurements
        #in the period (or the rainfall in mm/h).
        latlon = ee.Image.pixelLonLat().addBands(rainfall) #Extract latlon of the image.
        latlon = latlon.reduceRegion(reducer=ee.Reducer.toList(),geometry=rec,maxPixels=1e8,scale=10609) #Apply reducer to clip the image
        #to the boundaries of the rectangle (over the Itajai-Acu river basin).
        data = np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean")).getInfo())) #Get rainfall data.
        lats = np.array((ee.Array(latlon.get("latitude")).getInfo())) #Get latitude data.
        lons = np.array((ee.Array(latlon.get("longitude")).getInfo())) #Get longitude data.
        #Get the unique coordinates
        uniqueLats = np.unique(lats)
        uniqueLons = np.unique(lons)
        #Get the number of rows and columns in he image.
        ncols = len(uniqueLons) #Number of columns.
        nrows = len(uniqueLats) #Number of rows.
        #Determine the pixel sizes.
        ys = uniqueLats[1] - uniqueLats[0] #In the Y axis.
        xs = uniqueLons[1] - uniqueLons[0] #In the X axis.
        #Create the numpy array with the same dimensions as the original satellite image.
        ref_arr = np.zeros([nrows, ncols], np.float32) #Create a reference array.
        arr = np.zeros([nrows, ncols], np.float32) #Create an array for analysis.
        #Fill the array with the rainfall values.
        counter=0
        for y in range(0,len(arr),1): #Iterate over the array (y-axis).
            for x in range(0,len(arr[0]),1): #Iterate over the array (x-axis).
                if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats)-1: #If positions match.
                    counter+=1 #Update counter.
                    arr[len(uniqueLats)-1-y,x] = data[counter] #Add the data values to the array (arr).
        #Set transform.
        transform = (np.min(uniqueLons),xs,0,np.max(uniqueLats),0,-ys)
        #Set the coordinate system.
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326) #The coordinate system in the region.
        #Set driver.
        driver = gdal.GetDriverByName('GTiff')
        
        #In the second part, iterate over the entire time series to get the series of annual maxima.
        #The iterators over the hydrological years and duration were already presented before.
        #Now, we will iterate over the time series in a single hydrological year.
        start_date_dt=datetime.date(year,7,1) #Start date as the 1st July of the analyzed year.
        start_hour=0 #Start hour as 0.
        while ((start_date_dt < datetime.date(year+1,7,1))==True): #While start data is still part of the hydrological year.
            end_hour=start_hour+hour #End hour equals to start date plus the analyzed duration.
            start_year=str(start_date_dt.year) #Get year of start date.
            start_month=str(start_date_dt.month) #Get month of start date.
            start_day=str(start_date_dt.day) #Get day of start date.
            if end_hour>23: #If the end hour is higher than 23, the end day will be the following day.
                end_hour=end_hour-24 #Subtract 24 hours from the end hour (or 1 day).
                end_date=(start_date_dt+datetime.timedelta(days=1)) #Update the end date by summing one day.
                end_year=str(end_date.year) #Get year of end date.
                end_month=str(end_date.month) #Get month of end date.
                end_day=str(end_date.day) #Get day of end date.
            else: #If the end hour is equals or lower than 23.
                end_year=str(start_date_dt.year) #Get year of end date.
                end_month=str(start_date_dt.month) #Get month of end date.
                end_day=str(start_date_dt.day) #Get day of end date.

            #Define the start and end dates for the collection, following the data format of GEE.
            start_date = start_year+'-'+start_month+'-'+start_day+'T'+str(start_hour)+':00:00' #Define start date.
            end_date = end_year+'-'+end_month+'-'+end_day+'T'+str(end_hour)+':00:00' #Define end date.

            #Import the image collection.
            #Filter the collection by selecting the start and end date of the adopted duration (from 1 to 24 hours).
            if (start_date_dt.year<2014) or (start_date_dt.year==2014 and start_date_dt.month<3): #In this case, use GSMaP reanalysis (before March 2014).
                collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis").filterDate(start_date,end_date).filterBounds(rec).select('hourlyPrecipRateGC')
            else: #In this case, use GSMaP operational (after March 2014).
                collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(start_date,end_date).filterBounds(rec).select('hourlyPrecipRateGC')
            rainfall=collection.reduce(ee.Reducer.mean()) #Apply the reducer to extract the mean value among the hours
            #of the analyzed duration (or rainfall intensity in mm/h).
            latlon = ee.Image.pixelLonLat().addBands(rainfall) #Get lat and lon.
            latlon = latlon.reduceRegion(reducer=ee.Reducer.toList(),geometry=rec,maxPixels=1e8,scale=10609) #Apply the
            #reducer to clip the image to the limits of the Itajai-Acu river basin.
        
            #Convert the image to a numpy array.
            data=np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean"),ee.PixelType.float()).getInfo()))
            if data.size>0: #If array is not null.
                data=np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean")).getInfo()))
                prov_arr=ref_arr #Create a prov array copying the reference array created before.
                #Fill the provisory array with the rainfall data.
                counter=0
                for y in range(0,len(prov_arr),1): #Iterate over the provisory array (y-axis).
                    for x in range(0,len(prov_arr[0]),1): #Iterate over the provisory array (x-axis).
                        if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats)-1: #If positions match.
                            counter+=1 #Update counter.
                            prov_arr[len(uniqueLats)-1-y,x] = data[counter] #Fill the provisory array with the rainfall data.
                #Update the array (arr) with the maximum value between the provisory array (prov_arr) and the array (arr).
                #With this step, we will be always selecting the maximum throughout the entire time series.
                arr=np.maximum(prov_arr,arr)    
            #Iterate the start hour, sum 1 hours to the next image
            start_hour=start_hour+1
            if start_hour==24:
                start_hour=0
                start_date_dt=(start_date_dt+datetime.timedelta(days=1))

        #After iterating over the entire hydrological year, save the generated image as a .tif file.
        #This file represents the extreme value for a specific year and duration, according to the step along the iteration.
        #This images represents all pixels of the satellite product. Therefore, each pixel contains a different extreme value.
        outputDataset=driver.Create(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP_maps\EV_"+str(year)+"_"+str(hour)+"h.tif", ncols,nrows, 1,gdal.GDT_Float32)
        outputDataset.SetGeoTransform(transform) #Set transform.
        outputDataset.SetProjection(target.ExportToWkt()) #Set projection.
        outputDataset.GetRasterBand(1).WriteArray(arr) #Write image according to array (arr).
        outputDataset.GetRasterBand(1).SetNoDataValue(-9999) #Set no data value.
        outputDataset = None #Reset the output dataset.

#After extracting the series of extreme values, start the generation of intensity-duration-frequency (IDF) curves and design storms.
#IMPORTANT: Before performing this step, the series of extreme values of extracted in ArcGIS through the sample tool.
#All 20 maps refering to 20 hydrological years of the same analyzed duration were sampled to generate a series of extreme values
#at the location of each pixel over the study area.

#To start the analysis, import the names of the .csv files containing the output of the Sample tool in ArcGIS.
#The columns of the map represent the pixels, and the rows represent the series of extreme values.
input_names=[] #Create a list to store the names of the files.
directory=r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP' #Set directory.
for entry in os.scandir(directory): #Iterate over the directory.
    input_names.append(entry.name) #Add the names do the list.

#Create a function ds to create design storms.
def ds(input_names):
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP") #Set directory.
    #Create dictionaries to store all intermediary results throughout the analysis.
    EV={} #Extreme values.
    LR={} #Statistical parameters of the linea regression (coefficient, intercept, R2).
    RP={} #Estimated rainfall per return period (2, 5, 10, and 25 years).
    IDF={} #IDF curves (intensity vs. duration) per return period (2, 5, 10, 25 years).
    boxplot=[] #List to store the R2 values of the Gumbel distribution to be plotted as a boxplot.

    #Calculate the Gumbel reduced variate for the time series of extreme values.
    import math
    EV_gumbel=[] #List to store the probabilities for extreme values.
    for i in range(1,21): #Iterate over 20 years.
        pl=i/(21) #Calculate probability left.
        gumbel=-math.log(-math.log(pl)) #Calculate Gumbel reduced variate.
        EV_gumbel.extend([gumbel]) #Add the reduced variate to the list EV_gumbel.
    
    #Calculte the Gumbel reduced variate for the return periods of 2, 5, 10 and 25 years.
    import math
    RP_=[2,5,10,25] #List of return periods.
    RP_gumbel=[] #List to store the probabilities for each return period.
    for i in RP_: #Iterate over return periods.
        pr=1/i #Calculate probability right.
        pl=1-pr #Calculate probabilty left.
        gumbel=-math.log(-math.log(pl)) #Calculate Gumbel reduced variate.
        RP_gumbel.extend([gumbel]) #Add the reduced variate to the list RP_gumbel.

    for name in input_names: #Iterate over series of extreme values, per duration. Each "name" variable refers to a .cvs file for a different rainfall duration.
        EV_hour={} #Extreme values for a specific duration.
        LR_hour={} #Statistical parameters for a specific duration.
        RP_hour={} #Rainfall intensities per return period for a specific duration.
        EV_all=[] #Create a list to store the data of the extreme value .csv file.
        boxplot_px=[] #List to store the R2 values for a specific pixel.
        
        #Open the extreme value .csv file.
        with open(name, newline='') as f:
            reader = csv.reader(f)
            EV_extend = list(reader)     
            EV_all.extend(EV_extend) #Fill the list EV_all.
            r2max=0 #Start R2 maximum as the minimum value 0. So it can be updated by higher values.
            r2min=1 #Start R2 minumum as the maximum value 1. So it can be updated by lower values.
            
            #Iterate over each pixel of the map. Perform the extreme value statistics for each pixel.
            for i in range(len(EV_all[0])): #Iterate over each column (pixel) of the extreme value file.
                EV_px_0=[row[i] for row in EV_all] #Get the row correponding to each column. This refers to the series of annual maxima.
                EV_px_1=[] #Create a list to store the series of annual maxima for a specific pixel.
                EV_px=[] #Create a list to store the series of annual maxima for all pixels.
                rainfall_RP=[] #Create a list to store results of estimated rainfall per return period.
                
                for j in range(len(EV_px_0)): #Iterate over each value of the series of annual maxima.
                    if j!=0: #For all values higher than the position 0.
                        EV_px_1.extend([float(EV_px_0[j])]) #Add the corresponding rainfall intensity to the list EV_px_1, converted to float.
                    else: #For the first value in the position 0, which refers to the pixel ID.
                        if EV_px_0[j]=='??????0': #Pixel 0.
                            EV_code=int(0) #Adopt 0.
                        else: #Other pixels.
                            EV_code=int(EV_px_0[j]) #Adopt int of the pixel ID (from 0 to 194, total of 195 pixels).
                
                #Sort the series of annual maxima in ascending order.
                EV_px_1.sort()
                #Append EV_px_1 to EV_px to generate a graph with all Gumbel curves.
                EV_px.append(EV_px_1)                    
                #Add the values (rainfall and Gumbel) to the dictionary EV_hour for the duration i.
                EV_hour[i]=EV_px
                
                #Fit a linear regression. EV_px_1 is rainfall intensity (x) and EV_gumbel is Gumbel reduced variate (y).
                #Create a linear regression object.
                regr = linear_model.LinearRegression()
                #Convert the lists to arrays.
                x=np.array(EV_gumbel).reshape((-1,1)) #Gumbel reduced variate as y.
                y=np.array(EV_px_1) #Rainfall intensity as x.
                #Train the model using the sets.
                regr.fit(x,y)
                #Predict the gumbel values from the rainfall.
                y_pred=regr.predict(x) #y_pred refers to the predicted annual maxima, in contradiction with the observed (EV_px_1).
                #Calculate the regression parameters per pixel: coefficient, intercept, R2 score.
                coef=[regr.coef_[0]] #Coefficient.
                itcp=[regr.intercept_] #Intercept.
                r2=[r2_score(y,y_pred)] #R2.
                if r2[0]>r2max: #Check if the calculated R2 is higher than the previous R2 maximum.
                    r2max=r2[0] #If higher, update r2max.
                    ymax=y #Updated ymax.
                    y_predmax=y_pred #Update y predicted max.
                    xmax=x #Update xmax.
                if r2[0]<r2min: #Check if the calculated R2 is lower than the previous R2 minimum.
                    r2min=r2[0] #If lower, update r2min.
                    ymin=y #Update ymin.
                    y_predmin=y_pred #Update y predicted min.
                    xmin=x #Update xmin.
                boxplot_px.append(r2_score(y,y_pred)) #Append the R2 score of the analyzed pixel to the boxplot_px.
                stats=coef+itcp+r2 #Create a list to store stats for the pixel.
                #Add the stats values to the dictionary LR_hour, where i refers to the pixel ID.
                LR_hour[i]=stats
                #Calculate the rainfall intensity associated with each return period of 2, 5, 10 and 25 years.
                for k in RP_gumbel: #Iterate over return periods.
                    rainfall=[itcp[0]+coef[0]*k] #Calculate rainfall based on the fitted linear equation (Gumbel distribution).
                    rainfall_RP.extend(rainfall) #Add the rainfall intensity to the list rainfall_RP.
                #Add the list of rainfall intensities for the return periods of 2, 5, 10, and 25 years to the dictionary. i refers to the pixel ID.
                RP_hour[i]=rainfall_RP
                
            #Set the parameters for the graph of minimum and maximum R2, per duration.
            font = {'size': 10,'family':'Calibri'}
            plt.rc('font', **font)
            fig2,ax2=plt.subplots(1,2)
            for ext in ['min','max']: #Iterate over min and max graphs.
                if ext=='min': #For the min graph.
                    ax2[1].scatter(xmin,ymin,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),s=8,zorder=1,label='Annual maximum rainfall') #Minimum observed.
                    ax2[1].plot(xmin,y_predmin,'k--',lw=1.2,zorder=2,label='Linear function') #Minimum predicted.
                    ax2[1].set_title('(b) Min. R2 = 0.61',fontsize=10) #Set title.
                else: #For the max graph.
                    ax2[0].scatter(xmax,ymax,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),s=8,zorder=1) #Maximum observed.
                    ax2[0].plot(xmax,y_predmax,'k--',lw=1.2,zorder=2) #Maximum predicted.
                    ax2[0].set_title('(a) Max. R2 = 0.99',fontsize=10) #Set title.
            for i in [0,1]:
                ax2[i].tick_params(axis='both', which='major', labelsize=8) #Change tick properties.
                ax2[i].set_xticks(np.arange(-1, 4, 0.5)) #Change limits.
                ax2[i].set_xlim(-1.30,3.19) #Change limits.
            fig2.text(0.52,0.13,'Gumbel reducted variate',fontsize=10,ha="center") #Add text.
            ax2[0].set_ylabel("Rainfall intensity (mm/h)",fontsize=10) #Set label.
            fig2.set_size_inches(5,2.5) #Set size of graph.
            fig2.legend(loc="lower center", fontsize=8,ncol=4,frameon=False) #Set legend.
            fig2.subplots_adjust(bottom=0.27,left=0.09,right=0.97,top=0.90,wspace=0.15,hspace=0.4) #Adjust margins.
            fig2.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\GumbelReport\Pixel'+str(i)+'_'+name[5:-4]+'.jpg',dpi=500)
            plt.close() #Close plot.
            
            #Add the dictionaries for the analyzed duration to the main dictionary with all durations.
            boxplot.append(boxplot_px) #Append the boxplot_px of the analyzed duration the entire series of R2 scores (boxplot).
            EV[name[2:]]=EV_hour #Extreme values.
            LR[name[2:]]=LR_hour #Statistical parameters.
            RP[name[2:]]=RP_hour #Rainfall intensities per return period.

    #Plot the boxplot of the R2 scores per rainfall duration.
    #Settle the graph.
    font = {'size': 10,'family':'Calibri'}
    plt.rc('font', **font)
    fig,ax1=plt.subplots(1,1)
    boxprops = dict(linewidth=1, color='black') #Adjust properties of box.
    flierprops=dict(markersize=4,markeredgewidth=0.5) #Adjust properties of fliers.
    medianprops=dict(linewidth=0.8, color='black') #Adjust properties of median lines.
    plt.boxplot(boxplot,positions=range(1,13,1),flierprops=flierprops,medianprops=medianprops,boxprops=boxprops) #Plot the boxplot list (12 lists refering to 12 durations).
    ax1.tick_params(axis='both', which='major', labelsize=8) #Adjust ticks.
    ax1.set_xlabel("Rainfall duration (hours)",fontsize=10) #Change x labels.
    ax1.set_ylabel("Coefficient of\ndetermination (R2)",fontsize=10) #Change y labels.
    ax1.set_ylim(0.5,1) #Change y limits.
    ax1.set_xticklabels(['1','2','3','4','5','6','7','8','12','14','20','24']) #Update labels of x ticks to the durations.
    fig.set_size_inches(4,2) #Set size of the graph.
    fig.subplots_adjust(bottom=0.19,left=0.15,right=0.97,top=0.96,wspace=0.6,hspace=0.4) #Set margins of the graph.
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\GumbelR2BoxPlot.jpg',dpi=500) #Export graph.
    plt.close() #Close plot.

    #Plot the IDF curves, for each return period, with statistics of mean, standard deviation, minimum, and maximum.
    duration=[[1],[2],[3],[4],[5],[6],[7],[8],[12],[14],[20],[24]] #Define the series of durations.
    #Settle the graph.
    font = {'size': 10,'family':'Calibri'}
    plt.rc('font', **font)
    fig,ax1=plt.subplots(2,1)
    colors=sns.color_palette('Blues',5) #Define color palette with blue tones.
    color_code=1 #Create count for the colors.
    
    for i in range(len(RP_)): #Iterate over return periods of 2, 5, 10, and 25 years.
        count=0
        IDF_px={} #Create a dictionary to store the rainfall intensity vs. duration relationships for each return period.
        RP_dic=RP['DS_1h.csv']  #Select the first duration of 1 hour from the dictionary RP. This is  to be able to extract the keys of the dictionary.
        
        for k in RP_dic.keys(): #Iterate over pixel IDs.
            RP_list=RP_dic[k] #Select the list of rainfall intensities for the 4 reurn periods.
            IDF_list=copy.deepcopy(duration) #Create a copy of the series of durations.
            IDF_int_list=[] #Create a list to sotre the rainfall intensity vs. duration relationships for each return period, per pixel.
            
            for j in range(len(duration)): #Iterate over durations.
                RP_dic=RP['DS_'+str(duration[j][0])+'h.csv'] #Select the dictionary of rainfall intensities of all pixel IDs, for the duration j.
                RP_list=RP_dic[k] #Select the dictionary of rainfall intensities of all return periods, for the pixel ID k.
                IDF_list[j].extend([RP_list[i]]) #Add the rainfall intensity of the return period i to the IDF_list at the position of the duration j.
                IDF_int_list.append(RP_list[i]) #Add the rainfall intensity of the return period i to the IDF_int_list.
                
            IDF_px[k]=IDF_list #Add IDF_list to IDF_px at the location of pixel ID k. Basically, we are reorganizing the arrays of each pixel ID,
            #moving from rainfall intensities per return period to rainfall intensities per duration.
            if count==0: #For the first return period, 2 years.
                IDF_intensity=np.array([IDF_int_list]) #Start a new IDF_intensity array with IDF_int_list.
            else: #For all other return periods.
                IDF_int_add=np.array([IDF_int_list])
                IDF_intensity=np.concatenate((IDF_intensity,IDF_int_add),axis=0) #Concatenate the IDF_int_list to the existing IDF_intensity.
            count=count+1 #Update count.
            
        IDF[RP_[i]]=IDF_px #After iterating over durations and pixel IDs, add the list IDF_px to the dictionary IDF. RP_[i] refers to the code for the return period.
        #Calculate the statistical parameters of the IDF curves, among all pixels, for the return period i
        avg=np.mean(IDF_intensity,axis=0) #Average among all IDF curves.
        max_=np.amax(IDF_intensity,axis=0) #Maximum among all IDF curves.
        min_=np.amin(IDF_intensity,axis=0) #Minumum among all IDF curves.
        std = np.std(IDF_intensity,axis=0) #Standard deviation among all IDF curves.
        #Plot the statistical parameters.
        ax1[0].fill_between(duration1,avg-std,avg+std,alpha=.4,color=colors[color_code],lw=0,zorder=1) #Standard deviation.
        ax1[0].plot(duration1,avg,lw=1.5,color=colors[color_code],zorder=2,label=str(RP_[i])+'-yr RP') #Average.
        ax1[1].plot(duration1,max_,lw=1.5,color=colors[color_code],linestyle="dashed",zorder=2) #Maximum.
        ax1[1].plot(duration1,min_,lw=1.5,color=colors[color_code],linestyle="dashdot",zorder=2) #Minimum.
        color_code=color_code+1 #Update count for color (each color refers to a different return period).
        
    for i in [0,1]:
        if i==0: #Graph 1 (average and standard deviation).
            ax1[i].set_title('(a) Mean and standard deviation',fontsize=10) #Set title.
        else: #Graph 2 (minimum and maximum).
            ax1[i].set_title('(b) Maximum and minimum',fontsize=10) #Set title.
        ax1[i].tick_params(axis='both', which='major', labelsize=8) #Change ticks.
        ax1[i].set_xlim(0,25) #Set x limits.
        ax1[i].set_ylim(0,19) #Set y limits.
        ax1[i].set_xticks(np.arange(1, 25, 1.0)) #Set x limits.
        ax1[i].set_yticks(np.arange(0, 20, 2.0)) #Set y limits.
    ax1[1].set_xlabel("Rainfall duration (hours)",fontsize=10) #Set labels.
    fig.text(0.02,0.55,'Rainfall intensity (mm/h)',fontsize=10,va='center',rotation=90) #Add text.
    ax1[0].tick_params(axis='both',which='major',labelbottom=False) #Set graph properties.
    fig.legend(loc="lower center", fontsize=8,ncol=4,frameon=False,handletextpad=0.3) #Add legend.
    fig.set_size_inches(4.5,4) #Change size of the graph.
    fig.subplots_adjust(bottom=0.17,left=0.1,right=0.97,top=0.94,wspace=0.06,hspace=0.22) #Change margins of the graph.
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\IDFCurves.jpg',dpi=500) #Export graph.
    plt.close() #Close plot.

    return IDF #Return the IDF diciotionary with all rainfall intensities per duration and return period, for each analyzed pixel ID.

#Call the function ds and return the dictionary IDF. The function will also plot the desired graphs of R2 score of Gumbel distribution, examples of minimum
#and maximum R2 scores of the distribution, and IDF curves (with statistical parameters).
IDF=ds(input_names)

#Now that the IDF curves were created, generate the rainfall maps of the spatially distributed hyetographs based on the alternating block method, for each return period.
#Import the mask .tif file, which contains the locations of the pixel IDs.
mask=gdal.Open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\Sample.tif')
#Extract parameters from image
cols = mask.RasterXSize #Number of columns.
rows = mask.RasterYSize #Number of rows.
geotrans=mask.GetGeoTransform() #Get geo transform.
proj=mask.GetProjection() #Get projection.
driver = gdal.GetDriverByName('GTiff') #Get driver.
#Convert the mask into a numpy array. This will be the reference for the rainfall maps.
mask_np=np.array(mask.GetRasterBand(1).ReadAsArray())

#Iterate over return periods       
for i in IDF.keys():
    IDF_RP=IDF[i] #Extract the dictionary of rainfall intensities per pixel ID for the return period i
    ds=[['Pixel ID']] #Create a list to store the DS for the return period i. #The first row refers to the titles.
    
    for j in range(1,25): #Iterate over hours, from 1 to 24 hours (duration of the design storm).
        ds.append([str(j-1)+'-hr']) #Add the corresponding hour as a title in the list ds.
        
    for j in IDF_RP.keys(): #Iterate over pixel IDs.
        ds_px=[] #Create a list to store the rainfall intensities per pixel ID.
        ds_px_sort=[] #Create a list to store the sorted rainfall intensities per pixel ID.
        IDF_px=IDF_RP[j] #Extract the list with rainfall intensities, per duration, for the return period i and the pixel ID j.
        
        #Calculate the rainfall intensity (mm/h) for each duration, based on the IDF curve.    
        for duration in range(1,25): #Iterate over the hours, from 1 to 24 hours (duration of the design storm).
            
            for k in range(len(IDF_px)): #Iterate over the rainfall intensities.
                if duration==IDF_px[k][0]: #If the analyzed duration refers to one of the 12 adopted durations (1, 2, 3, 4, 5, 6, 7, 8, 12, 14, 20, 24).
                    ds_px.append([duration,IDF_px[k][1]]) #Adopt the corresponding rainfall intensity.
                elif duration>IDF_px[k][0] and duration<IDF_px[k+1][0]: #If the analyzed duration refers to a value inbetween the 12 adopted durations.
                    #In this case, fit a linear function between the previous and following points.
                    a=(IDF_px[k][1]-IDF_px[k+1][1])/(IDF_px[k][0]-IDF_px[k+1][0]) #Define coefficient a of the linear equation.
                    b=(IDF_px[k][1])-(a*IDF_px[k][0]) #Define coefficient b of the linear function.
                    ds_px.append([duration,(a*duration)+b]) #Calculate the rainfall intensity for the desired duration (9, 10, 11, 13, 15, 16, 17, 18, 19, 21, 22, 23).
                    
        #Calculate the cumulative depth, in mm, by multiplying duration and intensity.
        for k in range(len(ds_px)): #Iterate over the list of rainfall intensities per pixel ID.
            cum_dep=ds_px[k][0]*ds_px[k][1] #Calculated as duration/1hour * rainfall intensity
            ds_px[k].extend([cum_dep]) #Add the cumulative rainfall as a second column in the ds_px list.
            
        #Calculate the incremental depth in mm.
        for k in range(len(ds_px)):#Iterate over the list of rainfall intensities per pixel ID.
            if k==0: #If the value is the first in the list.
                inc_dep=ds_px[k][2] #Incremental is the cumulative depth.
            else: #If the value is any other.
                inc_dep=ds_px[k][2]-ds_px[k-1][2] #Incremental is the difference between this and the previous cumulative depth.
            ds_px[k].extend([inc_dep]) #Add incremental depth as a third column in the ds_px list.
            
        #Sort the incremental depth according to the alternating block method.
        #Start sorting the entire nested list by the incremental depth in ascending order.
        ds_px.sort(key=lambda x:x[3],reverse=True)
        #Add a count column.     
        for k in range(len(ds_px)): #Iterate over the list.
            ds_px[k].extend([k+1]) #Add the count as a forth column in the ds_px list.
        #First, start with uneven numbers and sort in descending order.
        for k in range(len(ds_px)): #Iterate over the list.
            if ds_px[k][-1]%2!=0: #If number if uneven.
                ds_px_sort.extend([ds_px[k][3]]) #Add the rainfall intensities to ds_px_sort.
        #Sort this list in descending order.
        ds_px_sort.sort()
        #Now, add the even number, which were already previously sorted in ascending order. 
        for k in range(len(ds_px)): #Iterate over the list.
            if ds_px[k][-1]%2==0: #If number is even.
                ds_px_sort.extend([ds_px[k][3]]) #Extend to the existing ds_px_sort list (previously 
        #The generated files represent the design storms for the return period i and the pixel ID j.     
                 
        #Finally, add the design storm to the  list countaining all pixels, for the return period i.
        ds[0].extend(['Pixel '+str(j)]) #Add the pixel code to the first row of the ds list, extended to the existing title.
        for k in range(len(ds_px_sort)): #Iterate over the rainfall intensities of the design storm, for return period i and pixel j.
            ds[k+1].extend([ds_px_sort[k]]) #Add the rainfall intensities in the following rows of the ds list.
        #The generated ds list will be a nested list where each row represents a different pixel ID, and the columns represent the rainfall intensities of the design storms.
            
    #Save the design storms as 24 rainfall maps representing the 24 hourly rainfall intensities for the return period i.
    #Set directory to save .tif files.
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputDSMaps")

    for t in range(1,25): #Iterate over the duration of the design storms.
        ds_np=np.copy(mask_np.astype('float64')) #Create a copy of the reference .tif file mask_np.
        ds_np[ds_np<0]=np.nan #Replace negative values by nan.
    
        for j in range(len(ds[0])-1): #Iterate over the pixel IDs.
            ds_px=[] #Create a list to store the rainfall intensity values for pixel ID j.
            ds_px=[row[j+1] for row in ds] #Replace this list by the rainfall intensity values, extracted from list ds.
   
            #Now, fill the reference array with the values.
            for row in range(len(mask_np)): #Iterate over the rows of the reference array.
                for column in range(len(mask_np[0])): #Iterate over the columns of the reference array.
                    if mask_np[row,column]==j: #If the value in the mask_np is equal to the pixel ID.
                        ds_np[row,column]=ds_px[t] #Add the rainfall intensity value to this pixel.
    
        #After finishing the iteration over all pixels of the image, for the duration t, export the rainfall map as a .tif file.
        dataset = driver.Create('DS_'+str(i)+'yr_'+str(t)+'hr.tif',cols,rows,1,gdal.GDT_Float32) #Export map with return period i, and duration t.
        dataset.GetRasterBand(1).WriteArray(ds_np) #Write array to .tif file.
        dataset.SetGeoTransform(geotrans) #Set geo transform.
        dataset.SetProjection(proj) #Set projection.
        dataset.FlushCache()
        dataset=None    
