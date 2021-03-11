from surround import Stage
from ..color import Color
from ..functions import get_downloaded_repos
import logging
import subprocess
import pandas as pd
from pathlib import Path
import json
from pydriller import GitRepository
from pygount import SourceAnalysis, ProjectSummary


class LogExtractor(Stage):
    all_repository_data = {}

    repository_logs_df = pd.DataFrame(
        columns=['log-id', 'repository-id', 'repository-type', 'repository-name', 'relative-file-path', 'line-number',
                 'log-level',
                 'log-statement', 'log-scope', 'log-scope-id', 'log-scope-lines', 'log-scope-content'])

    repository_metrics_df = pd.DataFrame(
        columns=['repository-id', 'repository-type', 'repository-name', 'total-file-count', 'module-count',
                 'class-count', 'method-count', 'function-count', 'lines-of-code'])

    # ------------------------------------------------------------------------------------------------------------------

    def load_repo_files(self, config, repository_id, repository_name, repository_type, repository_path):
        repository_data = {}

        files = GitRepository(repository_path).files()

        repository_data["repository_name"] = repository_name
        repository_data["repository_type"] = repository_type
        repository_data["total_file_count"] = len(files)

        # Get all of the python files with a .py extension
        python_files = [f for f in files if f.split(".")[-1] == "py" or f.split(".")[-1] == "pyi"]

        repository_data["python_modules"] = {}
        project_summary = ProjectSummary()

        # Store the code of each module
        for file in python_files:
            # Get the path of the current file relative to its repo
            relative_path = file.replace(f"{Path(repository_path).absolute().resolve()}/", "")
            repository_data["python_modules"][relative_path] = {}
            # Save each line of code into the array "lines". Each "python_modules" key will have its own "lines" array
            lines = []
            try:
                # Lines of code count
                source_analysis = SourceAnalysis.from_file(file, "repo")
                project_summary.add(source_analysis)
                file_contents = open(file, "r")
                for line in file_contents:
                    lines.append(line.rstrip())
                file_contents.close()
            except FileNotFoundError:
                logging.error(
                    f"{Color.RED}Error{Color.RESET} - File was not found: {file}")
            except UnicodeDecodeError:
                source_analysis = SourceAnalysis.from_file(file, "repo", encoding="iso-8859-1")
                project_summary.add(source_analysis)
                file_contents = open(file, "r", encoding="iso-8859-1")
                for line in file_contents:
                    lines.append(line.rstrip())
                file_contents.close()

            repository_data["python_modules"][relative_path]["lines"] = lines
            repository_data["python_modules"][relative_path]['functions'] = []
            repository_data["python_modules"][relative_path]['classes'] = []
            repository_data["python_modules"][relative_path]['methods'] = []

        repository_data["lines_of_code"] = project_summary.total_code_count

        # Get all of the classes, methods and functions inside of this module
        components = json.loads(subprocess.check_output(
            f"semgrep --config {config['path_semgrep']}{config['input_semgrep_repo_metrics']} {repository_path} --json",
            shell=True))

        for result in components['results']:
            # Pydriller ignores paths with '.git', do the same for the semgrep results
            if '.git' in result['path']:
                continue
            # Get the path of the current file relative to its repo
            file_path = result['path'].split('/', 5)[5]
            # Get the start and end lines of the current class/method/function (referred to here as component)
            component = {'start_line': result['start']['line'], 'end_line': result['end']['line']}

            # NOTE: The 'check_id' values in the semgrep results will be prepended with 'input.semgrep', matching the folder structure.
            # This 'input.semgrep' is discarded.
            check_id = result['check_id'].split('.')[-1]
            if check_id == 'Method':
                repository_data["python_modules"][file_path]['methods'].append(component)
            elif check_id == 'Class':
                repository_data["python_modules"][file_path]['classes'].append(component)
            elif check_id == 'Function':
                repository_data["python_modules"][file_path]['functions'].append(component)

        # Save all of the repo details inside of the "all_repository_data" object, accessible in the other methods
        self.all_repository_data[repository_id] = repository_data

    # ------------------------------------------------------------------------------------------------------------------

    def get_log_scope(self, config, repository_id, log_file_path, log_line_start, log_line_end):
        """
        Determines the scope details of a log, given the starting and ending line numbers of the log.

        Returns:
            - log_scope: module/function/class/method
            - log_scope_id: The index of the scope e.g. the 3rd function in this module
            - log_scope_content: The log and the surrounding code to provide context
            - log_scope_lines: The line numbers of the scope
        """

        def return_lines(module_lines, start_line, end_line, min_line, max_line):
            # Clamp The lines to grab surrounding code from
            lines_from = max(min(start_line - config['log_context_lines_before'], max_line), min_line) - 1
            lines_to = max(min(end_line + config['log_context_lines_after'], max_line), min_line)

            return "\n".join(module_lines[lines_from:lines_to])

        lines = self.all_repository_data[repository_id]["python_modules"][log_file_path]["lines"]

        # Method
        for index, method in enumerate(
                self.all_repository_data[repository_id]["python_modules"][log_file_path]['methods']):
            if log_line_start >= method['start_line'] and log_line_end <= method['end_line']:
                content = return_lines(lines, log_line_start, log_line_end, method['start_line'],
                                       method['end_line'])
                return 'method', index, content, f"{method['start_line']} - {method['end_line']}"

        # Class
        for index, class_ in enumerate(
                self.all_repository_data[repository_id]["python_modules"][log_file_path]['classes']):
            if log_line_start >= class_['start_line'] and log_line_end <= class_['end_line']:
                content = return_lines(lines, log_line_start, log_line_end, class_['start_line'], class_['end_line'])
                return 'class', index, content, f"{class_['start_line']} - {class_['end_line']}"

        # Function
        for index, function in enumerate(
                self.all_repository_data[repository_id]["python_modules"][log_file_path]['functions']):
            if log_line_start >= function['start_line'] and log_line_end <= function['end_line']:
                content = return_lines(lines, log_line_start, log_line_end, function['start_line'],
                                       function['end_line'])
                return 'function', index, content, f"{function['start_line']} - {function['end_line']}"

        # If the file has been encountered but no component match was found
        module = self.all_repository_data[repository_id]["python_modules"][log_file_path]
        length = len(module['lines'])
        content = return_lines(lines, log_line_start, log_line_end, 1, length)
        return 'module', 0, content, f"1 - {length}"

    # ------------------------------------------------------------------------------------------------------------------

    def repo_metrics(self, repository_id):
        repository_name = self.all_repository_data[repository_id]["repository_name"]
        repository_type = self.all_repository_data[repository_id]["repository_type"]

        module_count = len(self.all_repository_data[repository_id]["python_modules"])
        function_count = 0
        class_count = 0
        method_count = 0
        for file, value in self.all_repository_data[repository_id]["python_modules"].items():
            function_count += len(value['functions'])
            class_count += len(value['classes'])
            method_count += len(value['methods'])

        total_file_count = self.all_repository_data[repository_id]["total_file_count"]
        lines_of_code = self.all_repository_data[repository_id]["lines_of_code"]

        self.repository_metrics_df = self.repository_metrics_df.append(
            {'repository-id': repository_id,
             'repository-type': repository_type,
             'repository-name': repository_name,
             'total-file-count': total_file_count,
             'module-count': module_count,
             'class-count': class_count,
             'method-count': method_count,
             'function-count': function_count,
             'lines-of-code': lines_of_code},
            ignore_index=True)

    # ------------------------------------------------------------------------------------------------------------------

    def operate(self, state, config):
        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}---------------------------------\nExtracting Logs From Repositories\n---------------------------------{Color.RESET}")

        repos = get_downloaded_repos(config)

        if len(repos) == 0:
            logging.error(f"{Color.RED}{Color.BOLD}No Repositories Found{Color.RESET}")
            return

        working_dir = Path().absolute()

        # For each repo:
        log_id = 0
        repo_index = 0
        total_repos = len(repos)
        for repository_id in repos.keys():
            repository_name = repos[repository_id]['name']
            repository_path = repos[repository_id]['path']
            repository_type = repos[repository_id]['type']

            repo_index += 1
            logging.info(
                f" {Color.GREEN}{repo_index}{Color.RESET}/{Color.GREEN}{total_repos}{Color.RESET} - ID: {Color.BLUE}{repository_id}{Color.RESET} Name: {Color.BLUE}{repository_name}{Color.RESET}")

            logging.info(
                f" {Color.YELLOW}Extracting Repo Details...{Color.RESET}")

            self.load_repo_files(config, repository_id, repository_name, repository_type, repository_path)

            self.repo_metrics(repository_id)

            logging.info(
                f" {Color.YELLOW}Extracting Logs...{Color.RESET}")

            # Get all of the logs in the repo
            # These are found using the semgrep patterns defined in "log_levels.yaml"
            log_levels = json.loads(subprocess.check_output(
                f"semgrep --config {config['path_semgrep']}{config['input_semgrep_log_levels']} {repository_path} --json",
                shell=True))

            # For each log found in the semgrep search:
            for result in log_levels['results']:
                # Pydriller ignores paths with '.git', do the same for the semgrep results
                if '.git' in result['path']:
                    continue

                log_id += 1
                log_file_path = result['path'].split('/', 5)[5]
                log_line_start = result['start']['line']
                log_line_end = result['end']['line']

                # Discarded the prepended 'input.semgrep' (matching the folder structure).

                log_level = result['check_id'].split('.')[-1]
                # Do not assign any log level for print statements
                log_level = log_level if log_level != "Print" else ""

                # Get the log scope details and surrounding code
                log_scope, log_scope_id, log_scope_content, log_scope_lines = self.get_log_scope(config,
                                                                                                 repository_id,
                                                                                                 log_file_path,
                                                                                                 log_line_start,
                                                                                                 log_line_end)

                self.repository_logs_df = self.repository_logs_df.append(
                    {'log-id': log_id,
                     'repository-id': repository_id,
                     'repository-type': repository_type,
                     'repository-name': repository_name,
                     'relative-file-path': log_file_path,
                     'line-number': log_line_start,
                     'log-level': log_level,
                     'log-statement': result['extra']['lines'].strip(),
                     'log-scope': log_scope,
                     'log-scope-id': log_scope_id,
                     'log-scope-lines': log_scope_lines,
                     'log-scope-content': log_scope_content
                     },
                    ignore_index=True)

        self.repository_logs_df.to_csv(f"{config['path_output']}{config['output_logs']}", index=False)
        self.repository_metrics_df.to_csv(f"{config['path_output']}{config['output_metrics']}", index=False)
