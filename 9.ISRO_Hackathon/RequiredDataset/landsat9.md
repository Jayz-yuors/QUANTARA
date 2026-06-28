Dataset: Landsat 9 (Collection 2, Level-2)

Official source:

- USGS Landsat Collections via Google Earth Engine: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2

Quick Earth Engine load snippet (Python):

```python
import ee
ee.Initialize()
collection = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
.filterBounds(aoi)
.filterDate('2024-01-01', '2024-12-31')
.filter(ee.Filter.lt('CLOUD_COVER', 20))
```

Notes:

- Includes surface reflectance (`SR_B*`) and thermal (`ST_B*`).
- Follow `DATASET_COLLECTION_PLAN.md` directory layout when exporting raw GeoTIFFs.
