"""
============================================================

pipeline.py

Master GEE Processing Pipeline

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ Runs Entire GEE Pipeline

✔ Loads All Datasets

✔ Generates Feature Cubes

✔ AI Ready

============================================================
"""

from __future__ import annotations

from gee.logger import log
from gee.logger import timer

from gee.landsat import LandsatProcessor
from gee.sentinel import SentinelProcessor
from gee.terrain import TerrainProcessor
from gee.climate import ClimateProcessor
from gee.population import PopulationProcessor
from gee.urban import UrbanProcessor


# ============================================================
# Master Pipeline
# ============================================================

class UrbanHeatPipeline:

    """
    Master Processing Pipeline
    """

    # --------------------------------------------------------

    def __init__(

        self,

        region,

        start_date,

        end_date

    ):

        self.region = region

        self.start_date = start_date

        self.end_date = end_date

        self.landsat = LandsatProcessor(

            region,

            start_date,

            end_date

        )

        self.sentinel = SentinelProcessor(

            region,

            start_date,

            end_date

        )

        self.terrain = TerrainProcessor(

            region

        )

        self.climate = ClimateProcessor(

            region,

            start_date,

            end_date

        )

        self.population = PopulationProcessor(

            region

        )

        self.urban = UrbanProcessor(

            region

        )

        self.feature_cube = {}

        self.is_loaded = False

        self.is_generated = False

    # ========================================================

    @timer
    def load_all(self):

        """
        Loads every processor.
        """

        log.info(

            "Loading datasets..."

        )

        self.landsat.load()

        self.sentinel.load()

        self.terrain.load()

        self.climate.load()

        self.population.load()

        self.urban.load()

        self.is_loaded = True

        return self

    # ========================================================

    @timer
    def preprocess_all(self):

        """
        Runs preprocessing.

        """

        if not self.is_loaded:

            raise RuntimeError(

                "Call load_all() first."

            )

        self.landsat.preprocess()

        self.sentinel.preprocess()

        self.climate.preprocess()

        self.population.preprocess()

        return self

    # ========================================================

    @timer
    def generate_all(self):

        """
        Generates every feature.

        """

        self.landsat.generate_all()

        self.sentinel.generate_all()

        self.terrain.generate_all()

        self.climate.generate_all()

        self.population.generate_all()

        self.urban.generate_all()

        self.is_generated = True

        return self
    # ========================================================
# Build Feature Cube
# ========================================================

    @timer
    def build_feature_cube(self):

        """
        Creates the master AI feature dictionary.
        """

        if not self.is_generated:

            raise RuntimeError(

                "Call generate_all() first."

            )

        self.feature_cube = {

            "LANDSAT":

                self.landsat.get_feature_stack(),

            "SENTINEL":

                self.sentinel.get_feature_stack(),

            "TERRAIN":

                self.terrain.get_feature_stack(),

            "CLIMATE":

                self.climate.get_feature_stack(),

            "POPULATION":

                self.population.get_feature_stack(),

            "URBAN":

                self.urban.get_feature_stack()

        }

        return self.feature_cube


    # ========================================================
    # Statistics
    # ========================================================

    def statistics(self):

        return {

            "LANDSAT":

                self.landsat.statistics(),

            "SENTINEL":

                self.sentinel.statistics(),

            "TERRAIN":

                self.terrain.statistics(),

            "CLIMATE":

                self.climate.statistics(),

            "POPULATION":

                self.population.statistics(),

            "URBAN":

                self.urban.statistics()

        }


    # ========================================================
    # Processor Status
    # ========================================================

    def processor_status(self):

        return {

            "LANDSAT":

                self.landsat.status(),

            "SENTINEL":

                self.sentinel.status(),

            "TERRAIN":

                self.terrain.status(),

            "CLIMATE":

                self.climate.status(),

            "POPULATION":

                self.population.status(),

            "URBAN":

                self.urban.status()

        }


    # ========================================================
    # Available Products
    # ========================================================

    def available_products(self):

        return {

            "LANDSAT":

                self.landsat.available_products(),

            "SENTINEL":

                self.sentinel.available_products(),

            "TERRAIN":

                self.terrain.available_products(),

            "CLIMATE":

                self.climate.available_products(),

            "POPULATION":

                self.population.available_products(),

            "URBAN":

                self.urban.available_products()

        }


    # ========================================================
    # Summary
    # ========================================================

    def summary(self):

        print()

        print("=" * 70)

        print("MASTER URBAN HEAT PIPELINE")

        print("=" * 70)

        print(

            "Loaded :",

            self.is_loaded

        )

        print(

            "Generated :",

            self.is_generated

        )

        print()

        print("Processors")

        print("-" * 70)

        print("Landsat     :", self.landsat)

        print("Sentinel    :", self.sentinel)

        print("Terrain     :", self.terrain)

        print("Climate     :", self.climate)

        print("Population  :", self.population)

        print("Urban       :", self.urban)

        print()
# ========================================================
# Export Feature Cube
# ========================================================

    def export_feature_cube(self):

        return self.feature_cube.copy()


    # ========================================================
    # Self Test
    # ========================================================

    def self_test(self):

        self.load_all()

        self.preprocess_all()

        self.generate_all()

        self.build_feature_cube()

        return {

            "pipeline":

                "READY",

            "processors":

                self.processor_status()

        }


    # ========================================================
    # Run Entire Pipeline
    # ========================================================

    @timer
    def run(self):

        log.info(

            "Starting Urban Heat Pipeline..."

        )

        self.load_all()

        self.preprocess_all()

        self.generate_all()

        self.build_feature_cube()

        log.info(

            "Pipeline Completed Successfully."

        )

        return self.feature_cube


    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self):

        ready = len(

            self.feature_cube

        )

        return (

            f"UrbanHeatPipeline("

            f"Loaded={self.is_loaded}, "

            f"Generated={self.is_generated}, "

            f"FeatureCubes={ready}"

            f")"

        )