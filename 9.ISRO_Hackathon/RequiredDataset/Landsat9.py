import ee
import geemap
# CODE SPECIFIC TO MUMBAI REGION ONLY


# -------------------------------------------------------
# Initialize Google Earth Engine
# -------------------------------------------------------
ee.Initialize()

# -------------------------------------------------------
# Define Mumbai Area of Interest (AOI)
# -------------------------------------------------------
mumbai = ee.Geometry.Rectangle([
    72.77,   # West Longitude
    18.89,   # South Latitude
    72.99,   # East Longitude
    19.30    # North Latitude
])

# -------------------------------------------------------
# Load Landsat 9 Collection
# -------------------------------------------------------
dataset = (
    ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    .filterBounds(mumbai)
    .filterDate("2024-01-01", "2024-12-31")
    .filter(ee.Filter.lt("CLOUD_COVER", 20))
)

# -------------------------------------------------------
# Apply Scale Factors
# -------------------------------------------------------
def apply_scale_factors(image):

    optical = (
        image.select("SR_B.")
        .multiply(0.0000275)
        .add(-0.2)
    )

    thermal = (
        image.select("ST_B.*")
        .multiply(0.00341802)
        .add(149.0)
    )

    return (
        image.addBands(optical, None, True)
             .addBands(thermal, None, True)
    )

dataset = dataset.map(apply_scale_factors)

# -------------------------------------------------------
# Create Median Composite
# -------------------------------------------------------
image = dataset.median().clip(mumbai)

# -------------------------------------------------------
# Visualization Parameters
# -------------------------------------------------------
vis_params = {
    "bands": ["SR_B4", "SR_B3", "SR_B2"],
    "min": 0,
    "max": 0.3,
}

# -------------------------------------------------------
# Create Interactive Map
# -------------------------------------------------------
Map = geemap.Map()

Map.centerObject(mumbai, 10)

Map.addLayer(
    image,
    vis_params,
    "Mumbai Landsat 9 True Color"
)

Map.addLayer(
    mumbai,
    {"color": "red"},
    "Mumbai Boundary"
)

# -------------------------------------------------------
# Display Map
# -------------------------------------------------------
Map