#! --matrixtable --lddin --lddcut

##########################################################################
# PCRASTER script for the generation of a LISEM input database           #
# CHARIM project                                                         #
# (c) Victor Jetten 03/17/15                                             #
# Faculty ITC, Twente University, the Netherlands                        #
# v.g.jetten@utwente.nl                                                  #
# Editted by Cassiano Bastos Moroz 03/03/21                              #
##########################################################################

#########################
### ITAJAI DATABASE   ###
#########################

#binding
  
  ##################
  ### input maps ###
  ##################

  mask = mask.map; #Mask of the watershed (extracted from DEM in the limits of Blumenau)

  DEM = DEM_50m.map; #DEM to be adoped (resampled 1m to 50m SIGSC nearest neighborhood)

  unitmapbase = luse2011.map; #Land-use types, extracted for year 2011 from MAPBIOMAS, resampled to DEM

  #barriers = zero.map; #In m, anything that obstructs floods. Will be added to the DEM
  #Barriers not adopted because DEM will be modified to include dams (can be adopted in scenarios)

  rivers = chanmask.map; #Mask with the river system, generated from the DEM

  mainout = outlet.map; #Forced outlet, delimited manually in the limits of Blumenau

  outpointuser = mainout.map; #Points to generate output hydrographs
  #Points defined in the locations of the discharge gauge stations from ANA

  house_cover = building.map; #Housing density fraction (0-1)
  #Adopted from MAPBIOMAS for the year 2011, houses as all areas with urban infrastructure

  hard_surf = hard_surf.map; #Hard surfaces (0-1) such as airports, parking lots, etc.
  #Adopted from MAPBIOMAS for the year 2011, hard surfaces as all areas with urban infrastructure

  ndvi = ndvi.map; #NDVI map, obtained from GEE (check from where)

  ######################################
  ### hydrological data input tables ###
  ######################################

  lutbl = luseTBL.txt;     # land use surface properties
  # col 1=Micro roughness; 2 = manning's; 3 = plant height; 4 = cover

  ############################################
  ### output LISEM database, default names ###
  ############################################

  #This section represents the database that will be generated

  # basic topography related maps
  DEMm = dem.map;            # adjusted dem
  #barriersc = barriers.map; # Barriers map (not adopted)
  Ldd = ldd.map;             # Local Drain Direction surface runoff
  grad = grad.map;           # slope, sine
  landuse = landunit.map;    # land units combined soil and vegetation

  # vegetation maps
  coverc= per.map;           # cover fraction (0-1)
  lai= lai.map;              # leaf area index (m2/m2) for interception storage (extracted from NDVI)
  cropheight= ch.map;        # plant height in m, for erosion, not used (difference between DEM and DSM)

  # Soil depth maps
  soildep1 = soildep1.map;    # soil depth (mm), assumed constant
  soildep2 = soildep2.map;    # soil depth (mm), assumed constant
  
  #ksatcomp = ksatcomp.map;    # ksat of compacted areas (mm/h) (created with previous script)

  # surface maps
  rr = rr.map;               # surface roughness (cm)
  mann = n.map;              # mannings n ()
  stone = stonefrc.map;      # fraction on surface (0-1)
  crust = crustfrc.map;      # crusted soil (0-1)
  comp = compfrc.map;        # compacted soil (0-1), adopted as infrastructure
  hard = hardsurf.map;       # impermeable surfaces (0 or 1)

  # channel maps
  lddchan = lddchan.map;     # channel 1D network (extracted from DEM)
  chanwidth = chanwidth.map; # channel width (m) (from Fleischmann, based on drainge area)
  changrad = changrad.map;   # channel gradient, sine
  chanman = chanman.map;     # channel manning (-)
  chanside = chanside.map;   # angle channel side walls, 0 = rectangular
  chanmask = chanmask1.map;

  # channel flooding maps: channels that have a depth > 0 can flood
  # channels with a depth 0 will never flood but are infinitely deep!
  chandepth = chandepth.map;  # channel depth (m) (from Fleischmann, based on drainage area)
  #chanmaxq = chanmaxq.map;    # maximum discharge (m3/s) in culvert locations in channel (not adopted, bridges are opened)
  #chanlevees = chanlevee.map; # main levees along channels (not adopted)
  chanksat = chanksat.map;    # ksat in case channel infiltrates, for dry channels (from Fleischmann)
  floodzone = floodzone.map;  # flooding limited to areas with value 1 (adopted all one within the extent)

  # houses
  housecov = housecover.map; # house cover fraction (from MAPBIOMAS, same as urban infrastructure)
  roofstore = roofstore.map; # roof interception (mm)

  baseflow= baseflow.map;
  
#initial

  ##################
  ### PREPARATION ##
  ##################

  # limited all maps to mask extent
  unitmap = scalar(unitmapbase)*mask;
  DEM *= mask;
  rivers *= mask;
  #barriers *= mask; (not adopted)
  #road *= mask; (not adopted)
  hard_surf *= mask;
  house_cover *= mask;
  ndvi*=mask;


  ######################
  ### LAND COVER MAP ###
  ######################

  report landuse = unitmap; ------

  ########################
  ### BASE RELIEF MAPS ###
  ########################

  report DEMm = DEM; --------

  report Ldd = lddcreate (DEMm, 0, 0, 0, 0); -------------

  report grad = max(sin(atan(slope((DEMm)))), 0.005)*mask; ----------------- 
  
  #### not used in lisem, auxilary maps
  ups=scalar(accuflux(Ldd,0.0025)); -------------
  
  ########################
  ### VEGETATION MAPS  ###
  ########################
 
  report coverc = cover(1-((0.681-max(ndvi,0))/0.681)**0.9,0)*mask; # fraction plant soil cover --------

  # LAI of plants inside gridcell (m2/m2)
  coverc = min(coverc, 0.95);
  report lai = ln(1-coverc)/-0.4;   -------------------

  ##################
  ### HOUSE MAPS ###
  ##################

  report housecov = house_cover; # copy directly input ---------------
  report roofstore = if(housecov gt 0,1,0)*mask; # interception storage 1 mm -----------------

  ##################
  ### Soil depth ###
  ##################

  distriv = spread(nominal(rivers gt 0),0,1)*mask;
  soild = cover((1-min(1,grad))       # steeper slopes giver undeep soils
                 -0.5*distriv/mapmaximum(distriv),0)*mask;  # perpendicular distance to river, closer gives deeper soils
  soildb = 1500*(soild)**1.5;
  # m to mm for lisem, higher power emphasizes deep, updeep
  soildepth = mask*(500+cover(windowaverage(soildb,3*celllength()),mask))
  report soildep2 = soildepth*0.5;
  report soildep1 = soildepth*0.5;

  #########################
  ### SOIL SURFACE MAPS ###
  #########################
 
  report rr = max(lookupscalar(lutbl, 1, unitmap) * mask, 0.01); #Extracted from Victor's reference -----------
 
  report mann = lookupscalar(lutbl, 2, unitmap) * mask; #Extracted from Victor's reference ------------

  report crust = mask*0; #No crust in the area   -----
  report stone = mask*0; #No stone in the area   -----
  
  report hard = hard_surf;    --------
  
  ####################
  ### CHANNEL MAPS ###
  ####################

  report chanmask = rivers; #Channel mask originally created ---------
  
  report lddchan = lddcreate((DEMm-mainout*100)*chanmask,0,0,0,0); -----------

  #report outpoint = cover(scalar(pit(lddchan)),mask*0);

  changrad = max(0.01,sin(atan(slope(chanmask*DEMm)))); ------------
  report changrad = windowaverage(changrad, 5*celllength())*chanmask; -------------
  # channel slope, copy surface but smooth to avoid abrupt changes

  report chanman = chanmask*0.03; #Adopted according to Fleishmann ------------

  report chanside = chanmask*scalar(0); # rectangular channel --------------
  report chanwidth = (0.95*(ups**0.5))*chanmask; #Adopted according to Fleischmann -----------
  report chandepth = (0.3*(ups**0.3))*chanmask; #Adopted according to Fleischmann -------------

  #report chanmaxq = 0*mask; Not adopted
  report chanksat = 0*mask;   ------------
  # assume rocky channel or some baseflow so no extra infil

  report floodzone = mask*scalar(1); #Assumed as entired river basin -------------

  report baseflow=cover(scalar(pit(lddchan) ne 0)*chanwidth*1.0,0);
