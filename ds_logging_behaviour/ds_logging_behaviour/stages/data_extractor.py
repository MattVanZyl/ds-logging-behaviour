from surround import Stage
from ..print_colours import PrintColours
from ..functions import get_downloaded_repos
import logging
import subprocess
import pandas as pd
from pathlib import Path
import json
import os


class DataExtractor(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}---------------------------------\nExtracting Data From Repositories\n---------------------------------{PrintColours.RESET}")

        repos = get_downloaded_repos(config)

        if len(repos) == 0:
            logging.info(f"{PrintColours.RED}{PrintColours.BOLD}No Repositories Found{PrintColours.RESET}")
            return

        working_dir = Path().absolute()

        repo_logs = {}

        # NOTE: The 'check_id' values in the semgrep results will be prepended with 'input.semgrep', which matches the semgrep file locations relative to the working directory.
        # To remove the prepended 'input.semgrep' we change the working directory to the semgrep file location.
        os.chdir(f"{config['semgrep_path']}")

        log_levels_df = pd.DataFrame(
            columns=['log-id', 'repository-id', 'project-type', 'project-name', 'file-name', 'line-number', 'log-level',
                     'log-statement'])

        log_id = 0

        # For each repo:
        for repository_id in repos.keys():
            repo_name = repos[repository_id]['name']
            repo_path = repos[repository_id]['path']
            repo_type = repos[repository_id]['type']

            logging.info(
                f" {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Extracting log levels...{PrintColours.RESET}")

            log_levels = json.loads(subprocess.check_output(
                f"semgrep --config {config['semgrep_level_rules']} ../../{repo_path} --json",
                shell=True))

            repo_logs[repository_id] = []

            # For each log found in the semgrep search:
            for result in log_levels['results']:
                log_entry = {}
                log_entry['log-id'] = log_id
                log_id += 1
                log_entry['project-type'] = repo_type
                log_entry['project-type'] = repo_type
                log_entry['project-name'] = repo_name
                log_entry['file-name'] = result['path'].split('/')[-1]
                log_entry['line-number'] = result['start']['line']
                log_entry['log-level'] = result['check_id']
                log_entry['log-statement'] = result['extra']['lines'].strip()
                repo_logs[repository_id].append(log_entry)

            for entry in repo_logs[repository_id]:
                log_levels_df = log_levels_df.append(
                    {'log-id': entry['log-id'], 'repository-id': repository_id, 'project-type': entry['project-type'],
                     'project-name': entry['project-name'], 'file-name': entry['file-name'],
                     'line-number': entry['line-number'], 'log-level': entry['log-level'],
                     'log-statement': entry['log-statement']},
                    ignore_index=True)

        # Reset the working directory
        os.chdir(f"{working_dir}")

        log_levels_df.to_csv(f"{config['output_path']}log-levels.csv", index=False)
