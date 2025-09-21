# This module provides logging functionality for the application.
# errors are logged to logs/errors.log file with timestamps.
# running infos are logged to a logs/info.log file with timestamps.

# create a logs directory if it doesn't exist 
# Don't want any errors logged to console, only to files/errors.log neither info to console, only to files/info.log

import sys 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


def _setup_loggers():
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    if not os.path.exists(f"{BASE_DIR}/logs"):
        os.makedirs(f"{BASE_DIR}/logs")

    info_logger = logging.getLogger("info_logger")
    info_logger.setLevel(logging.INFO)
    info_logger.propagate = False
    info_handler = RotatingFileHandler(f"{BASE_DIR}/logs/info.log", maxBytes=5*1024*1024, backupCount=3)
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(info_formatter)
    info_logger.addHandler(info_handler)

    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    error_handler = RotatingFileHandler(f"{BASE_DIR}/logs/errors.log", maxBytes=5*1024*1024, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)

    return error_logger, info_logger

error_logger, info_logger = _setup_loggers()

def log_error(message):
    error_logger.error(message)
    info_logger.error("An error occurred. Check logs/errors.log for details.")

def log_info(message):
    info_logger.info(message)

def log_warning(message):
    info_logger.warning(message)
