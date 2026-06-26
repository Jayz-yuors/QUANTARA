"""
============================================================

sentinel.py

Sentinel-2 Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ Sentinel-2 Collection
✔ Automatic Caching
✔ Cloud Masking
✔ Surface Reflectance
✔ Composite Generation
✔ AI Ready

============================================================
"""

from __future__ import annotations

import ee

from gee.logger import log
from gee.logger import timer

from gee.data_fetch import (
    validate_geometry,
    validate_date_range,
    get_collection,
    filter_collection,
    cloud_filter
)

from gee.config import (
    SENTINEL_COLLECTION,
    SENTINEL_CLOUD
)

# ============================================================
# Sentinel Band Dictionary
# ============================================================

BLUE = "B2"

GREEN = "B3"

RED = "B4"

RE1 = "B5"

RE2 = "B6"

RE3 = "B7"

NIR = "B8"

NARROW_NIR = "B8A"

SWIR1 = "B11"

SWIR2 = "B12"

QA = "QA60"

# ============================================================
# Visualization
# ============================================================

RGB_VIS = {

    "bands": [RED, GREEN, BLUE],

    "min": 0,

    "max": 3000

}

FALSE_COLOR_VIS = {

    "bands": [NIR, RED, GREEN],

    "min": 0,

    "max": 3000

}

# ============================================================
# Sentinel Processor
# ============================================================

class SentinelProcessor:

    """
    Sentinel-2 Processing Engine
    """

    def __init__(

        self,

        region,

        start_date,

        end_date,

        cloud_threshold=SENTINEL_CLOUD

    ):

        self.region = region

        self.start_date = start_date

        self.end_date = end_date

        self.cloud_threshold = cloud_threshold

        self.collection = None

        self.products = {

            "COLLECTION": None,

            "COMPOSITE": None,

            "REFLECTANCE": None,

            "RGB": None,

            "FALSE_COLOR": None,

            "NDVI": None,

            "EVI": None,

            "SAVI": None,

            "MSAVI": None,

            "GCI": None,

            "NDWI": None,

            "MNDWI": None,

            "NDBI": None,

            "FEATURE_STACK": None

        }

        self.is_loaded = False

        self.is_preprocessed = False

        self.is_composite_ready = False

        validate_geometry(region)

        validate_date_range(start_date, end_date)

    # ========================================================

    @timer
    def load(self):

        log.info(

            "Loading Sentinel-2 Collection..."

        )

        collection = get_collection(

            SENTINEL_COLLECTION

        )

        collection = filter_collection(

            collection,

            self.region,

            self.start_date,

            self.end_date

        )

        collection = cloud_filter(

            collection,

            self.cloud_threshold

        )

        self.collection = collection

        self.products["COLLECTION"] = collection

        self.is_loaded = True

        return self

    # ========================================================

    def _mask_clouds(

        self,

        image

    ):

        qa = image.select(QA)

        cloud = 1 << 10

        cirrus = 1 << 11

        mask = (

            qa.bitwiseAnd(cloud)

            .eq(0)

            .And(

                qa.bitwiseAnd(cirrus)

                .eq(0)

            )

        )

        return (

            image

            .updateMask(mask)

            .divide(10000)

        )

    # ========================================================

    @timer
    def preprocess(self):

        self.collection = self.collection.map(

            self._mask_clouds

        )

        self.products["COLLECTION"] = self.collection

        self.is_preprocessed = True

        return self

    # ========================================================

    @timer
    def create_composite(

        self,

        reducer="median"

    ):

        if self.products["COMPOSITE"] is not None:

            return self.products["COMPOSITE"]

        reducer = reducer.lower()

        if reducer == "median":

            composite = self.collection.median()

        elif reducer == "mean":

            composite = self.collection.mean()

        elif reducer == "max":

            composite = self.collection.max()

        elif reducer == "min":

            composite = self.collection.min()

        else:

            raise ValueError(

                "Unsupported reducer."

            )

        self.products["COMPOSITE"] = composite

        self.is_composite_ready = True

        return composite

    # ========================================================
    # ========================================================
# Surface Reflectance
# ========================================================

    @timer
    def get_surface_reflectance(self):

        if self.products["REFLECTANCE"] is not None:
            return self.products["REFLECTANCE"]

        image = self.create_composite()

        reflectance = image.select([

            BLUE,

            GREEN,

            RED,

            RE1,

            RE2,

            RE3,

            NIR,

            NARROW_NIR,

            SWIR1,

            SWIR2

        ])

        self.products["REFLECTANCE"] = reflectance

        return reflectance


    # ========================================================
    # RGB Composite
    # ========================================================

    @timer
    def get_rgb(self):

        if self.products["RGB"] is not None:
            return self.products["RGB"]

        rgb = self.get_surface_reflectance().select(

            [RED, GREEN, BLUE]

        )

        self.products["RGB"] = rgb

        return rgb


    # ========================================================
    # False Color Composite
    # ========================================================

    @timer
    def get_false_color(self):

        if self.products["FALSE_COLOR"] is not None:
            return self.products["FALSE_COLOR"]

        false_color = self.get_surface_reflectance().select(

            [

                NIR,

                RED,

                GREEN

            ]

        )

        self.products["FALSE_COLOR"] = false_color

        return false_color


    # ========================================================
    # NDVI
    # ========================================================

    def _calculate_ndvi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [

                NIR,

                RED

            ]

        ).rename("NDVI")


    # ========================================================
    # EVI
    # ========================================================

    def _calculate_evi(self):

        image = self.create_composite()

        return image.expression(

            "2.5*((NIR-RED)/(NIR+6*RED-7.5*BLUE+1))",

            {

                "NIR": image.select(NIR),

                "RED": image.select(RED),

                "BLUE": image.select(BLUE)

            }

        ).rename("EVI")


    # ========================================================
    # SAVI
    # ========================================================

    def _calculate_savi(self):

        image = self.create_composite()

        return image.expression(

            "((NIR-RED)/(NIR+RED+0.5))*1.5",

            {

                "NIR": image.select(NIR),

                "RED": image.select(RED)

            }

        ).rename("SAVI")


    # ========================================================
    # MSAVI
    # ========================================================

    def _calculate_msavi(self):

        image = self.create_composite()

        return image.expression(

            "(2*NIR+1-sqrt((2*NIR+1)**2-8*(NIR-RED)))/2",

            {

                "NIR": image.select(NIR),

                "RED": image.select(RED)

            }

        ).rename("MSAVI")


    # ========================================================
    # GCI
    # ========================================================

    def _calculate_gci(self):

        image = self.create_composite()

        return image.expression(

            "(NIR/GREEN)-1",

            {

                "NIR": image.select(NIR),

                "GREEN": image.select(GREEN)

            }

        ).rename("GCI")


    # ========================================================
    # NDWI
    # ========================================================

    def _calculate_ndwi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [

                GREEN,

                NIR

            ]

        ).rename("NDWI")


    # ========================================================
    # MNDWI
    # ========================================================

    def _calculate_mndwi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [

                GREEN,

                SWIR1

            ]

        ).rename("MNDWI")


    # ========================================================
    # NDBI
    # ========================================================

    def _calculate_ndbi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [

                SWIR1,

                NIR

            ]

        ).rename("NDBI")


    # ========================================================
    # Compute All Spectral Indices
    # ========================================================

    @timer
    def get_indices(self):

        if self.products["NDVI"] is not None:

            return {

                "NDVI": self.products["NDVI"],

                "EVI": self.products["EVI"],

                "SAVI": self.products["SAVI"],

                "MSAVI": self.products["MSAVI"],

                "GCI": self.products["GCI"],

                "NDWI": self.products["NDWI"],

                "MNDWI": self.products["MNDWI"],

                "NDBI": self.products["NDBI"]

            }

        self.products["NDVI"] = self._calculate_ndvi()

        self.products["EVI"] = self._calculate_evi()

        self.products["SAVI"] = self._calculate_savi()

        self.products["MSAVI"] = self._calculate_msavi()

        self.products["GCI"] = self._calculate_gci()

        self.products["NDWI"] = self._calculate_ndwi()

        self.products["MNDWI"] = self._calculate_mndwi()

        self.products["NDBI"] = self._calculate_ndbi()

        return {

            "NDVI": self.products["NDVI"],

            "EVI": self.products["EVI"],

            "SAVI": self.products["SAVI"],

            "MSAVI": self.products["MSAVI"],

            "GCI": self.products["GCI"],

            "NDWI": self.products["NDWI"],

            "MNDWI": self.products["MNDWI"],

            "NDBI": self.products["NDBI"]

        }


    # ========================================================
    # AI Feature Stack
    # ========================================================

    @timer
    def get_feature_stack(self):

        if self.products["FEATURE_STACK"] is not None:

            return self.products["FEATURE_STACK"]

        indices = self.get_indices()

        stack = indices["NDVI"]

        stack = stack.addBands([

            indices["EVI"],

            indices["SAVI"],

            indices["MSAVI"],

            indices["GCI"],

            indices["NDWI"],

            indices["MNDWI"],

            indices["NDBI"]

        ])

        self.products["FEATURE_STACK"] = stack

        return stack

    # ========================================================
# Vegetation Mask
# ========================================================

    @timer
    def vegetation_mask(self, threshold=0.30):

        return self.get_indices()["NDVI"].gt(threshold)


    # ========================================================
    # Water Mask
    # ========================================================

    @timer
    def water_mask(self, threshold=0.20):

        return self.get_indices()["MNDWI"].gt(threshold)


    # ========================================================
    # Built-up Mask
    # ========================================================

    @timer
    def builtup_mask(self, threshold=0.10):

        return self.get_indices()["NDBI"].gt(threshold)


    # ========================================================
    # Bare Soil Mask
    # ========================================================

    @timer
    def bare_soil_mask(self):

        ndvi = self.get_indices()["NDVI"]

        ndbi = self.get_indices()["NDBI"]

        return (

            ndvi.lt(0.25)

            .And(

                ndbi.lt(0.10)

            )

        )


    # ========================================================
    # Statistics
    # ========================================================

    @timer
    def statistics(self):

        stack = self.get_feature_stack()

        return stack.reduceRegion(

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

            scale=10,

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

        self.validate()

        self.create_composite()

        self.get_surface_reflectance()

        self.get_rgb()

        self.get_false_color()

        self.get_indices()

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

        print("SENTINEL PROCESSOR")

        print("=" * 60)

        print(

            "Loaded :",

            self.is_loaded

        )

        print(

            "Preprocessed :",

            self.is_preprocessed

        )

        print(

            "Composite :",

            self.is_composite_ready

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

        self.validate()

        self.generate_all()

        return {

            "processor": "Sentinel",

            "status": self.status()

        }
    def validate(self):

        if not self.is_loaded:

            raise RuntimeError(

                "Collection not loaded."

            )

        if not self.is_preprocessed:

            raise RuntimeError(

                "Collection not preprocessed."

            )

        return True

    # ========================================================

    def __repr__(self):

        ready = sum(

            value is not None

            for value in self.products.values()

        )

        total = len(self.products)

        return (

            f"SentinelProcessor("

            f"Loaded={self.is_loaded}, "

            f"Preprocessed={self.is_preprocessed}, "

            f"Products={ready}/{total}"

            f")"

        )
    
