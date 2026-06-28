Dataset: ECOSTRESS (LST)

Official source:

- LP DAAC ECOSTRESS product page: https://lpdaac.usgs.gov/products/eco2lstev002/

Notes / access:

- ECOSTRESS LST products are distributed by LP DAAC (NASA) and can be downloaded via Earthdata/LPDAAC or ingested into Google Earth Engine when available.
- For this project, use official LP DAAC downloads (L2 LST) or check for an Earth Engine collection; if not present, download NetCDF/HDF and preprocess to GeoTIFFs.

Suggested local workflow:

- Download L2 products from LP DAAC for the study dates.
- Convert to GeoTIFF, reproject to project CRS, and clip to AOI.
- Place raw files in `data/raw/gee_exports/ecostress/`.
