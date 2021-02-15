from surround import Stage
from ..color import Color
import logging
import pandas as pd

class GiniCalculator(Stage):
    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nCalculating Gini Indexes\n---------------------------------{Color.RESET}")

        logs_df = pd.read_csv(f"{config['path_output']}{config['output_logs']}")
        metrics_df = pd.read_csv(f"{config['path_output']}{config['output_metrics']}")

        gini_df = pd.DataFrame(
            columns=['repository-id', 'repository-name','repository-type', 'gini-index-repo'])

        for index, row in metrics_df.iterrows():
            repository_id = row["repository-id"]
            repository_name = row["repository-name"]
            repository_type = row["repository-type"]
            count_module = row["module-count"]

            #Get all the logs of the current repo
            repo_logs = logs_df.loc[logs_df['repository-id'] == repository_id]

            logging.info(f"REPO: {repository_id} - {repository_name}")

            # Gini Repo - Logs per file
            # ---------------------

            # Count the number of logs in each file and put the counts in an array
            logs_counts = []
            for count in repo_logs["relative-file-path"].value_counts():
                logs_counts.append(count)

            # Create an array of log counts per file in the repo and initialise each to 0
            logs_per_file = [0] * count_module

            gini_index_file = 0

            # Replace elements at the start with the counts saved earlier
            if len(logs_counts) > 0:
                logs_per_file[0:len(logs_counts)-1] = logs_counts

                logging.info(f"Logs per file: {logs_per_file}")

                gini_index_file = self.gini(logs_per_file)

                logging.info(f"Gini index: {gini_index_file}")

            # Save Gini Indexes
            gini_df = gini_df.append(
                {'repository-id': repository_id, 'repository-name': repository_name, 'repository-type':repository_type, 'gini-index-repo': gini_index_file},
                ignore_index=True)

            gini_df.to_csv(f"{config['path_output']}{config['output_gini_indexes']}", index=False)

    def gini(self, list_of_values):
        sorted_list = sorted(list_of_values)
        height, area = 0, 0
        for value in sorted_list:
            height += value
            area += height - value / 2.
        fair_area = height * len(list_of_values) / 2.
        return (fair_area - area) / fair_area
