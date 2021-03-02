from surround import Stage
from ..color import Color
import logging
import pandas as pd
from enum import Enum


class ScopeType(Enum):
    FILE = "file"
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"

class GiniCalculator(Stage):
    def gini(self, list_of_values):
        sorted_list = sorted(list_of_values)
        height, area = 0, 0
        for value in sorted_list:
            height += value
            area += height - value / 2.
        fair_area = height * len(list_of_values) / 2.
        return (fair_area - area) / fair_area

    # def calculateRepoGini(self, logs_df, repository_id, count_module):
    #     gini_index_repo = 0
    #
    #     repo_logs = logs_df.loc[logs_df["repository-id"] == repository_id]
    #     # Count the number of logs in each file and put the counts in an array
    #     logs_counts = []
    #
    #     did_find_logs_for_repo = not repo_logs.empty
    #
    #     if did_find_logs_for_repo:
    #
    #         for count in repo_logs["relative-file-path"].value_counts():
    #             logs_counts.append(count)
    #
    #         # Create an array of log counts per file in the repo and initialise each to 0
    #         total_logs_per_file = [0] * count_module
    #
    #         # logging.info(f"Logs per file BEFORE: {total_logs_per_file}")
    #         # logging.info(f"logs_counts: {logs_counts}")
    #
    #         # Replace elements at the start with the counts saved earlier
    #         if len(logs_counts) > 0:
    #             total_logs_per_file[0:len(logs_counts)] = logs_counts
    #
    #             # logging.info(f"Logs per file AFTER: {total_logs_per_file}")
    #
    #             gini_index_repo = self.gini(total_logs_per_file)
    #
    #     return gini_index_repo

    def calculateScopeGini(self, logs_df, repository_id, scope: ScopeType, count_scope, ):

        def get_scope_columns():
            logging.info(f"{scope} == {ScopeType.FILE} : {scope == ScopeType.FILE}")
            if scope == ScopeType.FILE:
                return logs_df.loc[logs_df["repository-id"] == repository_id]
            else:
                return logs_df.loc[(logs_df["repository-id"] == repository_id) & (logs_df["log-scope"] == scope.value)]

        def get_scope_log_counts():
            if scope == ScopeType.FILE:
                return repo_logs["relative-file-path"].value_counts()
            else:
                return repo_logs.groupby(["relative-file-path", "log-scope-id"]).size()

        logging.info(f" - {scope.name} - ")
        logging.info(f"{scope.name} Count: {count_scope}")


        gini_index_scope = 0

        # repo_logs = logs_df.loc[(logs_df["repository-id"] == repository_id) & (logs_df["log-scope"] == scope)]
        repo_logs = get_scope_columns()

        logs_counts = []

        if not repo_logs.empty:
            for count in get_scope_log_counts(): #repo_logs.groupby(["relative-file-path", "log-scope-id"]).size():
                logs_counts.append(count)

            # Create an array of log counts per file in the repo and initialise each to 0
            total_logs_per_file = [0] * count_scope

            logging.info(f"Logs per file BEFORE: {total_logs_per_file}")
            logging.info(f"logs_counts: {logs_counts}")

            # Replace elements at the start with the counts saved earlier
            if len(logs_counts) > 0:
                total_logs_per_file[0:len(logs_counts)] = logs_counts

                logging.info(f"Logs per file AFTER: {total_logs_per_file}")

                gini_index_scope = self.gini(total_logs_per_file)

        return gini_index_scope

    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nCalculating Gini Indexes\n---------------------------------{Color.RESET}")

        logs_df = pd.read_csv(f"{config['path_output']}{config['output_logs']}")
        metrics_df = pd.read_csv(f"{config['path_output']}{config['output_metrics']}")

        gini_df = pd.DataFrame(
            columns=['repository-id',
                     'repository-name',
                     'repository-type',
                     'gini-index-file',
                     'gini-index-module',
                     'gini-index-function',
                     'gini-index-class',
                     'gini-index-method'])

        for index, row in metrics_df.iterrows():
            repository_id = row["repository-id"]
            repository_name = row["repository-name"]
            repository_type = row["repository-type"]
            count_module = row["module-count"]
            count_function = row["function-count"]
            count_class = row["class-count"]
            count_method = row["method-count"]


            # Get all the logs of the current repo
            # repo_logs = logs_df.loc[logs_df['repository-id'] == repository_id]

            logging.info(f"\n\nREPO: {repository_id} - {repository_name}")

            gini_index_file = self.calculateScopeGini(logs_df, repository_id, ScopeType.FILE, count_module)
            logging.info(f"gini_index_file: {gini_index_file}")
            gini_index_module = self.calculateScopeGini(logs_df, repository_id, ScopeType.MODULE, count_module)
            logging.info(f"gini_index_module: {gini_index_module}")
            gini_index_function = self.calculateScopeGini(logs_df, repository_id, ScopeType.FUNCTION, count_function)
            logging.info(f"gini_index_function: {gini_index_function}")
            gini_index_class = self.calculateScopeGini(logs_df, repository_id, ScopeType.CLASS, count_class)
            logging.info(f"gini_index_class: {gini_index_class}")
            gini_index_method = self.calculateScopeGini(logs_df, repository_id, ScopeType.METHOD, count_method)
            logging.info(f"gini_index_method: {gini_index_method}")

            # # Gini Repo - Logs per file
            # # ---------------------
            #
            # # Count the number of logs in each file and put the counts in an array
            # logs_counts = []
            # for count in repo_logs["relative-file-path"].value_counts():
            #     logs_counts.append(count)
            #
            # # Create an array of log counts per file in the repo and initialise each to 0
            # total_logs_per_file = [0] * count_module
            #
            # gini_index_file = 0
            #
            # logging.info(f"Logs per file BEFORE: {total_logs_per_file}")
            # logging.info(f"logs_counts: {logs_counts}")
            #
            # # Replace elements at the start with the counts saved earlier
            # if len(logs_counts) > 0:
            #     total_logs_per_file[0:len(logs_counts)] = logs_counts
            #
            #     logging.info(f"Logs per file AFTER: {total_logs_per_file}")
            #
            #     gini_index_file = self.gini(total_logs_per_file)
            #
            #     logging.info(f"Gini index: {gini_index_file}")

            # Save Gini Indexes
            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index-file': gini_index_file,
                 'gini-index-module': gini_index_module,
                 'gini-index-function': gini_index_function,
                 'gini-index-class': gini_index_class,
                 'gini-index-method': gini_index_method},
                ignore_index=True)

            gini_df.to_csv(f"{config['path_output']}{config['output_gini_indexes']}", index=False)


