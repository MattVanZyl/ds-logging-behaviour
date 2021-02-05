import seaborn as sns
from surround import Stage
from ..color import Color
import logging
import pandas as pd

class Visualization(Stage):
    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nVisualization\n---------------------------------{Color.RESET}")

        df = pd.read_csv(f"{config['path_output']}{config['output_gini_indexes']}")
        sns_plot = sns.relplot(data=df, x="repository-id", y="gini-index-file", hue="repository-type")

        sns_plot.savefig(f"{config['path_output']}output.png")