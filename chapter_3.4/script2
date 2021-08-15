import csv
import re
import datetime
import numpy as np
import os

#Import the names of the files from PERSIANN
i=0
input_names=[] #Create a list to store the codes of the stations and associate these codes with the dictionary
directory=r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\SatelliteRainfall\GSMaP_V5_6\2000_2020'
for entry in os.scandir(directory):
    input_names.append(entry.name)

os.chdir(r'C:\Users\cassi\Desktop\Academia\ITC\Thesis\Secondary_data\SatelliteRainfall\GSMaP_V5_6\2000_2020')
GSMaP=[]
for i in input_names:
    with open(i, newline='') as f:
        reader = csv.reader(f)
        GSMaP_extend = list(reader)
        GSMaP_extend = GSMaP_extend[1:]       
        GSMaP.extend(GSMaP_extend)

prec_GSMaP={}
prec1=[]
prec2=[]
prec3=[]
prec4=[]
prec5=[]
prec6=[]
prec7=[]
prec8=[]
prec9=[]
prec10=[]
prec11=[]
prec12=[]
prec13=[]
prec14=[]
prec15=[]
prec16=[]
prec17=[]
prec18=[]
prec19=[]
prec20=[]
prec21=[]
prec22=[]
prec23=[]
prec24=[]
prec25=[]
prec26=[]
prec27=[]
prec28=[]
prec29=[]
prec30=[]
prec31=[]
prec32=[]
prec33=[]
prec34=[]
prec35=[]
prec36=[]
prec37=[]
prec38=[]
j=1
for i in range(len(GSMaP)):
    if GSMaP[i][2]=="":
        if j==1:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec1.append(append_list)
            j=j+1
        elif j==2:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec2.append(append_list)
            j=j+1
        elif j==3:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec3.append(append_list)
            j=j+1
        elif j==4:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec4.append(append_list)
            j=j+1
        elif j==5:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec5.append(append_list)
            j=j+1
        elif j==6:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec6.append(append_list)
            j=j+1
        elif j==7:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec7.append(append_list)
            j=j+1
        elif j==8:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec8.append(append_list)
            j=j+1
        elif j==9:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec9.append(append_list)
            j=j+1
        elif j==10:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec10.append(append_list)
            j=j+1
        elif j==11:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec11.append(append_list)
            j=j+1
        elif j==12:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec12.append(append_list)
            j=j+1
        elif j==13:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec13.append(append_list)
            j=j+1
        elif j==14:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec14.append(append_list)
            j=j+1
        elif j==15:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec15.append(append_list)
            j=j+1
        elif j==16:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec16.append(append_list)
            j=j+1
        elif j==17:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec17.append(append_list)
            j=j+1
        elif j==18:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec18.append(append_list)
            j=j+1
        elif j==19:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec19.append(append_list)
            j=j+1
        elif j==20:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec20.append(append_list)
            j=j+1
        elif j==21:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec21.append(append_list)
            j=j+1
        elif j==22:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec22.append(append_list)
            j=j+1
        elif j==23:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec23.append(append_list)
            j=j+1
        elif j==24:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec24.append(append_list)
            j=j+1
        elif j==25:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec25.append(append_list)
            j=j+1
        elif j==26:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec26.append(append_list)
            j=j+1
        elif j==27:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec27.append(append_list)
            j=j+1
        elif j==28:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec28.append(append_list)
            j=j+1
        elif j==29:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec29.append(append_list)
            j=j+1
        elif j==30:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec30.append(append_list)
            j=j+1
        elif j==31:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec31.append(append_list)
            j=j+1
        elif j==32:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec32.append(append_list)
            j=j+1
        elif j==33:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec33.append(append_list)
            j=j+1
        elif j==34:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec34.append(append_list)
            j=j+1
        elif j==35:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec35.append(append_list)
            j=j+1
        elif j==36:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec36.append(append_list)
            j=j+1
        elif j==37:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec37.append(append_list)
            j=j+1
        else:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=-1
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec38.append(append_list)
            j=1
    else:
        if j==1:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec1.append(append_list)
            j=j+1
        elif j==2:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec2.append(append_list)
            j=j+1
        elif j==3:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec3.append(append_list)
            j=j+1
        elif j==4:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec4.append(append_list)
            j=j+1
        elif j==5:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec5.append(append_list)
            j=j+1
        elif j==6:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec6.append(append_list)
            j=j+1
        elif j==7:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec7.append(append_list)
            j=j+1
        elif j==8:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec8.append(append_list)
            j=j+1
        elif j==9:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec9.append(append_list)
            j=j+1
        elif j==10:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec10.append(append_list)
            j=j+1
        elif j==11:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec11.append(append_list)
            j=j+1
        elif j==12:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec12.append(append_list)
            j=j+1
        elif j==13:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec13.append(append_list)
            j=j+1
        elif j==14:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec14.append(append_list)
            j=j+1
        elif j==15:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec15.append(append_list)
            j=j+1
        elif j==16:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec16.append(append_list)
            j=j+1
        elif j==17:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec17.append(append_list)
            j=j+1
        elif j==18:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec18.append(append_list)
            j=j+1
        elif j==19:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec19.append(append_list)
            j=j+1
        elif j==20:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec20.append(append_list)
            j=j+1
        elif j==21:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec21.append(append_list)
            j=j+1
        elif j==22:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec22.append(append_list)
            j=j+1
        elif j==23:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec23.append(append_list)
            j=j+1
        elif j==24:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec24.append(append_list)
            j=j+1
        elif j==25:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec25.append(append_list)
            j=j+1
        elif j==26:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec26.append(append_list)
            j=j+1
        elif j==27:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec27.append(append_list)
            j=j+1
        elif j==28:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec28.append(append_list)
            j=j+1
        elif j==29:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec29.append(append_list)
            j=j+1
        elif j==30:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec30.append(append_list)
            j=j+1
        elif j==31:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec31.append(append_list)
            j=j+1
        elif j==32:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec32.append(append_list)
            j=j+1
        elif j==33:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec33.append(append_list)
            j=j+1
        elif j==34:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec34.append(append_list)
            j=j+1
        elif j==35:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec35.append(append_list)
            j=j+1
        elif j==36:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec36.append(append_list)
            j=j+1
        elif j==37:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec37.append(append_list)
            j=j+1
        else:
            date=re.split("T|:|-",GSMaP[i][1])
            prec=float(GSMaP[i][2])
            append_list=[datetime.date(int(date[0]),int(date[1]),int(date[2])),
                (int(date[3])+(int(date[4])/60)),prec]
            prec38.append(append_list)
            j=1
prec1.sort(key = lambda x: x[0])
prec2.sort(key = lambda x: x[0])
prec3.sort(key = lambda x: x[0])
prec4.sort(key = lambda x: x[0])
prec5.sort(key = lambda x: x[0])
prec6.sort(key = lambda x: x[0])
prec7.sort(key = lambda x: x[0])
prec8.sort(key = lambda x: x[0])
prec9.sort(key = lambda x: x[0])
prec10.sort(key = lambda x: x[0])
prec11.sort(key = lambda x: x[0])
prec12.sort(key = lambda x: x[0])
prec13.sort(key = lambda x: x[0])
prec14.sort(key = lambda x: x[0])
prec15.sort(key = lambda x: x[0])
prec16.sort(key = lambda x: x[0])
prec17.sort(key = lambda x: x[0])
prec18.sort(key = lambda x: x[0])
prec19.sort(key = lambda x: x[0])
prec20.sort(key = lambda x: x[0])
prec21.sort(key = lambda x: x[0])
prec22.sort(key = lambda x: x[0])
prec23.sort(key = lambda x: x[0])
prec24.sort(key = lambda x: x[0])
prec25.sort(key = lambda x: x[0])
prec26.sort(key = lambda x: x[0])
prec27.sort(key = lambda x: x[0])
prec28.sort(key = lambda x: x[0])
prec29.sort(key = lambda x: x[0])
prec30.sort(key = lambda x: x[0])
prec31.sort(key = lambda x: x[0])
prec32.sort(key = lambda x: x[0])
prec33.sort(key = lambda x: x[0])
prec34.sort(key = lambda x: x[0])
prec35.sort(key = lambda x: x[0])
prec36.sort(key = lambda x: x[0])
prec37.sort(key = lambda x: x[0])
prec38.sort(key = lambda x: x[0])

#Replace missing values (negatives) for 0:
def remove_na(prec):
    prec_v1=[]
    for i in range(len(prec)):
        if prec[i][2]<0:
            prec_append=[prec[i][0],prec[i][1],0.0]
        else:
            prec_append=prec[i]
        prec_v1.append(prec_append)
    return prec_v1

prec_GSMaP["Rainfall_02648001"]=remove_na(prec1)
prec_GSMaP["Rainfall_02648002"]=remove_na(prec2)
prec_GSMaP["Rainfall_02648038"]=remove_na(prec3)
prec_GSMaP["Rainfall_02649001"]=remove_na(prec4)
prec_GSMaP["Rainfall_02649002"]=remove_na(prec5)
prec_GSMaP["Rainfall_02649003"]=remove_na(prec6)
prec_GSMaP["Rainfall_02649004"]=remove_na(prec7)
prec_GSMaP["Rainfall_02649005"]=remove_na(prec8)
prec_GSMaP["Rainfall_02649007"]=remove_na(prec9)
prec_GSMaP["Rainfall_02649008"]=remove_na(prec10)
prec_GSMaP["Rainfall_02649009"]=remove_na(prec11)
prec_GSMaP["Rainfall_02649010"]=remove_na(prec12)
prec_GSMaP["Rainfall_02649017"]=remove_na(prec13)
prec_GSMaP["Rainfall_02649053"]=remove_na(prec14)
prec_GSMaP["Rainfall_02649058"]=remove_na(prec15)
prec_GSMaP["Rainfall_02649061"]=remove_na(prec16)
prec_GSMaP["Rainfall_02649065"]=remove_na(prec17)
prec_GSMaP["Rainfall_02650022"]=remove_na(prec18)
prec_GSMaP["Rainfall_02650023"]=remove_na(prec19)
prec_GSMaP["Rainfall_02748000"]=remove_na(prec20)
prec_GSMaP["Rainfall_02749000"]=remove_na(prec21)
prec_GSMaP["Rainfall_02749001"]=remove_na(prec22)
prec_GSMaP["Rainfall_02749002"]=remove_na(prec23)
prec_GSMaP["Rainfall_02749003"]=remove_na(prec24)
prec_GSMaP["Rainfall_02749005"]=remove_na(prec25)
prec_GSMaP["Rainfall_02749006"]=remove_na(prec26)
prec_GSMaP["Rainfall_02749007"]=remove_na(prec27)
prec_GSMaP["Rainfall_02749013"]=remove_na(prec28)
prec_GSMaP["Rainfall_02749016"]=remove_na(prec29)
prec_GSMaP["Rainfall_02749017"]=remove_na(prec30)
prec_GSMaP["Rainfall_02749033"]=remove_na(prec31)
prec_GSMaP["Rainfall_02749037"]=remove_na(prec32)
prec_GSMaP["Rainfall_02749039"]=remove_na(prec33)
prec_GSMaP["Rainfall_02749041"]=remove_na(prec34)
prec_GSMaP["Rainfall_02749045"]=remove_na(prec35)
prec_GSMaP["Rainfall_02749046"]=remove_na(prec36)
prec_GSMaP["Rainfall_02750014"]=remove_na(prec37)
prec_GSMaP["Rainfall_02750021"]=remove_na(prec38)

#Aggregate the precipitation per day and per month. First per day. Hours in satellites are defined at UTC.
#A day in Brasilia time (UTC-3) goes from 7 am until 7 am from the following days, because manual measurements
#are made at 7 am. Therefore, the PERSIANN day goes from 10 am until 10 am from the following day.
import datetime

prec_GSMaP_daily={}
for i in prec_GSMaP.keys():
    station_list=prec_GSMaP[i]
    date_list=[row[0] for row in station_list]
    prec_list=[row[2] for row in station_list]
    prec_daily=[]
    dateuse=0
    for j in range(len(date_list)-10):
        if prec_list[j+10]<0:
            dateuse="No"
        elif prec_list[j+10]>=0 and dateuse!=0:
            dateuse="Yes"
        if j==0:
            prec=prec_list[j+10] #10 hours more than midnight
        elif date_list[j]==date_list[j-1]:
            prec=prec+prec_list[j+10]
        elif j==(len(date_list)-10):
            prec_append=[date_list[j],prec,dateuse]
            prec_daily.append(prec_append)
            prec=0
            dateuse=0
        else:
            prec_append=[date_list[j-1],prec,dateuse] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_daily.append(prec_append)
            prec=0
            dateuse=0
    prec_daily_v1=[]
    for j in range(len(prec_daily)):
        if prec_daily[j][2]=="Yes":
            prec_daily_v1.append(prec_daily[j])
    prec_GSMaP_daily[i]=prec_daily

#Create a datelist:
dates=[]
for day in range(0,7305): #Increase days 1 by 1 until the present date
    date = (datetime.date(2000,7,1) + datetime.timedelta(days=day))
    dates.append(date)

#Create a new dictionary only with the desired dates.
prec_GSMaP_daily_v1={}
for i in prec_GSMaP_daily.keys():
    station_list=prec_GSMaP_daily[i]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_daily=[]
    for j in range(len(date_list)):
        if date_list[j] in dates:
            append=[date_list[j],prec_list[j]]
            prec_daily.append(append)
    prec_GSMaP_daily_v1[i]=prec_daily

#Aggregate 3-daily
prec_GSMaP_3daily={}
for i in prec_GSMaP_daily_v1.keys():
    station_list=prec_GSMaP_daily_v1[i]
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
    prec_GSMaP_3daily[i]=prec_3daily

#Aggregate monthly
prec_GSMaP_monthly={}
for i in prec_GSMaP_daily_v1.keys():
    station_list=prec_GSMaP_daily_v1[i]
    date_list=[row[0] for row in station_list]
    prec_list=[row[1] for row in station_list]
    prec_monthly=[]
    prec=0
    for j in range(len(date_list)):
        if j==0:
            prec=prec_list[j] #10 hours more than midnight
        elif j==len(date_list)-1:
            prec=prec+prec_list[j]
            date=datetime.date(int(date_list[j].year),int(date_list[j].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
            prec=0
        elif date_list[j].month==date_list[j-1].month and j!=len(date_list)-1:
            prec=prec+prec_list[j]          
        else:
            date=datetime.date(int(date_list[j-1].year),int(date_list[j-1].month),1)
            prec_append=[date,prec] #Get the date of the previous day and relate it with the accumulated precipitation.
            prec_monthly.append(prec_append)
            prec=0
    prec_GSMaP_monthly[i]=prec_monthly
    
os.chdir(r"C:\Users\cassi\Desktop\Academia\ITC\Thesis\Edit_data\Rainfall\SatelliteValidation\InputData")
np.save('prec_GSMaP_daily.npy', prec_GSMaP_daily_v1)
np.save('prec_GSMaP_3daily.npy', prec_GSMaP_3daily)
np.save('prec_GSMaP_monthly.npy', prec_GSMaP_monthly)
