from surround import Stage
from ..print_colours import PrintColours
import logging

class RepoMetrics(Stage):

    def operate(self, state, config):
        logging.info(
            f"\n{PrintColours.CYAN}{PrintColours.BOLD}---------------------------------\nGetting Metrics From Repositories\n---------------------------------{PrintColours.RESET}")
        logging.info("Work Work")