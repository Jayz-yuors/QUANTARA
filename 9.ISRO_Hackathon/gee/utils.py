"""
===========================================================
utils.py

Common Utility Functions

Urban Heat Mitigation Project
Quantara

===========================================================
"""

from __future__ import annotations

import os
import json
import math
import tempfile
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import ee

from gee.logger import log


# ==========================================================
# DIRECTORY UTILITIES
# ==========================================================

def ensure_directory(path: str) -> Path:
    """
    Creates directory if it doesn't exist.
    """

    directory = Path(path)

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


def project_root() -> Path:
    """
    Returns project root.
    """

    return Path.cwd()


def temp_directory() -> Path:

    return Path(tempfile.gettempdir())


# ==========================================================
# DATE UTILITIES
# ==========================================================

def today():

    return datetime.date.today()


def current_timestamp():

    return datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


def previous_month(date):

    first = date.replace(day=1)

    return first - datetime.timedelta(days=1)


def month_range(year, month):

    start = datetime.date(year, month, 1)

    if month == 12:

        end = datetime.date(year + 1, 1, 1)

    else:

        end = datetime.date(year, month + 1, 1)

    return start.isoformat(), end.isoformat()


# ==========================================================
# JSON UTILITIES
# ==========================================================

def save_json(data, filepath):

    with open(filepath, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

    log.success(f"Saved JSON -> {filepath}")


def load_json(filepath):

    with open(filepath) as f:

        return json.load(f)


# ==========================================================
# BAND UTILITIES
# ==========================================================

def list_bands(image):

    return image.bandNames().getInfo()


def band_exists(image, band):

    return band in list_bands(image)


def print_bands(image):

    bands = list_bands(image)

    print()

    print("="*50)

    print("Bands")

    print("="*50)

    for b in bands:

        print(b)


# ==========================================================
# IMAGE UTILITIES
# ==========================================================

def rename_bands(image, mapping):

    """
    mapping

    {

    "SR_B4":"RED",

    "SR_B5":"NIR"

    }

    """

    old = list(mapping.keys())

    new = list(mapping.values())

    return image.select(old).rename(new)


def select_bands(image, bands):

    return image.select(bands)


# ==========================================================
# GEOMETRY UTILITIES
# ==========================================================

def rectangle(

    xmin,

    ymin,

    xmax,

    ymax

):

    return ee.Geometry.Rectangle(

        [

            xmin,

            ymin,

            xmax,

            ymax

        ]

    )


def point(

    lon,

    lat

):

    return ee.Geometry.Point(

        [

            lon,

            lat

        ]

    )


def polygon(coordinates):

    return ee.Geometry.Polygon(

        coordinates

    )


# ==========================================================
# AREA UTILITIES
# ==========================================================

def area_sqkm(region):

    return (

        region.area()

        .divide(1000000)

        .getInfo()

    )


def perimeter(region):

    return (

        region.perimeter()

        .getInfo()

    )


# ==========================================================
# CRS UTILITIES
# ==========================================================

def projection(image):

    return image.projection()


def crs(image):

    return projection(image).crs().getInfo()


def nominal_scale(image):

    return projection(image).nominalScale().getInfo()


# ==========================================================
# IMAGE COLLECTION UTILITIES
# ==========================================================

def first(collection):

    return ee.Image(

        collection.first()

    )


def last(collection):

    size = collection.size()

    return ee.Image(

        collection.toList(size).get(

            size.subtract(1)

        )

    )


def collection_size(collection):

    return collection.size().getInfo()


# ==========================================================
# PRINT HELPERS
# ==========================================================

def divider():

    print("=" * 70)


def title(text):

    divider()

    print(text)

    divider()


def subtitle(text):

    print("-" * 40)

    print(text)

    print("-" * 40)


# ==========================================================
# NUMERIC HELPERS
# ==========================================================

def normalize(

    value,

    minimum,

    maximum

):

    return (

        value - minimum

    ) / (

        maximum - minimum

    )


def percentage(

    value,

    total

):

    return (

        value / total

    ) * 100


def round2(value):

    return round(

        value,

        2

    )


# ==========================================================
# FILE HELPERS
# ==========================================================

def file_exists(path):

    return os.path.exists(path)


def filename(path):

    return Path(path).stem


def extension(path):

    return Path(path).suffix


# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

def system_info():

    import platform

    return {

        "OS": platform.system(),

        "Release": platform.release(),

        "Python": platform.python_version()

    }


# ==========================================================
# TEST
# ==========================================================
# ==========================================================
# EARTH ENGINE TYPE UTILITIES
# ==========================================================

def is_image(obj):
    """
    Returns True if object is an Earth Engine Image.
    """

    return isinstance(
        obj,
        ee.image.Image
    )


def is_collection(obj):
    """
    Returns True if object is an Earth Engine ImageCollection.
    """

    return isinstance(
        obj,
        ee.imagecollection.ImageCollection
    )


def is_feature(obj):
    """
    Returns True if object is an Earth Engine Feature.
    """

    return isinstance(
        obj,
        ee.feature.Feature
    )


def is_feature_collection(obj):
    """
    Returns True if object is an Earth Engine FeatureCollection.
    """

    return isinstance(
        obj,
        ee.featurecollection.FeatureCollection
    )


def is_geometry(obj):
    """
    Returns True if object is an Earth Engine Geometry.
    """

    return isinstance(
        obj,
        ee.geometry.Geometry
    )


# ==========================================================
# EARTH ENGINE INFORMATION UTILITIES
# ==========================================================

def image_info(image):
    """
    Returns useful information about an image.
    """

    return {

        "Bands":
            image.bandNames().getInfo(),

        "Projection":
            image.projection().getInfo(),

        "CRS":
            image.projection().crs().getInfo(),

        "Scale":
            image.projection()
                 .nominalScale()
                 .getInfo()

    }


def collection_info(collection):
    """
    Returns useful information about an ImageCollection.
    """

    return {

        "Images":
            collection.size().getInfo(),

        "Bands":
            ee.Image(
                collection.first()
            ).bandNames().getInfo()

    }


def projection_info(image):
    """
    Returns projection metadata.
    """

    projection = image.projection()

    return {

        "CRS":
            projection.crs().getInfo(),

        "Scale":
            projection.nominalScale().getInfo()

    }


# ==========================================================
# EARTH ENGINE CONVERSION UTILITIES
# ==========================================================

def ee_dict(dictionary):
    """
    Converts ee.Dictionary to Python dict.
    """

    return dictionary.getInfo()


def ee_list(lst):
    """
    Converts ee.List to Python list.
    """

    return lst.getInfo()


def ee_number(number):
    """
    Converts ee.Number to Python number.
    """

    return number.getInfo()


def safe_getinfo(obj):
    """
    Safe wrapper around getInfo().
    """

    try:

        return obj.getInfo()

    except Exception as e:

        log.warning(

            f"getInfo() failed : {e}"

        )

        return None
# ==========================================================
# EARTH ENGINE IMAGE UTILITIES
# ==========================================================

def clip(image, region):
    """
    Clips an image to the specified region.
    """

    return image.clip(region)


def resample(image, method="bilinear"):
    """
    Resamples an image.
    """

    return image.resample(method)


def stack(images):
    """
    Stacks multiple images into a single multiband image.
    """

    if not images:

        raise ValueError(

            "Image list cannot be empty."

        )

    output = images[0]

    for image in images[1:]:

        output = output.addBands(image)

    return output


# ==========================================================
# GEOMETRY HELPERS
# ==========================================================

def bounds(region):
    """
    Returns bounding box of region.
    """

    return region.bounds()


def centroid(region):
    """
    Returns centroid of region.
    """

    return region.centroid()


# ==========================================================
# FILE HELPERS
# ==========================================================

def timestamp_filename(name, extension=""):

    """
    Generates timestamped filename.

    Example:

    landsat_20260628_103245.tif
    """

    filename = (

        f"{name}_"

        f"{current_timestamp()}"

    )

    if extension:

        extension = extension.lstrip(".")

        filename += f".{extension}"

    return filename


# ==========================================================
# PRINT UTILITIES
# ==========================================================

def print_dict(dictionary):

    """
    Pretty prints dictionary.
    """

    divider()

    for key, value in dictionary.items():

        print(

            f"{key:<30}",

            value

        )

    divider()


# ==========================================================
# NUMERIC UTILITIES
# ==========================================================

def clamp(

    value,

    minimum,

    maximum

):

    """
    Restricts value between minimum and maximum.
    """

    return max(

        minimum,

        min(

            value,

            maximum

        )

    )


def safe_divide(

    numerator,

    denominator,

    default=0

):

    """
    Division with zero protection.
    """

    if denominator == 0:

        return default

    return numerator / denominator


# ==========================================================
# LOGGING HELPERS
# ==========================================================

def success(message):

    log.success(message)


def warning(message):

    log.warning(message)


def error(message):

    log.error(message)


def info(message):

    log.info(message)
if __name__ == "__main__":

    title("Utils Module")

    print(system_info())