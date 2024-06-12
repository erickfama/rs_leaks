# Modules
import ee
import os
import math
import requests
from datetime import timedelta

# Initialize ee
try:
    ee.Initialize()

except:
    ee.Authenticate()
    ee.Initialize()

# Download class
class ee_download:

    '''
    Function to get Sentinel-2 images
    '''

    # Get image from image collection
    def get_image(self, start, end, poi_leak):
    
        if isinstance(start, str) == False:
            start = str(start)
            end = str(end)
    
        collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")\
        .filterBounds(poi_leak)\
        .filterDate(ee.Date(start), ee.Date(end))\
        .sort("system:time_start", opt_ascending = False)\
        .sort("CLOUDY_PIXEL_PERCENTAGE")

        img = collection.first()

        print("Date of selected image (Sentinel): ", ee.Date(img.get("system:time_start")).format("yyyy-MM-dd").getInfo(),
            "\nSentinel images found:", collection.size().getInfo(),
            "\nCloud %: ", img.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()) 
    
        return img

    def get_landsat_images(self, start, end, poi_leak, buffer_regression):

        '''
        Download a Landsat image around a point of interest with a buffer radius
        '''

        poi_regression = poi_leak.buffer(buffer_regression).bounds(proj = "EPSG:32613", maxError = 0.001)
 
        try:

            if isinstance(start, str) == False:
                start = str(start)
                end = str(end)
        
            selected_Landsat_collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")\
                                            .filterBounds(poi_leak)\
                                            .filterDate(ee.Date(start), ee.Date(end))\
                                            .sort("CLOUD_COVER")

            img_landsat = selected_Landsat_collection.first().clip(poi_regression)

            print("Date of selected image (Landsat):", ee.Date(img_landsat.get("system:time_start")).format("yyyy-MM-dd").getInfo(),
                "\nLandsat images found: ", selected_Landsat_collection.size().getInfo(),
                "\nCloud %: ", img_landsat.get("CLOUD_COVER").getInfo())
    
            if selected_Landsat_collection.size().getInfo() == 0:
                print("THERES NO LANDSAT IMAGES FOR THE SELECTED DATES")
                print("Stopped in rep", rep)

        except:
            start = start + timedelta(days = 5)

            if isinstance(start, str) == False:
                start = str(start)
                end = str(end)

            selected_Landsat_collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")\
                                            .filterBounds(poi_leak)\
                                            .filterDate(ee.Date(start), ee.Date(end))\
                                            .sort("CLOUD_COVER")

            img_landsat = selected_Landsat_collection.first().clip(poi_regression)

            print("Date of selected image (Landsat):", ee.Date(img_landsat.get("system:time_start")).format("yyyy-MM-dd").getInfo(),
                "\nLandsat images found: ", selected_Landsat_collection.size().getInfo(),
                "\nCloud %: ", img_landsat.get("CLOUD_COVER").getInfo())
    
            if selected_Landsat_collection.size().getInfo() == 0:
                print("THERES NO LANDSAT IMAGES FOR THE SELECTED DATES")

        return img_landsat

    # Download patch image
    def download_image(self, image, path, date_label):

        if os.path.exists(path + "S2" + "_" + date_label + ".zip"):
            print("S2" + "_" + date_label + ".zip" + " already exists.")
    
        else:
            url = image.getDownloadURL(
                {
                "scale": 10,
                "crs": "EPSG:32613",
                "fileFormat": "GeoTIFF",
                "maxPixels": 1e13
                }
            )

            r = requests.get(url, allow_redirects = True)
            open(path + "S2" + "_" + date_label + ".zip", "wb").write(r.content)
            print("Download complete")

class ee_utils:

    '''
    Class to image manipulation
    '''

    def get_poi(self, lat, lon):
        coords = [lat, lon]

        return ee.Geometry.Point(coords)

    # Define the bands to select and the patch size (radius in meters respect to leak point)
    def bands_clip_image(self, image, poi, buffer_size=100, bands=["B4", "B3", "B2"]):
        # Clip image
        image = image.clip(poi.buffer(buffer_size).bounds(proj="EPSG:32613", maxError = 0.001))

        # Select bands
        image = image.select(bands)

        return image
    
class ee_LST:

    '''
    Class to calculate LST 10m and add it as a spectral band to a S2 image
    '''

    # Create compund bands in order to perform linear regression
    def lst_regression(self, landsat_image, sentinel_image, poi_leak, buffer_size, buffer_regression = 500, error = True):
        ndvi_landsat = landsat_image.normalizedDifference(["SR_B5", "SR_B4"]).rename("ndvi")
        ndwi_landsat = landsat_image.normalizedDifference(["SR_B3", "SR_B5"]).rename("ndwi")
        ndbi_landsat = landsat_image.normalizedDifference(["SR_B6", "SR_B5"]).rename("ndbi")
        lst_landsat_30m = landsat_image.select("ST_B10").rename("Landsat_LST_30m")

        ndvi_sentinel = sentinel_image.normalizedDifference(["B8", "B4"]).rename("s2_ndvi")
        ndwi_sentinel = sentinel_image.normalizedDifference(["B3", "B11"]).rename("s2_ndwi")
        ndbi_sentinel = sentinel_image.normalizedDifference(["B11", "B8"]).rename("s2_ndbi")

        # Poi for regression, this increases n
        poi_regression = poi_leak.buffer(buffer_regression).bounds(proj = "EPSG:32613", maxError = 0.001)

        # Linear regression
        bands = ee.Image(1).addBands(ndvi_landsat).addBands(ndbi_landsat).addBands(ndwi_landsat).addBands(lst_landsat_30m).rename(["constant", "ndvi", "ndbi", "ndwi", "lst"])

        img_landsat_regression = bands.reduceRegion(
            reducer = ee.Reducer.linearRegression(4, 1),
            geometry = poi_regression,
            scale = 30,
            maxPixels = 1e13
        )

        # Get coefficients of linear regression
        coefList2 = ee.Array(img_landsat_regression.get("coefficients")).toList()
        intercept2 = ee.Image(ee.Number(ee.List(coefList2.get(0)).get(0))).reproject(crs = "EPSG:32613")
        slopeNDVI2 = ee.Image(ee.Number(ee.List(coefList2.get(1)).get(0))).reproject(crs = "EPSG:32613")
        slopeNDBI2 = ee.Image(ee.Number(ee.List(coefList2.get(2)).get(0))).reproject(crs = "EPSG:32613")
        slopeNDWI2 = ee.Image(ee.Number(ee.List(coefList2.get(3)).get(0))).reproject(crs = "EPSG:32613")

        # Predict LST with Landsat info 
        LST_model = intercept2.add(slopeNDVI2.multiply(ndvi_landsat))\
                    .add(slopeNDBI2.multiply(ndbi_landsat))\
                    .add(slopeNDWI2.multiply(ndwi_landsat))

        # Get residuals
        residuals = lst_landsat_30m.subtract(LST_model)

        # Predict LST with Sentinel info (downscaled image)
        lst_landsat_10m_final = ee.Image(intercept2).add(slopeNDVI2.multiply(ndvi_sentinel))\
                                                    .add(slopeNDBI2.multiply(ndbi_sentinel)).add(slopeNDWI2.multiply(ndwi_sentinel))\
                                                    .clip(poi_leak.buffer(buffer_size).bounds(proj = "EPSG:32613", maxError = 0.001))

        if error == True:
        
            # Compute number of pixels in the image (n)
            n = landsat_image.select("ST_B10").reduceRegion(
                reducer = ee.Reducer.count(),
                scale = 30,
                maxPixels = 1e13
            ).getInfo()["ST_B10"]

            # Compute Root Mean Squared Error
            rmse = math.sqrt(residuals.select("Landsat_LST_30m").pow(2).reduceRegion(
                reducer = ee.Reducer.sum(),
                scale = 30,
                maxPixels = 1e13
            ).getInfo()["Landsat_LST_30m"]/n)

        return (lst_landsat_10m_final, rmse)
    

    def add_lst10m_band(self, sentinel_image, lst_image):
    
        return sentinel_image.addBands(lst_image.rename("LST_10m"))