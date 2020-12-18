from surround import Stage
from ..fields import Fields
from ..print_colours import PrintColours
from pydriller import GitRepository, RepositoryMining
from git.exc import GitCommandError, NoSuchPathError
import logging
from pathlib import Path
import pandas as pd


class RepoDownloader(Stage):
    def operate(self, state, config):
        repositories = self.initialise(state.input_data)

        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}-----------------------\nSetting Up Repositories\n-----------------------{PrintColours.RESET}")

        repo_count = 1

        failed_downloads_df = pd.DataFrame(columns=['number','name','url'])

        for repo_name in repositories.keys():
            download_folder = f"{config['repositories_path']}repository_{repo_count}"
            local_path = f"{download_folder}/{repo_name}"

            state.repos[repo_name] = {}
            state.repos[repo_name]['path'] = local_path
            state.repos[repo_name]['type'] = repositories[repo_name]['type']

            try:
                # Check if repo already exists
                GitRepository(local_path)._open_repository()
                logging.info(
                    f" {repo_count}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Already downloaded{PrintColours.RESET}")

            except NoSuchPathError:
                try:
                    # Otherwise, clone the repo
                    logging.info(
                        f" {repo_count}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Cloning...{PrintColours.RESET}")
                    Path(download_folder).mkdir(parents=True, exist_ok=True)
                    # Clone the specified commit, if no commit is provided then clone the latest
                    RepositoryMining(repositories[repo_name]['url'],
                                     from_commit=repositories[repo_name]['commit'])._clone_remote_repo(
                        tmp_folder=download_folder, repo=repositories[repo_name]['url'])

                except GitCommandError as err:
                    logging.info(
                        f" {repo_count}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.RED}Download failed:{PrintColours.RESET}\n{err.stderr}")
                    failed_downloads_df = failed_downloads_df.append({'number': repo_count,'name': repo_name,'url': repositories[repo_name]['url']}, ignore_index=True)

            repo_count += 1

        failed_downloads_df.to_csv(f"{config['repositories_path']}failed_downloads.csv", index=False)

    def initialise(self, repo_data):
        repo_details = {}
        names = repo_data[Fields.NAME]
        urls = repo_data[Fields.URL]
        commits = repo_data[Fields.COMMIT]
        types = repo_data[Fields.TYPE]

        for i in range(names.count()):
            repo_name = names[i]
            repo_details[repo_name] = {}
            repo_details[repo_name]['url'] = urls[i]
            repo_details[repo_name]['commit'] = commits[i]
            repo_details[repo_name]['type'] = types[i]
        return repo_details
