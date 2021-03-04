from surround import Stage
from ..color import Color
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


class Visualization(Stage):
    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nVisualization\n---------------------------------{Color.RESET}")

        df = pd.read_csv(f"{config['path_output']}{config['output_gini_indexes']}")

        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        fig.suptitle('Logs Per File')

        sns.histplot(data=df, x="gini-index-file", hue="repository-type", multiple="dodge", ax=axes[0])
        axes[0].set(xticks=np.arange(0, 1, 0.1))

        sns.kdeplot(data=df, x="gini-index-file", hue="repository-type", fill=True, cut=0, ax=axes[1])
        axes[1].set(xticks=np.arange(0, 1, 0.1))

        fig.savefig(f"{config['path_output']}plot_gini_repos.png")

        fig, axes = plt.subplots(2, 4, figsize=(30, 10))
        fig.suptitle('Logs Per Scope')

        for ax in axes.flat:
            ax.set(xticks=np.arange(0, 1, 0.1))

        sns.histplot(data=df, x="gini-index-module", hue="repository-type", multiple="dodge", ax=axes[0, 0])
        sns.kdeplot(data=df, x="gini-index-module", hue="repository-type", fill=True, ax=axes[1, 0], cut=0)
        axes[0, 0].set_title("Module (outside of classes, functions and methods)")
        axes[0, 0].set(title="Module (outside of classes, functions and methods)",
                       xticks=np.arange(0, 1, 0.1),
                       ylim=(0, 500))

        sns.histplot(data=df, x="gini-index-function", hue="repository-type", multiple="dodge", ax=axes[0, 1])
        sns.kdeplot(data=df, x="gini-index-function", hue="repository-type", fill=True, ax=axes[1, 1], cut=0)
        axes[0, 1].set(title="Function",
                       xticks=np.arange(0, 1, 0.1),
                       ylim=(0, 500))

        sns.histplot(data=df, x="gini-index-class", hue="repository-type", multiple="dodge", ax=axes[0, 2])
        sns.kdeplot(data=df, x="gini-index-class", hue="repository-type", fill=True, ax=axes[1, 2], cut=0)
        axes[0, 2].set(title="Class (outside of methods)",
                       xticks=np.arange(0, 1, 0.1),
                       ylim=(0, 500))

        sns.histplot(data=df, x="gini-index-method", hue="repository-type", multiple="dodge", ax=axes[0, 3])
        sns.kdeplot(data=df, x="gini-index-method", hue="repository-type", fill=True, ax=axes[1, 3], cut=0)
        axes[0, 3].set(title="Method",
                       xticks=np.arange(0, 1, 0.1),
                       ylim=(0, 500))

        fig.savefig(f"{config['path_output']}plot_gini_scopes.png")
