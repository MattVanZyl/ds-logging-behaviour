from surround import Stage
from ..fields import Fields
from ..print_colours import PrintColours

import git
import logging

class RepoDownloader(Stage):
    def operate(self, state, config):
        repositories = self.initialise(state.input_data)

        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}-----------------------\nSetting Up Repositories\n-----------------------{PrintColours.END_COLOUR}")

        for repo_name in repositories.keys():
            repo_path = f"{config['repos_path']}{repositories[repo_name]['type']}/{repo_name}"

            # Check if repo has already been cloned
            try:
                repo = git.Repo(repo_path)
                # If the local repo already exists, pull the latest version
                logging.info(f" {PrintColours.BLUE}{repo_name}{PrintColours.END_COLOUR} - Pulling latest...")
                repo.remotes.origin.pull()
            except:
                # Otherwise, clone the repo
                logging.info(f" {PrintColours.BLUE}{repo_name}{PrintColours.END_COLOUR} - Cloning...")
                git.Repo.clone_from(repositories[repo_name]['repo_link'], repo_path)

    def initialise(self, repo_data):
        repo_details = {}
        api_links = repo_data[Fields.API_LINK]
        repo_links = repo_data[Fields.REPO_LINK]
        types = repo_data[Fields.TYPE]

        for i in range(api_links.count()):
            repo_name = repo_links[i].split('/')[-1]
            repo_details[repo_name] = {}
            repo_details[repo_name]['type'] = types[i]
            repo_details[repo_name]['api_link'] = api_links[i]
            repo_details[repo_name]['repo_link'] = repo_links[i]
        return repo_details
