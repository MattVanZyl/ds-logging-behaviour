from surround import Stage
from ..print_colours import PrintColours
from ..functions import get_downloaded_repos
import logging
import subprocess
import pandas as pd
from pathlib import Path
import json
import os
from pydriller import GitRepository
from pygount import SourceAnalysis, ProjectSummary


class RepoMetrics(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}---------------------------------\nGetting Metrics From Repositories\n---------------------------------{PrintColours.RESET}")

        repos = get_downloaded_repos(config)

        working_dir = Path().absolute()

        repo_metrics = {}

        # NOTE: The 'check_id' values in the semgrep results will be prepended with 'input.semgrep', which matches the semgrep file locations relative to the working directory.
        # To remove the prepended 'input.semgrep' we change the working directory to the semgrep file location.
        os.chdir(f"{config['semgrep_path']}")

        repo_metrics_df = pd.DataFrame(
            columns=['repository-id', 'project-type', 'project-name', 'total-file-count', 'python-file-count',
                     'class-count', 'method-count', 'lines-of-code'])

        # For each repo:
        for repository_id in repos.keys():
            repo_name = repos[repository_id]['name']
            repo_path = repos[repository_id]['path']
            repo_type = repos[repository_id]['type']

            logging.info(
                f" {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Extracting Repo Metrics...{PrintColours.RESET}")

            metrics = json.loads(subprocess.check_output(
                f"semgrep --config {config['semgrep_repo_metrics']} ../../{repo_path} --json",
                shell=True))

            repo_metrics[repository_id] = {}

            class_count = 0
            method_count = 0

            # For each log found in the semgrep search:
            for result in metrics['results']:
                if result['check_id'] == 'class-count':
                    class_count += 1
                elif result['check_id'] == 'method-count':
                    method_count += 1

            files = GitRepository(f'../../{repo_path}').files()

            # Get the count of all the files in the repo
            total_file_count = len(files)

            # Get the count of all the python files in the repo
            python_files = [f for f in files if f.split(".")[-1] == "py"]
            python_file_count = len(python_files)

            project_summary = ProjectSummary()

            for file in python_files:
                source_analysis = SourceAnalysis.from_file(file, "repo")
                project_summary.add(source_analysis)

            lines_of_code = project_summary.total_code_count

            repo_metrics_df = repo_metrics_df.append(
                {'repository-id': repository_id, 'project-type': repo_type,
                 'project-name': repo_name, 'total-file-count': total_file_count,
                 'python-file-count': python_file_count, 'class-count': class_count,
                 'method-count': method_count, 'lines-of-code': lines_of_code},
                ignore_index=True)

        # Reset the working directory
        os.chdir(f"{working_dir}")

        repo_metrics_df.to_csv(f"{config['output_path']}repo-metrics.csv", index=False)
