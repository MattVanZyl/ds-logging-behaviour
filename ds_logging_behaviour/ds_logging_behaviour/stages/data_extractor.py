from surround import Stage
from ..print_colours import PrintColours
import logging
import subprocess

class DataExtractor(Stage):

    def operate(self, state, config):

        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}---------------------------------\nExtracting Data From Repositories\n---------------------------------{PrintColours.RESET}")

        for repo_name in state.repos.keys():
            repo_path = state.repos[repo_name]['path']

            # NOTE: At the moment all of the 'check_id' values will be prepended with 'input.semgrep' which matches the folder structure.
            # To remove this you have to change directory to the semgrep yaml file location and then run the semgrep command

            # Get repo log counts
            logging.info(f" {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Extracting log counts...{PrintColours.RESET}")
            counts_path = f"{config['input_path']}log_data/counts/log_counts_{repo_name}.json"
            subprocess.call(f"semgrep --config {config['semgrep_path']}{config['semgrep_count_rules']} {repo_path} --json -o {counts_path}", shell=True)

            # Get repo log levels
            logging.info(f" {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Extracting log levels...{PrintColours.RESET}")
            counts_path = f"{config['input_path']}log_data/levels/log_levels_{repo_name}.json"
            subprocess.call(f"semgrep --config {config['semgrep_path']}{config['semgrep_level_rules']} {repo_path} --json -o {counts_path}",shell=True)
