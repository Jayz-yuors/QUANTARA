Dataset: Water Bodies (Global Surface Water / Dynamic Water)

Official sources:

- JRC Global Surface Water (Occurrence, change): https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_GlobalSurfaceWater
- Dynamic World (water probability): https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1

Quick Earth Engine load snippet (JRC Global Surface Water):

```python
import ee
ee.Initialize()
gsw = ee.Image('JRC/GSW1_3/GlobalSurfaceWater')
```

Notes:

- Useful for distance-to-water cooling features and water masking.
