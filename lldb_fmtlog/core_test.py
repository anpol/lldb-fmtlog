#!/usr/bin/env python
"""Tests for the core module."""

import unittest
from pathlib import Path

from lldb_fmtlog.core import LoggingLevel, LoggingOutput
from lldb.formatters import Logger as LoggerModule


def _clean_logger_globals():
    if hasattr(LoggerModule, '_lldb_formatters_debug_level'):
        delattr(LoggerModule, '_lldb_formatters_debug_level')
    if hasattr(LoggerModule, '_lldb_formatters_debug_filename'):
        delattr(LoggerModule, '_lldb_formatters_debug_filename')


class LoggerModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        _clean_logger_globals()

    def tearDown(self) -> None:
        _clean_logger_globals()


class LoggingLevelTest(LoggerModuleTest):
    def test_get(self):
        self.assertEqual(LoggingLevel.NONE, LoggingLevel.get())

    def test_set(self):
        for level in LoggingLevel:
            LoggingLevel.set(level)
            self.assertEqual(level, LoggingLevel.get())


class LoggingOutputTest(LoggerModuleTest):
    def test_get(self):
        self.assertIsNone(LoggingOutput.get())

    def test_set(self):
        for output_name in ('foo', '../bar', '~/baz'):
            output = Path(output_name)
            LoggingOutput.set(output)
            output = output.expanduser().resolve()
            self.assertEqual(output, LoggingOutput.get())
        LoggingOutput.set(None)
        self.assertIsNone(LoggingOutput.get())


if __name__ == '__main__':
    unittest.main()
