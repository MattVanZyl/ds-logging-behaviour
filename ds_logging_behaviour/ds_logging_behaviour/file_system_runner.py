"""
This module is responsible for loading the data and running the pipeline.
"""

import logging
from surround import Runner, RunMode
from .stages import AssemblerState
import pandas as pd

logging.basicConfig(level=logging.INFO)

class FileSystemRunner(Runner):

    def load_data(self, mode, config):
        df = pd.read_csv(config["input_file"])
        state = AssemblerState(df)
        return state
