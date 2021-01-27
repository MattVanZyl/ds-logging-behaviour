from surround import Stage
from ..print_colours import PrintColours
import logging
import pandas as pd



class DataSampler(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}---------------------------------\nGetting Sample\n---------------------------------{PrintColours.RESET}")

        df = pd.read_csv(f"{config['output_path']}log-levels.csv")
        sample = df.sample(100)

        sample.to_csv(f"{config['output_path']}log-sample.csv", index=False)

