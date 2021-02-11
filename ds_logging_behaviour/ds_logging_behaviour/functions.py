from glob import iglob


def get_downloaded_repos(config):
    """Get the details of all the downloaded repos.
    Returns a json object that has each repo_id mapped to it's corresponding name, type and local path.
    """
    repos = {}

    # Each of the repos are downloaded into a path that fits the structure:
    # repositories/{repo_type}/{repo_id}/{repo_name}
    # From this path we can extract the required repo details and store them in a json object
    repo_paths = iglob(f"{config['path_repositories']}*/*/*")

    for repo_path in repo_paths:
        repo_id = repo_path.split("/")[-2]
        repos[repo_id] = {}
        repos[repo_id]['name'] = repo_path.split("/")[-1]
        repos[repo_id]['type'] = repo_path.split("/")[-3]
        repos[repo_id]['path'] = repo_path
    return repos
