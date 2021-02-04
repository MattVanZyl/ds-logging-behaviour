from surround import Stage
from ..color import Color
import logging
import pandas as pd

class GiniCalculator(Stage):
    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nCalculating Gini Indexes\n---------------------------------{Color.RESET}")

        logs_per_file = self.get_file_logs(config)



        # repo_metrics_df.to_csv(f"{config['path_output']}repo-metrics.csv", index=False)

    def get_file_logs(self, config):
        logs_df = pd.read_csv(f"{config['path_output']}{config['output_logs']}")
        metrics_df = pd.read_csv(f"{config['path_output']}{config['output_metrics']}")

        for index, row in metrics_df.iterrows():
            repository_id = row["repository-id"]

            #Get all logs of repo
            repo_logs = logs_df.loc[logs_df['repository-id'] == repository_id]
            file_count = row["python-file-count"]

            logging.info(f"REPO: {repository_id}")
            counts = []
            for count in repo_logs["file-name"].value_counts():
                counts.append(count)

            # Create an array of log counts per file and initialise each to 0
            logs_per_file = [0] * file_count

            logs_per_file[0:len(counts)-1] = counts

            logging.info(f"Logs per file: {logs_per_file}")
            gini_index = self.gini(logs_per_file)

            logging.info(f"Gini index: {gini_index}")



    def gini(self, list_of_values):
        sorted_list = sorted(list_of_values)
        height, area = 0, 0
        for value in sorted_list:
            height += value
            area += height - value / 2.
        fair_area = height * len(list_of_values) / 2.
        return (fair_area - area) / fair_area
