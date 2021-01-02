#!/usr/bin/env python
"""Helpers for manipulating LLDB formatters logging facility."""

from enum import Enum
from pathlib import Path

from lldb.formatters import Logger as LoggerModule


class LoggingLevel(Enum):
    """A enumeration of valid logging levels."""
    NONE = 0
    FAST = 1
    AUTO_FLUSH = 2
    CALLER_INFO = 3

    @staticmethod
    def get() -> 'LoggingLevel':
        level: int = getattr(LoggerModule, '_lldb_formatters_debug_level', 0)
        return LoggingLevel(level)

    @staticmethod
    def set(new_value: 'LoggingLevel') -> None:
        # pylint: disable=protected-access
        LoggerModule._lldb_formatters_debug_level = new_value.value


class LoggingOutput:
    """A helper for manipulating logging output file path."""
    @staticmethod
    def get() -> Path:
        output: str = getattr(LoggerModule, '_lldb_formatters_debug_filename',
                              'formatters.log')
        return Path(output)

    @staticmethod
    def set(new_value: Path) -> None:
        # pylint: disable=protected-access
        LoggerModule._lldb_formatters_debug_filename = str(
            new_value.expanduser().resolve())
