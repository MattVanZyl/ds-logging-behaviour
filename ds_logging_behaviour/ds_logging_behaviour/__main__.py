"""
Main entry-point for the Surround project.
Runners and assemblies are defined in here.
"""

import os
import argparse
from surround import Surround, Assembler, has_config
from .stages import RepoDownloader, RepoMetrics, LogExtractor, LogSampler, GiniCalculator
from .file_system_runner import FileSystemRunner

RUNNERS = [
    FileSystemRunner()
]

ASSEMBLIES = [
    Assembler("downloader")
        .set_stages([RepoDownloader()]),
    Assembler("metrics")
        .set_stages([RepoMetrics()]),
    Assembler("extractor")
        .set_stages([LogExtractor()]),
    Assembler("sampler")
        .set_stages([LogSampler()]),
    Assembler("gini")
        .set_stages([GiniCalculator()])
]

@has_config
def main(config=None):
    default_runner = config.get_path('runner.default')
    default_assembler = config.get_path('assembler.default')

    parser = argparse.ArgumentParser(
        prog='ds_logging_behaviour',
        description="Surround mode(s) available to run this module")
    parser.add_argument(
        '-r',
        '--runner',
        help="Runner for the Assembler (index or name)",
        default=default_runner if default_runner is not None else "0")
    parser.add_argument(
        '-a',
        '--assembler',
        help="Assembler to run (index or name)",
        default=default_assembler if default_assembler is not None else "0")
    parser.add_argument(
        '--status',
        help="Display information about the project such as available RUNNERS and assemblers",
        action="store_true")
    parser.add_argument('-n', '--note', help="Add a note to the experiment", type=str)
    parser.add_argument('--mode', help="Mode to run (predict, train, batch)", default="predict")
    args = parser.parse_args()

    surround = Surround(
        RUNNERS,
        ASSEMBLIES,
        "ds_logging_behaviour",
        "",
        os.path.dirname(os.path.dirname(__file__))
    )

    if args.status:
        surround.show_info()
    else:
        surround.run(args.runner, args.assembler, args.mode, args)

if __name__ == "__main__":
    main()
