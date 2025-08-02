"""enums.py

Log level enumeration used across the advanced logging system.
Keeping the enum in its own module follows the Single-Responsibility
principle and allows it to be reused by other packages without creating
cyclic dependencies.
"""

from enum import Enum


class LogLevel(str, Enum):
    """Enumeration for supported log levels.

    Extends ``str`` and ``Enum`` so that values are both comparable as
    strings (useful when parsing environment variables) and as enum
    members (type safety / auto-completion).
    """

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
