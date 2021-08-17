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

#Inititalize the Google Earth Engine API
ee.Initialize()

#Create a rectangle to clip the satellite images only to the region of the Itajai River Basin
rec = ee.Geometry.Rectangle([-50.5, -28, -48.5, -26])

#Import the correction factors.
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData")
cor_factor=np.load("cor_monthly_GSMaP.npy",allow_pickle=True).tolist()

#Iterate for all hours, from 1 to 24:
for year in range(2018,2019):
    for hour in [1]:
        #Create an array with the same dimensions as the satellite image.
        if hour in [1,2,3,4,5,6,7,8]:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-01T0'+str(hour)+':00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        elif hour==24:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-02T00:00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        else:
            collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(str(year)+'-07-01T00:00:00',str(year)+'-07-01T'+str(hour)+':00:00').filterBounds(rec).select('hourlyPrecipRateGC')
        rainfall=collection.reduce(ee.Reducer.mean())
        latlon = ee.Image.pixelLonLat().addBands(rainfall)
        #Apply reducer to select only the pixels within the boundaries of the polygon "rec", or the Itajai River Basin region
        latlon = latlon.reduceRegion(reducer=ee.Reducer.toList(),geometry=rec,maxPixels=1e8,scale=10609)    
        #Get data into three different arrays: one for lat, one for lon, and one for the cumulative rainfall
        data = np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean")).getInfo()))
        lats = np.array((ee.Array(latlon.get("latitude")).getInfo()))
        lons = np.array((ee.Array(latlon.get("longitude")).getInfo()))
        #Get the unique coordinates
        uniqueLats = np.unique(lats)
        uniqueLons = np.unique(lons)
        #Get the number of rows and columns based on the coordinates
        ncols = len(uniqueLons)
        nrows = len(uniqueLats)
        #Determine pixel sizes
        ys = uniqueLats[1] - uniqueLats[0] 
        xs = uniqueLons[1] - uniqueLons[0]
        #Create the numpy array with the same dimensions
        ref_arr = np.zeros([nrows, ncols], np.float32)
        arr = np.zeros([nrows, ncols], np.float32)
        #Fill the array with values
        counter=0
        for y in range(0,len(arr),1):
            for x in range(0,len(arr[0]),1):
                if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats)-1:
                    counter+=1
                    arr[len(uniqueLats)-1-y,x] = data[counter]
        #Apply the correction factor to the date
        for i in range(len(cor_factor)):
            if cor_factor[i][0].month == 7 and cor_factor[i][0].year == year:
                corr=cor_factor[i][1]
                break
        arr_cor=arr*corr
        #SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        transform = (np.min(uniqueLons),xs,0,np.max(uniqueLats),0,-ys)
        #Set the coordinate system
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        #Set driver
        driver = gdal.GetDriverByName('GTiff')
        #Convert the GEE collection to a nested list (check how much time it takes).
        start_date_dt=datetime.date(year,7,1)
        start_hour=0
        while ((start_date_dt < datetime.date(year+1,7,1))==True):
            end_hour=start_hour+hour
            start_year=str(start_date_dt.year)
            start_month=str(start_date_dt.month)
            start_day=str(start_date_dt.day)
            if end_hour>23:
                end_hour=end_hour-24
                end_date=(start_date_dt+datetime.timedelta(days=1))
                end_year=str(end_date.year)
                end_month=str(end_date.month)
                end_day=str(end_date.day)
            else:
                end_year=str(start_date_dt.year)
                end_month=str(start_date_dt.month)
                end_day=str(start_date_dt.day)        

            #Define the start and end dates for the collection:
            start_date = start_year+'-'+start_month+'-'+start_day+'T'+str(start_hour)+':00:00'
            end_date = end_year+'-'+end_month+'-'+end_day+'T'+str(end_hour)+':00:00'

            #Import the image collection, filtering it by date and selecting only the gauge-corrected band
            if (start_date_dt.year<2014) or (start_date_dt.year==2014 and start_date_dt.month<3):
                collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis").filterDate(start_date,end_date).filterBounds(rec).select('hourlyPrecipRateGC')
            else:
                collection=ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/operational").filterDate(start_date,end_date).filterBounds(rec).select('hourlyPrecipRateGC')
            #Apply reducer to select only the pixels within the boundaries of the polygon "rec", or the Itajai River Basin region
            rainfall=collection.reduce(ee.Reducer.mean())
            latlon = ee.Image.pixelLonLat().addBands(rainfall)
            latlon = latlon.reduceRegion(reducer=ee.Reducer.toList(),geometry=rec,maxPixels=1e8,scale=10609)
        
            #Get the data from the specific date
            data=np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean"),ee.PixelType.float()).getInfo()))

            if data.size>0:
                data=np.array((ee.Array(latlon.get("hourlyPrecipRateGC_mean")).getInfo()))
        
                #Create a prov array with the same characteristics as the previous
                prov_arr=ref_arr
                #Fill the provisory array with the rainfall data
                counter=0
                for y in range(0,len(prov_arr),1):
                    for x in range(0,len(prov_arr[0]),1):
                        if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats)-1:
                            counter+=1
                            prov_arr[len(uniqueLats)-1-y,x] = data[counter]
                #Apply the correction factor to the date
                for i in range(len(cor_factor)):
                    if start_date_dt.month == cor_factor[i][0].month and start_date_dt.year == cor_factor[i][0].year:
                        corr=cor_factor[i][1]
                        break
                prov_arr_cor=prov_arr*corr

                #Get the maximum value
                arr_cor=np.maximum(prov_arr_cor,arr_cor)    

            #Transform the numpy array into a list
            #arr_list=prov_arr_cor.tolist()

            #Iterate the start hour, sum 1 hours to the next image
            start_hour=start_hour+1
            if start_hour==24:
                start_hour=0
                start_date_dt=(start_date_dt+datetime.timedelta(days=1))

        #Save the image for the specific hour
        outputDataset=driver.Create(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP-gauge\DS_"+str(year)+"_"+str(hour)+"h.tif", ncols,nrows, 1,gdal.GDT_Float32)
        #Add some information
        outputDataset.SetGeoTransform(transform)
        outputDataset.SetProjection(target.ExportToWkt())
        outputDataset.GetRasterBand(1).WriteArray(arr_cor)
        outputDataset.GetRasterBand(1).SetNoDataValue(-9999)
        outputDataset = None
        
    #Append the list to the dictionary sat_merged
    #sat_merged['2000']=arr_list   

#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputData")
#np.save('sat_GSMaP_merged.npy', sat_merged)

#Import the names of the files from each duration (1 hour to 24 hours)
input_names=[] #Create a list to store the codes of the stations and associate these codes with the dictionary
directory=r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP'
for entry in os.scandir(directory):
    input_names.append(entry.name)

def ds(input_names,samples,label): #input_names is the list with the .csv files, samples is the number of years (0,-1,-2,1,2,3), and label is the folder to save ('All','-1',etc.)
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\GSMaP")
    #Create dictionaries
    #EV refers to the rainfall extreme values for the 20 years
    #LR refers to the statistial parameters of the linears regression. In this order: coefficient, intercept, R2 and RSE
    #RP refers to the rainfall estimated for each return period. In this order: 2, 5, 10 and 20 years
    #IDF refers to the IDF curves (rainfall intensity vs. duration), per return period of 2, 5, 10 and 20 years, per pixel
    EV={}
    LR={}
    RP={}
    IDF={}

    #Calculate the gumbel for 20 years duration
    import math
    EV_gumbel=[]
    for i in range(1,21+samples):
        pl=i/(21+samples)
        gumbel=-math.log(-math.log(pl))
        EV_gumbel.extend([gumbel])
    
    #Calculte the gumbel for the return periods of 2, 5, 10 and 20 years.
    import math
    RP_=[2,5,10,25]
    RP_gumbel=[]
    for i in RP_:
        pr=1/i
        pl=1-pr
        gumbel=-math.log(-math.log(pl))
        RP_gumbel.extend([gumbel])

    #Define parameters for the graph
    row=0
    column=0
    font = {'size': 10,'family':'Calibri'}
    plt.rc('font', **font)
    fig,axs=plt.subplots(3,4)
    count1=0
    count2=0
    boxplot=[]

    #Iterate each duration, from 1 to 24 hours
    for name in input_names:
        count=0
        EV_hour={}
        LR_hour={}
        RP_hour={}
        EV_all=[]
        boxplot_px=[]
        #Open the dataset
        with open(name, newline='') as f:
            reader = csv.reader(f)
            EV_extend = list(reader)     
            EV_all.extend(EV_extend)
            r2max=0
            r2min=1
            #Iterate over each pixel of the map to create an extreme value statistics for each pixel
            for i in range(len(EV_all[0])):
                EV_px_0=[row[i] for row in EV_all]
                EV_px_1=[]
                EV_px=[]
                rainfall_RP=[]
                #Extreme rainfall values for the years per pixel
                for j in range(len(EV_px_0)):
                    if j!=0:
                        EV_px_1.extend([float(EV_px_0[j])])
                    else:
                        if EV_px_0[j]=='ï»¿0':
                            EV_code=int(0)
                        else:
                            EV_code=int(EV_px_0[j])
                #Sort the maximum annual rainfall in ascending order
                EV_px_1.sort()
                #Eliminate the outliers according to the input samples:
                if samples!=0:
                    EV_px_1=EV_px_1[0:samples]
                #Append EV_px_1 
                EV_px.append(EV_px_1)                    
                #Add the values (rainfall and gumbel) to the dictionary EV_hour for the duration X
                EV_hour[i]=EV_px
                #Fit a linear regression to the datasets EV_px_1 as x and EV_gumbel as y
                #Create a linear regression object
                regr = linear_model.LinearRegression()
                #Convert the lists to arrays
                x=np.array(EV_gumbel).reshape((-1,1))
                y=np.array(EV_px_1)
                #Train the model using the sets
                regr.fit(x,y)
                #Predict the gumbel values from the rainfall
                y_pred=regr.predict(x)
                #Plot the Gumbel distribution
                #Define parameters for the other graph
                font = {'size': 10,'family':'Calibri'}
                plt.rc('font', **font)
                fig1,ax1=plt.subplots(1,1)
                #Plot the points (observed)
                ax1.scatter(x,y,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),s=8,zorder=1,label='Annual maximum rainfall')
                #Plot the linear distribution (fitted)
                ax1.plot(x,y_pred,'k--',lw=1.2,zorder=2,label='Linear function')
                #Export the graph
                ax1.tick_params(axis='both', which='major', labelsize=8)
                ax1.set_xlabel("Gumbel reduced variate",fontsize=10)
                ax1.set_ylabel("Rainfall intensity (mm/h)",fontsize=10)
                ax1.set_xticks(np.arange(-1, 4, 0.5))
                ax1.set_xlim(-1.30,3.19)
                #ax1.set_title('Pixel '+str(i)+' - Duration '+name[5:-4],fontsize=10)
                r2=round(r2_score(y,y_pred),2)
                #coef=round(regr.coef_[0],2)
                #itcp=round(regr.intercept_,2)
                fig1.text(0.14,0.8,'R2='+str(r2),fontsize=8)
                fig1.set_size_inches(6,3)
                fig1.legend(loc="lower center", fontsize=10,ncol=4,frameon=False)
                fig1.subplots_adjust(bottom=0.24,left=0.09,right=0.97,top=0.90,wspace=0.4,hspace=0.4)
                #Activate the savefig function 
                #fig1.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\Gumbel\Pixel'+str(i)+'_'+name[5:-4]+'_'+label+'.jpg')
                plt.close()
                #Add y_pred to the dictionary
                if count==0:
                    EV_pred=np.array([y_pred])
                else:
                    y_pred_np=np.array([y_pred])
                    EV_pred=np.concatenate((EV_pred,y_pred_np),axis=0)
                #Plot the linear tendency line
                if count2==0:
                    axs[row,column].plot(x,y_pred,alpha=.4,color="silver",lw=0.8,zorder=1,label='Individual linear function')
                else:
                    axs[row,column].plot(x,y_pred,alpha=.4,color="silver",lw=0.8,zorder=1)
                count=count+1
                count2=count2+1
                #Calculate the regression parameters per pixel: coefficient, intercept, R2 score and mean squared error
                coef=[regr.coef_[0]]
                itcp=[regr.intercept_]
                r2=[r2_score(y,y_pred)]
                if r2[0]>r2max:
                    r2max=r2[0]
                    ymax=y
                    y_predmax=y_pred
                    xmax=x
                if r2[0]<r2min:
                    r2min=r2[0]
                    ymin=y
                    y_predmin=y_pred
                    xmin=x
                boxplot_px.append(r2_score(y,y_pred))
                mse=[mean_squared_error(y,y_pred)]
                stats=coef+itcp+r2+mse
                #Add the stats values to the dictionary LR_hour
                LR_hour[i]=stats       
                #Calculate the rainfall associated with each return period of 2, 5, 10 and 20 years
                for k in RP_gumbel:
                    rainfall=[itcp[0]+coef[0]*k]
                    rainfall_RP.extend(rainfall)
                #Add the rainfall, for each return period, for the related pixel, to the dictionary
                RP_hour[i]=rainfall_RP
            #Plot the distributions with max and min R2, for this duration
            font = {'size': 10,'family':'Calibri'}
            plt.rc('font', **font)
            fig2,ax2=plt.subplots(1,2)
            for ext in ['min','max']:
                #Plot the points (observed)
                if ext=='min':
                    ax2[1].scatter(xmin,ymin,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),s=8,zorder=1,label='Annual maximum rainfall')
                    #Plot the linear distribution (fitted)
                    ax2[1].plot(xmin,y_predmin,'k--',lw=1.2,zorder=2,label='Linear function')
                    ax2[1].set_title('(b) Min. R2 = 0.61',fontsize=10)
                else:
                    ax2[0].scatter(xmax,ymax,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),s=8,zorder=1)
                    #Plot the linear distribution (fitted)
                    ax2[0].plot(xmax,y_predmax,'k--',lw=1.2,zorder=2)
                    ax2[0].set_title('(a) Max. R2 = 0.99',fontsize=10)
            #Export the graph
            for i in [0,1]:
                ax2[i].tick_params(axis='both', which='major', labelsize=8)
                ax2[i].set_xticks(np.arange(-1, 4, 0.5))
                ax2[i].set_xlim(-1.30,3.19)
            fig2.text(0.52,0.13,'Gumbel reducted variate',fontsize=10,ha="center")
            ax2[0].set_ylabel("Rainfall intensity (mm/h)",fontsize=10)
            fig2.set_size_inches(5,2.5)
            fig2.legend(loc="lower center", fontsize=8,ncol=4,frameon=False)
            fig2.subplots_adjust(bottom=0.27,left=0.09,right=0.97,top=0.90,wspace=0.15,hspace=0.4)
            #Activate the savefig function 
            fig2.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\GumbelReport\Pixel'+str(i)+'_'+name[5:-4]+'_'+label+'.jpg',dpi=500)
            plt.close()
            #Add the dictionaries from each duration to the main dictionary with all durations, from 1 to 24 hours
            boxplot.append(boxplot_px)
            EV[name[2:]]=EV_hour
            LR[name[2:]]=LR_hour
            RP[name[2:]]=RP_hour
            #Calculate and plot the average and standard deviation of Gumbel distrituions for each duration
            avg=np.mean(EV_pred,axis=0)
            std=np.std(EV_pred,axis=0)
            #Plot the mean and std dev
            if count1==0:
                axs[row,column].fill_between(EV_gumbel,avg-std,avg+std,alpha=.6,color='royalblue',label='Standard deviation',lw=0,zorder=2)
                axs[row,column].plot(EV_gumbel,avg,lw=1.2,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),label='Mean',zorder=3)
                count1=1
            else:
                axs[row,column].fill_between(EV_gumbel,avg-std,avg+std,alpha=.6,color='royalblue',lw=0,zorder=2)
                axs[row,column].plot(EV_gumbel,avg,lw=1.2,color=(0.41708573625528644, 0.6806305267204922, 0.8382314494425221),zorder=3)
            if column==0 and row==1:
                axs[row,column].set_ylabel("Rainfall intensity (mm/h)",fontsize=10)
            elif column!=0:
                axs[row,column].tick_params(axis='both',which='major',labelleft=False)
            if row!=2:
                axs[row,column].tick_params(axis='both',which='major',labelbottom=False)
            #Iterate the graph
            column=column+1
            if column>3:
                column=0
                row=row+1

    #Save the gumbel plot with the tendency lines from all 400 pixels
    duration1=[1,2,3,4,5,6,7,8,12,14,20,24]
    duration=[[1],[2],[3],[4],[5],[6],[7],[8],[12],[14],[20],[24]]
    count=0
    for i in range(len(axs)):
        for j in range(len(axs[0])):
            ax=axs[i,j]
            ax.tick_params(axis='both', which='major', labelsize=8)
            ax.set_xticks(np.arange(-1, 4, 1))
            ax.set_xlim(-1.30,3.19)
            ax.set_ylim(0,20)
            if count==0:
                ax.set_title(str(duration[count][0])+" hour",size=10)
            else:
                ax.set_title(str(duration[count][0])+" hours",size=10)
            count=count+1
    fig.text(0.5,0.05,'Gumbel reduced variate',fontsize=10)
    fig.legend(loc="lower center", fontsize=8,ncol=4,frameon=False)
    fig.set_size_inches(6, 6)
    fig.subplots_adjust(bottom=0.1,left=0.08,right=0.97,top=0.95,wspace=0.06,hspace=0.25)
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\GumbelSpatialVariation_'+label+'.jpg',dpi=500)
    plt.close()

    #Plot the boxplot for gumbel
    font = {'size': 10,'family':'Calibri'}
    plt.rc('font', **font)
    fig,ax1=plt.subplots(1,1)
    boxprops = dict(linewidth=1, color='black')
    flierprops=dict(markersize=4,markeredgewidth=0.5)
    medianprops=dict(linewidth=0.8, color='black')
    plt.boxplot(boxplot,positions=range(1,13,1),flierprops=flierprops,medianprops=medianprops,boxprops=boxprops)
    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax1.set_xlabel("Rainfall duration (hours)",fontsize=10)
    ax1.set_ylabel("Coefficient of\ndetermination (R2)",fontsize=10)
    ax1.set_ylim(0.5,1)
    ax1.set_xticklabels(['1','2','3','4','5','6','7','8','12','14','20','24'])
    fig.set_size_inches(4,2)
    fig.subplots_adjust(bottom=0.19,left=0.15,right=0.97,top=0.96,wspace=0.6,hspace=0.4)
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\GumbelR2BoxPlot_'+label+'.jpg',dpi=500)
    plt.close()

    #Generate the IDF dictionary, the keys will be the return periods (2,5,10 and 20 years)
    #Plot the IDF curves, for each return period, average and standard deviation
    font = {'size': 10,'family':'Calibri'}
    plt.rc('font', **font)
    fig,ax1=plt.subplots(2,1)
    colors=sns.color_palette('Blues',5)
    color_code=1
    for i in range(len(RP_)):
        count=0
        IDF_px={}
        RP_dic=RP['DS_1h.csv']
        for k in RP_dic.keys():
            RP_list=RP_dic[k]
            IDF_list=copy.deepcopy(duration)
            IDF_int_list=[]
            for j in range(len(duration)):
                RP_dic=RP['DS_'+str(duration[j][0])+'h.csv']
                RP_list=RP_dic[k]
                IDF_list[j].extend([RP_list[i]])
                IDF_int_list.append(RP_list[i])
            IDF_px[k]=IDF_list
            if count==0:
                IDF_intensity=np.array([IDF_int_list])
            else:
                IDF_int_add=np.array([IDF_int_list])
                IDF_intensity=np.concatenate((IDF_intensity,IDF_int_add),axis=0)
            count=count+1
        IDF[RP_[i]]=IDF_px
        #Calculate the average and standard deviation of the IDF curves for the return period i
        avg=np.mean(IDF_intensity,axis=0)
        max_=np.amax(IDF_intensity,axis=0)
        min_=np.amin(IDF_intensity,axis=0)
        std = np.std(IDF_intensity,axis=0)
        #Plot the average and standard deviation
        ax1[0].fill_between(duration1,avg-std,avg+std,alpha=.4,color=colors[color_code],lw=0,zorder=1)
        ax1[0].plot(duration1,avg,lw=1.5,color=colors[color_code],zorder=2,label=str(RP_[i])+'-yr RP')
        ax1[1].plot(duration1,max_,lw=1.5,color=colors[color_code],linestyle="dashed",zorder=2)
        ax1[1].plot(duration1,min_,lw=1.5,color=colors[color_code],linestyle="dashdot",zorder=2)
        #ax1.scatter(duration1,avg,lw=1,color=colors[color_code],zorder=3,s=8)
        color_code=color_code+1
    for i in [0,1]:
        if i==0:
            ax1[i].set_title('(a) Mean and standard deviation',fontsize=10)
        else:
            ax1[i].set_title('(b) Maximum and minimum',fontsize=10)
        ax1[i].tick_params(axis='both', which='major', labelsize=8)
        ax1[i].set_xlim(0,25)
        ax1[i].set_ylim(0,19)
        ax1[i].set_xticks(np.arange(1, 25, 1.0))
        ax1[i].set_yticks(np.arange(0, 20, 2.0))
    ax1[1].set_xlabel("Rainfall duration (hours)",fontsize=10)
    fig.text(0.02,0.55,'Rainfall intensity (mm/h)',fontsize=10,va='center',rotation=90)
    ax1[0].tick_params(axis='both',which='major',labelbottom=False)
    fig.legend(loc="lower center", fontsize=8,ncol=4,frameon=False,handletextpad=0.3)
    fig.set_size_inches(4.5,4)
    fig.subplots_adjust(bottom=0.17,left=0.1,right=0.97,top=0.94,wspace=0.06,hspace=0.22)
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\Graphs\IDFCurves_'+label+'.jpg',dpi=500)
    plt.close()

    return IDF

#It was observed that, in many cases, the low R2 of the linear fit was caused by a single outlier, which refers to he maximum precipitation. Therefore,
#we decided to rerun the code excluding the highest value from the analysis. A function was created
IDF=ds(input_names,0,'')#0 refers to not exclude any point

#Save the IDF data
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputData")
np.save("IDF.npy", IDF)

#Open the IDF data
#os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputData")
#IDF=np.load("IDF.npy",allow_pickle=True).item()

#Now that the IDF curves were created, generate the hyetograph based on the alternating block method, per return period
#Import the mask .tif file
mask=gdal.Open(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\InputData\Sample_vf_vf.tif')
#Extract parameters from image
cols = mask.RasterXSize
rows = mask.RasterYSize
geotrans=mask.GetGeoTransform()
proj=mask.GetProjection()
driver = gdal.GetDriverByName('GTiff')
#Convert the mask into a numpy array
mask_np=np.array(mask.GetRasterBand(1).ReadAsArray()) #This will be the basis for the rainfall
#Iterate over return periods
#Create a list for time (y-axis)
time=[]
for j in range(0,25):
    if j==0 or j==24:
        time.extend([j])
    else:
        time.extend([j,j])
for i in IDF.keys():
    count=0
    IDF_RP=IDF[i] #Defined the dictionaty for the return period i
    #Generate lists to store the DS for the return period
    ds=[['Pixel ID']]
    for j in range(1,25):
        ds.append([str(j-1)+'-hr'])
    for j in IDF_RP.keys():
        ds_px=[]
        ds_px_sort=[]
        ds_px_np=[]
        IDF_px=IDF_RP[j] #Defined the nested list with IDF curve for RP i and pixel j
        #Calculate the rainfall intensity (mm/h) for each duration, based on the IDF curve
        for duration in range(1,25): #Defines the duration of the design storm. 1 to 24 hours.
            for k in range(len(IDF_px)):
                if duration==IDF_px[k][0]:
                    ds_px.append([duration,IDF_px[k][1]])
                elif duration>IDF_px[k][0] and duration<IDF_px[k+1][0]:
                    a=(IDF_px[k][1]-IDF_px[k+1][1])/(IDF_px[k][0]-IDF_px[k+1][0])
                    b=(IDF_px[k][1])-(a*IDF_px[k][0])
                    ds_px.append([duration,(a*duration)+b])
        #Calculate the cumulative depth, in mm, by multiplying duration and intensity
        for k in range(len(ds_px)):
            cum_dep=ds_px[k][0]*ds_px[k][1]#duration/1h * intensity
            ds_px[k].extend([cum_dep])
        #Calculate the incremental depth in mm
        for k in range(len(ds_px)):
            if k==0:
                inc_dep=ds_px[k][2]
            else:
                inc_dep=ds_px[k][2]-ds_px[k-1][2]
            ds_px[k].extend([inc_dep])
        #Sort the incremental depth according to the alternating block method
        #Start sorting the entire nested list by the incremental depth, ascending order
        ds_px.sort(key=lambda x:x[3],reverse=True)
        #Add a count columns
        for k in range(len(ds_px)):
            ds_px[k].extend([k+1])
        #First, start with uneven number and sort in descending order
        for k in range(len(ds_px)):
            if ds_px[k][-1]%2!=0:
                ds_px_sort.extend([ds_px[k][3]])
                ds_px_np.extend([ds_px[k][3],ds_px[k][3]])
        #Sort this list in descending order
        ds_px_sort.sort()
        ds_px_np.sort()
        #Now, add the even number in ascending order
        for k in range(len(ds_px)):
            if ds_px[k][-1]%2==0:
                ds_px_sort.extend([ds_px[k][3]])
                ds_px_np.extend([ds_px[k][3],ds_px[k][3]])
        #Transform the ds into a numpy array. Add to existing
        if count==0:
            ds_np=np.array([ds_px_np])
        else:
            ds_np_add=np.array([ds_px_np])
            ds_np=np.concatenate((ds_np,ds_np_add),axis=0)
        count=count+1
        #Finally, add the design storm to the nested list countaining all pixels
        #Add the pixel code
        ds[0].extend(['Pixel '+str(j)])
        for k in range(len(ds_px_sort)):
            ds[k+1].extend([ds_px_sort[k]])
    #Export the nested list for RP i
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputDS")
    np.save("DS_RP_"+str(i)+"yr.npy", ds)
    #Set directory to save .tif files
    os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\DesignStorms\OutputDSMaps")
    #Also save the design storm
    #for t in range(1,25):
    #    ds_np=np.copy(mask_np.astype('float64'))
    #    ds_np[ds_np<0]=np.nan
    #    for j in range(len(ds[0])-1):
    #        ds_px=[]
    #        ds_px=[row[j+1] for row in ds]
    #        for row in range(len(mask_np)):
    #            for column in range(len(mask_np[0])):
    #                if mask_np[row,column]==j:
    #                    ds_np[row,column]=ds_px[t]
        #Export the ds_np as a .tif
    #    dataset = driver.Create('DS_'+str(i)+'yr_'+str(t)+'hr.tif',cols,rows,1,gdal.GDT_Float32)
    #    dataset.GetRasterBand(1).WriteArray(ds_np)
    #    dataset.SetGeoTransform(geotrans)
    #    dataset.SetProjection(proj)
    #    dataset.FlushCache()
    #    dataset=None    
