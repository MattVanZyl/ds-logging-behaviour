from surround import Stage
import os
from pathlib import Path
import glob
from ..fields import Fields

import subprocess
import json
import re

from ..export_functions import export_final, export_summary, export_gini

class DataExtractor(Stage):
    repositories = {}
    repository_log_counts = {}
    repository_log_levels = {}
    working_dir = Path().absolute()

    def operate(self, state, config):

        self.repositories = self.initialise(state.input_data)


        # Create a data_science and non_data_science directories
        Path(f"{config['input_path']}repo_data/data_science").mkdir(parents=True, exist_ok=True)
        Path(f"{config['input_path']}repo_data/non_data_science").mkdir(parents=True, exist_ok=True)

        for repo_name in self.repositories.keys():
            # Change directory to either the data_science or non_data_science folder based on repo type
            os.chdir(f"{self.working_dir}/{config['input_path']}repo_data/{self.repositories[repo_name]['type']}")

            # Clone the repo
            os.system(f"git clone {self.repositories[repo_name]['repo_link']}")

            self.get_log_counts(config, repo_name)
            self.get_log_levels(config, repo_name)

            # =============================================
            # Log Vs. Non-Log
            # =============================================
            os.chdir(f"{self.working_dir}")

            log_vs_nlog = f"{config['input_path']}log_vs_nonlog/"
            Path(log_vs_nlog).mkdir(parents=True, exist_ok=True)

            repo_path = f"{dir}/{repo_name}/"
            os.system(
                f"git --git-dir={repo_path}.git log -10 -p '*.py' | grep '^[+-]' | grep -Ev '^(--- a/|\+\+\+ b/)'> {log_vs_nlog}{repo_name}.txt")

        log_vs_nonlog = self.load_log_vs_non_log(config)

        export_final(config, self.repositories, self.repository_log_counts, self.repository_log_levels, log_vs_nonlog)
        export_summary(config, self.repositories, self.repository_log_counts, self.repository_log_levels, log_vs_nonlog)
        export_gini(config)

    def initialise(self, repo_data):
        repo_details = {}
        api_links = repo_data[LinkFields.API_LINK]
        repo_links = repo_data[LinkFields.REPO_LINK]
        types = repo_data[LinkFields.TYPE]

        for i in range(api_links.count()):
            repo_name = repo_links[i].split('/')[-1]
            repo_details[repo_name] = {}
            repo_details[repo_name]['type'] = types[i]
            repo_details[repo_name]['api_link'] = api_links[i]
            repo_details[repo_name]['repo_link'] = repo_links[i]
        return repo_details

    # Counting the individual log statements in the repo
    def get_log_counts(self, config, repo_name):
        os.chdir(f"{self.working_dir}/{config['semgrep_path']}")

        output = json.loads(
            subprocess.check_output(f"semgrep --config {config['semgrep_count_rules']} ../repo_data/{self.repositories[repo_name]['type']}/{repo_name} --json",
                                    shell=True))

        self.repository_log_counts[repo_name] = {'print': 0, 'logging': 0, 'trace-traceback': 0, 'io-file.write': 0,
                                      'stderr': 0}

        for file_in_repo in output['results']:
            # for stoping the redundancy of sys.stderr in io and stdrr, """ is to avoid conflict when formatting is used
            if file_in_repo['check_id'] == 'stderr':
                self.repository_log_counts[repo_name]['io-file.write'] -= 1
            check_id = file_in_repo['check_id']
            self.repository_log_counts[repo_name][check_id] += 1

    # Extract log level based information from the repo
    def get_log_levels(self, config, repo_name):
        os.chdir(f"{self.working_dir}/{config['semgrep_path']}")

        output = json.loads(
            subprocess.check_output(f"semgrep --config {config['semgrep_level_rules']} ../repo_data/{self.repositories[repo_name]['type']}/{repo_name} --json",
                                    shell=True))

        self.repository_log_levels[repo_name] = {}
        info_log = {}
        for i in range(len(output['results'])):
            f_name_list = output['results'][i]['path']
            f_name = f_name_list.split('/')[-1]
            self.repository_log_levels[repo_name].setdefault(f_name, {})
            log_type = output['results'][i]['check_id']
            self.repository_log_levels[repo_name][f_name].setdefault('end_line_', {'line': 0})
            self.repository_log_levels[repo_name][f_name].setdefault('logs', "")
            t_line = ""
            if log_type in ['info', 'error', 'warning', 'debug', 'trace', 'fatal']:
                t_line = output['results'][i]['extra']['lines']
                self.repository_log_levels[repo_name][f_name]["logs"] += t_line + ','
            if log_type == 'end_line_':
                self.repository_log_levels[repo_name][f_name][log_type]['line'] = output['results'][i]['end']['line'] - 1
            else:
                self.repository_log_levels[repo_name][f_name].setdefault(log_type, {'lines': [], 'count': 0})
                self.repository_log_levels[repo_name][f_name][log_type]['count'] += 1
                # To remove the redundancy of count in info when it matches with other log
                info_log.setdefault(f_name, [])
                if log_type == 'info':
                    info_log[f_name].append(
                        [output['results'][i]['extra']['lines'], output['results'][i]['start']['col']])
                # to elimate the matching confusion for a statement with two logs
                elif [output['results'][i]['extra']['lines'], output['results'][i]['start']['col']] in info_log[
                    f_name]:
                    self.repository_log_levels[repo_name][f_name]['info']['count'] -= 1
                start, end = output['results'][i]['start']['line'], output['results'][i]['end']['line']
                self.repository_log_levels[repo_name][f_name][log_type]['lines'].append([start, end])

    # changes data to json for adding it to the final format
    def load_log_vs_non_log(self, config):
        files = f"{config['input_path']}log_vs_nonlog/*.txt"
        logvsnlog_changes = {}
        for repo_changes in glob.glob(files, recursive=True):
            log_lines = []
            total_lines, logc = 0, 0
            name = repo_changes.split('/')[-1]
            with open(repo_changes) as rc:
                for line in rc:
                    total_lines += 1
                    temp_line = line[1:].strip()
                    if len(temp_line) != 0:
                        regexList = ['^print', 'io\.', '^trace\.', '^traceback\.', 'logging\.', '^sys\.stderr\.write',
                                     '.*\.write']
                        for regex in regexList:
                            s = re.search(regex, temp_line)
                            if s:
                                log_lines.append(temp_line)
                                logc += 1
                                break
            logvsnlog_changes[name.split('.')[0]] = {'logchanges': logc, 'nonlogchanges': total_lines - logc,
                                                     'log_lines': log_lines}
        return logvsnlog_changes
