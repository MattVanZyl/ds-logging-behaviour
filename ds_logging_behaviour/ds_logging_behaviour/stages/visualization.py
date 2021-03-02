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
        #FILE
        plot_density = sns.displot(data=df, x="gini-index-file", hue="repository-type", kind="kde", fill=True, cut=0)
        plot_density.savefig(f"{config['path_output']}plot_density_file.png")

        plot_histo = sns.displot(data=df, x="gini-index-file", hue="repository-type", multiple="dodge").set_title('Logs per file')
        plot_histo.savefig(f"{config['path_output']}plot_histogram_file.png")

        plot_histo = sns.displot(data=df, x="gini-index-module", hue="repository-type", multiple="dodge").set_title('Logs per module (outside of classes, functions and methods)')
        plot_histo.savefig(f"{config['path_output']}plot_histogram_module.png")

        plot_histo = sns.displot(data=df, x="gini-index-function", hue="repository-type", multiple="dodge").set_title('Logs per function')
        plot_histo.savefig(f"{config['path_output']}plot_histogram_function.png")

        plot_histo = sns.displot(data=df, x="gini-index-class", hue="repository-type", multiple="dodge").set_title('Logs per class (outside of methods)')
        plot_histo.savefig(f"{config['path_output']}plot_histogram_class.png")

        plot_histo = sns.displot(data=df, x="gini-index-method", hue="repository-type", multiple="dodge").set_title('Logs per method')
        plot_histo.savefig(f"{config['path_output']}plot_histogram_method.png")

