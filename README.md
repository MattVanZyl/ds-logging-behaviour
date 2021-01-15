# ds_logging_behaviour

## Setup
In a terminal navigate to the `ds-logging-behaviour/ds_logging_behaviour`

Run the following commands:
`pip3 install -r requirements.txt`

## Downloading The Repositories
To download repos:
`surround run downloadRepos`

The repos will be downloaded into `ds-logging-behaviour/repositories`
When the command finishes a `repo-manifest.csv` file will be created in the repository folder providing details about each repository and whether their download was successful or not. 

The `input_file` entry in the `congif.yaml` file specifies which repos need to be downloaded.

## Extracting Data From The Repositories
To extract log data from the repos after they have been downloaded:
`surround run extractData`

The csvs outputed by the `extractData` command will be located in the output folder, they are `repo-metrics.csv` and `log-level.csv` respectively. 
## Troubleshooting
If you get the error: `ERROR: Cannot uninstall 'ruamel-yaml'`
Use the following command:
`pip3 install -r requirements.txt --ignore-installed ruamel.yaml`