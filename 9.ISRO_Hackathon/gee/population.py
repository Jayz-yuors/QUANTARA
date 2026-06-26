"""
============================================================

population.py

Population Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ WorldPop Population
✔ Population Density
✔ Urban Population
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
    WORLDPOP
)

# ============================================================
# Population Visualization
# ============================================================

POP_VIS = {

    "min": 0,

    "max": 1000,

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

# ============================================================
# Population Processor
# ============================================================

class PopulationProcessor:

    """
    Population Processing Engine
    """

    def __init__(

        self,

        region

    ):

        self.region = region

        self.collection = None

        self.products = {

            "COLLECTION": None,

            "COMPOSITE": None,

            "POPULATION": None,

            "POPULATION_DENSITY": None,

            "URBAN_POPULATION": None,

            "EXPOSURE": None,

            "FEATURE_STACK": None

        }

        self.is_loaded = False

        self.is_preprocessed = False

        self.is_composite_ready = False

        validate_geometry(region)

    # ========================================================

    @timer
    def load(self):

        log.info(

            "Loading WorldPop Dataset..."

        )

        collection = get_collection(

            WORLDPOP

        )

        self.collection = collection

        self.products["COLLECTION"] = collection

        self.is_loaded = True

        return self

    # ========================================================

    @timer
    def preprocess(self):

        self.products["COLLECTION"] = self.collection

        self.is_preprocessed = True

        return self

    # ========================================================

    @timer
    def create_composite(self):

        if self.products["COMPOSITE"] is not None:

            return self.products["COMPOSITE"]

        composite = (

            self.collection

            .mosaic()

            .clip(self.region)

        )

        self.products["COMPOSITE"] = composite

        self.is_composite_ready = True

        return composite

    # ========================================================

    @timer
    def get_population(self):

        if self.products["POPULATION"] is not None:

            return self.products["POPULATION"]

        population = (

            self.create_composite()

            .rename("POPULATION")

        )

        self.products["POPULATION"] = population

        return population

    # ========================================================

    @timer
    def get_population_density(self):

        if self.products["POPULATION_DENSITY"] is not None:

            return self.products["POPULATION_DENSITY"]

        density = (

            self.get_population()

            .rename("POPULATION_DENSITY")

        )

        self.products["POPULATION_DENSITY"] = density

        return density

    # ========================================================

    @timer
    def get_urban_population(self):

        if self.products["URBAN_POPULATION"] is not None:

            return self.products["URBAN_POPULATION"]

        urban_population = (

            self.get_population()

            .updateMask(

                self.get_population().gt(300)

            )

            .rename("URBAN_POPULATION")

        )

        self.products["URBAN_POPULATION"] = urban_population

        return urban_population
    # ========================================================
# Population Exposure Layer
# ========================================================

    @timer
    def get_population_exposure(self):

        if self.products["EXPOSURE"] is not None:

            return self.products["EXPOSURE"]

        exposure = (

            self.get_population_density()

            .unitScale(0, 1000)

            .rename("POPULATION_EXPOSURE")

        )

        self.products["EXPOSURE"] = exposure

        return exposure


    # ========================================================
    # Population Feature Stack
    # ========================================================

    @timer
    def get_feature_stack(self):

        if self.products["FEATURE_STACK"] is not None:

            return self.products["FEATURE_STACK"]

        stack = self.get_population()

        stack = stack.addBands([

            self.get_population_density(),

            self.get_urban_population(),

            self.get_population_exposure()

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

            scale=100,

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

        self.get_population()

        self.get_population_density()

        self.get_urban_population()

        self.get_population_exposure()

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
    # Metadata
    # ========================================================

    def metadata(self):

        return self.create_composite().toDictionary()


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
    # Scale
    # ========================================================

    def scale(self):

        return self.projection().nominalScale()


    # ========================================================
    # Summary
    # ========================================================

    def summary(self):

        print()

        print("=" * 60)

        print("POPULATION PROCESSOR")

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

            "processor": "Population",

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

            f"PopulationProcessor("

            f"Loaded={self.is_loaded}, "

            f"Preprocessed={self.is_preprocessed}, "

            f"Products={ready}/{total}"

            f")"

        )
