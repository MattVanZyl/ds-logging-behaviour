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

    def calculateScopeGini(self, logs_df, repository_id, scope: ScopeType, count_scope, ):

        def get_scope_columns():
            if scope == ScopeType.FILE:
                return logs_df.loc[logs_df["repository-id"] == repository_id]
            else:
                return logs_df.loc[(logs_df["repository-id"] == repository_id) & (logs_df["log-scope"] == scope.value)]

        def get_scope_log_counts():
            if scope == ScopeType.FILE:
                return repo_logs["relative-file-path"].value_counts()
            else:
                return repo_logs.groupby(["relative-file-path", "log-scope-id"]).size()
        gini_index_scope = 0
        repo_logs = get_scope_columns()
        logs_counts = []
        if not repo_logs.empty:
            for count in get_scope_log_counts():
                logs_counts.append(count)
            # Create an array of log counts per file in the repo and initialise each to 0
            total_logs_per_file = [0] * count_scope
            # Replace elements at the start with the counts saved earlier
            if len(logs_counts) > 0:
                total_logs_per_file[0:len(logs_counts)] = logs_counts
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
                     'gini-index',
                     'scope-type'])

        total_repos = len(metrics_df)

        for index, row in metrics_df.iterrows():
            repository_id = row["repository-id"]
            repository_name = row["repository-name"]
            repository_type = row["repository-type"]
            count_module = row["module-count"]
            count_function = row["function-count"]
            count_class = row["class-count"]
            count_method = row["method-count"]

            logging.info(
                f" {Color.GREEN}{index}{Color.RESET}/{Color.GREEN}{total_repos}{Color.RESET} - ID: {Color.BLUE}{repository_id}{Color.RESET} Name: {Color.BLUE}{repository_name}{Color.RESET}")

            gini_index_file = self.calculateScopeGini(logs_df, repository_id, ScopeType.FILE, count_module)
            gini_index_module = self.calculateScopeGini(logs_df, repository_id, ScopeType.MODULE, count_module)
            gini_index_function = self.calculateScopeGini(logs_df, repository_id, ScopeType.FUNCTION, count_function)
            gini_index_class = self.calculateScopeGini(logs_df, repository_id, ScopeType.CLASS, count_class)
            gini_index_method = self.calculateScopeGini(logs_df, repository_id, ScopeType.METHOD, count_method)

            # Save Gini Indexes
            # gini_df = gini_df.append(
            #     {'repository-id': repository_id,
            #      'repository-name': repository_name,
            #      'repository-type': repository_type,
            #      'gini-index-file': gini_index_file,
            #      'gini-index-module': gini_index_module,
            #      'gini-index-function': gini_index_function,
            #      'gini-index-class': gini_index_class,
            #      'gini-index-method': gini_index_method},
            #     ignore_index=True)

            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index': gini_index_file,
                 'scope-type': ScopeType.FILE.value},
                ignore_index=True)
            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index': gini_index_module,
                 'scope-type': ScopeType.MODULE.value},
                ignore_index=True)
            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index': gini_index_function,
                 'scope-type': ScopeType.FUNCTION.value},
                ignore_index=True)
            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index': gini_index_class,
                 'scope-type': ScopeType.CLASS.value},
                ignore_index=True)
            gini_df = gini_df.append(
                {'repository-id': repository_id,
                 'repository-name': repository_name,
                 'repository-type': repository_type,
                 'gini-index': gini_index_method,
                 'scope-type': ScopeType.METHOD.value},
                ignore_index=True)

        gini_df.to_csv(f"{config['path_output']}{config['output_gini_indexes']}", index=False)


