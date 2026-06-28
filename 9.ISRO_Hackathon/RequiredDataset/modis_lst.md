Dataset: MODIS Terra LST (MOD11A2)

Official source:

- MODIS MOD11A2 (8-day LST): https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2

Quick Earth Engine load snippet (Python):

```python
import ee
ee.Initialize()
modis = ee.ImageCollection('MODIS/061/MOD11A2')
.filterBounds(aoi)
.filterDate('2023-01-01', '2023-12-31')
```

Notes:

- MOD11A2 LST is typically stored as scaled integer; consult dataset docs for scale factor.
- Useful for long-term / coarse validation of Landsat-derived LST.
