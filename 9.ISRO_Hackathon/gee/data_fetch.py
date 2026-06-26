"""
===========================================================
Google Earth Engine Data Fetch Module

Urban Heat Mitigation Project

Author : Quantara

===========================================================

Core Responsibilities

✓ Initialize Earth Engine
✓ Authenticate User
✓ Project Validation
✓ Geometry Validation
✓ Date Validation
✓ ImageCollection Validation
✓ Common Helper Functions

===========================================================
"""

from __future__ import annotations

import ee
import datetime
import functools
import traceback

from typing import Optional
from typing import Union

from gee.logger import log
from gee.logger import timer

from gee.config import DEFAULT_PROJECT


# ==========================================================
# Exceptions
# ==========================================================

class GEEInitializationError(Exception):
    """Raised when Earth Engine initialization fails."""
    pass


class InvalidGeometryError(Exception):
    """Raised when invalid geometry is supplied."""
    pass


class InvalidDateError(Exception):
    """Raised when invalid date is supplied."""
    pass


# ==========================================================
# Authentication
# ==========================================================

@timer
def initialize_gee(project: Optional[str] = None):

    """
    Authenticate and Initialize Google Earth Engine.

    Parameters
    ----------
    project : str

        GEE Project ID

    """

    if project is None:
        project = DEFAULT_PROJECT

    try:

        log.info("Initializing Google Earth Engine...")

        try:

            ee.Initialize(project=project)

        except Exception:

            log.warning("Authentication required...")

            ee.Authenticate()

            ee.Initialize(project=project)

        log.success("Google Earth Engine Initialized Successfully")

    except Exception as ex:

        log.error("Failed to initialize Earth Engine")

        traceback.print_exc()

        raise GEEInitializationError(str(ex))


# ==========================================================
# Geometry Validation
# ==========================================================

def validate_geometry(region):

    """
    Validate ee.Geometry object.

    Parameters
    ----------

    region : ee.Geometry

    Returns
    -------

    ee.Geometry

    """

    if region is None:

        raise InvalidGeometryError(
            "Region cannot be None."
        )

    if not isinstance(region, ee.geometry.Geometry):

        raise InvalidGeometryError(
            "Input must be ee.Geometry."
        )

    return region


# ==========================================================
# Date Validation
# ==========================================================

def validate_date(date_string: str):

    """
    Validate YYYY-MM-DD format.

    """

    try:

        datetime.datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return date_string

    except Exception:

        raise InvalidDateError(
            f"Invalid date : {date_string}"
        )


# ==========================================================
# Validate Date Range
# ==========================================================

def validate_date_range(
        start_date: str,
        end_date: str
):

    validate_date(start_date)

    validate_date(end_date)

    start = datetime.datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    end = datetime.datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )

    if start > end:

        raise InvalidDateError(
            "Start date must be before End date."
        )

    return start_date, end_date


# ==========================================================
# Decorator
# ==========================================================

def validate_inputs(func):

    """
    Automatically validates

    Geometry

    Start Date

    End Date

    """

    @functools.wraps(func)

    def wrapper(
            region,
            start_date,
            end_date,
            *args,
            **kwargs
    ):

        validate_geometry(region)

        validate_date_range(
            start_date,
            end_date
        )

        return func(
            region,
            start_date,
            end_date,
            *args,
            **kwargs
        )

    return wrapper


# ==========================================================
# Collection Loader
# ==========================================================

def get_collection(
        collection_name: str
):

    """
    Return an Earth Engine ImageCollection.

    This helper intentionally stays lazy: it does not call getInfo(),
    so creating a collection does not trigger a server request.

    """

    return ee.ImageCollection(
        collection_name
    )


def load_collection(
        collection_name: str
):

    """
    Backward-compatible alias for get_collection().
    Prefer get_collection() in new code.
    """

    return get_collection(collection_name)


# ==========================================================
# Filter Collection
# ==========================================================

def filter_collection(
        collection,
        region,
        start_date,
        end_date
):

    return (
        collection
        .filterBounds(region)
        .filterDate(
            start_date,
            end_date
        )
    )


# ==========================================================
# Cloud Filter
# ==========================================================

def cloud_filter(
        collection,
        threshold=20
):

    return collection.filter(
        ee.Filter.lt(
            "CLOUD_COVER",
            threshold
        )
    )


# ==========================================================
# Get Collection Size
# ==========================================================

def collection_size(collection):

    return collection.size()


# ==========================================================
# Get First Image
# ==========================================================

def first_image(collection):

    return ee.Image(
        collection.first()
    )


# ==========================================================
# Print Collection Info
# ==========================================================

def print_collection_info(collection):

    print()

    print("=" * 60)

    print("Collection Information")

    print("=" * 60)

    print(
        "Images :",
        collection.size().getInfo()
    )

    print()

# ==========================================================
# Image Loader
# ==========================================================

@timer
def load_image(image_id: str):

    """
    Load a single Earth Engine image.

    Parameters
    ----------
    image_id : str

    Returns
    -------
    ee.Image
    """

    try:

        image = ee.Image(image_id)

        log.success(f"Loaded Image : {image_id}")

        return image

    except Exception as ex:

        log.error(f"Unable to load image : {image_id}")

        raise ex


# ==========================================================
# Band Names
# ==========================================================

def get_band_names(image):

    """
    Returns all available bands as an ee.List.
    """

    return image.bandNames()



# ==========================================================
# Validate Required Bands
# ==========================================================

def validate_bands(
        image,
        required_bands
):

    """
    Return missing required bands as an ee.List.

    Higher-level code can call getInfo() on the returned list if it
    needs to fail fast with a Python exception.
    """

    return ee.List(required_bands).removeAll(
        image.bandNames()
    )


# ==========================================================
# Projection
# ==========================================================

def get_projection(image):

    """
    Returns image CRS.
    """

    projection = image.projection()

    return projection


# ==========================================================
# CRS
# ==========================================================

def get_crs(image):

    projection = image.projection()

    return projection.crs()


# ==========================================================
# Scale
# ==========================================================

def get_scale(image):

    projection = image.projection()

    return projection.nominalScale()


# ==========================================================
# Image Metadata
# ==========================================================

def get_metadata(image):

    """
    Returns image properties.
    """

    return image.toDictionary()


# ==========================================================
# Image Information
# ==========================================================

def print_image_info(image):

    print()

    print("="*60)

    print("IMAGE INFORMATION")

    print("="*60)

    print("Bands")

    print(get_band_names(image).getInfo())

    print()

    print("CRS")

    print(get_crs(image).getInfo())

    print()

    print("Resolution")

    print(get_scale(image).getInfo(), "meters")

    print()


# ==========================================================
# Bounding Box
# ==========================================================

def get_bounds(region):

    """
    Returns bounding rectangle.
    """

    return region.bounds()


# ==========================================================
# Area
# ==========================================================

def get_area(region):

    """
    Returns area in square kilometers as an ee.Number.
    """

    return (

        region

        .area()

        .divide(1000000)

    )


# ==========================================================
# Centroid
# ==========================================================

def get_centroid(region):

    return region.centroid()


# ==========================================================
# Geometry Coordinates
# ==========================================================

def get_coordinates(region):

    return region.coordinates()


# ==========================================================
# Image Statistics
# ==========================================================

@timer
def image_statistics(

        image,

        region,

        scale=30

):

    """
    Computes statistics for image.

    """

    stats = image.reduceRegion(

        reducer=ee.Reducer.mean()

            .combine(

                reducer2=ee.Reducer.min(),

                sharedInputs=True

            )

            .combine(

                reducer2=ee.Reducer.max(),

                sharedInputs=True

            )

            .combine(

                reducer2=ee.Reducer.stdDev(),

                sharedInputs=True

            ),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Pixel Count
# ==========================================================

def pixel_count(

        image,

        region,

        scale=30

):

    stats = image.reduceRegion(

        reducer=ee.Reducer.count(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Region Mean
# ==========================================================

def region_mean(

        image,

        region,

        scale=30

):

    stats = image.reduceRegion(

        reducer=ee.Reducer.mean(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Region Median
# ==========================================================

def region_median(

        image,

        region,

        scale=30

):

    stats = image.reduceRegion(

        reducer=ee.Reducer.median(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Region Min-Max
# ==========================================================

def region_minmax(

        image,

        region,

        scale=30

):

    stats = image.reduceRegion(

        reducer=ee.Reducer.minMax(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Region Histogram
# ==========================================================

def region_histogram(

        image,

        region,

        scale=30

):

    stats = image.reduceRegion(

        reducer=ee.Reducer.frequencyHistogram(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    return stats


# ==========================================================
# Print Statistics
# ==========================================================

def print_statistics(stats):

    print()

    print("="*60)

    print("IMAGE STATISTICS")

    print("="*60)

    for key, value in stats.items():

        print(f"{key:<30} : {value}")

    print()
# ==========================================================
# Image Clipping
# ==========================================================

@timer
def clip_image(image, region):
    """
    Clip image to supplied geometry.
    """
    validate_geometry(region)

    return image.clip(region)


# ==========================================================
# Image Reprojection
# ==========================================================

@timer
def reproject_image(
    image,
    crs="EPSG:4326",
    scale=30
):
    """
    Reproject image.
    """

    return image.reproject(
        crs=crs,
        scale=scale
    )


# ==========================================================
# Image Resampling
# ==========================================================

@timer
def resample_image(
    image,
    method="bilinear"
):
    """
    bilinear
    bicubic
    nearest
    """

    return image.resample(method)


# ==========================================================
# Normalize Image
# ==========================================================

@timer
def normalize_image(
    image,
    region,
    scale=30
):
    """
    Min-Max Normalization
    """

    stats = image.reduceRegion(

        reducer=ee.Reducer.minMax(),

        geometry=region,

        scale=scale,

        maxPixels=1e13

    )

    bands = image.bandNames()

    def add_normalized_band(band, acc):

        band = ee.String(band)

        minimum = ee.Number(
            stats.get(band.cat("_min"))
        )

        maximum = ee.Number(
            stats.get(band.cat("_max"))
        )

        normalized_band = (
            image
            .select(band)
            .subtract(minimum)
            .divide(maximum.subtract(minimum))
            .rename(band.cat("_normalized"))
        )

        return ee.Image(acc).addBands(
            normalized_band,
            overwrite=True
        )

    return ee.Image(
        bands.iterate(
            add_normalized_band,
            image
        )
    )


# ==========================================================
# Mosaic Image Collection
# ==========================================================

@timer
def mosaic_collection(collection):

    """
    Merge image collection into one image.
    """

    return collection.mosaic()


# ==========================================================
# Median Composite
# ==========================================================

@timer
def median_composite(collection):

    return collection.median()


# ==========================================================
# Mean Composite
# ==========================================================

@timer
def mean_composite(collection):

    return collection.mean()


# ==========================================================
# Maximum Composite
# ==========================================================

@timer
def max_composite(collection):

    return collection.max()


# ==========================================================
# Minimum Composite
# ==========================================================

@timer
def min_composite(collection):

    return collection.min()


# ==========================================================
# Merge Collections
# ==========================================================

@timer
def merge_collections(
    collection1,
    collection2
):

    return collection1.merge(collection2)


# ==========================================================
# Sort Collection
# ==========================================================

def sort_collection(
    collection,
    property_name="system:time_start"
):

    return collection.sort(property_name)


# ==========================================================
# Filter Metadata
# ==========================================================

def filter_metadata(

    collection,

    property_name,

    operator,

    value

):

    return collection.filterMetadata(

        property_name,

        operator,

        value

    )


# ==========================================================
# Image Date
# ==========================================================

def get_image_date(image):

    return ee.Date(

        image.get("system:time_start")

    ).format("YYYY-MM-dd")


# ==========================================================
# Collection Dates
# ==========================================================

def collection_dates(collection):

    dates = collection.aggregate_array(
        "system:time_start"
    )

    return dates.map(
        lambda timestamp: ee.Date(timestamp).format("YYYY-MM-dd")
    )



# ==========================================================
# Collection Summary
# ==========================================================

def collection_summary(collection):

    print()

    print("=" * 60)

    print("COLLECTION SUMMARY")

    print("=" * 60)

    print(

        "Total Images :", collection.size().getInfo()

    )

    print()

    print(

        "First Date :", collection_dates(collection).get(0).getInfo()

    )

    print(

        "Last Date :", collection_dates(collection).get(-1).getInfo()

    )

    print()


# ==========================================================
# Empty Collection Check
# ==========================================================

def is_collection_empty(collection):

    return collection.size().eq(0)


# ==========================================================
# Image Exists
# ==========================================================

def image_exists(image):

    return image.bandNames().size().gt(0)


# ==========================================================
# Image Cache
# ==========================================================

_IMAGE_CACHE = {}


def cache_image(

    key,

    image

):

    _IMAGE_CACHE[key] = image


def get_cached_image(

    key

):

    return _IMAGE_CACHE.get(key)


def clear_cache():

    _IMAGE_CACHE.clear()


# ==========================================================
# Retry Wrapper
# ==========================================================

def retry(

    function,

    retries=3,

    *args,

    **kwargs

):

    for attempt in range(retries):

        try:

            return function(

                *args,

                **kwargs

            )

        except Exception as ex:

            log.warning(

                f"Retry {attempt+1}/{retries}"

            )

    raise RuntimeError(

        "Maximum retries exceeded."

    )


# ==========================================================
# Timer Utility
# ==========================================================

def benchmark(

    function,

    *args,

    **kwargs

):

    import time

    start = time.perf_counter()

    result = function(

        *args,

        **kwargs

    )

    elapsed = time.perf_counter() - start

    log.success(

        f"{function.__name__} : {elapsed:.2f} sec"

    )

    return result
# ==========================================================
# Health Check
# ==========================================================

if __name__ == "__main__":

    initialize_gee()

    log.success("data_fetch.py Ready")
