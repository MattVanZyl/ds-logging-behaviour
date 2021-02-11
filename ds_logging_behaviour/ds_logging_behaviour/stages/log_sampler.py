from surround import Stage
from ..color import Color
import logging
import pandas as pd

class LogSampler(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nGetting Sample\n---------------------------------{Color.RESET}")

        df = pd.read_csv(f"{config['path_output']}{config['output_logs']}")
        sample = df.sample(config['log_sample_size'])

        sample.to_csv(f"{config['path_output']}{config['output_logs_sample']}", index=False)

