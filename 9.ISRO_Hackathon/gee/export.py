"""
============================================================

export.py

Google Earth Engine Export Manager

Urban Heat Mitigation Project

Author : Quantara

============================================================

Features

✔ Image Export

✔ ImageCollection Export

✔ FeatureCollection Export

✔ Feature Cube Export

✔ Metadata Export

============================================================
"""

from __future__ import annotations

import ee

from gee.logger import log
from gee.logger import timer

from gee.config import (

    EXPORT_FOLDER,

    DEFAULT_CRS

)


# ============================================================
# Export Manager
# ============================================================

class ExportManager:

    """
    Handles all Earth Engine exports.
    """

    def __init__(

        self,

        folder=EXPORT_FOLDER

    ):

        self.folder = folder

        self.tasks = []

    # ========================================================

    @timer
    def export_image(

        self,

        image,

        description,

        region,

        scale=30,

        crs=DEFAULT_CRS

    ):

        task = ee.batch.Export.image.toDrive(

            image=image,

            description=description,

            folder=self.folder,

            fileNamePrefix=description,

            region=region,

            scale=scale,

            crs=crs,

            maxPixels=1e13

        )

        task.start()

        self.tasks.append(task)

        log.success(

            f"Started Image Export : {description}"

        )

        return task

    # ========================================================

    @timer
    def export_collection(

        self,

        collection,

        description,

        region,

        scale=30

    ):

        image = collection.median()

        return self.export_image(

            image,

            description,

            region,

            scale

        )

    # ========================================================

    @timer
    def export_feature_collection(

        self,

        feature_collection,

        description

    ):

        task = ee.batch.Export.table.toDrive(

            collection=feature_collection,

            description=description,

            folder=self.folder,

            fileFormat="GeoJSON"

        )

        task.start()

        self.tasks.append(task)

        log.success(

            f"Started Feature Export : {description}"

        )

        return task
# ========================================================
# Export Feature Cube
# ========================================================

    @timer
    def export_feature_cube(

        self,

        feature_cube,

        region,

        scale=30

    ):

        """
        Exports every image contained in the
        feature cube dictionary.
        """

        for name, image in feature_cube.items():

            self.export_image(

                image=image,

                description=name,

                region=region,

                scale=scale

            )

        return self


    # ========================================================
    # Export Metadata
    # ========================================================

    @timer
    def export_metadata(

        self,

        metadata,

        description="metadata"

    ):

        task = ee.batch.Export.table.toDrive(

            collection=ee.FeatureCollection([

                ee.Feature(

                    None,

                    metadata

                )

            ]),

            description=description,

            folder=self.folder,

            fileFormat="CSV"

        )

        task.start()

        self.tasks.append(task)

        log.success(

            f"Started Metadata Export : {description}"

        )

        return task


    # ========================================================
    # Task Information
    # ========================================================

    def list_tasks(self):

        """
        Returns current export task status.
        """

        return [

            {

                "Description":

                    task.status().get(

                        "description"

                    ),

                "State":

                    task.status().get(

                        "state"

                    )

            }

            for task in self.tasks

        ]


    # ========================================================
    # Wait For Completion
    # ========================================================

    def wait_for_tasks(

        self,

        interval=5

    ):

        """
        Blocks until all tasks finish.
        """

        import time

        while True:

            running = False

            for task in self.tasks:

                state = task.status()["state"]

                if state in (

                    "READY",

                    "RUNNING"

                ):

                    running = True

                    break

            if not running:

                break

            time.sleep(interval)

        log.success(

            "All export tasks completed."

        )


    # ========================================================
    # Cancel Tasks
    # ========================================================

    def cancel_all(self):

        """
        Cancels every active task.
        """

        for task in self.tasks:

            try:

                task.cancel()

            except Exception:

                pass

        log.warning(

            "All export tasks cancelled."

        )


    # ========================================================
    # Summary
    # ========================================================

    def summary(self):

        print()

        print("=" * 70)

        print("EXPORT MANAGER")

        print("=" * 70)

        print(

            "Export Folder :",

            self.folder

        )

        print()

        print(

            "Active Tasks :",

            len(self.tasks)

        )

        print()

        for task in self.list_tasks():

            print(

                f"{task['Description']:<35}",

                task["State"]

            )

        print()


    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self):

        return (

            f"ExportManager("

            f"Folder='{self.folder}', "

            f"Tasks={len(self.tasks)}"

            f")"

        )