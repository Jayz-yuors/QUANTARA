import ee
import geemap
import os

# Initialize with your exact project ID
PROJECT_ID = "isro-urban-heat-ps1"
ee.Initialize(project=PROJECT_ID)

# Coordinates for the test grid (Thane West)
LAT = 19.2045
LON = 72.9749

def extract_thermal_data():
    print("Defining 2km Region of Interest (ROI)...")
    roi = ee.Geometry.Point([LON, LAT]).buffer(2000)

    print("Fetching Landsat 8 Surface Temperature data from Earth Engine...")
    # Using Landsat 8 Collection 2 Tier 1 Level 2 (Surface Temp & Reflectance)
    # We filter for pre-monsoon months (March-May) for maximum heat stress visibility
    dataset = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
                .filterBounds(roi) \
                .filterDate('2023-03-01', '2023-05-31') \
                .filter(ee.Filter.lt('CLOUD_COVER', 10))

    # Get the median image to reduce any remaining clouds/noise
    image = dataset.median()

    print("Applying NASA scaling factors to convert raw sensor data to Celsius...")
    # Landsat 8 Thermal Band is ST_B10.
    # NASA's official Conversion Formula: (Band * 0.00341802 + 149.0) - 273.15
    thermal_band = image.select('ST_B10')
    lst_celsius = thermal_band.multiply(0.00341802).add(149.0).subtract(273.15)

    # Clip the massive satellite image down to just our 2km ROI
    lst_clipped = lst_celsius.clip(roi)

    print("Generating offline interactive heat map...")
    # Create a geemap object centered on our coordinates
    Map = geemap.Map(center=[LAT, LON], zoom=14)

    # Visualization parameters (Blue = Cool, Red = Hot)
    vis_params = {
        'min': 30, # Minimum temp ~30°C
        'max': 45, # Maximum temp ~45°C
        'palette': ['blue', 'cyan', 'green', 'yellow', 'red']
    }

    # Add the Heat layer to the map
    Map.addLayer(lst_clipped, vis_params, 'Land Surface Temperature (°C)')

    # Export to HTML for offline viewing and fail-safe presentation
    output_file = "thane_lst_heatmap.html"
    Map.to_html(output_file)
    print(f"\nSUCCESS! Map saved locally as: {os.path.abspath(output_file)}")
    print("Go to your project folder and double-click the HTML file to view the heat signature.")

if __name__ == "__main__":
    extract_thermal_data()