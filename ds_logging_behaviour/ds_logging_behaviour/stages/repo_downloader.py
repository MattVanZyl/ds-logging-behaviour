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
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}------------------------\nDownloading Repositories\n------------------------{PrintColours.RESET}")

        repository_id = 0

        manifest_df = pd.DataFrame(columns=['repository-id','project-type','project-name','url','local-path','download-successful'])

        for repo_name in repositories.keys():
            local_path = f"{config['repositories_path']}{repositories[repo_name]['type']}/{repository_id}"

            state.repos[repo_name] = {}
            state.repos[repo_name]['path'] = local_path
            state.repos[repo_name]['type'] = repositories[repo_name]['type']

            download_successful = False

            try:
                # Check if repo already exists
                GitRepository(f'{local_path}/{repo_name}')._open_repository()
                logging.info(
                    f" {repository_id}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Already downloaded{PrintColours.RESET}")
                download_successful = True

            except NoSuchPathError:
                try:
                    # Otherwise, clone the repo
                    logging.info(
                        f" {repository_id}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.YELLOW}Cloning...{PrintColours.RESET}")
                    Path(local_path).mkdir(parents=True, exist_ok=True)
                    # Clone the specified commit, if no commit is provided then clone the latest
                    RepositoryMining(repositories[repo_name]['url'],
                                     from_commit=repositories[repo_name]['commit'])._clone_remote_repo(
                        tmp_folder=local_path, repo=repositories[repo_name]['url'])
                    download_successful = True

                except GitCommandError as err:
                    logging.info(
                        f" {repository_id}. {PrintColours.BLUE}{repo_name}{PrintColours.RESET} - {PrintColours.RED}Download failed:{PrintColours.RESET}\n{err.stderr}")
                    Path(local_path).rmdir()

            manifest_df = manifest_df.append(
                {'repository-id': repository_id, 'project-type': repositories[repo_name]['type'],
                 'project-name': repo_name, 'url': repositories[repo_name]['url'], 'local-path': Path(local_path).absolute(), 'download-successful': f'{download_successful}'}, ignore_index=True)
            repository_id += 1

        manifest_df.to_csv(f"{config['repositories_path']}repo-manifest.csv", index=False)

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
