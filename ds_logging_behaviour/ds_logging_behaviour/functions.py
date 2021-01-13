from pathlib import Path


def getrepos(config):
    repos = {}
    local_path = f"{config['repositories_path']}"
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
