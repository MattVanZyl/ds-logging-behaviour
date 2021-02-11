"""
This file is needed to make Python treat this directory as a package
"""

import logging
import os

from logging.handlers import RotatingFileHandler

from surround import has_config

@has_config
def setup(config):

    os.makedirs(config["path_output"], exist_ok=True)

    # Initialise logging
    level = logging.INFO
    log_file = os.path.join(config["path_output"], "output.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=5)
    handlers = [file_handler, logging.StreamHandler()]
    logging.basicConfig(level=level, handlers=handlers)

setup(config=None)
