import ee
import pandas as pd
import os

# Initialize with your project ID
PROJECT_ID = "isro-urban-heat-ps1"
ee.Initialize(project=PROJECT_ID)

LAT = 19.2045
LON = 72.9749


def generate_training_data():
    print("Defining 2km Region of Interest (ROI)...")
    roi = ee.Geometry.Point([LON, LAT]).buffer(2000)

    print("Fetching and clipping Landsat 8 LST (Target Variable)...")
    landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterBounds(roi).filterDate('2023-03-01', '2023-05-31') \
        .filter(ee.Filter.lt('CLOUD_COVER', 10)).median().clip(roi)

    lst = landsat.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).rename('LST_Celsius')

    print("Fetching and clipping Sentinel-2 Features (Predictor Variables)...")
    sentinel = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(roi).filterDate('2023-03-01', '2023-05-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).median().clip(roi)

    ndvi = sentinel.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndbi = sentinel.normalizedDifference(['B11', 'B8']).rename('NDBI')

    print("Stacking spatial layers into a single mathematical matrix...")
    # Combine the temperature, vegetation, and concrete data into one unified image
    stacked_image = lst.addBands(ndvi).addBands(ndbi)

    print("Extracting 5,000 random data points for AI training...")
    # Randomly sample pixels across the 2km grid to create a training dataset
    sampled_data = stacked_image.sample(
        region=roi,
        scale=30,  # 30-meter resolution matching Landsat
        numPixels=5000,
        geometries=True  # Keeps the latitude/longitude data
    )

    print("Converting spatial data to Pandas DataFrame...")
    # Extract the properties from the Earth Engine feature collection
    features = sampled_data.getInfo()['features']

    # Parse the data into a clean tabular format
    data_list = []
    for f in features:
        props = f['properties']
        coords = f['geometry']['coordinates']
        data_list.append({
            'Longitude': coords[0],
            'Latitude': coords[1],
            'NDVI': props.get('NDVI'),
            'NDBI': props.get('NDBI'),
            'LST_Celsius': props.get('LST_Celsius')
        })

    df = pd.DataFrame(data_list)

    # Drop any rows where satellite data might have been null (due to water or edge clipping)
    df = df.dropna()

    output_csv = "urban_heat_training_data.csv"
    df.to_csv(output_csv, index=False)

    print(f"\nSUCCESS! AI Training dataset saved as: {os.path.abspath(output_csv)}")
    print(f"Total valid training points extracted: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    generate_training_data()