## Running In A Container
In a terminal navigate to the `ds-logging-behaviour/ds_logging_behaviour`

Run the following commands:
`surround run build`

Download and extract data from repos:
`surround run downloadAndExtract`

The csvs outputed by the extractor will be located in the output folder, they are `repo-metrics.csv` and `log-level.csv` respectively. 

## Running Locally 

### Setup
In a terminal navigate to the `ds-logging-behaviour/ds_logging_behaviour`

Run the following commands:
`pip3 install -r requirements.txt`

### Downloading The Repositories
To download repos:
`surround run downloadRepos`

The repos will be downloaded into `ds-logging-behaviour/repositories`
When the command finishes a `repo-manifest.csv` file will be created in the repository folder providing details about each repository and whether their download was successful or not. 

The `input_file` entry in the `congif.yaml` file specifies which repos need to be downloaded.

### Extracting Data From The Repositories
To extract log data from the repos after they have been downloaded:
`surround run extractData`