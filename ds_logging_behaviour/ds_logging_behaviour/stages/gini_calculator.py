from surround import Stage
from ..color import Color
import logging
import pandas as pd

from ..enums import ScopeType, LogLevelType


class GiniCalculator(Stage):
    def gini(self, list_of_values):
        sorted_list = sorted(list_of_values)
        height, area = 0, 0
        for value in sorted_list:
            height += value
            area += height - value / 2.
        fair_area = height * len(list_of_values) / 2.
        return (fair_area - area) / fair_area

    # ==================================================================================================================
    def get_total_log_count_at_scope(self, logs_df, repository_id, scope: ScopeType):
        if scope == ScopeType.FILE:
            return len(logs_df.loc[logs_df["repository-id"] == repository_id])
        else:
            return len(logs_df.loc[
                           (logs_df["repository-id"] == repository_id) &
                           (logs_df["log-scope"] == scope.value)
                       ])

    # ==================================================================================================================
    def get_total_log_levels_at_scope(self, logs_df, repository_id, scope: ScopeType, log_level: LogLevelType):
        if scope == ScopeType.FILE:
            return len(logs_df.loc[
                           (logs_df["repository-id"] == repository_id) &
                           (logs_df["log-level"] == log_level.value)
                       ])
        else:
            return len(logs_df.loc[(logs_df["repository-id"] == repository_id) &
                                   (logs_df["log-scope"] == scope.value) &
                                   (logs_df["log-level"] == log_level.value)
                       ])

    # ==================================================================================================================
    def calculate_scope_gini(self, logs_df, repository_id, scope: ScopeType, count_scope, ):

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

    # ==================================================================================================================
    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nCalculating Gini Indexes\n---------------------------------{Color.RESET}")

        logs_df = pd.read_csv(f"{config['path_output']}{config['output_logs']}")
        metrics_df = pd.read_csv(f"{config['path_output']}{config['output_metrics']}")

        gini_df = pd.DataFrame(columns=[
            'repository-id',
            'repository-name',
            'repository-type',
            'repository-lines-of-code',
            'gini-index',
            'scope-type',
            'scope-count',
            'scope-log-count',
            'scope-log-level-critical',
            'scope-log-level-error',
            'scope-log-level-warning',
            'scope-log-level-info',
            'scope-log-level-debug',
            'scope-log-level-print',
        ])

        total_repos = len(metrics_df)

        for index, row in metrics_df.iterrows():
            repository_id = row["repository-id"]
            repository_name = row["repository-name"]
            repository_type = row["repository-type"]
            repository_lines_of_code = row["repository-lines-of-code"]
            # Number of modules corresponds to number of python files.
            count_file = row["module-count"]
            count_module = row["module-count"]
            count_function = row["function-count"]
            count_class = row["class-count"]
            count_method = row["method-count"]

            logging.info(
                f" {Color.GREEN}{index + 1}{Color.RESET}/{Color.GREEN}{total_repos}{Color.RESET} - ID: {Color.BLUE}{repository_id}{Color.RESET} Name: {Color.BLUE}{repository_name}{Color.RESET}")

            gini_index_file = self.calculate_scope_gini(logs_df, repository_id, ScopeType.FILE, count_module)
            gini_index_module = self.calculate_scope_gini(logs_df, repository_id, ScopeType.MODULE, count_module)
            gini_index_function = self.calculate_scope_gini(logs_df, repository_id, ScopeType.FUNCTION, count_function)
            gini_index_class = self.calculate_scope_gini(logs_df, repository_id, ScopeType.CLASS, count_class)
            gini_index_method = self.calculate_scope_gini(logs_df, repository_id, ScopeType.METHOD, count_method)

            gini_df = gini_df.append({
                'repository-id': repository_id,
                'repository-name': repository_name,
                'repository-type': repository_type,
                'repository-lines-of-code': repository_lines_of_code,
                'gini-index': gini_index_file,
                'scope-type': ScopeType.FILE.value,
                'scope-count': count_file,
                'scope-log-count': self.get_total_log_count_at_scope(logs_df, repository_id, ScopeType.FILE,),

                'scope-log-level-critical': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                               LogLevelType.CRITICAL),
                'scope-log-level-error': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                            LogLevelType.ERROR),
                'scope-log-level-warning': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                              LogLevelType.WARNING),
                'scope-log-level-info': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                           LogLevelType.INFO),
                'scope-log-level-debug': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                            LogLevelType.DEBUG),
                'scope-log-level-print': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FILE,
                                                                            LogLevelType.PRINT),
            }, ignore_index=True)

            gini_df = gini_df.append({
                'repository-id': repository_id,
                'repository-name': repository_name,
                'repository-type': repository_type,
                'repository-lines-of-code': repository_lines_of_code,
                'gini-index': gini_index_module,
                'scope-type': ScopeType.MODULE.value,
                'scope-count': count_module,
                'scope-log-count': self.get_total_log_count_at_scope(logs_df, repository_id, ScopeType.MODULE, ),

                'scope-log-level-critical': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.CRITICAL),
                'scope-log-level-error': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.ERROR),
                'scope-log-level-warning': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.WARNING),
                'scope-log-level-info': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.INFO),
                'scope-log-level-debug': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.DEBUG),
                'scope-log-level-print': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.MODULE, LogLevelType.PRINT),
            }, ignore_index=True)

            gini_df = gini_df.append({
                'repository-id': repository_id,
                'repository-name': repository_name,
                'repository-type': repository_type,
                'repository-lines-of-code': repository_lines_of_code,
                'gini-index': gini_index_function,
                'scope-type': ScopeType.FUNCTION.value,
                'scope-count': count_function,
                'scope-log-count': self.get_total_log_count_at_scope(logs_df, repository_id, ScopeType.FUNCTION, ),

                'scope-log-level-critical': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                               LogLevelType.CRITICAL),
                'scope-log-level-error': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                            LogLevelType.ERROR),
                'scope-log-level-warning': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                              LogLevelType.WARNING),
                'scope-log-level-info': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                           LogLevelType.INFO),
                'scope-log-level-debug': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                            LogLevelType.DEBUG),
                'scope-log-level-print': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.FUNCTION,
                                                                            LogLevelType.PRINT),
            }, ignore_index=True)

            gini_df = gini_df.append({
                'repository-id': repository_id,
                'repository-name': repository_name,
                'repository-type': repository_type,
                'repository-lines-of-code': repository_lines_of_code,
                'gini-index': gini_index_class,
                'scope-type': ScopeType.CLASS.value,
                'scope-count': count_class,
                'scope-log-count': self.get_total_log_count_at_scope(logs_df, repository_id, ScopeType.CLASS, ),

                'scope-log-level-critical': self.get_total_log_levels_at_scope(logs_df, repository_id,
                                                                               ScopeType.CLASS,
                                                                               LogLevelType.CRITICAL),
                'scope-log-level-error': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.CLASS,
                                                                            LogLevelType.ERROR),
                'scope-log-level-warning': self.get_total_log_levels_at_scope(logs_df, repository_id,
                                                                              ScopeType.FUNCTION,
                                                                              LogLevelType.WARNING),
                'scope-log-level-info': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.CLASS,
                                                                           LogLevelType.INFO),
                'scope-log-level-debug': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.CLASS,
                                                                            LogLevelType.DEBUG),
                'scope-log-level-print': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.CLASS,
                                                                            LogLevelType.PRINT),
            }, ignore_index=True)

            gini_df = gini_df.append({
                'repository-id': repository_id,
                'repository-name': repository_name,
                'repository-type': repository_type,
                'repository-lines-of-code': repository_lines_of_code,
                'gini-index': gini_index_method,
                'scope-type': ScopeType.METHOD.value,
                'scope-count': count_method,
                'scope-log-count': self.get_total_log_count_at_scope(logs_df, repository_id, ScopeType.METHOD, ),

                'scope-log-level-critical': self.get_total_log_levels_at_scope(logs_df, repository_id,
                                                                               ScopeType.METHOD,
                                                                               LogLevelType.CRITICAL),
                'scope-log-level-error': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.METHOD,
                                                                            LogLevelType.ERROR),
                'scope-log-level-warning': self.get_total_log_levels_at_scope(logs_df, repository_id,
                                                                              ScopeType.FUNCTION,
                                                                              LogLevelType.WARNING),
                'scope-log-level-info': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.METHOD,
                                                                           LogLevelType.INFO),
                'scope-log-level-debug': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.METHOD,
                                                                            LogLevelType.DEBUG),
                'scope-log-level-print': self.get_total_log_levels_at_scope(logs_df, repository_id, ScopeType.METHOD,
                                                                            LogLevelType.PRINT),
            }, ignore_index=True)

        gini_df.to_csv(f"{config['path_output']}{config['output_gini_indexes']}", index=False)


