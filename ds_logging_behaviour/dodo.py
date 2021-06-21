"""
This module defines the tasks that can be executed using `surround run [task name]`
"""

import os
import sys
import subprocess

from pathlib import Path

from surround import Config
from surround.util import generate_docker_volume_path
from surround_cli.experiment.util import get_surround_config

CONFIG = Config(os.path.dirname(__file__))
DOIT_CONFIG = {'verbosity':2, 'backend':'sqlite3'}
PACKAGE_PATH = os.path.basename(CONFIG["package_path"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
IMAGE_JUPYTER = "%s/%s-jupyter:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
DOCKER_JUPYTER = "Dockerfile.Notebook"

PARAMS = [
    {
        'name': 'args',
        'long': 'args',
        'type': str,
        'default': ""
    }
]

def task_status():
    """Show information about the project such as available runners and assemblers"""
    return {
        'actions': ["%s -m %s --status" % (sys.executable, PACKAGE_PATH)]
    }

def task_build():
    """Build the Docker image for the current project"""
    return {
        'actions': ['docker build --tag=%s .' % IMAGE],
        'params': PARAMS
    }

def task_remove():
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s %s -f' % (IMAGE, IMAGE_JUPYTER)],
        'params': PARAMS
    }

def task_dev():
    """Run the main task for the project"""
    cmd = [
        "docker",
        "run",
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        "%s" % IMAGE,
        "python3 -m %s %s" % (PACKAGE_PATH, "%(args)s")
    ]
    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_interactive():
    """Run the Docker container in interactive mode"""
    def run():
        cmd = [
            'docker',
            'run',
            '-it',
            '--rm',
            '-w',
            '/app',
            '--volume',
            '%s/:/app' % CONFIG['volume_path'],
            IMAGE,
            'bash'
        ]
        process = subprocess.Popen(cmd, encoding='utf-8')
        process.wait()

    return {
        'actions': [run]
    }

def task_prod():
    """Run the main task inside a Docker container for use in production """
    return {
        'actions': ["docker run %s python3 -m %s %s" % (IMAGE, PACKAGE_PATH, "%(args)s")],
        'task_dep': ["build"],
        'params': PARAMS
    }

def task_build_jupyter():
    """Build the Docker image for a Jupyter Lab notebook"""
    return {
        'basename': 'buildJupyter',
        'actions': ['docker build --tag=%s . -f %s' % (IMAGE_JUPYTER, DOCKER_JUPYTER)],
        'task_dep': ['build'],
        'params': PARAMS
    }

def task_jupyter():
    """Run a Jupyter Lab notebook"""
    cmd = [
        "docker",
        "run",
        "-itp",
        "8888:8888",
        '-w',
        '/app',
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        IMAGE_JUPYTER
    ]
    return {
        'actions': [" ".join(cmd)],
    }

# ======================================================================================================================
# Download repositories
# ======================================================================================================================

def task_download_repos():
    """Download all the repositories, run inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"
    repo_path = CONFIG["volume_path"] + "../../repositories"

    global_config = get_surround_config()

    # Inject user's name and email into the env variables of the container
    user_name = global_config.get_path("user.name")
    user_email = global_config.get_path("user.email")
    experiment_args = "-e \"SURROUND_USER_NAME=%s\" " % user_name
    experiment_args += "-e \"SURROUND_USER_EMAIL=%s\"" % user_email

    experiment_path = os.path.join(str(Path.home()), ".experiments")
    experiment_volume_path = generate_docker_volume_path(experiment_path)

    # Ensure experiments will work if using a local storage location (not in the cloud)
    if os.path.join(experiment_path, "local") == global_config.get_path("experiment.url"):
        experiment_args += " --volume \"%s\":/experiments " % experiment_volume_path
        experiment_args += "-e \"SURROUND_EXPERIMENT_URL=/experiments/local\""
    else:
        current_url = global_config.get_path("experiment.url")
        experiment_args += " -e \"SURROUND_EXPERIMENT_URL=%s\"" % current_url

    cmd = [
        "docker run %s" % experiment_args,
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        "--volume \"%s\":/app/../../repositories" % repo_path,
        IMAGE,
        "python3 -m ds_logging_behaviour --mode batch -a downloader %(args)s"
    ]

    return {
        'basename': 'downloadRepos',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_download_repos_local():
    """Download all the repositories"""
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "--mode batch",
        "-a downloader",
        "%(args)s"
    ]

    return {
        'basename': 'downloadReposLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

# ======================================================================================================================
# Extract logs from repositories
# ======================================================================================================================

def task_extract_logs():
    """Extracts logs from the downloaded repos, run inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"
    repo_path = CONFIG["volume_path"] + "../../repositories"

    global_config = get_surround_config()

    # Inject user's name and email into the env variables of the container
    user_name = global_config.get_path("user.name")
    user_email = global_config.get_path("user.email")
    experiment_args = "-e \"SURROUND_USER_NAME=%s\" " % user_name
    experiment_args += "-e \"SURROUND_USER_EMAIL=%s\"" % user_email

    experiment_path = os.path.join(str(Path.home()), ".experiments")
    experiment_volume_path = generate_docker_volume_path(experiment_path)

    # Ensure experiments will work if using a local storage location (not in the cloud)
    if os.path.join(experiment_path, "local") == global_config.get_path("experiment.url"):
        experiment_args += " --volume \"%s\":/experiments " % experiment_volume_path
        experiment_args += "-e \"SURROUND_EXPERIMENT_URL=/experiments/local\""
    else:
        current_url = global_config.get_path("experiment.url")
        experiment_args += " -e \"SURROUND_EXPERIMENT_URL=%s\"" % current_url

    cmd = [
        "docker run %s" % experiment_args,
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        "--volume \"%s\":/app/../../repositories" % repo_path,
        IMAGE,
        "python3 -m ds_logging_behaviour --mode batch -a extractor %(args)s"
    ]

    return {
        'basename': 'extractLogs',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_extract_logs_local():
    """Extracts logs from the downloaded repos"""
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "--mode batch",
        "-a extractor",
        "%(args)s"
    ]

    return {
        'basename': 'extractLogsLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

# ======================================================================================================================
# Sample extracted logs
# ======================================================================================================================

def task_sample_logs():
    """Sample from extracted logs, run inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    global_config = get_surround_config()

    # Inject user's name and email into the env variables of the container
    user_name = global_config.get_path("user.name")
    user_email = global_config.get_path("user.email")
    experiment_args = "-e \"SURROUND_USER_NAME=%s\" " % user_name
    experiment_args += "-e \"SURROUND_USER_EMAIL=%s\"" % user_email

    experiment_path = os.path.join(str(Path.home()), ".experiments")
    experiment_volume_path = generate_docker_volume_path(experiment_path)

    # Ensure experiments will work if using a local storage location (not in the cloud)
    if os.path.join(experiment_path, "local") == global_config.get_path("experiment.url"):
        experiment_args += " --volume \"%s\":/experiments " % experiment_volume_path
        experiment_args += "-e \"SURROUND_EXPERIMENT_URL=/experiments/local\""
    else:
        current_url = global_config.get_path("experiment.url")
        experiment_args += " -e \"SURROUND_EXPERIMENT_URL=%s\"" % current_url

    cmd = [
        "docker run %s" % experiment_args,
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        IMAGE,
        "python3 -m ds_logging_behaviour --mode batch -a sampler %(args)s"
    ]

    return {
        'basename': 'sampleLogs',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_sample_logs_local():
    """Sample from extracted logs"""
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "--mode batch",
        "-a sampler",
        "%(args)s"
    ]

    return {
        'basename': 'sampleLogsLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

# ======================================================================================================================
# Extract gini calculations
# ======================================================================================================================

def task_gini_local():
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "--mode batch",
        "-a gini",
        "%(args)s"
    ]

    return {
        'basename': 'giniLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_gini():
    """Sample from extracted logs, run inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    global_config = get_surround_config()

    # Inject user's name and email into the env variables of the container
    user_name = global_config.get_path("user.name")
    user_email = global_config.get_path("user.email")
    experiment_args = "-e \"SURROUND_USER_NAME=%s\" " % user_name
    experiment_args += "-e \"SURROUND_USER_EMAIL=%s\"" % user_email

    experiment_path = os.path.join(str(Path.home()), ".experiments")
    experiment_volume_path = generate_docker_volume_path(experiment_path)

    # Ensure experiments will work if using a local storage location (not in the cloud)
    if os.path.join(experiment_path, "local") == global_config.get_path("experiment.url"):
        experiment_args += " --volume \"%s\":/experiments " % experiment_volume_path
        experiment_args += "-e \"SURROUND_EXPERIMENT_URL=/experiments/local\""
    else:
        current_url = global_config.get_path("experiment.url")
        experiment_args += " -e \"SURROUND_EXPERIMENT_URL=%s\"" % current_url

    cmd = [
        "docker run %s" % experiment_args,
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        IMAGE,
        "python3 -m ds_logging_behaviour --mode batch -a gini %(args)s"
    ]

    return {
        'basename': 'gini',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

