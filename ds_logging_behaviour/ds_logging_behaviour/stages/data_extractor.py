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

from ..functions import initialise, save_json, read_json

LOGGER = logging.getLogger(__name__)

class DataExtractor(Stage):
    def operate(self, state, config):

        api_links, repo_links, types = initialise(state.input_data)
        Path(config['input_folder'] + "log_instances/").mkdir(parents=True, exist_ok=True)

        working_dir = Path().absolute()
        print(working_dir)

        for i in range(api_links.count()):
            repo_name = repo_links[i].split('/')[-1]
            print(repo_name + " -- " + api_links[i])

            # Create repo directories
            dir = config['input_folder'] + "repo_data/" + types[i]
            Path(dir).mkdir(parents=True, exist_ok=True)

            os.chdir(f"{dir}/")

            # os.system(f"git clone {repo_links[i]}")
            # os.system(f"semgrep -f {config['semgrep_logcount']} {repo_name} --json -o {working_dir}/{config['input_folder']}log_instances/{repo_name}.json")

            os.chdir(f"{working_dir}")

        self.semgrep2json(config)
        os.chdir(f"{working_dir}")

    def semgrep2json(self, config):
        os.chdir(f"{config['input_folder']}log_instances/")
        path = '*.json'
        repo_log_count = {}
        for reponame in glob.glob(path, recursive = True):
            repo_log_count[reponame.split('.')[0]] = {'print' : 0, 'logging' : 0, 'trace-traceback' : 0, 'io-file.write' : 0,  'stderr' : 0}
            file_logcount = read_json(reponame)
            for file_in_repo in file_logcount['results']:
                #for stoping the redundancy of sys.stderr in io and stdrr, """ is to avoid conflict when formatting is used
                if file_in_repo['check_id'] == 'stderr':
                    repo_log_count[reponame.split('.')[0]]['io-file.write'] -= 1
                repo_log_count[reponame.split('.')[0]][file_in_repo['check_id']] += 1
        save_json(repo_log_count, f"{config['input_folder']}log_instances/log_count.json")


