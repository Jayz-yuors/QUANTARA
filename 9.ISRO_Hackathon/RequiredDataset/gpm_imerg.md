Dataset: GPM IMERG (IMERG Final/IMERG V07)

Official source:

- GPM IMERG via GES DISC / Earth Engine: https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07

Quick Earth Engine load snippet (Python):

```python
import ee
ee.Initialize()
gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_V07')
.filterDate('2023-01-01', '2023-12-31')
```

Notes:

- Useful for rainfall features and wet/dry context during sample dates.
