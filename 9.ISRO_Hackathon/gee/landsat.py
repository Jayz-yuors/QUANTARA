"""
============================================================

landsat.py

Landsat 8 / Landsat 9 Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ Landsat Collection
✔ Composite Generation
✔ Automatic Caching
✔ Surface Reflectance
✔ Heat Feature Cube
✔ Visualization
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
    LANDSAT_COLLECTION,
    LANDSAT_CLOUD
)


# ============================================================
# Landsat Band Dictionary
# ============================================================

BLUE = "SR_B2"

GREEN = "SR_B3"

RED = "SR_B4"

NIR = "SR_B5"

SWIR1 = "SR_B6"

SWIR2 = "SR_B7"

THERMAL = "ST_B10"

QA = "QA_PIXEL"


# ============================================================
# Visualization Parameters
# ============================================================

RGB_VIS = {

    "bands": [RED, GREEN, BLUE],

    "min": 0,

    "max": 0.30

}

FALSE_COLOR_VIS = {

    "bands": [NIR, RED, GREEN],

    "min": 0,

    "max": 0.40

}

LST_VIS = {

    "min": 20,

    "max": 45,

    "palette": [

        "040274",

        "2C7BB6",

        "ABDDA4",

        "FFFFBF",

        "FDAE61",

        "D7191C"

    ]

}


# ============================================================
# Landsat Processor
# ============================================================

class LandsatProcessor:

    """
    Complete Landsat Processing Engine
    """

    # --------------------------------------------------------

    def __init__(

        self,

        region,

        start_date,

        end_date,

        cloud_threshold=LANDSAT_CLOUD

    ):

        self.region = region

        self.start_date = start_date

        self.end_date = end_date

        self.cloud_threshold = cloud_threshold

        self.collection = None
        # =====================================================
# Product Cache
# =====================================================

        self.products = {

            "COLLECTION": None,

            "COMPOSITE": None,

            "RGB": None,

            "FALSE_COLOR": None,

            "REFLECTANCE": None,

            "NDVI": None,

            "NDBI": None,

            "NDWI": None,

            "EVI": None,

            "ALBEDO": None,

            "LST": None,

            "HEAT_CUBE": None

        }
        self.is_loaded = False
        self.is_preprocessed = False
        self.is_composite_ready = False

        

        validate_geometry(region)

        validate_date_range(start_date, end_date)

    # ========================================================

    @timer
    def load(self):

        """
        Load Landsat Collection
        """

        log.info(

            "Loading Landsat Collection..."

        )

        collection = get_collection(

            LANDSAT_COLLECTION

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

        cloud = 1 << 3

        shadow = 1 << 4

        snow = 1 << 5

        mask = (

            qa.bitwiseAnd(cloud)

            .eq(0)

            .And(

                qa.bitwiseAnd(shadow)

                .eq(0)

            )

            .And(

                qa.bitwiseAnd(snow)

                .eq(0)

            )

        )

        return image.updateMask(mask)

    # ========================================================

    def _apply_scale(

        self,

        image

    ):

        optical = (

            image

            .select("SR_B.*")

            .multiply(0.0000275)

            .add(-0.2)

        )

        thermal = (

            image

            .select(THERMAL)

            .multiply(0.00341802)

            .add(149.0)

        )

        image = image.addBands(

            optical,

            overwrite=True

        )

        image = image.addBands(

            thermal,

            overwrite=True

        )

        return image

    # ========================================================

    @timer
    def preprocess(self):

        """
        Cloud Mask

        Scale Factors

        """

        self.collection = self.collection.map(

            self._mask_clouds

        )

        self.collection = self.collection.map(

            self._apply_scale

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

        """
        Creates a cached Landsat composite.
        """

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
# Land Surface Temperature
# ========================================================
    # ========================================================
# NDVI
# ========================================================

    def _calculate_ndvi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [NIR, RED]

        ).rename("NDVI")


    # ========================================================
    # NDBI
    # ========================================================

    def _calculate_ndbi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [SWIR1, NIR]

        ).rename("NDBI")


    # ========================================================
    # NDWI
    # ========================================================

    def _calculate_ndwi(self):

        image = self.create_composite()

        return image.normalizedDifference(

            [GREEN, NIR]

        ).rename("NDWI")


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
    # Compute All Indices
    # ========================================================

    @timer
    def get_indices(self):

        """
        Computes all spectral indices only once.
        """

        if self.products["NDVI"] is not None:

            return {

                "NDVI": self.products["NDVI"],

                "NDBI": self.products["NDBI"],

                "NDWI": self.products["NDWI"],

                "EVI": self.products["EVI"]

            }

        self.products["NDVI"] = self._calculate_ndvi()

        self.products["NDBI"] = self._calculate_ndbi()

        self.products["NDWI"] = self._calculate_ndwi()

        self.products["EVI"] = self._calculate_evi()

        return {

            "NDVI": self.products["NDVI"],

            "NDBI": self.products["NDBI"],

            "NDWI": self.products["NDWI"],

            "EVI": self.products["EVI"]

        }


    # ========================================================
    # Feature Stack
    # ========================================================

    @timer
    def get_feature_stack(self):

        indices = self.get_indices()

        stack = indices["NDVI"]

        stack = stack.addBands([

            indices["NDBI"],

            indices["NDWI"],

            indices["EVI"]

        ])

        return stack
    @timer
    def get_lst(self):
        """
        Returns Land Surface Temperature (°C).
        """

        if self.products["LST"] is not None:
            return self.products["LST"]

        image = self.create_composite()

        lst = (
            image
            .select(THERMAL)
            .subtract(273.15)
            .rename("LST")
        )

        self.products["LST"] = lst

        return lst


    # ========================================================
    # Broadband Surface Albedo
    # ========================================================

    @timer
    def get_albedo(self):
        """
        Computes broadband albedo using Landsat reflectance.
        """

        if self.products["ALBEDO"] is not None:
            return self.products["ALBEDO"]

        image = self.create_composite()

        albedo = image.expression(

            "(0.356*B2)+(0.130*B4)+(0.373*B5)+(0.085*B6)+(0.072*B7)-0.0018",

            {

                "B2": image.select(BLUE),

                "B4": image.select(RED),

                "B5": image.select(NIR),

                "B6": image.select(SWIR1),

                "B7": image.select(SWIR2)

            }

        ).rename("ALBEDO")

        self.products["ALBEDO"] = albedo

        return albedo


    # ========================================================
    # Heat Feature Cube
    # ========================================================

    @timer
    def get_heat_cube(self):
        """
        AI-ready feature cube for Urban Heat modelling.
        """

        if self.products["HEAT_CUBE"] is not None:
            return self.products["HEAT_CUBE"]

        indices = self.get_indices()

        cube = self.get_lst()

        cube = cube.addBands([

            indices["NDVI"],

            indices["NDBI"],

            indices["NDWI"],

            indices["EVI"],

            self.get_albedo()

        ])

        self.products["HEAT_CUBE"] = cube

        return cube


    # ========================================================
    # Heat Cube Bands
    # ========================================================

    def heat_cube_bands(self):

        return self.get_heat_cube().bandNames()


    # ========================================================
    # Heat Statistics
    # ========================================================

    @timer
    def heat_statistics(self):

        cube = self.get_heat_cube()

        stats = cube.reduceRegion(

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

        return stats


    # ========================================================
    # Quick Heat Summary
    # ========================================================

    def heat_summary(self):

        print()

        print("=" * 60)

        print("HEAT FEATURES")

        print("=" * 60)

        print(

            "LST         :",

            self.products["LST"] is not None

        )

        print(

            "ALBEDO      :",

            self.products["ALBEDO"] is not None

        )

        print(

            "HEAT CUBE   :",

            self.products["HEAT_CUBE"] is not None

        )

        print()
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

            NIR,

            SWIR1,

            SWIR2

        ])

        self.products["REFLECTANCE"] = reflectance

        return reflectance


    # ========================================================
    # Natural RGB
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
    # False Color
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
    # Visualization Presets
    # ========================================================

    def rgb_vis(self):

        return RGB_VIS


    def false_color_vis(self):

        return FALSE_COLOR_VIS


    def lst_vis(self):

        return LST_VIS


    # ========================================================
    # Available Products
    # ========================================================

    def available_products(self):

        return {

            key: value is not None

            for key, value in self.products.items()

        }


    # ========================================================
    # Product Bands
    # ========================================================

    def product_bands(self, product):

        if product not in self.products:

            raise ValueError(

                f"{product} not found."

            )

        image = self.products[product]

        if image is None:

            return None

        return image.bandNames()


    # ========================================================
    # Metadata
    # ========================================================

    def metadata(self):

        image = self.create_composite()

        return image.toDictionary()


    # ========================================================
    # Projection
    # ========================================================

    def projection(self):

        return self.create_composite().projection()


    # ========================================================
    # CRS
    # ========================================================

    def crs(self):

        return self.projection().crs()


    # ========================================================
    # Nominal Scale
    # ========================================================

    def scale(self):

        return self.projection().nominalScale()
    def summary(self):

        print()

        print("=" * 60)

        print("LANDSAT PROCESSOR")

        print("=" * 60)

        print(

            "Loaded              :",

            self.is_loaded

        )

        print(

            "Preprocessed        :",

            self.is_preprocessed

        )

        print(

            "Composite Ready     :",

            self.is_composite_ready

        )

        print()

        print("Cached Products")

        print("-" * 60)

        for key, value in self.products.items():

            print(

                f"{key:<15}",

                ":",

                value is not None

            )

        print()
    # ========================================================
    # ========================================================
# Reset Cache
# ========================================================

    def reset_cache(self):

        """
        Clears every cached product except the collection.
        """

        collection = self.products["COLLECTION"]

        self.products = {

            key: None

            for key in self.products

        }

        self.products["COLLECTION"] = collection

        self.is_composite_ready = False

        return self
    # ========================================================
# Validate Pipeline
# ========================================================

    def validate(self):

        """
        Validates processor state.
        """

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
# Generate Everything
# ========================================================

    @timer
    def generate_all(self):

        """
        Generates every available Landsat product.
        """

        self.validate()

        self.create_composite()

        self.get_surface_reflectance()

        self.get_rgb()

        self.get_false_color()

        self.get_indices()

        self.get_lst()

        self.get_albedo()

        self.get_heat_cube()

        return self
    # ========================================================
# Product Status
# ========================================================

    def status(self):

        return {

            key: (

                "READY"

                if value is not None

                else "NOT GENERATED"

            )

            for key, value in self.products.items()

        }
# ========================================================
# Self Test
# ========================================================

    def self_test(self):

        """
        Runs a basic processor health check.
        """

        self.validate()

        self.generate_all()

        return {

            "loaded": self.is_loaded,

            "preprocessed": self.is_preprocessed,

            "composite": self.is_composite_ready,

            "products": self.status()

        }
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

            f"LandsatProcessor("

            f"Loaded={self.is_loaded}, "

            f"Preprocessed={self.is_preprocessed}, "

            f"Products={ready}/{total}"

            f")"

        )



