# Dataset Collection Plan

Project: AI-Powered Urban Heat Decision Support System

Study area currently used in code:
- Center: Thane West, Maharashtra
- Latitude: 19.2045
- Longitude: 72.9749
- Radius: 2 km
- Current season window: March-May 2023

Recommended collection strategy:
1. Keep everything clipped to one shared Area of Interest (AOI).
2. Use a common target grid, preferably Landsat 30 m for ML samples.
3. Store raw/source exports separately from processed feature tables.
4. Preserve source name, date range, resolution, license, and acquisition script for every layer.

## Priority 1 - Required Core Layers

These are mandatory for a strong first working system.

| Dataset | Source | Access | Resolution | Required fields/features | Project use | Status |
|---|---|---|---:|---|---|---|
| Landsat 8 Collection 2 Level 2 | USGS via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2 | 30 m | ST_B10, QA_PIXEL, SR bands | Primary LST target, albedo, baseline heat map | Partially implemented |
| Landsat 9 Collection 2 Level 2 | USGS via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2 | 30 m | ST_B10, QA_PIXEL, SR bands | Extends Landsat 8 LST coverage after 2021 | Not started |
| Sentinel-2 Surface Reflectance Harmonized | Copernicus via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED | 10-20 m | B2, B3, B4, B8, B11, B12, cloud mask | NDVI, NDBI, NDWI, EVI, land cover features | Partially implemented |
| OpenStreetMap buildings, roads, parks, water | OSM / Overpass / OSMnx | https://overpass-api.de/ and https://www.openstreetmap.org/copyright | Vector | building, highway, leisure=park, natural=water, waterway | Building density, road density, distance to park/water | Partially implemented |
| ERA5-Land Hourly | ECMWF via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_HOURLY | ~11 km | temperature_2m, dewpoint_temperature_2m, wind, radiation, precipitation | Weather drivers and temporal context | Not started |
| SRTM DEM | NASA/USGS via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003 | 30 m | elevation | Elevation, slope, aspect | Not started |
| GHSL Built-up Surface | EC JRC via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S | 100 m | built_surface, built_surface_nres | Urban density, built-up intensity | Not started |
| GHSL Population | EC JRC via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_POP | 100 m | population_count | Population exposure and vulnerability | Not started |
| ESA WorldCover | ESA via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200 | 10 m | Map classes | LULC validation and land-cover fractions | Not started |

## Priority 2 - High-Value Validation and Enrichment

These make the project feel serious and defensible.

| Dataset | Source | Access | Resolution | Required fields/features | Project use | Status |
|---|---|---|---:|---|---|---|
| ECOSTRESS LST/E | NASA LP DAAC | https://lpdaac.usgs.gov/products/eco2lstev002/ | ~70 m | LST, emissivity, cloud mask | Independent LST validation, daytime variation | Not started |
| MODIS Terra LST 8-Day | NASA via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2 | 1 km | LST_Day_1km, LST_Night_1km | Long-term temperature trends | Not started |
| VIIRS Nighttime Lights | NOAA via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG | ~500 m | avg_rad | Human activity / urbanization proxy | Not started |
| WorldPop Population | WorldPop via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop | 100 m | population | Alternative population layer | Not started |
| GPM IMERG Rainfall | NASA via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07 | ~11 km | precipitation | Rainfall and wet/dry thermal context | Not started |
| Dynamic World | Google / WRI via Google Earth Engine | https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1 | 10 m | water, trees, grass, built, bare probabilities | Dynamic LULC probabilities | Not started |
| Microsoft Global ML Building Footprints | Microsoft | https://github.com/microsoft/GlobalMLBuildingFootprints | Vector | building polygons, optional heights where available | Building footprint gap-filling vs OSM | Not started |
| Air Quality | OpenAQ / CPCB | https://openaq.org/ and https://app.cpcbccr.com/ | Station | PM2.5, PM10, NO2, O3, CO, SO2 | Pollution/heat co-risk layer | Not started |

## Priority 3 - India-Specific / Planning Layers

These are useful for hackathon storytelling and policy relevance.

| Dataset | Source | Access | Resolution | Required fields/features | Project use | Status |
|---|---|---|---:|---|---|---|
| Bhuvan / NRSC layers | ISRO/NRSC | https://bhuvan.nrsc.gov.in/ | Varies | LULC, administrative, urban, thematic layers where available | India-specific authoritative support | Not started |
| Administrative boundaries | geoBoundaries | https://www.geoboundaries.org/ | Vector | country/state/district/admin polygons | Region summaries and reports | Not started |
| Administrative boundaries backup | GADM | https://gadm.org/ | Vector | country/state/district/admin polygons | Boundary fallback | Not started |
| Ward / municipal boundaries | Local authority / OSM / manual GIS | Depends on city | Vector | ward ID, name, geometry | Ward-wise dashboard and recommendations | Not started |
| Water bodies and drainage | OSM / Bhuvan / Dynamic World | Multiple | Vector/raster | lakes, rivers, streams, wetland classes | Distance to water, cooling proximity | Not started |

## Target ML Feature Table

Each sample/pixel should eventually include:

- Longitude
- Latitude
- LST_Celsius
- NDVI
- NDBI
- NDWI
- EVI
- Albedo
- Built-up fraction
- Impervious surface proxy
- Building density
- Road density
- Distance to nearest park
- Distance to nearest water body
- Elevation
- Slope
- Aspect
- Air temperature
- Relative humidity
- Wind speed
- Solar radiation
- Rainfall
- Population density
- Nighttime lights
- LULC class
- AQI / PM2.5 / PM10, if station coverage is usable

## Collection Order

1. Finish current GEE core stack: Landsat 8/9 LST + Sentinel-2 NDVI/NDBI/NDWI/EVI.
2. Add terrain: SRTM elevation, slope, aspect.
3. Add built environment: OSM roads/buildings/parks/water + GHSL built-up.
4. Add population: GHSL population, then WorldPop as a comparison layer.
5. Add weather: ERA5-Land daily aggregates for the same dates as satellite scenes.
6. Add validation: ECOSTRESS and MODIS LST.
7. Add advanced enrichment: VIIRS nighttime lights, Dynamic World, GPM rainfall, air quality.
8. Build final stacked CSV and metadata report.

## Local Folder Layout To Use

```text
data/
  raw/
    gee_exports/
    osm/
    external/
  processed/
    rasters/
    vectors/
    tables/
  metadata/
outputs/
  maps/
  reports/
models/
```

