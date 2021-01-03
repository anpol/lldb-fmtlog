#!/usr/bin/env python
"""Helpers for manipulating LLDB formatters logging facility."""

from enum import Enum
from pathlib import Path
from typing import Optional

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
    def get() -> Optional[Path]:
        output: Optional[str] = getattr(LoggerModule,
                                        '_lldb_formatters_debug_filename',
                                        None)
        if not output:
            return None
        return Path(output)

    @staticmethod
    def set(new_value: Optional[Path]) -> None:
        # pylint: disable=protected-access
        if new_value is None:
            LoggerModule._lldb_formatters_debug_filename = None
        else:
            resolved_path = new_value.expanduser().resolve()
            LoggerModule._lldb_formatters_debug_filename = str(resolved_path)
