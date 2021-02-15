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
        plot_density = sns.displot(data=df, x="gini-index-repo", hue="repository-type", kind="kde", fill=True, cut=0)
        plot_density.savefig(f"{config['path_output']}plot_density.png")

        plot_histo = sns.displot(data=df, x="gini-index-repo", hue="repository-type", multiple="dodge")
        plot_histo.savefig(f"{config['path_output']}plot_histogram.png")