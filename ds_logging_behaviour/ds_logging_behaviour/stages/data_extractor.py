"""
This module defines the input validator which is executed
before all other stages in the pipeline and checks whether
the data contained in the State object is valid.
"""

from surround import Stage
import logging
import os
from pathlib import Path
import glob

import subprocess
import json
import re

from ..functions import initialise, finalcalc, export_summary

LOGGER = logging.getLogger(__name__)


class DataExtractor(Stage):
    def operate(self, state, config):

        api_links, repo_links, types = initialise(state.input_data)
        working_dir = Path().absolute()

        repo_details = {}
        repo_log_counts = {}
        repo_log_levels = {}

        # For each repo...
        for i in range(api_links.count()):
            # Reset to the working directory
            os.chdir(f"{working_dir}")

            # Get the name of the repo
            repo_name = repo_links[i].split('/')[-1]

            repo_details[repo_name] = {}
            repo_details[repo_name]['Type'] = types[i]
            repo_details[repo_name]['Repo Link'] = repo_links[i]

            # Create a data_science and non_data_science directory
            dir = f"{config['input_path']}repo_data/{types[i]}"
            Path(dir).mkdir(parents=True, exist_ok=True)

            # Clone the repo
            os.chdir(f"{dir}/")
            os.system(f"git clone {repo_links[i]}")

            # =============================================
            # Log Count
            # =============================================
            output = json.loads(
                subprocess.check_output(f"semgrep --config ../../../{config['semgrep_logcount']} {repo_name} --json", shell=True))
                #subprocess.check_output(f"semgrep -f {config['semgrep_logcount']} {repo_name} --json", shell=True))

            repo_log_counts[repo_name] = {'print': 0, 'logging': 0, 'trace-traceback': 0, 'io-file.write': 0,
                                         'stderr': 0}

            for file_in_repo in output['results']:
                # for stoping the redundancy of sys.stderr in io and stdrr, """ is to avoid conflict when formatting is used
                if file_in_repo['check_id'] == 'stderr':
                    repo_log_counts[repo_name]['io-file.write'] -= 1

                # Remove the "input" at the start of the "check_id"
                check_id = file_in_repo['check_id'].split('.',1)[1]
                repo_log_counts[repo_name][check_id] += 1


            # =============================================
            # Log Level
            # =============================================
            output2 = json.loads(
                subprocess.check_output(f"semgrep --config ../../../{config['semgrep_loglevel']} {repo_name} --json",
                                        shell=True))
                # subprocess.check_output(f"semgrep -f {config['semgrep_loglevel']} {repo_name} --json", shell=True))


            repo_log_levels[repo_name] = {}
            info_log = {}
            for i in range(len(output2['results'])):
                f_name_list = output2['results'][i]['path']
                f_name = f_name_list.split('/')[-1]
                repo_log_levels[repo_name].setdefault(f_name, {})
                log_type = output2['results'][i]['check_id']
                repo_log_levels[repo_name][f_name].setdefault('end_line_', {'line': 0})
                repo_log_levels[repo_name][f_name].setdefault('logs', "")
                t_line = ""
                if log_type in ['info', 'error', 'warning', 'debug', 'trace', 'fatal']:
                    t_line = output2['results'][i]['extra']['lines']
                    repo_log_levels[repo_name][f_name]["logs"] += t_line + ','
                if log_type == 'end_line_':
                    repo_log_levels[repo_name][f_name][log_type]['line'] = output2['results'][i]['end']['line'] - 1
                else:
                    repo_log_levels[repo_name][f_name].setdefault(log_type, {'lines': [], 'count': 0})
                    repo_log_levels[repo_name][f_name][log_type]['count'] += 1
                    # To remove the redundancy of count in info when it matches with other log
                    info_log.setdefault(f_name, [])
                    if log_type == 'info':
                        info_log[f_name].append(
                            [output2['results'][i]['extra']['lines'], output2['results'][i]['start']['col']])
                    # to elimate the matching confusion for a statement with two logs
                    elif [output2['results'][i]['extra']['lines'], output2['results'][i]['start']['col']] in info_log[
                        f_name]:
                        repo_log_levels[repo_name][f_name]['info']['count'] -= 1
                    start, end = output2['results'][i]['start']['line'], output2['results'][i]['end']['line']
                    repo_log_levels[repo_name][f_name][log_type]['lines'].append([start, end])

            # =============================================
            # Log Vs. Non-Log
            # =============================================
            os.chdir(f"{working_dir}")

            # Create a data_science and non_data_science directory
            log_vs_nlog = f"{config['input_path']}log_vs_nonlog/"
            Path(log_vs_nlog).mkdir(parents=True, exist_ok=True)

            repo_path = f"{dir}/{repo_name}/"
            os.system(
                f"git --git-dir={repo_path}.git log -10 -p '*.py' | grep '^[+-]' | grep -Ev '^(--- a/|\+\+\+ b/)'> {log_vs_nlog}{repo_name}.txt")

            # =============================================


        log_vs_nonlog = changesjson(config)
        finalcalc(config, repo_details, repo_log_counts, repo_log_levels, log_vs_nonlog)
        # export_summary(config, repo_details, repo_log_counts, repo_log_levels, log_vs_nonlog)

# changes json for adding the data to the final format
def changesjson(config):
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
