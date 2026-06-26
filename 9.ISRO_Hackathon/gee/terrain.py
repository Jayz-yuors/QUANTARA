"""
============================================================

terrain.py

Terrain Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ ASTER DEM / SRTM Collection
✔ Elevation
✔ Slope
✔ Aspect
✔ Hillshade
✔ Terrain Feature Cube
✔ AI Ready

============================================================
"""

from __future__ import annotations

import ee

from gee.logger import log
from gee.logger import timer

from gee.data_fetch import (
    validate_geometry,
    get_collection
)

from gee.config import (
    DEM_COLLECTION
)

# ============================================================
# Terrain Visualization
# ============================================================

DEM_VIS = {

    "min": 0,

    "max": 3000,

    "palette": [

        "006400",

        "7FFF00",

        "FFFF00",

        "FFA500",

        "A52A2A",

        "FFFFFF"

    ]

}

# ============================================================
# Terrain Processor
# ============================================================

class TerrainProcessor:

    """
    Terrain Processing Engine
    """

    def __init__(

        self,

        region

    ):

        self.region = region

        self.dem = None

        self.products = {

            "DEM": None,

            "ELEVATION": None,

            "SLOPE": None,

            "ASPECT": None,

            "HILLSHADE": None,

            "TRI": None,

            "TPI": None,

            "FEATURE_STACK": None

        }

        self.is_loaded = False

        validate_geometry(region)

    # ========================================================

    @timer
    def load(self):

        log.info(

            "Loading DEM..."

        )

        dem = (

    ee.Image(

        DEM_COLLECTION

    )

    .clip(

        self.region

    )

)

        self.dem = dem

        self.products["DEM"] = dem

        self.is_loaded = True

        return self

    # ========================================================

    @timer
    def get_elevation(self):

        if self.products["ELEVATION"] is not None:

            return self.products["ELEVATION"]

        elevation = self.dem.rename(

            "ELEVATION"

        )

        self.products["ELEVATION"] = elevation

        return elevation

    # ========================================================

    @timer
    def get_slope(self):

        if self.products["SLOPE"] is not None:

            return self.products["SLOPE"]

        slope = ee.Terrain.slope(

            self.dem

        ).rename(

            "SLOPE"

        )

        self.products["SLOPE"] = slope

        return slope

    # ========================================================

    @timer
    def get_aspect(self):

        if self.products["ASPECT"] is not None:

            return self.products["ASPECT"]

        aspect = ee.Terrain.aspect(

            self.dem

        ).rename(

            "ASPECT"

        )

        self.products["ASPECT"] = aspect

        return aspect

    # ========================================================

    @timer
    def get_hillshade(self):

        if self.products["HILLSHADE"] is not None:

            return self.products["HILLSHADE"]

        hillshade = ee.Terrain.hillshade(

            self.dem

        ).rename(

            "HILLSHADE"

        )

        self.products["HILLSHADE"] = hillshade

        return hillshade
    # ========================================================
# Terrain Ruggedness Index (Approximation)
# ========================================================

    @timer
    def get_tri(self):

        if self.products["TRI"] is not None:

            return self.products["TRI"]

        tri = (

            self.get_slope()

            .pow(2)

            .sqrt()

            .rename("TRI")

        )

        self.products["TRI"] = tri

        return tri


    # ========================================================
    # Topographic Position Index (Approximation)
    # ========================================================

    @timer
    def get_tpi(self):

        if self.products["TPI"] is not None:

            return self.products["TPI"]

        neighborhood = ee.Kernel.square(1)

        mean = self.dem.reduceNeighborhood(

            reducer=ee.Reducer.mean(),

            kernel=neighborhood

        )

        tpi = (

            self.dem

            .subtract(mean)

            .rename("TPI")

        )

        self.products["TPI"] = tpi

        return tpi


    # ========================================================
    # Terrain Feature Stack
    # ========================================================

    @timer
    def get_feature_stack(self):

        if self.products["FEATURE_STACK"] is not None:

            return self.products["FEATURE_STACK"]

        stack = self.get_elevation()

        stack = stack.addBands([

            self.get_slope(),

            self.get_aspect(),

            self.get_hillshade(),

            self.get_tri(),

            self.get_tpi()

        ])

        self.products["FEATURE_STACK"] = stack

        return stack


    # ========================================================
    # Statistics
    # ========================================================

    @timer
    def statistics(self):

        return self.get_feature_stack().reduceRegion(

            reducer=ee.Reducer.mean()

            .combine(

                reducer2=ee.Reducer.stdDev(),

                sharedInputs=True

            )

            .combine(

                reducer2=ee.Reducer.min(),

                sharedInputs=True

            )

            .combine(

                reducer2=ee.Reducer.max(),

                sharedInputs=True

            ),

            geometry=self.region,

            scale=30,

            maxPixels=1e13

        )


    # ========================================================
    # Available Products
    # ========================================================

    def available_products(self):

        return {

            key: value is not None

            for key, value in self.products.items()

        }


    # ========================================================
    # Generate Everything
    # ========================================================

    @timer
    def generate_all(self):

        self.get_elevation()

        self.get_slope()

        self.get_aspect()

        self.get_hillshade()

        self.get_tri()

        self.get_tpi()

        self.get_feature_stack()

        return self


    # ========================================================
    # Product Export
    # ========================================================

    def export_products(self):

        return self.products.copy()


    # ========================================================
    # Status
    # ========================================================

    def status(self):

        return {

            key:

            (

                "READY"

                if value is not None

                else "NOT GENERATED"

            )

            for key, value in self.products.items()

        }


    # ========================================================
    # Summary
    # ========================================================

    def summary(self):

        print()

        print("=" * 60)

        print("TERRAIN PROCESSOR")

        print("=" * 60)

        print(

            "Loaded :",

            self.is_loaded

        )

        print()

        print("Products")

        print("-" * 60)

        for key, value in self.products.items():

            print(

                f"{key:<18}",

                ":",

                value is not None

            )

        print()


    # ========================================================
    # Self Test
    # ========================================================

    def self_test(self):

        self.generate_all()

        return {

            "processor": "Terrain",

            "status": self.status()

        }


    # ========================================================
    # Metadata
    # ========================================================

    def metadata(self):

        return self.dem.toDictionary()


    # ========================================================
    # Projection
    # ========================================================

    def projection(self):

        return self.dem.projection()


    # ========================================================
    # CRS
    # ========================================================

    def crs(self):

        return self.projection().crs()


    # ========================================================
    # Scale
    # ========================================================

    def scale(self):

        return self.projection().nominalScale()


    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self):

        ready = sum(

            value is not None

            for value in self.products.values()

        )

        total = len(self.products)

        return (

            f"TerrainProcessor("

            f"Loaded={self.is_loaded}, "

            f"Products={ready}/{total}"

            f")"

        )
        
