## Requirements

- Docker
- Python 3

## Setup
Install Surround:
`pip install surround==0.1.0`
`pip install surround_cli==0.0.3`

## Running In A Container
In a terminal, navigate to `ds-logging-behaviour/ds_logging_behaviour`

Run the following command to build an image for the container:
`surround run build`

### Download Repos
Download the repos:
`surround run downloadRepos`

The repos will be downloaded into a `repositories` folder at the root of the project. 
When the command finishes a `repo-manifest.csv` file will be created in the repository folder providing details about each repository and whether their download was successful or not.

### Repo Metrics
To extract metrics of the repos after they have been downloaded:
`surround run repoMetrics`

A `output/repo-metrics.csv` file will be outputted after the metrics extraction is completed.

### Extract Logs
To extract log data from the repos after they have been downloaded:
`surround run extractLogs`

A `output/repo-logs.csv` file will be outputted after the log extraction is completed.

### Sample Logs
Once the logs have been extracted from the repos, a sample of a given size specified in the `config.yaml` file can be taken.
`surround run sampleLogs`

A `output/repo-logs-sample.csv` file will be outputted with the sample.

## Additional Information
### Config
The `ds_logging_behaviour/config.yaml` file defines the relative locations of all the files, folders and configurable variables used in this project.

### Semgrep Rules
There are two config files that house the semgrep rules used when determining the repo metrics and extracting the log data, these are located in `input/semgrep/repo_metrics.yaml` and `input/semgrep/log_levels.yaml` respectively.

### Repo List
The `input/repositories_data.csv` provides the details of the repositories used in this project.

### Generated Outputs
All generated output files such as those created when extracting repo metrics or logging levels are placed within the `output` folder.