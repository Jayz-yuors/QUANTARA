"""
============================================================

climate.py

Climate Processing Engine

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ ERA5-Land Collection
✔ Air Temperature
✔ Relative Humidity
✔ Wind Speed
✔ Wind Direction
✔ Surface Pressure
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
    filter_collection
)

from gee.config import (
    ERA5,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE
)

# ============================================================
# ERA5 Band Dictionary
# ============================================================

TEMPERATURE = "temperature_2m"

DEWPOINT = "dewpoint_temperature_2m"

U_WIND = "u_component_of_wind_10m"

V_WIND = "v_component_of_wind_10m"

PRESSURE = "surface_pressure"

PRECIPITATION = "total_precipitation"

SOLAR = "surface_solar_radiation_downwards"

# ============================================================
# Climate Processor
# ============================================================

class ClimateProcessor:

    """
    ERA5 Climate Processing Engine
    """

    def __init__(

        self,

        region,

        start_date=DEFAULT_START_DATE,

        end_date=DEFAULT_END_DATE

    ):

        self.region = region

        self.start_date = start_date

        self.end_date = end_date

        self.collection = None

        self.products = {

            "COLLECTION": None,

            "COMPOSITE": None,

            "TEMPERATURE": None,

            "HUMIDITY": None,

            "WIND_SPEED": None,

            "WIND_DIRECTION": None,

            "PRESSURE": None,

            "PRECIPITATION": None,

            "SOLAR_RADIATION": None,

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

            "Loading ERA5 Climate Dataset..."

        )

        collection = get_collection(

            ERA5

        )

        collection = filter_collection(

            collection,

            self.region,

            self.start_date,

            self.end_date

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
    def create_composite(

        self,

        reducer="mean"

    ):

        if self.products["COMPOSITE"] is not None:

            return self.products["COMPOSITE"]

        reducer = reducer.lower()

        if reducer == "mean":

            composite = self.collection.mean()

        elif reducer == "median":

            composite = self.collection.median()

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

    @timer
    def get_temperature(self):

        if self.products["TEMPERATURE"] is not None:

            return self.products["TEMPERATURE"]

        temperature = (

            self.create_composite()

            .select(TEMPERATURE)

            .subtract(273.15)

            .rename("TEMPERATURE")

        )

        self.products["TEMPERATURE"] = temperature

        return temperature

    # ========================================================

    @timer
    def get_humidity(self):

        if self.products["HUMIDITY"] is not None:

            return self.products["HUMIDITY"]

        image = self.create_composite()

        humidity = image.expression(

            "100 - 5 * (T - Td)",

            {

                "T": image.select(TEMPERATURE),

                "Td": image.select(DEWPOINT)

            }

        ).rename(

            "HUMIDITY"

        )

        self.products["HUMIDITY"] = humidity

        return humidity

    # ========================================================

    @timer
    def get_wind_speed(self):

        if self.products["WIND_SPEED"] is not None:

            return self.products["WIND_SPEED"]

        image = self.create_composite()

        speed = image.expression(

            "sqrt((u*u)+(v*v))",

            {

                "u": image.select(U_WIND),

                "v": image.select(V_WIND)

            }

        ).rename(

            "WIND_SPEED"

        )

        self.products["WIND_SPEED"] = speed

        return speed

    # ========================================================

    @timer
    def get_wind_direction(self):

        if self.products["WIND_DIRECTION"] is not None:

            return self.products["WIND_DIRECTION"]

        image = self.create_composite()

        direction = image.expression(

            "atan2(u,v)",

            {

                "u": image.select(U_WIND),

                "v": image.select(V_WIND)

            }

        ).rename(

            "WIND_DIRECTION"

        )

        self.products["WIND_DIRECTION"] = direction

        return direction

    # ========================================================

    @timer
    def get_pressure(self):

        if self.products["PRESSURE"] is not None:

            return self.products["PRESSURE"]

        pressure = (

            self.create_composite()

            .select(PRESSURE)

            .rename("PRESSURE")

        )

        self.products["PRESSURE"] = pressure

        return pressure
    # ========================================================
# Total Precipitation
# ========================================================

    @timer
    def get_precipitation(self):

        if self.products["PRECIPITATION"] is not None:

            return self.products["PRECIPITATION"]

        precipitation = (

            self.create_composite()

            .select(PRECIPITATION)

            .multiply(1000)

            .rename("PRECIPITATION")

        )

        self.products["PRECIPITATION"] = precipitation

        return precipitation


    # ========================================================
    # Solar Radiation
    # ========================================================

    @timer
    def get_solar_radiation(self):

        if self.products["SOLAR_RADIATION"] is not None:

            return self.products["SOLAR_RADIATION"]

        solar = (

            self.create_composite()

            .select(SOLAR)

            .rename("SOLAR_RADIATION")

        )

        self.products["SOLAR_RADIATION"] = solar

        return solar


    # ========================================================
    # Climate Feature Stack
    # ========================================================

    @timer
    def get_feature_stack(self):

        if self.products["FEATURE_STACK"] is not None:

            return self.products["FEATURE_STACK"]

        stack = self.get_temperature()

        stack = stack.addBands([

            self.get_humidity(),

            self.get_wind_speed(),

            self.get_wind_direction(),

            self.get_pressure(),

            self.get_precipitation(),

            self.get_solar_radiation()

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

            scale=1000,

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

        self.get_temperature()

        self.get_humidity()

        self.get_wind_speed()

        self.get_wind_direction()

        self.get_pressure()

        self.get_precipitation()

        self.get_solar_radiation()

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

        print("CLIMATE PROCESSOR")

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

                f"{key:<20}",

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

            "processor": "Climate",

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

            f"ClimateProcessor("

            f"Loaded={self.is_loaded}, "

            f"Preprocessed={self.is_preprocessed}, "

            f"Products={ready}/{total}"

            f")"

        )
