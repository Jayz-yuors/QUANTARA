"""Registry of external datasets used by the project.

This file lists official dataset identifiers (Earth Engine where available)
and official source URLs. It does NOT download data — it centralizes references
so other scripts can import known IDs/links.
"""
from typing import Dict, Optional

DATASETS: Dict[str, Dict[str, Optional[str]]] = {
    "landsat9": {
        "ee_id": "LANDSAT/LC09/C02/T1_L2",
        "source": "https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2",
    },
    "ecostress": {
        # ECOSTRESS is distributed via LP DAAC - use LP DAAC product pages to download
        "ee_id": None,
        "source": "https://lpdaac.usgs.gov/products/eco2lstev002/",
    },
    "modis_lst": {
        "ee_id": "MODIS/061/MOD11A2",
        "source": "https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2",
    },
    "esa_worldcover": {
        "ee_id": "ESA/WorldCover/v200",
        "source": "https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200",
    },
    "dynamic_world": {
        "ee_id": "GOOGLE/DYNAMICWORLD/V1",
        "source": "https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1",
    },
    "gpm_imerg": {
        "ee_id": "NASA/GPM_L3/IMERG_V07",
        "source": "https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07",
    },
    "microsoft_buildings": {
        "ee_id": None,
        "source": "https://github.com/microsoft/GlobalMLBuildingFootprints",
    },
    "openaq": {
        "ee_id": None,
        "source": "https://openaq.org/",
    },
    "cpcb_air": {
        "ee_id": None,
        "source": "https://app.cpcbccr.com/",
    },
}


def get(dataset_key: str) -> Dict[str, Optional[str]]:
    """Return dataset entry by key (lowercase)."""
    return DATASETS.get(dataset_key.lower(), {})
