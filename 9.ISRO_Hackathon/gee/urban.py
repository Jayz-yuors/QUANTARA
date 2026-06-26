"""
============================================================

urban.py

Urban Infrastructure Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ GHSL Built-up
✔ GHSL Population
✔ VIIRS Night Lights
✔ OpenStreetMap Roads
✔ OpenStreetMap Buildings
✔ Urban Feature Generation
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

    GHSL_BUILTUP,

    GHSL_POP,

    VIIRS

)

# ============================================================
# Visualization
# ============================================================

BUILTUP_VIS = {

    "min": 0,

    "max": 100,

    "palette": [

        "FFFFFF",

        "FFF7BC",

        "FEC44F",

        "FE9929",

        "EC7014",

        "CC4C02",

        "993404"

    ]

}

NIGHTLIGHT_VIS = {

    "min": 0,

    "max": 60,

    "palette": [

        "000000",

        "2C7BB6",

        "ABDDA4",

        "FFFFBF",

        "FDAE61",

        "D7191C"

    ]

}

# ============================================================
# Urban Processor
# ============================================================

class UrbanProcessor:

    """
    Urban Infrastructure Processor

    Multi-source processor combining

    GHSL

    VIIRS

    OpenStreetMap

    """

    def __init__(

        self,

        region

    ):

        self.region = region

        self.products = {

            "GHSL_BUILTUP": None,

            "GHSL_POP": None,

            "VIIRS": None,

            "ROADS": None,

            "BUILDINGS": None,

            "BUILTUP": None,

            "BUILDING_DENSITY": None,

            "ROAD_DENSITY": None,

            "NIGHT_LIGHTS": None,

            "URBAN_MORPHOLOGY": None,

            "IMPERVIOUS": None,

            "FEATURE_STACK": None

        }

        self.is_loaded = False

        validate_geometry(region)

    # ========================================================

    @timer
    def load(self):

        log.info(

            "Loading Urban Datasets..."

        )

        builtup = (

    ee.Image(

        GHSL_BUILTUP

    )

    .clip(

        self.region

    )

)

        population = (

    ee.Image(

        GHSL_POP

    )

    .clip(

        self.region

    )

)

        viirs = (

            get_collection(

                VIIRS

            )

            .median()

            .clip(

                self.region

            )

        )

        self.products["GHSL_BUILTUP"] = builtup

        self.products["GHSL_POP"] = population

        self.products["VIIRS"] = viirs

        self.is_loaded = True

        return self

    # ========================================================

    @timer
    def load_osm(

        self,

        roads=None,

        buildings=None

    ):

        """
        Optional OSM Loader.

        Can later accept

        GeoJSON

        FeatureCollection

        Local Vector

        """

        self.products["ROADS"] = roads

        self.products["BUILDINGS"] = buildings

        return self

    # ========================================================
    # ========================================================
# Built-up Layer
# ========================================================

    @timer
    def get_builtup(self):

        if self.products["BUILTUP"] is not None:

            return self.products["BUILTUP"]

        builtup = (

            self.products["GHSL_BUILTUP"]

            .rename("BUILTUP")

        )

        self.products["BUILTUP"] = builtup

        return builtup


    # ========================================================
    # Building Density
    # ========================================================

    @timer
    def get_building_density(self):

        if self.products["BUILDING_DENSITY"] is not None:

            return self.products["BUILDING_DENSITY"]

        if self.products["BUILDINGS"] is None:

            density = (

    self.get_builtup()

    .rename(

        "BUILDING_DENSITY"

    )

)

        else:

            density = (

                ee.Image()

                .float()

                .paint(

                    self.products["BUILDINGS"],

                    1

                )

                .focal_mean(

                    radius=100,

                    units="meters"

                )

                .rename(

                    "BUILDING_DENSITY"

                )

            )

        self.products["BUILDING_DENSITY"] = density

        return density


    # ========================================================
    # Road Density
    # ========================================================

    @timer
    def get_road_density(self):

        if self.products["ROAD_DENSITY"] is not None:

            return self.products["ROAD_DENSITY"]

        if self.products["ROADS"] is None:

            density = ee.Image.constant(0).rename(

                "ROAD_DENSITY"

            )

        else:

            density = (

                ee.Image()

                .float()

                .paint(

                    self.products["ROADS"],

                    1

                )

                .focal_mean(

                    radius=100,

                    units="meters"

                )

                .rename(

                    "ROAD_DENSITY"

                )

            )

        self.products["ROAD_DENSITY"] = density

        return density


    # ========================================================
    # Night Lights
    # ========================================================

    @timer
    def get_night_lights(self):

        if self.products["NIGHT_LIGHTS"] is not None:

            return self.products["NIGHT_LIGHTS"]

        night = (

            self.products["VIIRS"]

            .rename("NIGHT_LIGHTS")

        )

        self.products["NIGHT_LIGHTS"] = night

        return night


    # ========================================================
    # Urban Morphology
    # ========================================================

    @timer
    def get_urban_morphology(self):

        if self.products["URBAN_MORPHOLOGY"] is not None:

            return self.products["URBAN_MORPHOLOGY"]

        morphology = (

            self.get_builtup()

            .focal_max(

                radius=100,

                units="meters"

            )

            .subtract(

                self.get_builtup()

                .focal_min(

                    radius=100,

                    units="meters"

                )

            )

            .rename(

                "URBAN_MORPHOLOGY"

            )

        )

        self.products["URBAN_MORPHOLOGY"] = morphology

        return morphology


    # ========================================================
    # Impervious Surface Proxy
    # ========================================================

    @timer
    def get_impervious_surface(self):

        if self.products["IMPERVIOUS"] is not None:

            return self.products["IMPERVIOUS"]

        impervious = (

            self.get_builtup()

            .multiply(0.6)

            .add(

                self.get_night_lights()

                .unitScale(

                    0,

                    60

                )

                .multiply(0.4)

            )

            .rename(

                "IMPERVIOUS"

            )

        )

        self.products["IMPERVIOUS"] = impervious

        return impervious
    # ========================================================
# Urban Feature Stack
# ========================================================

    @timer
    def get_feature_stack(self):

        if self.products["FEATURE_STACK"] is not None:

            return self.products["FEATURE_STACK"]

        stack = self.get_builtup()

        stack = stack.addBands([

            self.get_building_density(),

            self.get_road_density(),

            self.get_night_lights(),

            self.get_urban_morphology(),

            self.get_impervious_surface()

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
    # Metadata
    # ========================================================

    def metadata(self):

        return {

            "datasets": [

                "GHSL",

                "VIIRS",

                "OpenStreetMap"

            ]

        }


    # ========================================================
    # Projection
    # ========================================================

    def projection(self):

        return self.get_builtup().projection()


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
    # Available Products
    # ========================================================

    def available_products(self):

        return {

            key: value is not None

            for key, value in self.products.items()

        }


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
    # Validate
    # ========================================================

    def validate(self):

        if not self.is_loaded:

            raise RuntimeError(

                "Urban datasets not loaded."

            )

        return True


    # ========================================================
    # Generate Everything
    # ========================================================

    @timer
    def generate_all(self):

        self.validate()

        self.get_builtup()

        self.get_building_density()

        self.get_road_density()

        self.get_night_lights()

        self.get_urban_morphology()

        self.get_impervious_surface()

        self.get_feature_stack()

        return self


    # ========================================================
    # Product Export
    # ========================================================

    def export_products(self):

        return self.products.copy()


    # ========================================================
    # Summary
    # ========================================================

    def summary(self):

        print()

        print("=" * 60)

        print("URBAN PROCESSOR")

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

                f"{key:<22}",

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

            "processor": "Urban",

            "status": self.status()

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

            f"UrbanProcessor("

            f"Loaded={self.is_loaded}, "

            f"Products={ready}/{total}"

            f")"

        )
