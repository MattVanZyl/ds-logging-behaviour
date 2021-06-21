from enum import Enum


class ScopeType(Enum):
    FILE = "file"
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"


class LogLevelType(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    PRINT = "Print"
