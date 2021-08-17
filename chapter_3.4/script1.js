/////////////////////////////////
// Created by: C. B. Moroz //////
/////////////////////////////////

//Description: code to extract the hourly (GSMaP) or half-hourly (IMERG) time series of rainfall estimates at a specific location (e.g. location of rain gauges).

//Before start, create a polygon over the study area (Itajai-Acu river basin).

//Add the point that is being analyzed (e.g. Y and X coordinates of the gauge).
var location = ee.Geometry.Point([-48.83, -26.92]); //example location of one of the rain gauges.
//Create a list with all locations (if adopting more than one).
var pts = ee.FeatureCollection(ee.List([ee.Feature(location)]));

//Import Image Collections.
//For GSMaP.
var GSMaPpre = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GSMaP image collection.
.filterDate(ee.Date.fromYMD(2000,7,1), ee.Date.fromYMD(2020,7,1)) //Filter date.
.filterBounds(geometry) //Filter boundary to geometry.
.select('hourlyPrecipRateGC'); //Select the band with rainfall estimates.
//For IMERG.
var IMERGpre = ee.ImageCollection("NASA/GPM_L3/IMERG_V06") //IMERG image collection.
.filterDate(ee.Date.fromYMD(2000,7,1), ee.Date.fromYMD(2020,7,1)) //Filter date.
.filterBounds(geometry) //Filter boundary to geometry.
.select('precipitationCal'); //Select the band with rainfall estimates.

// Empty Collection to fill
var ft = ee.FeatureCollection(ee.List([]));
var fill = function(img, ini) {
  // type cast
  var inift = ee.FeatureCollection(ini);
  // gets the values for the points in the current img
  var ft2 = img.reduceRegions(pts, ee.Reducer.first());
  // gets the date of the img
  var date = img.date().format();
  // writes the date in each feature
  var ft3 = ft2.map(function(f){return f.set("date", date)});
  // merges the FeatureCollections
  return inift.merge(ft3);
};

// Iterates over the ImageCollection
var GSMaPnew = ee.FeatureCollection(GSMaPpre.iterate(fill, ft));
var IMERGnew = ee.FeatureCollection(IMERGpre.iterate(fill, ft));

// Export the time series to Google Drive.
Export.table.toDrive(GSMaPnew,
"GSMaP",
"SatelliteRainfall",
"GSMaP_timeseries");
Export.table.toDrive(IMERGnew,
"IMERG",
"SatelliteRainfall",
"IMERG_timeseries");
