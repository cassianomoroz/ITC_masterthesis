import os
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.ticker
import datetime
import seaborn as sns

#Set directory where the input files
directory=r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData"
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")

#KGE. Starting with B (bias ratio).
def KGE(input_sat_daily,input_sat_3daily,input_sat_monthly,input_gauge_daily,input_gauge_3daily,input_gauge_monthly,codes_yr):
    
    satproducts=['GSMaP','GSMaP MBC 3-daily','GSMaP MBC monthly','GSMaP RIDW 3-daily','GSMaP RIDW monthly','IMERG','IMERG MBC 3-daily','IMERG MBC monthly','IMERG RIDW 3-daily','IMERG RIDW monthly','Gauge IDW']
    timestep=['daily','3daily','monthly']
    stats_export=[['Timestep','Satellite product','Gauge station','B','Y','R','KGE','Sample size']]
    stats_export_all=[['Timestep','Satellite product','B','Y','R','KGE','Sample size']]
    #Create the graph elements
    font = {'size':10,'family': 'Calibri'}
    plt.rc('font', **font)
    fig,axs=plt.subplots(4,3,sharey='row',sharex=False)
    medianprops=dict(linewidth=0.7, color='black')
    boxprops=dict(linewidth=0.5, color="black")
    colors=sns.color_palette('tab10',10)
    colors=colors+[(1.0,1.0,1.0)]#Color white for IDW
    #Start the analysis
    for s in timestep:
        #Create lists to store the entire boxplot stats
        stats_B=[]
        stats_Y=[]
        stats_R=[]
        stats_KGE=[]
        for r in satproducts:
            #Create lists to store the boxplot stats per rainfall products
            stats_B_prod=[]
            stats_Y_prod=[]
            stats_R_prod=[]
            stats_KGE_prod=[]
            if s=="daily":
                column=0
                input_sat=input_sat_daily[r]
                input_gauge=input_gauge_daily
            elif s=="3daily":
                column=1
                input_sat=input_sat_3daily[r]
                input_gauge=input_gauge_3daily
            else:
                column=2
                input_sat=input_sat_monthly[r]
                input_gauge=input_gauge_monthly

            #Calculate the statistics per station
            for i in input_gauge.keys():
                a=0
                b=0
                leng=0
                sat=input_sat[i]
                gauge=input_gauge[i]
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr): #and math.isnan(gauge[j][1])==False
                        a=a+(sat[j][1])
                        b=b+(gauge[j][1])
                        leng=leng+1
                                
                mean_sat=a/leng
                mean_gauge=b/leng
                B=mean_sat/mean_gauge
                stats_B_prod=stats_B_prod+[B]

                a=0
                b=0
                leng=0 
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr):
                        a=a+((sat[j][1]-mean_sat)**2)
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        leng=leng+1
                                
                std_sat=(a/leng)**0.5
                std_gauge=(b/leng)**0.5
                Y=(std_sat/mean_sat)/(std_gauge/mean_gauge)
                stats_Y_prod=stats_Y_prod+[Y]

                a=0
                b=0
                c=0
                #Finally, calculate r
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr):
                        a=a+((gauge[j][1]-mean_gauge)*(sat[j][1]-mean_sat))
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        c=c+((sat[j][1]-mean_sat)**2)
                R=a/((b**0.5)*(c**0.5))
                stats_R_prod=stats_R_prod+[R]

                #Based on these measurements, calculate the KGE for each station:
                KGE=(1-(((R-1)**2+(B-1)**2+(Y-1)**2)**0.5))
                stats_KGE_prod=stats_KGE_prod+[KGE]
                stats_add_e=[s,r,i,B,Y,R,KGE,leng]
                stats_export.append(stats_add_e)

            #Append the boxplot list per rainfall product to the general list
            stats_B.append(stats_B_prod)
            stats_Y.append(stats_Y_prod)
            stats_R.append(stats_R_prod)
            stats_KGE.append(stats_KGE_prod)

            #Now, calculate the general statistics for the entire sample.
            a1=0
            a2=0
            a3=0
            b1=0
            b2=0
            b3=0
            c3=0
            leng1=0
            leng2=0
            for i in input_gauge.keys():
                leng=0
                sat=input_sat[i]
                gauge=input_gauge[i]
                #Start with B
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr):
                        a1=a1+(sat[j][1])
                        b1=b1+(gauge[j][1])
                        leng1=leng1+1
            #Final B
            mean_sat=a1/leng1
            mean_gauge=b1/leng1
            B=mean_sat/mean_gauge
            stats_add_e=[s,r,B]
            
            for i in input_gauge.keys():
                leng=0
                sat=input_sat[i]
                gauge=input_gauge[i]
                #Follow with Y
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr):
                        a2=a2+((sat[j][1]-mean_sat)**2)
                        b2=b2+((gauge[j][1]-mean_gauge)**2)
                        leng2=leng2+1
            #Final Y
            std_sat=(a2/leng2)**0.5
            std_gauge=(b2/leng2)**0.5
            Y=(std_sat/mean_sat)/(std_gauge/mean_gauge)
            stats_add_e=stats_add_e+[Y]

            for i in input_gauge.keys():
                leng=0
                sat=input_sat[i]
                gauge=input_gauge[i]
                #Finally, calculate r
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr):
                        a3=a3+((gauge[j][1]-mean_gauge)*(sat[j][1]-mean_sat))
                        b3=b3+((gauge[j][1]-mean_gauge)**2)
                        c3=c3+((sat[j][1]-mean_sat)**2)

            #Final R
            R=a3/((b3**0.5)*(c3**0.5))
            #Final KGE
            KGE=(1-(((R-1)**2+(B-1)**2+(Y-1)**2)**0.5))
            stats_add_e=stats_add_e+[R,KGE,leng2]
            stats_export_all.append(stats_add_e)
        #Plot the boxplot
        bplot1=axs[0,column].boxplot(stats_B,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot2=axs[1,column].boxplot(stats_Y,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot3=axs[2,column].boxplot(stats_R,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot4=axs[3,column].boxplot(stats_KGE,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        for bplot in (bplot1,bplot2,bplot3,bplot4):
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)
        #Create intervals for plot
        for row in range(0,4):
            axs[row,column].plot([-2,13],[1,1],'k--',linewidth=1,zorder=1)
            if row==0:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.1))
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.05))
            else:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.2))
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.1))
            if column==2 and row==0:
                axs[row,column].set_title('Monthly',fontsize=10)
            elif column==1 and row==0:
                axs[row,column].set_title('3-Daily',fontsize=10)
            elif column==0 and row==0:
                axs[row,column].set_title('Daily',fontsize=10)
            elif column==1 and row==3:
                axs[row,column].set_xlabel('Rainfall products',fontsize=10)
            #axs[row,column].invert_xaxis()
            axs[row,column].set_xlim(0.5,11.5)
            axs[row,column].set_xticklabels(['GOr','GM3','GMm','GR3','GRm','IOr','IM3','IMm','IR3','IRm','IDW'])
            if row<3:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelbottom=False,bottom=False)
            else:
                axs[row,column].tick_params(axis='x',which='major',labelsize=8,rotation=90)
            if column>0:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelleft=False)
            else:
                if row==0:
                    axs[row,column].set_ylabel('β',fontsize=10)
                if row==1:
                    axs[row,column].set_ylabel("γ",fontsize=10)                        
                elif row==2:
                    axs[row,column].set_ylabel('R',fontsize=10)
                elif row==3:
                    axs[row,column].set_ylabel('KGE',fontsize=10)
                axs[row,column].tick_params(axis='both',which='major',labelsize=8)
    fig.set_size_inches(6,8)
    fig.subplots_adjust(bottom=0.08,left=0.08,right=0.98,top=0.97,wspace=0.05,hspace=0.04)
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Plot_stats\KGE_stats.jpg',dpi=500)
    plt.close()
    #Export the statistics for each station and for all sample.
    with open(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Statistics\KGE_stations_"+code+".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_export)
    with open(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Statistics\KGE_total_"+code+".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_export_all)

def KGE_intensity(input_sat_all,input_gauge,codes_yr):
    #First, extract the rainfall intensity per station related to the 70th and 90th percentile
    thresholds={}
    for i in input_gauge.keys():
        thresholds_append=[]
        for percentile in [0.5,0.7,0.9,1.0]:
            rainfall=[]
            gauge=input_gauge[i]
            for j in range(len(gauge)):
                if gauge[j][0].year in codes_yr:
                    rainfall=rainfall+[gauge[j][1]]
            rainfall.sort()
            freq=[]
            for j in range(len(rainfall)):
                freq=((j+1)/len(rainfall))
                if freq>=percentile:
                    rainfreq=rainfall[j]
                    break
            thresholds_append.append([percentile,rainfreq])
        thresholds[i]=thresholds_append

    #Start calculating the statistical parameters
    satproducts=['GSMaP','GSMaP MBC 3-daily','GSMaP MBC monthly','GSMaP RIDW 3-daily','GSMaP RIDW monthly','IMERG','IMERG MBC 3-daily','IMERG MBC monthly','IMERG RIDW 3-daily','IMERG RIDW monthly','Gauge IDW']
    #Create the graph elements
    font = {'size':10,'family': 'Calibri'}
    plt.rc('font', **font)
    fig,axs=plt.subplots(4,3,sharey='row',sharex=False)
    medianprops=dict(linewidth=0.7, color='black')
    boxprops=dict(linewidth=0.5, color="black")
    colors=sns.color_palette('tab10',10)
    colors=colors+[(1.0,1.0,1.0)]#Color white for IDW
    stats_export=[['Percentile','Satellite product','Gauge station','B','Y','R','KGE','Sample size']]
    #Create the list for the percentiles:
    for percentile in [0.7,0.9,1]:
        #Create lists to store the entire boxplot stats
        stats_B=[]
        stats_Y=[]
        stats_R=[]
        stats_KGE=[]
        for r in satproducts:
            #Create lists to store the boxplot stats per rainfall products
            stats_B_prod=[]
            stats_Y_prod=[]
            stats_R_prod=[]
            stats_KGE_prod=[]
            column=1
            input_sat=input_sat_all[r]
            if percentile==0.7:
                column=0
                indexmax=1
                indexmin=0
            elif percentile==0.9:
                column=1
                indexmax=2
                indexmin=1
            else:
                column=2
                indexmax=3
                indexmin=2
            #Calculate the statistics per station
            for i in input_gauge.keys():
                a=0
                b=0
                leng=0
                thresholds_gauge=thresholds[i]
                sat=input_sat[i]
                gauge=input_gauge[i]
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]):
                        a=a+(sat[j][1])
                        b=b+(gauge[j][1])
                        leng=leng+1
                                
                mean_sat=a/leng
                mean_gauge=b/leng
                B=mean_sat/mean_gauge
                stats_B_prod=stats_B_prod+[B]

                a=0
                b=0
                leng=0 
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]):
                        a=a+((sat[j][1]-mean_sat)**2)
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        leng=leng+1
                                
                std_sat=(a/leng)**0.5
                std_gauge=(b/leng)**0.5
                Y=(std_sat/mean_sat)/(std_gauge/mean_gauge)
                stats_Y_prod=stats_Y_prod+[Y]

                a=0
                b=0
                c=0
                #Finally, calculate r
                for j in range(len(sat)):
                    if (sat[j][0].year in codes_yr) and (gauge[j][1]>thresholds_gauge[indexmin][1]) and (gauge[j][1]<=thresholds_gauge[indexmax][1]):
                        a=a+((gauge[j][1]-mean_gauge)*(sat[j][1]-mean_sat))
                        b=b+((gauge[j][1]-mean_gauge)**2)
                        c=c+((sat[j][1]-mean_sat)**2)
                R=a/((b**0.5)*(c**0.5))
                stats_R_prod=stats_R_prod+[R]

                #Based on these measurements, calculate the KGE for each station:
                KGE=(1-(((R-1)**2+(B-1)**2+(Y-1)**2)**0.5))
                stats_KGE_prod=stats_KGE_prod+[KGE]
                stats_add_e=[percentile,r,i,B,Y,R,KGE,leng]
                stats_export.append(stats_add_e)
            #Append the boxplot list per rainfall product to the general list
            stats_B.append(stats_B_prod)
            stats_Y.append(stats_Y_prod)
            stats_R.append(stats_R_prod)
            stats_KGE.append(stats_KGE_prod)

        #Plot the boxplot
        bplot1=axs[0,column].boxplot(stats_B,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot2=axs[1,column].boxplot(stats_Y,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot3=axs[2,column].boxplot(stats_R,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        bplot4=axs[3,column].boxplot(stats_KGE,showfliers=False,medianprops=medianprops,boxprops=boxprops,patch_artist=True,zorder=2)
        for bplot in (bplot1,bplot2,bplot3,bplot4):
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)
        #Create intervals for plot
        for row in range(0,4):
            axs[row,column].plot([-2,13],[1,1],'k--',linewidth=1,zorder=1)
            if row==0:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.25))
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.125))
            elif row==1 or row==3:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.5))
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.25))
            else:
                axs[row,column].yaxis.set_major_locator(MultipleLocator(0.2))
                axs[row,column].yaxis.set_minor_locator(MultipleLocator(0.1))
            if column==2 and row==0:
                axs[row,column].set_title('Above the 90th percentile',fontsize=10)
            elif column==1 and row==0:
                axs[row,column].set_title('70th to 90th percentile',fontsize=10)
            elif column==0 and row==0:
                axs[row,column].set_title('50th to 70th percentile',fontsize=10)
            elif column==1 and row==3:
                axs[row,column].set_xlabel('Rainfall products',fontsize=10)
            axs[row,column].set_xlim(0.5,11.5)
            axs[row,column].set_xticklabels(['GOr','GM3','GMm','GR3','GRm','IOr','IM3','IMm','IR3','IRm','IDW'])
            if row<3:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelbottom=False,bottom=False)
            else:
                axs[row,column].tick_params(axis='x',which='major',labelsize=8,rotation=90)
            if column>0:
                axs[row,column].tick_params(axis='both',which='major',labelsize=8,labelleft=False)
            else:
                if row==0:
                    axs[row,column].set_ylabel('β',fontsize=10)
                if row==1:
                    axs[row,column].set_ylabel("γ",fontsize=10)                        
                elif row==2:
                    axs[row,column].set_ylabel('R',fontsize=10)
                elif row==3:
                    axs[row,column].set_ylabel('KGE',fontsize=10)
                axs[row,column].tick_params(axis='both',which='major',labelsize=8)
    fig.set_size_inches(6,8)
    fig.subplots_adjust(bottom=0.08,left=0.08,right=0.98,top=0.97,wspace=0.05,hspace=0.04)
    fig.savefig(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Plot_stats\KGE_stats_intensity.jpg',dpi=500)
    plt.close()

    with open(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\Statistics\KGE_stations_percentile.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_export)

    return thresholds
    
#Open the files npy as dictionaries for daily, 3daily and monthly measurements, for all analyzed rainfall products
prod_daily={}
prod_3daily={}
prod_monthly={}

#Import gauge IDW measurements
prod_daily['Gauge IDW']=np.load("prec_gaugeIDW_daily.npy",allow_pickle=True).item()
prod_3daily['Gauge IDW']=np.load("prec_gaugeIDW_3daily.npy",allow_pickle=True).item()
prod_monthly['Gauge IDW']=np.load("prec_gaugeIDW_monthly.npy",allow_pickle=True).item()

#Import GSMaP
prod_daily['GSMaP']=np.load("prec_GSMaP_daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP']=np.load("prec_GSMaP_3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP']=np.load("prec_GSMaP_monthly.npy",allow_pickle=True).item()

#Import GSMaP MBC 3-daily
prod_daily['GSMaP MBC 3-daily']=np.load("prec_GSMaP_daily_MBC3daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP MBC 3-daily']=np.load("prec_GSMaP_3daily_MBC3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP MBC 3-daily']=np.load("prec_GSMaP_monthly_MBC3daily.npy",allow_pickle=True).item()

#Import GSMaP MBC monthly
prod_daily['GSMaP MBC monthly']=np.load("prec_GSMaP_daily_MBCmonthly.npy",allow_pickle=True).item()
prod_3daily['GSMaP MBC monthly']=np.load("prec_GSMaP_3daily_MBCmonthly.npy",allow_pickle=True).item()
prod_monthly['GSMaP MBC monthly']=np.load("prec_GSMaP_monthly_MBCmonthly.npy",allow_pickle=True).item()

#Import GSMaP RIDW 3-daily
prod_daily['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_daily_RIDW3daily.npy",allow_pickle=True).item()
prod_3daily['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_3daily_RIDW3daily.npy",allow_pickle=True).item()
prod_monthly['GSMaP RIDW 3-daily']=np.load("prec_GSMaP_monthly_RIDW3daily.npy",allow_pickle=True).item()

#Import GSMaP RIDW monthly
prod_daily['GSMaP RIDW monthly']=np.load("prec_GSMaP_daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_3daily['GSMaP RIDW monthly']=np.load("prec_GSMaP_3daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_monthly['GSMaP RIDW monthly']=np.load("prec_GSMaP_monthly_RIDWmonthly.npy",allow_pickle=True).item()

#Import IMERG
prod_daily['IMERG']=np.load("prec_IMERG_daily.npy",allow_pickle=True).item()
prod_3daily['IMERG']=np.load("prec_IMERG_3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG']=np.load("prec_IMERG_monthly.npy",allow_pickle=True).item()

#Import IMERG MBC 3-daily
prod_daily['IMERG MBC 3-daily']=np.load("prec_IMERG_daily_MBC3daily.npy",allow_pickle=True).item()
prod_3daily['IMERG MBC 3-daily']=np.load("prec_IMERG_3daily_MBC3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG MBC 3-daily']=np.load("prec_IMERG_monthly_MBC3daily.npy",allow_pickle=True).item()

#Import IMERG MBC monthly
prod_daily['IMERG MBC monthly']=np.load("prec_IMERG_daily_MBCmonthly.npy",allow_pickle=True).item()
prod_3daily['IMERG MBC monthly']=np.load("prec_IMERG_3daily_MBCmonthly.npy",allow_pickle=True).item()
prod_monthly['IMERG MBC monthly']=np.load("prec_IMERG_monthly_MBCmonthly.npy",allow_pickle=True).item()

#Import IMERG RIDW 3-daily
prod_daily['IMERG RIDW 3-daily']=np.load("prec_IMERG_daily_RIDW3daily.npy",allow_pickle=True).item()
prod_3daily['IMERG RIDW 3-daily']=np.load("prec_IMERG_3daily_RIDW3daily.npy",allow_pickle=True).item()
prod_monthly['IMERG RIDW 3-daily']=np.load("prec_IMERG_monthly_RIDW3daily.npy",allow_pickle=True).item()

#Import IMERG RIDW monthly
prod_daily['IMERG RIDW monthly']=np.load("prec_IMERG_daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_3daily['IMERG RIDW monthly']=np.load("prec_IMERG_3daily_RIDWmonthly.npy",allow_pickle=True).item()
prod_monthly['IMERG RIDW monthly']=np.load("prec_IMERG_monthly_RIDWmonthly.npy",allow_pickle=True).item()

#Import gauge measurements
gauge_daily=np.load("prec_gauge_daily_yr.npy",allow_pickle=True).item()
gauge_3daily=np.load("prec_gauge_3daily_yr.npy",allow_pickle=True).item()
gauge_monthly=np.load("prec_gauge_monthly_yr.npy",allow_pickle=True).item()

#Import the adopted codes
codes_yr=np.load("codes_yr.npy",allow_pickle=True).tolist()

#Call the functions
#KGE(prod_daily,prod_3daily,prod_monthly,gauge_daily,gauge_3daily,gauge_monthly,codes_yr)
x=KGE_intensity(prod_3daily,gauge_3daily,codes_yr)
#Freq90th(gauge_3daily,codes_yr)
