from surround import Stage
from ..color import Color
import logging
import pandas as pd

class DataSampler(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nGetting Sample\n---------------------------------{Color.RESET}")

        df = pd.read_csv(f"{config['output_path']}log-levels.csv")
        sample = df.sample(config['log_sample_size'])

        sample.to_csv(f"{config['output_path']}log-sample.csv", index=False)

