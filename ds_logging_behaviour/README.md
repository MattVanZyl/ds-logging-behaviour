## Requirements

- Docker
- Python 3

## Setup
Install Surround:
`pip install surround==0.1.0`
`pip install surround_cli==0.0.3`

## Running In A Container
In a terminal navigate to the `ds-logging-behaviour/ds_logging_behaviour`

Run the following command to build an image for the container:
`surround run build`

### Download Repos
Download the repos:
`surround run downloadRepos`

The repos will be downloaded into `output/repositories`
When the command finishes a `repo-manifest.csv` file will be created in the repository folder providing details about each repository and whether their download was successful or not. 

The `input_file` entry in the `congif.yaml` file specifies which repos need to be downloaded.

### Extract Data
To extract log data from the repos after they have been downloaded:
`surround run extractData`

The csvs outputed by the extractor will be located in the output folder, they are `repo-metrics.csv` and `log-level.csv` respectively. 

## Running Locally 
In a terminal navigate to the `ds-logging-behaviour/ds_logging_behaviour`

Run the following commands:
`pip3 install -r requirements.txt`

### Download Repos
To download repos:
`surround run downloadReposLocal`

### Extract Data
To extract log data from the repos after they have been downloaded:
`surround run extractDataLocal`