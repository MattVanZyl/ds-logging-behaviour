from surround import Stage
from ..color import Color
from ..functions import get_downloaded_repos
import logging
import subprocess
import pandas as pd
from pathlib import Path
import json
import os
from pydriller import GitRepository
from pygount import SourceAnalysis, ProjectSummary

# repo_components json structure:
#
# repository_id {
#     file_path {
#         functions[
#             {
#                 content :
#                 start_line :
#                 end_line :
#             },
#             {
#                 content :
#                 start_line :
#                 end_line :
#             }
#         ]
#         classes[
#             {
#                 content :
#                 start_line :
#                 end_line :
#             }
#         ]
#         methods[
#             {
#                 content :
#                 start_line :
#                 end_line :
#             }
#         ]
#     }
# }

class LogExtractor(Stage):

    repo_components = {}

    repository_logs_df = pd.DataFrame(
        columns=['log-id', 'repository-id', 'repository-type', 'repository-name', 'relative-file-path', 'line-number', 'log-level',
                 'log-statement', 'log-scope', 'log-scope-id', 'log-scope-lines', 'log-scope-content'])

    repository_metrics_df = pd.DataFrame(
        columns=['repository-id', 'repository-type', 'repository-name', 'file-count', 'module-count',
                 'class-count', 'method-count', 'function-count', 'lines-of-code'])

    def append_repo_components(self, config, repository_id, repo_path):
        components = json.loads(subprocess.check_output(
            f"semgrep --config {config['input_semgrep_repo_metrics']} ../../{repo_path} --json",
            shell=True))

        self.repo_components[repository_id] = {}

        for result in components['results']:
            file_path = result['path']

            # If the file has not yet been encountered, add it
            if file_path not in self.repo_components[repository_id]:
                self.repo_components[repository_id][file_path] = {}
                self.repo_components[repository_id][file_path]['functions'] = []
                self.repo_components[repository_id][file_path]['classes'] = []
                self.repo_components[repository_id][file_path]['methods'] = []

            component = {}
            content = result['extra']['lines'].strip()
            content = content[:32000] + (content[32000:] and '...')
            component['content'] = content
            component['start_line'] = result['start']['line']
            component['end_line'] = result['end']['line']

            if result['check_id'] == 'Method':
                self.repo_components[repository_id][file_path]['methods'].append(component)
            elif result['check_id'] == 'Class':
                self.repo_components[repository_id][file_path]['classes'].append(component)
            elif result['check_id'] == 'Function':
                self.repo_components[repository_id][file_path]['functions'].append(component)

    def get_log_scope(self, repository_id, log_file_path, log_line):

        # 'log_scope', 'log_scope_id', 'log_scope_content', 'log_scope_lines'

        # Module
        # If the file has not yet been encountered, it means that no functions, classes or methods
        # were found in the file and thus the log must be at the module level.
        if log_file_path not in self.repo_components[repository_id]:
            return 'module', 0, "", ""

        # Method
        for index, method in enumerate(self.repo_components[repository_id][log_file_path]['methods']):
            if log_line >= method['start_line'] and log_line <= method['end_line']:
                return 'method', index, method['content'], f"{method['start_line']} - {method['end_line']}"

        # Class
        for index, class_ in enumerate(self.repo_components[repository_id][log_file_path]['classes']):
            if log_line >= class_['start_line'] and log_line <= class_['end_line']:
                return 'class', index, class_['content'], f"{class_['start_line']} - {class_['end_line']}"

        # Function
        for index, function in enumerate(self.repo_components[repository_id][log_file_path]['functions']):
            if log_line >= function['start_line'] and log_line <= function['end_line']:
                return 'function', index, function['content'], f"{function['start_line']} - {function['end_line']}"

        # If the file has been encountered but no component match was found
        return 'module', 0, "", ""

    def repo_metrics(self, repository_id, repository_name, repository_path, repository_type):

        files = GitRepository(f'../../{repository_path}').files()

        # Total file count
        file_count = len(files)

        # Components counts (Module, Function, Class, Method)
        python_files = [f for f in files if f.split(".")[-1] == "py"]
        module_count = len(python_files)
        function_count = 0
        class_count = 0
        method_count = 0
        for file, value in self.repo_components[repository_id].items():
            function_count += len(value['functions'])
            class_count += len(value['classes'])
            method_count += len(value['methods'])

        # Lines of code
        project_summary = ProjectSummary()
        for file in python_files:
            try:
                source_analysis = SourceAnalysis.from_file(file, "repo")
                project_summary.add(source_analysis)
            except:
                # Ran into a symbolic link that broke this
                logging.error(
                    f"{Color.RED}Error {Color.RESET}occurred while analysing file: {file}")
        lines_of_code = project_summary.total_code_count

        self.repository_metrics_df = self.repository_metrics_df.append(
            {'repository-id': repository_id,
             'repository-type': repository_type,
             'repository-name': repository_name,
             'file-count': file_count,
             'module-count': module_count,
             'class-count': class_count,
             'method-count': method_count,
             'function-count': function_count,
             'lines-of-code': lines_of_code},
            ignore_index=True)

    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nExtracting Logs From Repositories\n---------------------------------{Color.RESET}")

        repos = get_downloaded_repos(config)

        if len(repos) == 0:
            logging.error(f"{Color.RED}{Color.BOLD}No Repositories Found{Color.RESET}")
            return

        working_dir = Path().absolute()

        # NOTE: The 'check_id' values in the semgrep results will be prepended with 'input.semgrep', which matches the semgrep file locations relative to the working directory.
        # To remove the prepended 'input.semgrep' we change the working directory to the semgrep file location.
        os.chdir(f"{config['path_semgrep']}")

        # For each repo:
        log_id = 0
        for repository_id in repos.keys():
            repository_name = repos[repository_id]['name']
            repository_path = repos[repository_id]['path']
            repository_type = repos[repository_id]['type']

            logging.info(
                f" {Color.BLUE}- {repository_id}. {repository_name} -{Color.RESET}")

            logging.info(
                f" {Color.YELLOW}Finding Repo Functions, Classes and Methods...{Color.RESET}")

            self.append_repo_components(config, repository_id, repository_path)

            logging.info(
                f" {Color.YELLOW}Extracting Logs...{Color.RESET}")

            log_levels = json.loads(subprocess.check_output(
                f"semgrep --config {config['input_semgrep_log_levels']} ../../{repository_path} --json",
                shell=True))

            # For each log found in the semgrep search:
            for result in log_levels['results']:
                log_id += 1
                log_file_path = result['path']
                log_line = result['start']['line']

                # Do not assign any log level for print statements
                log_level = result['check_id']
                log_level = log_level if log_level != "Print" else ""

                log_scope, log_scope_id, log_scope_content, log_scope_lines = self.get_log_scope(repository_id, log_file_path, log_line)

                self.repository_logs_df = self.repository_logs_df.append(
                    {'log-id': log_id,
                     'repository-id': repository_id,
                     'repository-type': repository_type,
                     'repository-name': repository_name,
                     'relative-file-path': log_file_path.split('/',7)[7],
                     'line-number': log_line,
                     'log-level': log_level,
                     'log-statement': result['extra']['lines'].strip(),
                     'log-scope': log_scope,
                     'log-scope-id': log_scope_id,
                     'log-scope-lines': log_scope_lines,
                     'log-scope-content': log_scope_content
                     },
                    ignore_index=True)

            logging.info(
                f" {Color.YELLOW}Extracting repo metrics...{Color.RESET}")
            self.repo_metrics(repository_id, repository_name, repository_path, repository_type)

        # Reset the working directory
        os.chdir(f"{working_dir}")

        self.repository_logs_df.to_csv(f"{config['path_output']}{config['output_logs']}", index=False)
        self.repository_metrics_df.to_csv(f"{config['path_output']}{config['output_metrics']}", index=False)
