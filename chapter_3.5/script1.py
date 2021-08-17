#################################
## Created by: C. B. Moroz ######
#################################

#Description: code to validate the rainfall products through the calculation of the modified Kling Gupta-Efficiency (KGE) and its components of
#bias ratio, variability ratio and linear correlation.

import os
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.ticker
import datetime
import seaborn as sns

#Set directory where the input files are located.
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")

#Create a function to calculate KGE for the entire series.
def KGE(input_sat_daily,input_sat_3daily,input_sat_monthly,input_gauge_daily,input_gauge_3daily,input_gauge_monthly,codes_yr):
    
    satproducts=['GSMaP','GSMaP MBC 3-daily','GSMaP MBC monthly','GSMaP RIDW 3-daily','GSMaP RIDW monthly','IMERG','IMERG MBC 3-daily',
                 'IMERG MBC monthly','IMERG RIDW 3-daily','IMERG RIDW monthly','Gauge IDW'] #Create list with the names of the rainfall products.
    timestep=['daily','3daily','monthly'] #Create a list with the adopted time scales.
    stats_export=[['Timestep','Satellite product','Gauge station','B','Y','R','KGE','Sample size']] #Create a list to store the statistics.
    #Settle the graph.
    font = {'size':10,'family': 'Calibri'}
    plt.rc('font', **font)
    fig,axs=plt.subplots(4,3,sharey='row',sharex=False)
    medianprops=dict(linewidth=0.7, color='black')
    boxprops=dict(linewidth=0.5, color="black")
    colors=sns.color_palette('tab10',10)
    colors=colors+[(1.0,1.0,1.0)]#Color white for IDW
    #Start the analysis
    for s in timestep: #Iterate over time scales.
        #Create lists to store the entire statistics.
        stats_B=[] #bias ratio.
        stats_Y=[] #variability ratio.
        stats_R=[] #linear correlation.
        stats_KGE=[] #Kling-Gupta efficiency.
        for r in satproducts: #Iterate over the rainfall products.
            #Create lists to store the statistics per rainfall product.
            stats_B_prod=[] #bias ratio.
            stats_Y_prod=[] #variability ratio.
            stats_R_prod=[] #linear correlation.
            stats_KGE_prod=[] #Kling-Gupta efficiency.
            if s=="daily":
                column=0 #position in the graph.
                input_sat=input_sat_daily[r] #Satellite data.
                input_gauge=input_gauge_daily #Gauge data.
            elif s=="3daily":
                column=1 #position in the graph.
                input_sat=input_sat_3daily[r] #Satellite data.
                input_gauge=input_gauge_3daily #Gauge data.
            else:
                column=2 #position in the graph.
                input_sat=input_sat_monthly[r] #Satellite data.
                input_gauge=input_gauge_monthly #Gauge data.

            #Calculate the statistics per station
            for i in input_gauge.keys(): #Iterate over gauge stations.
                a=0
                b=0
                leng=0
                sat=input_sat[i] #Get satellite time series.
                gauge=input_gauge[i] #Get gauge time series.
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr): #If the year should be considered (only 5 years were adopted for gauges from Group 2).
                        a=a+(sat[j][1]) #Sum of satellite estimates.
                        b=b+(gauge[j][1]) #Sum of gauge estimates.
                        leng=leng+1 #Total number of measurements.
                                
                mean_sat=a/leng #Calculate mean satellite estimates.
                mean_gauge=b/leng #Calculate mean gauge estimates.
                B=mean_sat/mean_gauge #Calculate bias ratio.
                stats_B_prod=stats_B_prod+[B] #Add bias ratio to the list.

                a=0
                b=0
                leng=0 
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr): #If the year should be considered.
                        a=a+((sat[j][1]-mean_sat)**2)
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        leng=leng+1
                                
                std_sat=(a/leng)**0.5 #Calculate std. deviation of satellite.
                std_gauge=(b/leng)**0.5 #Calculate std. deviation of gauge.
                Y=(std_sat/mean_sat)/(std_gauge/mean_gauge) #Calculate variability ratio.
                stats_Y_prod=stats_Y_prod+[Y] #Add variability ratio to the list.

                a=0
                b=0
                c=0
                #Finally, calculate r
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr): #If the year should be considered.
                        a=a+((gauge[j][1]-mean_gauge)*(sat[j][1]-mean_sat))
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        c=c+((sat[j][1]-mean_sat)**2)
                R=a/((b**0.5)*(c**0.5)) #Calculate linear correlation.
                stats_R_prod=stats_R_prod+[R] #Add linear correlation to the list.

                #Based on these measurements, calculate the KGE for each station:
                KGE=(1-(((R-1)**2+(B-1)**2+(Y-1)**2)**0.5)) #Calculate KGE.
                stats_KGE_prod=stats_KGE_prod+[KGE] #Add KGE to the list.
                stats_add_e=[s,r,i,B,Y,R,KGE,leng] #Add all statistics to the stats_add_e.
                stats_export.append(stats_add_e) #Apend stats_add_e to stats_export.

            #Append the statistics listso of each rainfall product to the general list.
            stats_B.append(stats_B_prod) #Bias ratio.
            stats_Y.append(stats_Y_prod) #Variability ratio.
            stats_R.append(stats_R_prod) #Linear correlation.
            stats_KGE.append(stats_KGE_prod) #Kling-Gupta efficiency.

        #Plot the boxplot graph.
        bplot1=axs[0,column].boxplot(stats_B,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 1 (B).
        bplot2=axs[1,column].boxplot(stats_Y,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 2 (Y).
        bplot3=axs[2,column].boxplot(stats_R,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 3 (r).
        bplot4=axs[3,column].boxplot(stats_KGE,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 4 (KGE).
        for bplot in (bplot1,bplot2,bplot3,bplot4):
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color) #Change colors of boxplots.
        for row in range(0,4):
            axs[row,column].plot([-2,13],[1,1],'k--',linewidth=1,zorder=1) #Plot reference line (optimal values).
            if row==0:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.1)) #Adjust major and minor ticks.
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.05)) #Adjust major and minor ticks.
            else:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.2)) #Adjust major and minor ticks.
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.1)) #Adjust major and minor ticks.
            if column==2 and row==0:
                axs[row,column].set_title('Monthly',fontsize=10) #Set title.
            elif column==1 and row==0:
                axs[row,column].set_title('3-Daily',fontsize=10) #Set title.
            elif column==0 and row==0:
                axs[row,column].set_title('Daily',fontsize=10) #Set title.
            elif column==1 and row==3:
                axs[row,column].set_xlabel('Rainfall products',fontsize=10) #Set labels.
            axs[row,column].set_xlim(0.5,11.5) #Set limits.
            axs[row,column].set_xticklabels(['GOr','GM3','GMm','GR3','GRm','IOr','IM3','IMm','IR3','IRm','IDW']) #Change x-axis labels for ticks.
            if row<3:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelbottom=False,bottom=False) #Edit graph.
            else:
                axs[row,column].tick_params(axis='x',which='major',labelsize=8,rotation=90) #Edit graph.
            if column>0:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelleft=False) #Edit graph.
            else:
                if row==0:
                    axs[row,column].set_ylabel('β',fontsize=10) #Set label.
                if row==1:
                    axs[row,column].set_ylabel("γ",fontsize=10) #Set label.                  
                elif row==2:
                    axs[row,column].set_ylabel('R',fontsize=10) #Set label.
                elif row==3:
                    axs[row,column].set_ylabel('KGE',fontsize=10) #Set label.
                axs[row,column].tick_params(axis='both',which='major',labelsize=8) #Edit graph.
    fig.set_size_inches(6,8) #Set size of figure.
    fig.subplots_adjust(bottom=0.08,left=0.08,right=0.98,top=0.97,wspace=0.05,hspace=0.04) #Adjust margins.
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Plot_stats\KGE_stats.jpg',dpi=500) #Save figure.
    plt.close() #Close plot.
    #Export the statistics to a .csv file.
    with open(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Statistics\KGE_stations_"+code+".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_export)

#Create  function to calculate the KGE per rainfall intensity class.
def KGE_intensity(input_sat_all,input_gauge,codes_yr):
    #First, extract the rainfall intensity per station related to the 70th and 90th percentiles.
    thresholds={} #Dictionary to store the rainfall values.
    for i in input_gauge.keys(): #Iterate over rain gauges.
        thresholds_append=[] #List of thresholds for a specific location.
        for percentile in [0.5,0.7,0.9,1.0]: #Iterate of percentiles of interest.
            rainfall=[] #Create temporary list to store rainfall values.
            gauge=input_gauge[i] #Get rainfall time series.
            for j in range(len(gauge)): #Iterate over time series.
                if gauge[j][0].year in codes_yr: #Adopt only the 5 years of interest.
                    rainfall=rainfall+[gauge[j][1]] #Add rainfall measurement to the rainfall list.
            rainfall.sort() #Sort the list in ascending order.
            freq=[] #Create a list to store frequency percentages.
            for j in range(len(rainfall)): #Iterate over the sorted list.
                freq=((j+1)/len(rainfall)) #Calculate the frequency for each position.
                if freq>=percentile: #Verify if frequency is higher than thershold percentile.
                    rainfreq=rainfall[j] #Get threshold value.
                    break #After getting value, stop iteraction.
            thresholds_append.append([percentile,rainfreq]) #Append the percentile and corresponding rainfall threshold to thresholds_append.
        thresholds[i]=thresholds_append #Add thresholds append of this specific gauge to the dictionary.

    #Start calculating the statistical parameters
    satproducts=['GSMaP','GSMaP MBC 3-daily','GSMaP MBC monthly','GSMaP RIDW 3-daily','GSMaP RIDW monthly','IMERG','IMERG MBC 3-daily',
                 'IMERG MBC monthly','IMERG RIDW 3-daily','IMERG RIDW monthly','Gauge IDW'] #Define the name of the rainfall products.
    #Create the elements of the graph.
    font = {'size':10,'family': 'Calibri'}
    plt.rc('font', **font)
    fig,axs=plt.subplots(4,3,sharey='row',sharex=False)
    medianprops=dict(linewidth=0.7, color='black')
    boxprops=dict(linewidth=0.5, color="black")
    colors=sns.color_palette('tab10',10)
    colors=colors+[(1.0,1.0,1.0)]#Color white for IDW
    stats_export=[['Percentile','Satellite product','Gauge station','B','Y','R','KGE','Sample size']]
    #Create the list for the percentiles:
    for percentile in [0.7,0.9,1]: #Iterate over percentiles.
        #Create lists to store the entire statistics.
        stats_B=[] #Bias ratio.
        stats_Y=[] #Variability ratio.
        stats_R=[] #Linear correlation.
        stats_KGE=[] #Kling-Gupta efficiency.
        for r in satproducts: #Iterate over rainfall products.
            #Create lists to store the statistics for each rainfall product.
            stats_B_prod=[] #Bias ratio.
            stats_Y_prod=[] #Variability ratio.
            stats_R_prod=[] #Linear correlation.
            stats_KGE_prod=[] #Kling-Gupta efficiency.
            column=1 #Position in the graph.
            input_sat=input_sat_all[r] #Get rainfall time series.
            if percentile==0.7:
                column=0 #Position in the graph.
                indexmax=1 #Position in the list of thresholds.
                indexmin=0 #Position in the list of thresholds.
            elif percentile==0.9:
                column=1 #Position in the list of graph.
                indexmax=2 #Position in the list of thresholds.
                indexmin=1 #Position in the list of thresholds.
            else:
                column=2 #Position in the list of graph.
                indexmax=3 #Position in the list of thresholds.
                indexmin=2 #Position in the list of thresholds.
            #Calculate the statistics per station
            for i in input_gauge.keys(): #Iterate over rain gauges.
                a=0
                b=0
                leng=0
                thresholds_gauge=thresholds[i] #Get list of thresholds.
                sat=input_sat[i] #Get satellite rainfall time series.
                gauge=input_gauge[i] #Get gauge rainfall time series.
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]): #Adopt only the 
                        #5 considered years and only the gauge measurements between thresholds of minimum and maximum percentiles.
                        a=a+(sat[j][1]) #Sum of satellite estimates.
                        b=b+(gauge[j][1]) #Sum of gauge estimates.
                        leng=leng+1 #Total sample size.
                                
                mean_sat=a/leng #Calculate mean satellite estimate.
                mean_gauge=b/leng #Calculate mean gauge estimate.
                B=mean_sat/mean_gauge #Calculate bias ratio.
                stats_B_prod=stats_B_prod+[B] #Add bias ratio to the statistics list.

                a=0
                b=0
                leng=0 
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]): #Adopt only the 
                        #5 considered years and only the gauge measurements between thresholds of minimum and maximum percentiles.
                        a=a+((sat[j][1]-mean_sat)**2)
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        leng=leng+1
                                
                std_sat=(a/leng)**0.5 #Calculate std. deviation of satellite estimates.
                std_gauge=(b/leng)**0.5 #Calcute std. deviation of gauge estimates.
                Y=(std_sat/mean_sat)/(std_gauge/mean_gauge) # Calculate variability ratio.
                stats_Y_prod=stats_Y_prod+[Y] #Add variability ratio to the statistics list.

                a=0
                b=0
                c=0
                for j in range(len(sat)): #Iterate over time series.
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]): #Adopt only the 
                        #5 considered years and only the gauge measurements between thresholds of minimum and maximum percentiles.
                        a=a+((gauge[j][1]-mean_gauge)*(sat[j][1]-mean_sat))
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        c=c+((sat[j][1]-mean_sat)**2)
                R=a/((b**0.5)*(c**0.5)) #Calculate linear correlation.
                stats_R_prod=stats_R_prod+[R] #Add linear correlation to the statistics list.

                #Based on these measurements, calculate the KGE for each station:
                KGE=(1-(((R-1)**2+(B-1)**2+(Y-1)**2)**0.5)) #Calculate KGE.
                stats_KGE_prod=stats_KGE_prod+[KGE] #Add KGE to the statistics list.
                stats_add_e=[percentile,r,i,B,Y,R,KGE,leng] #Add all statistics to stats_add_e.
                stats_export.append(stats_add_e) #Append stats_add_e to stats_export.
            #Append the statistics list of each rainfall product to the general list.
            stats_B.append(stats_B_prod) #Bias ratio.
            stats_Y.append(stats_Y_prod) #Variability ratio.
            stats_R.append(stats_R_prod) #Linear correlation.
            stats_KGE.append(stats_KGE_prod) #Kling-Gupta efficiency.

        #Plot the boxplot
        bplot1=axs[0,column].boxplot(stats_B,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 0 (B).
        bplot2=axs[1,column].boxplot(stats_Y,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 1 (Y).
        bplot3=axs[2,column].boxplot(stats_R,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 2 (r).
        bplot4=axs[3,column].boxplot(stats_KGE,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2) #Plot row 3 (KGE).
        for bplot in (bplot1,bplot2,bplot3,bplot4):
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color) #Change color of boxplots.
        #Create intervals for plot
        for row in range(0,4):
            axs[row,column].plot([-2,13],[1,1],'k--',linewidth=1,zorder=1) #Add reference line, optimal values.
            if row==0:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.25)) #Define interval of ticks.
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.125)) #Define interval of ticks.
            elif row==1 or row==3:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.5)) #Define interval of ticks.
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.25)) #Define interval of ticks.
            else:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.2)) #Define interval of ticks.
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.1)) #Define interval of ticks.
            if column==2 and row==0:
                axs[row,column].set_title('Above the 90th percentile',fontsize=10) #Set title.
            elif column==1 and row==0:
                axs[row,column].set_title('70th to 90th percentile',fontsize=10) #Set title.
            elif column==0 and row==0:
                axs[row,column].set_title('50th to 70th percentile',fontsize=10) #Set title.
            elif column==1 and row==3:
                axs[row,column].set_xlabel('Rainfall products',fontsize=10) #Set labels.
            axs[row,column].set_xlim(0.5,11.5) #Set limits.
            axs[row,column].set_xticklabels(['GOr','GM3','GMm','GR3','GRm','IOr','IM3','IMm','IR3','IRm','IDW']) #Change name of x-axis labels.
            if row<3:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelbottom=False,bottom=False) #Edit graph.
            else:
                axs[row,column].tick_params(axis='x',which='major',labelsize=8,rotation=90) #Edit graph.
            if column>0:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelleft=False) #Edit graph.
            else:
                if row==0:
                    axs[row,column].set_ylabel('β',fontsize=10) #Set label.
                if row==1:
                    axs[row,column].set_ylabel("γ",fontsize=10) #Set label.                      
                elif row==2:
                    axs[row,column].set_ylabel('R',fontsize=10) #Set label.
                elif row==3:
                    axs[row,column].set_ylabel('KGE',fontsize=10) #Set label.
                axs[row,column].tick_params(axis='both',which='major',labelsize=8) #Edit graph.
    fig.set_size_inches(6,8) #Set size of the graph.
    fig.subplots_adjust(bottom=0.08,left=0.08,right=0.98,top=0.97,wspace=0.05,hspace=0.04) #Set margins of the graph.
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Plot_stats\KGE_stats_intensity.jpg',dpi=500) #Export graph.
    plt.close() #Close plot.
    
    #Export the statistics to a .cvs file.
    with open(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Statistics\KGE_stations_percentile.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_export)
    
#Open the files npy as dictionaries for daily, 3daily and monthly measurements, for all analyzed rainfall products.
prod_daily={}
prod_3daily={}
prod_monthly={}

#Import gauge IDW measurements.
prod_daily['Gauge IDW']=np.load("prec_gaugeIDW_daily.npy",allow_pickle=True).item()
prod_3daily['Gauge IDW']=np.load("prec_gaugeIDW_3daily.npy",allow_pickle=True).item()
prod_monthly['Gauge IDW']=np.load("prec_gaugeIDW_monthly.npy",allow_pickle=True).item()

#Import GSMaP.
prod_daily['GSMaP']=np.load("prec_GSMaP_daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP']=np.load("prec_GSMaP_3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP']=np.load("prec_GSMaP_monthly.npy",allow_pickle=True).item()

#Import GSMaP MBC 3-daily.
prod_daily['GSMaP MBC 3-daily']=np.load("prec_GSMaP_daily_MBC3daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP MBC 3-daily']=np.load("prec_GSMaP_3daily_MBC3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP MBC 3-daily']=np.load("prec_GSMaP_monthly_MBC3daily.npy",allow_pickle=True).item()

#Import GSMaP MBC monthly.
prod_daily['GSMaP MBC monthly']=np.load("prec_GSMaP_daily_MBCmonthly.npy",allow_pickle=True).item()
prod_3daily['GSMaP MBC monthly']=np.load("prec_GSMaP_3daily_MBCmonthly.npy",allow_pickle=True).item()
prod_monthly['GSMaP MBC monthly']=np.load("prec_GSMaP_monthly_MBCmonthly.npy",allow_pickle=True).item()

#Import GSMaP RIDW 3-daily.
prod_daily['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_daily_RIDW3daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_3daily_RIDW3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_monthly_RIDW3daily.npy",allow_pickle=True).item()

#Import GSMaP RIDW monthly.
prod_daily['GSMaP RIDW monthly']=np.load("prec_GSMaP_daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_3daily['GSMaP RIDW monthly']=np.load("prec_GSMaP_3daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_monthly['GSMaP RIDW monthly']=np.load("prec_GSMaP_monthly_RIDWmonthly.npy",allow_pickle=True).item()

#Import IMERG.
prod_daily['IMERG']=np.load("prec_IMERG_daily.npy",allow_pickle=True).item()
prod_3daily['IMERG']=np.load("prec_IMERG_3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG']=np.load("prec_IMERG_monthly.npy",allow_pickle=True).item()

#Import IMERG MBC 3-daily.
prod_daily['IMERG MBC 3-daily']=np.load("prec_IMERG_daily_MBC3daily.npy",allow_pickle=True).item()
prod_3daily['IMERG MBC 3-daily']=np.load("prec_IMERG_3daily_MBC3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG MBC 3-daily']=np.load("prec_IMERG_monthly_MBC3daily.npy",allow_pickle=True).item()

#Import IMERG MBC monthly.
prod_daily['IMERG MBC monthly']=np.load("prec_IMERG_daily_MBCmonthly.npy",allow_pickle=True).item()
prod_3daily['IMERG MBC monthly']=np.load("prec_IMERG_3daily_MBCmonthly.npy",allow_pickle=True).item()
prod_monthly['IMERG MBC monthly']=np.load("prec_IMERG_monthly_MBCmonthly.npy",allow_pickle=True).item()

#Import IMERG RIDW 3-daily.
prod_daily['IMERG RIDW 3-daily']=np.load("prec_IMERG_daily_RIDW3daily.npy",allow_pickle=True).item()
prod_3daily['IMERG RIDW 3-daily']=np.load("prec_IMERG_3daily_RIDW3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG RIDW 3-daily']=np.load("prec_IMERG_monthly_RIDW3daily.npy",allow_pickle=True).item()

#Import IMERG RIDW monthly.
prod_daily['IMERG RIDW monthly']=np.load("prec_IMERG_daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_3daily['IMERG RIDW monthly']=np.load("prec_IMERG_3daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_monthly['IMERG RIDW monthly']=np.load("prec_IMERG_monthly_RIDWmonthly.npy",allow_pickle=True).item()

#Import gauge measurements.
gauge_daily=np.load("prec_gauge_daily_yr.npy",allow_pickle=True).item()
gauge_3daily=np.load("prec_gauge_3daily_yr.npy",allow_pickle=True).item()
gauge_monthly=np.load("prec_gauge_monthly_yr.npy",allow_pickle=True).item()

#Import the adopted codes from Groups 1 and 2.
codes_yr=np.load("codes_yr.npy",allow_pickle=True).tolist()

#Call the functions
KGE(prod_daily,prod_3daily,prod_monthly,gauge_daily,gauge_3daily,gauge_monthly,codes_yr)
KGE_intensity(prod_3daily,gauge_3daily,codes_yr)
