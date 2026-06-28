Dataset: Dynamic World (10 m probabilistic LULC)

Official source:

- Dynamic World (Google/WRI): https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1

Quick Earth Engine load snippet (Python):

```python
import ee
ee.Initialize()
dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
.filterBounds(aoi)
.filterDate('2023-01-01', '2023-12-31')
```

Notes:

- Useful for time-varying land cover probabilities (water, built, trees, etc.).
