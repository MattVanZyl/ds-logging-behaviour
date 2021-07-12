from surround import Stage
from ..fields import Fields
from ..color import Color
from pydriller import GitRepository, RepositoryMining
from git.exc import GitCommandError, NoSuchPathError
import logging
from pathlib import Path
import pandas as pd


class RepoDownloader(Stage):
    def initialise(self, repo_data):
        """Maps the contents of the csv file specified by 'input_repo_list' in config.yaml to a json object.
        """
        repo_details = {}
        ids = repo_data[Fields.ID]
        names = repo_data[Fields.NAME]
        urls = repo_data[Fields.URL]
        commits = repo_data[Fields.COMMIT]
        types = repo_data[Fields.TYPE]

        for i in range(names.count()):
            repo_id = ids[i]
            repo_details[repo_id] = {}
            repo_details[repo_id]['name'] = names[i]
            repo_details[repo_id]['url'] = urls[i]
            repo_details[repo_id]['commit'] = commits[i]
            repo_details[repo_id]['type'] = types[i]

        return repo_details

    def operate(self, state, config):
        repositories = self.initialise(state.input_data)

        logging.info(
            f"\n{Color.CYAN}{Color.BOLD}------------------------\nDownloading Repositories\n------------------------{Color.RESET}")

        manifest_df = pd.DataFrame(columns=['repository-id','project-type','project-name','url','commit','local-path','download-successful'])

        for repository_id in repositories.keys():
            repo_name = repositories[repository_id]['name']
            local_path = f"{config['path_repositories']}{repositories[repository_id]['type']}/{repository_id}"

            download_successful = False
            try:
                # Check if repo already exists
                GitRepository(f'{local_path}/{repo_name}')._open_repository()
                logging.info(
                    f" {Color.BLUE}{repository_id}. {repo_name}{Color.RESET} - {Color.YELLOW}Already downloaded{Color.RESET}")
                download_successful = True

            except NoSuchPathError:
                try:
                    # Otherwise, clone the repo
                    logging.info(
                        f" {Color.BLUE}{repository_id}. {repo_name}{Color.RESET} - {Color.YELLOW}Cloning...{Color.RESET}")
                    Path(local_path).mkdir(parents=True, exist_ok=True)
                    # Clone the specified commit, if no commit is provided then clone the latest
                    RepositoryMining(
                        repositories[repository_id]['url'],
                        from_commit=repositories[repository_id]['commit']
                    )._clone_remote_repo(
                        tmp_folder=local_path,
                        repo=repositories[repository_id]['url']
                    )
                    download_successful = True

                except GitCommandError as err:
                    logging.info(
                        f" {Color.BLUE}{repository_id}. {repo_name}{Color.RESET} - {Color.RED}Download failed:{Color.RESET}\n{err.stderr}")
                    Path(local_path).rmdir()

            manifest_df = manifest_df.append({
                'repository-id': repository_id,
                'project-type': repositories[repository_id]['type'],
                'project-name': repo_name,
                'url': repositories[repository_id]['url'],
                'local-path': Path(local_path).absolute(),
                'commit': repositories[repository_id]['commit'],
                'download-successful': f'{download_successful}'
            }, ignore_index=True)

        manifest_df.to_csv(f"{config['path_repositories']}{config['output_manifest']}", index=False)


