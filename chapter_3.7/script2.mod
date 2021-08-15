########################################################
# Model: Saxtons pedotransfer function SWAP model 2005 #                                  
# input data SOILGRIDS.ORG                             #
# Date:  20/09/2020                                    #
# Version: 1.2                                         #
# Author:  V Jetten & DP Shrestha @ ITC                #
# Editted by Cassiano Bastos Moroz 03/03/21            #               
########################################################

### VERSION FOR THE OPENLISEM online TUTORIAL!!!

### assumes new version of soilgrids with g/kg values

#binding
 
  S = S_$1.map;  # sand g/kg
  C = C_$1.map;  # clay g/kg
  Si = Si_$1.map; # silt g/kg
  OC = OC_$1.map;  # organic carbon in dg/kg
  Gravel = Gravel_$1.map; # coarse fragments cm3/dm3, 
  bd = BD_$1.map;   # bulk density in 

  cover=vegcover.map; #Divide it by 100 because it is expressed in percentage
  # optional, can use for bulkdensity, higher cover is more structure, lower density 
  
  standardBD = scalar(1470); # standard bulk dens assumed by saxton and rawls. High! 1350 would be better

  fractionmoisture = scalar(0.79);  #inital moisture as fraction between porosity and field capacity 
                                   # 0 = init moist is at FC, 1.0 = init moist is at porosity

  # output maps
  POROSITY = thetas1.0_$1.map;  	#porosity (cm3/cm3)
  Ksat = ksat1.0_$1.map;     		# ksat in mm/h
  initmoist = thetai0.79_$1.map; 	# inital moisture (cm3/cm3)
  psi= psi1.0_$1.map; 		# suction with init moisture in cm, used in LISEM
  Densityfactor = densfact1.0_$1.map;
  
#initial

  # prep data
  S = S/1000; # from g/kg to fraction
  C = C/1000;
  OC= (OC/10000)*100; # conversion OC from dg/kg to percentage
  OM = OC*1.73; #/2.0;  #conversion org carbon to org matter factor 2
  
  Densityfactor = (1-0.1*cover);
  # density factor is 1.0, but could be made lower for organic soils and higher for compacted urban areas.

  bdsg=bd*10;           #bulkdensity cg/m3 to kg/m3
  Gravel = Gravel/1000; # from cm3/dm3 (1000 cc in a liter)
  report Densityfactor = bdsg/standardBD*(1-0.1*cover);
  
  #scalar(1.0); # range 0.9 to 1.15
  # calculated as the bulk density from soilgrids divided by some standard bd
  # multiple regression from excel 

# wilting point stuff
  M1500 =-0.024*S+0.487*C+0.006*OM+0.005*S*OM-0.013*C*OM+0.068*S*C+0.031;
  M1500adj =M1500+0.14*M1500-0.02;
# field capacity stuff
  M33  =-0.251*S+0.195*C+0.011*OM+0.006*S*OM-0.027*C*OM+0.452*S*C+0.299;
  M33adj = M33+(1.283*M33*M33-0.374*M33-0.015);
# porosity - FC
  PM33    = 0.278*S+0.034*C+0.022*OM-0.018*S*OM-0.027*C*OM-0.584*S*C+0.078;
  PM33adj = PM33+(0.636*PM33-0.107);
# porosity
  SatPM33 = M33adj + PM33adj;
  SatSadj = -0.097*S+0.043;
  SadjSat = SatPM33  + SatSadj;
  Dens_om = (1-SadjSat)*2.65;
  Dens_comp = Dens_om * Densityfactor;
  PORE_comp =(1-Dens_om/2.65)-(1-Dens_comp/2.65);
  M33comp = M33adj + 0.2*PORE_comp;

  #output maps 
  report POROSITY = 1-(Dens_comp/2.65);
  PoreMcomp = POROSITY-M33comp;
  LAMBDA = (ln(M33comp)-ln(M1500adj))/(ln(1500)-ln(33));
  GravelRedKsat =(1-Gravel)/(1-Gravel*(1-1.5*(Dens_comp/2.65)));
  
  report Ksat = max(0.0, 1930*(PoreMcomp)**(3-LAMBDA)*GravelRedKsat);
  BD = Gravel*2.65+(1-Gravel)*Dens_comp;
  WP = M1500adj;
  FC = M33adj;
  PAW = (M33adj - M1500adj)*(1-Gravel);
  report initmoist= fractionmoisture*POROSITY+ (1-fractionmoisture)*FC;

  bB = (ln(1500)-ln(33))/(ln(FC)-ln(WP));  
  aA = exp(ln(33)+bB*ln(FC));
  report psi= aA * initmoist**-bB *100/9.8; 
