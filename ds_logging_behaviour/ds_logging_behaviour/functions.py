from .fields import LinkFields
import json

def initialise(repo_data):
    api_links = repo_data[LinkFields.API_LINK]
    repo_links = repo_data[LinkFields.REPO_LINK]
    types = repo_data[LinkFields.TYPE]
    return api_links, repo_links, types

def save_json(dictionary, fname = 'output.json'):
    with open(fname, "w") as output:
        json.dump(dictionary, output)

def read_json(fname):
    with open(fname) as f:
        data = json.load(f)
    return data