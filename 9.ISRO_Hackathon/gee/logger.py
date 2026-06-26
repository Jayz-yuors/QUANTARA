"""
===========================================================
logger.py

Centralized Logger
Urban Heat Mitigation Project

Author : Quantara

===========================================================
"""

from __future__ import annotations

import logging
import os
import sys
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "urban_heat.log")

MAX_LOG_SIZE = 5 * 1024 * 1024      # 5 MB
BACKUP_COUNT = 5

os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------
# ANSI COLORS
# ---------------------------------------------------------

RESET = "\033[0m"

COLORS = {
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[94m",       # Blue
    "SUCCESS": "\033[92m",    # Green
    "WARNING": "\033[93m",    # Yellow
    "ERROR": "\033[91m",      # Red
    "CRITICAL": "\033[95m",   # Purple
}

# ---------------------------------------------------------
# CUSTOM SUCCESS LEVEL
# ---------------------------------------------------------

SUCCESS_LEVEL = 25

logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


logging.Logger.success = success

# ---------------------------------------------------------
# COLOR FORMATTER
# ---------------------------------------------------------


class ColoredFormatter(logging.Formatter):

    def format(self, record):

        levelname = record.levelname

        color = COLORS.get(levelname, "")

        record.levelname = f"{color}{levelname:<8}{RESET}"

        return super().format(record)


# ---------------------------------------------------------
# LOGGER CLASS
# ---------------------------------------------------------


class ProjectLogger:

    def __init__(self):

        self.logger = logging.getLogger("UrbanHeat")

        self.logger.setLevel(logging.DEBUG)

        if self.logger.handlers:
            return

        console_handler = logging.StreamHandler(sys.stdout)

        console_handler.setLevel(logging.INFO)

        console_formatter = ColoredFormatter(
            "[%(levelname)s] %(message)s"
        )

        console_handler.setFormatter(console_formatter)

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )

        file_handler.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(

            "%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s"

        )

        file_handler.setFormatter(file_formatter)

        self.logger.addHandler(console_handler)

        self.logger.addHandler(file_handler)

    # -----------------------------------------------------

    def debug(self, msg):

        self.logger.debug(msg)

    def info(self, msg):

        self.logger.info(msg)

    def success(self, msg):

        self.logger.success(msg)

    def warning(self, msg):

        self.logger.warning(msg)

    def error(self, msg):

        self.logger.error(msg)

    def critical(self, msg):

        self.logger.critical(msg)

# ---------------------------------------------------------
# GLOBAL LOGGER
# ---------------------------------------------------------

log = ProjectLogger()

# ---------------------------------------------------------
# TIMER DECORATOR
# ---------------------------------------------------------


def timer(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        log.info(f"Running {func.__name__}()")

        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start

        log.success(
            f"{func.__name__} completed in {elapsed:.2f} sec"
        )

        return result

    return wrapper

# ---------------------------------------------------------
# SECTION HEADER
# ---------------------------------------------------------


def section(title: str):

    line = "=" * 60

    log.info(line)

    log.info(title.upper())

    log.info(line)

# ---------------------------------------------------------
# SUBSECTION
# ---------------------------------------------------------


def subsection(title: str):

    log.info("-" * 40)

    log.info(title)

    log.info("-" * 40)

# ---------------------------------------------------------
# PROGRESS BAR
# ---------------------------------------------------------


def progress(current, total, prefix="Progress"):

    percent = current / total

    width = 30

    filled = int(width * percent)

    bar = "█" * filled + "-" * (width - filled)

    print(

        f"\r{prefix}: |{bar}| {percent*100:6.2f}%",

        end="",

        flush=True,

    )

    if current == total:
        print()

# ---------------------------------------------------------
# PIPELINE STATUS
# ---------------------------------------------------------


def pipeline_status(title, status):

    if status:

        log.success(f"{title:<35} PASS")

    else:

        log.error(f"{title:<35} FAIL")

# ---------------------------------------------------------
# EXCEPTION LOGGER
# ---------------------------------------------------------


def log_exception(ex):

    log.error(str(ex))

# ---------------------------------------------------------
# MODULE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    section("LOGGER TEST")

    log.info("Logger initialized.")

    log.success("Authentication Successful")

    log.warning("Cloud percentage is high.")

    log.error("Dataset not found.")

    log.critical("Pipeline aborted.")

    @timer
    def demo():

        time.sleep(2)

    demo()

    for i in range(101):

        progress(i, 100)

        time.sleep(0.01)

    pipeline_status("Google Earth Engine", True)

    pipeline_status("Landsat Collection", True)

    pipeline_status("Sentinel Collection", False)

    section("END")