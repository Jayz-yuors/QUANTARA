import ee

from gee.data_fetch import initialize_gee
from gee.pipeline import UrbanHeatPipeline


# -----------------------------------------
# Initialize Earth Engine
# -----------------------------------------

initialize_gee()

# -----------------------------------------
# Example Region
# -----------------------------------------

region = ee.Geometry.Rectangle([

    72.75,

    18.85,

    73.05,

    19.20

])

# -----------------------------------------
# Build Pipeline
# -----------------------------------------

pipeline = UrbanHeatPipeline(

    region,

    "2024-01-01",

    "2024-12-31"

)

# -----------------------------------------
# Run
# -----------------------------------------

feature_cube = pipeline.run()

# -----------------------------------------
# Summary
# -----------------------------------------

pipeline.summary()

print()

print("=" * 60)

print("Pipeline Completed Successfully")

print("=" * 60)

print()

print("Generated Feature Cubes")

print(feature_cube.keys())

print()

print("Processor Status")

print(pipeline.processor_status())