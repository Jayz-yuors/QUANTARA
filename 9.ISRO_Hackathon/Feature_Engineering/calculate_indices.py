import ee
import geemap
import os

# Initialize with your project ID
PROJECT_ID = "isro-urban-heat-ps1"
ee.Initialize(project=PROJECT_ID)

LAT = 19.2045
LON = 72.9749


def extract_heat_drivers():
    print("Defining 2km Region of Interest (ROI)...")
    roi = ee.Geometry.Point([LON, LAT]).buffer(2000)

    print("Fetching High-Resolution Sentinel-2 Imagery...")
    # Sentinel-2 provides 10m resolution for ultra-accurate vegetation/concrete mapping
    dataset = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(roi) \
        .filterDate('2023-03-01', '2023-05-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

    image = dataset.median().clip(roi)

    print("Calculating NDVI (Vegetation Index)...")
    # NDVI Formula: (NIR - RED) / (NIR + RED)
    # Sentinel-2: NIR is Band 8, RED is Band 4
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    print("Calculating NDBI (Built-up Index)...")
    # NDBI Formula: (SWIR - NIR) / (SWIR + NIR)
    # Sentinel-2: SWIR is Band 11, NIR is Band 8
    ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')

    print("Generating Feature Engineering Maps...")
    Map = geemap.Map(center=[LAT, LON], zoom=14)

    # NDVI Visualization (Dark Green = Dense Trees, White/Brown = Barren/Concrete)
    ndvi_vis = {'min': -0.2, 'max': 0.8, 'palette': ['white', 'lightgreen', 'darkgreen']}

    # NDBI Visualization (Dark Red = Dense Concrete, White/Blue = Open Space/Water)
    ndbi_vis = {'min': -0.5, 'max': 0.5, 'palette': ['blue', 'white', 'red']}

    Map.addLayer(ndvi, ndvi_vis, 'NDVI (Vegetation)')
    Map.addLayer(ndbi, ndbi_vis, 'NDBI (Concrete/Built-up)')

    # Add a layer control panel so you can toggle between vegetation and concrete
    Map.addLayerControl()

    output_file = "thane_drivers_map.html"
    Map.to_html(output_file)
    print(f"\nSUCCESS! Feature map saved locally as: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    extract_heat_drivers()