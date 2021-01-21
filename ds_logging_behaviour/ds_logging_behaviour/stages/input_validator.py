"""
This module defines the input validator which is executed
before all other stages in the pipeline and checks whether
the data contained in the State object is valid.
"""

from surround import Stage

class InputValidator(Stage):
    def operate(self, state, config):
        if state.input_data.empty:
            raise ValueError("'input_data' is None")

