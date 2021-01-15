from pathlib import Path


def get_downloaded_repos(config):
    """Get the details of all the downloaded repos.
    Returns a json object that has each repo_id mapped to it's corresponding name, type and local path.
    """
    repos = {}
    local_path = f"{config['repositories_path']}"

    if Path(local_path).exists():
        for type_folder in Path(local_path).iterdir():
            if type_folder.is_dir():
                repo_type = type_folder.name
                for id_folder in type_folder.iterdir():
                    if id_folder.is_dir():
                        repo_id = id_folder.name
                        for name_folder in id_folder.iterdir():
                            repo_name = name_folder.name
                            repos[repo_id] = {}
                            repos[repo_id]['name'] = repo_name
                            repos[repo_id]['type'] = repo_type
                            repos[repo_id]['path'] = f'{local_path}{repo_type}/{repo_id}/{repo_name}'
                            break
    return repos
