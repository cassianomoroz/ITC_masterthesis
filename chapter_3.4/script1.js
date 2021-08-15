//Before start, create a polygon in the Itajai River Basin

var year1=2020

// Add the points representing the gauge stations
var gauge_2648001 = ee.Geometry.Point([-48.83916667, -26.92166667]);
var gauge_2648002 = ee.Geometry.Point([-48.93166667, -26.72416667]);
var gauge_2648038 = ee.Geometry.Point([-48.96416667, -26.92638889]);
var gauge_2649001 = ee.Geometry.Point([-49.28944444, -26.94361111]);
var gauge_2649002 = ee.Geometry.Point([-49.17027778, -26.73666667]);
var gauge_2649003 = ee.Geometry.Point([-49.365, -26.78111111]);
var gauge_2649004 = ee.Geometry.Point([-49.27194444, -26.82972222]);
var gauge_2649005 = ee.Geometry.Point([-49.2675, -26.91361111]);
var gauge_2649007 = ee.Geometry.Point([-49.06527778, -26.91805555]);
var gauge_2649008 = ee.Geometry.Point([-49.27055556, -26.74083333]);
var gauge_2649009 = ee.Geometry.Point([-49.07416667, -26.96833333]);
var gauge_2649010 = ee.Geometry.Point([-49.08361111, -26.79666667]);
var gauge_2649017 = ee.Geometry.Point([-49.48305556, -26.71722222]);
var gauge_2649053 = ee.Geometry.Point([-49.8025, -26.92611111]);
var gauge_2649058 = ee.Geometry.Point([-49.82805556, -26.6975]);
var gauge_2649061 = ee.Geometry.Point([-49.67222222, -26.895]);
var gauge_2649065 = ee.Geometry.Point([-49.48, -26.54611111]);
var gauge_2650022 = ee.Geometry.Point([-50.00305556, -26.45861111]);
var gauge_2650023 = ee.Geometry.Point([-50.14777778, -26.69305555]);
var gauge_2748000 = ee.Geometry.Point([-48.91805556, -27.10083333]);
var gauge_2749000 = ee.Geometry.Point([-49.395, -27.03805555]);
var gauge_2749001 = ee.Geometry.Point([-49.51666667, -27.05388889]);
var gauge_2749002 = ee.Geometry.Point([-49.60583333, -27.39861111]);
var gauge_2749003 = ee.Geometry.Point([-49.99444444, -27.11305555]);
var gauge_2749005 = ee.Geometry.Point([-49.58972222, -27.03416667]);
var gauge_2749006 = ee.Geometry.Point([-49.94083333, -27.25722222]);
var gauge_2749007 = ee.Geometry.Point([-49.38277778, -27.73055555]);
var gauge_2749013 = ee.Geometry.Point([-49.76888889, -27.29027778]);
var gauge_2749016 = ee.Geometry.Point([-49.38138889, -27.04027778]);
var gauge_2749017 = ee.Geometry.Point([-49.55305556, -27.50194444]);
var gauge_2749033 = ee.Geometry.Point([-49.36555556, -27.3925]);
var gauge_2749037 = ee.Geometry.Point([-49.36527778, -27.68333333]);
var gauge_2749039 = ee.Geometry.Point([-49.63166667, -27.20555555]);
var gauge_2749041 = ee.Geometry.Point([-49.83138889, -27.41138889]);
var gauge_2749045 = ee.Geometry.Point([-49.08722222, -27.19666667]);
var gauge_2749046 = ee.Geometry.Point([-49.32833333, -27.33194444]);
var gauge_2750014 = ee.Geometry.Point([-50.03388889, -27.09722222]);
var gauge_2750021 = ee.Geometry.Point([-50.26444444, -27.14111111]);
var pts = ee.FeatureCollection(ee.List([ee.Feature(gauge_2648001),ee.Feature(gauge_2648002),ee.Feature(gauge_2648038),ee.Feature(gauge_2649001),ee.Feature(gauge_2649002),ee.Feature(gauge_2649003),ee.Feature(gauge_2649004),ee.Feature(gauge_2649005),ee.Feature(gauge_2649007),ee.Feature(gauge_2649008),ee.Feature(gauge_2649009),ee.Feature(gauge_2649010),ee.Feature(gauge_2649017),ee.Feature(gauge_2649053),ee.Feature(gauge_2649058),ee.Feature(gauge_2649061),ee.Feature(gauge_2649065),ee.Feature(gauge_2650022),ee.Feature(gauge_2650023),ee.Feature(gauge_2748000),ee.Feature(gauge_2749000),ee.Feature(gauge_2749001),ee.Feature(gauge_2749002),ee.Feature(gauge_2749003),ee.Feature(gauge_2749005),ee.Feature(gauge_2749006),ee.Feature(gauge_2749007),ee.Feature(gauge_2749013),ee.Feature(gauge_2749016),ee.Feature(gauge_2749017),ee.Feature(gauge_2749033),ee.Feature(gauge_2749037),ee.Feature(gauge_2749039),ee.Feature(gauge_2749041),ee.Feature(gauge_2749045),ee.Feature(gauge_2749046),ee.Feature(gauge_2750014),ee.Feature(gauge_2750021)]));

//Import GPM and GSMaP Image Collections
var GPMpre1 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,1,1), ee.Date.fromYMD(year1,2,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre2 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,2,1), ee.Date.fromYMD(year1,3,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre3 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,3,1), ee.Date.fromYMD(year1,4,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre4 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,4,1), ee.Date.fromYMD(year1,5,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre5 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,5,1), ee.Date.fromYMD(year1,6,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre6 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,6,1), ee.Date.fromYMD(year1,7,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre7 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,7,1), ee.Date.fromYMD(year1,8,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre8 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,8,1), ee.Date.fromYMD(year1,9,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre9 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,9,1), ee.Date.fromYMD(year1,10,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre10 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,10,1), ee.Date.fromYMD(year1,11,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre11 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,11,1), ee.Date.fromYMD(year1,12,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');
var GPMpre12 = ee.ImageCollection("JAXA/GPM_L3/GSMaP/v6/reanalysis") //GPM Precipitation half-hourly
.filterDate(ee.Date.fromYMD(year1,12,1), ee.Date.fromYMD(year1 + 1,1,1))
.filterBounds(geometry)
.select('hourlyPrecipRateGC');


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
var GPMnew1 = ee.FeatureCollection(GPMpre1.iterate(fill, ft));
var GPMnew2 = ee.FeatureCollection(GPMpre2.iterate(fill, ft));
var GPMnew3 = ee.FeatureCollection(GPMpre3.iterate(fill, ft));
var GPMnew4 = ee.FeatureCollection(GPMpre4.iterate(fill, ft));
var GPMnew5 = ee.FeatureCollection(GPMpre5.iterate(fill, ft));
var GPMnew6 = ee.FeatureCollection(GPMpre6.iterate(fill, ft));
var GPMnew7 = ee.FeatureCollection(GPMpre7.iterate(fill, ft));
var GPMnew8 = ee.FeatureCollection(GPMpre8.iterate(fill, ft));
var GPMnew9 = ee.FeatureCollection(GPMpre9.iterate(fill, ft));
var GPMnew10 = ee.FeatureCollection(GPMpre10.iterate(fill, ft));
var GPMnew11 = ee.FeatureCollection(GPMpre11.iterate(fill, ft));
var GPMnew12 = ee.FeatureCollection(GPMpre12.iterate(fill, ft));

// Export all information to Google Drive
Export.table.toDrive(GPMnew1,
"GSMaP_1",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_1");
Export.table.toDrive(GPMnew2,
"GSMaP_2",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_2");
Export.table.toDrive(GPMnew3,
"GSMaP_3",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_3");
Export.table.toDrive(GPMnew4,
"GSMaP_4",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_4");
Export.table.toDrive(GPMnew5,
"GSMaP_5",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_5");
Export.table.toDrive(GPMnew6,
"GSMaP_6",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_6");
Export.table.toDrive(GPMnew7,
"GSMaP_7",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_7");
Export.table.toDrive(GPMnew8,
"GSMaP_8",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_8");
Export.table.toDrive(GPMnew9,
"GSMaP_9",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_9");
Export.table.toDrive(GPMnew10,
"GSMaP_10",
"SatelliteRainfall",
"GSMaP"+String(year1)+"_10");
Export.table.toDrive(GPMnew11,
"GSMaP_11",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_11");
Export.table.toDrive(GPMnew12,
"GSMaP_12",
"SatelliteRainfall",
"GSMaP_"+String(year1)+"_12");
