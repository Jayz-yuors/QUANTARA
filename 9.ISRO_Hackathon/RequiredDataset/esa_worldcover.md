Dataset: ESA WorldCover

Official source:

- ESA WorldCover v2.0: https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200

Quick Earth Engine load snippet (Python):

```python
import ee
ee.Initialize()
wc = ee.Image('ESA/WorldCover/v200/2020')
```

Notes:

- Provides land-cover class for 10 m resolution; useful for LULC features in ML.
