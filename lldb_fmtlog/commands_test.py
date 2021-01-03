#!/usr/bin/env python
"""Tests for arguments parsing for commands and subcommands."""

import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import lldb

from lldb_fmtlog.commands import FormattersLoggerCommand
from lldb_fmtlog.core import LoggingLevel, LoggingOutput
from lldb_fmtlog.core_test import LoggerModuleTest

TEST_PACKAGE = f'{__package__}.commands_test'


def _create_debugger_for_testing() -> lldb.SBDebugger:
    debugger = lldb.SBDebugger.Create()
    # debugger.SetOutputFile(io.StringIO())  # Ignore output
    debugger.HandleCommand(f'command script import {TEST_PACKAGE}')
    return debugger


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    FormattersLoggerCommand.lldb_init_class(debugger)


class FormattersLoggerCommandTest(LoggerModuleTest):
    def setUp(self) -> None:
        self.debugger = _create_debugger_for_testing()
        self.output_file = io.StringIO()
        self.debugger.SetOutputFile(self.output_file)
        self.error_file = io.StringIO()
        self.debugger.SetErrorFile(self.error_file)

    @property
    def combined_output(self):
        result = []

        def _append_prefixed_value(prefix, value: str):
            nonlocal result
            if value:
                result += [prefix, value]

        _append_prefixed_value('stdout:', self.output_file.getvalue())
        _append_prefixed_value('stderr:', self.error_file.getvalue())
        return '\n'.join(result)

    def test_fmtlog_help(self):
        self.debugger.HandleCommand('help fmtlog')
        self.assertEqual(
            '''stdout:
     Commands for manipulating formatters logging facility.  Expects 'raw'
     input (see 'help raw-input'.)

Syntax: fmtlog
 usage: fmtlog <subcommand> ...

The following subcommands are supported:
  <subcommand>
    enable      Enable logging.
    disable     Disable logging.
    state       Show the state of the logging facility.

For more help on any particular subcommand, type 'fmtlog <subcommand> --help'.
''', self.combined_output)

    def test_fmtlog_bad_subcommand(self):
        self.debugger.HandleCommand('fmtlog bad-subcommand')
        self.assertEqual(
            '''stderr:
usage: fmtlog <subcommand> ...
fmtlog: error: argument <subcommand>: invalid choice: 'bad-subcommand' \
(choose from 'enable', 'disable', 'state')
''', self.combined_output)

    def test_fmtlog_bad_option(self):
        self.debugger.HandleCommand('fmtlog --bad-option')
        self.assertEqual(
            '''stderr:
usage: fmtlog <subcommand> ...
fmtlog: error: unrecognized arguments: --bad-option
''', self.combined_output)

    def test_fmtlog_enable_help(self):
        self.debugger.HandleCommand('fmtlog enable --help')
        self.assertEqual(
            '''stdout:
usage: fmtlog enable [-h] [-l <level>] [-o <file>]

Enable logging.

Optional arguments:
  -h, --help            Show this help message and exit.
  -l <level>, --level <level>
                        Logging level. Values: fast | auto-flush | caller-info
  -o <file>, --output <file>
                        Output file path.
''', self.combined_output)

    def test_fmtlog_enable(self):
        self.debugger.HandleCommand('fmtlog enable')
        self.assertEqual(LoggingLevel.FAST, LoggingLevel.get())
        self.assertIsNone(LoggingOutput.get())

    def test_fmtlog_enable_with_level(self):
        self.debugger.HandleCommand('fmtlog enable --level auto-flush')
        self.assertEqual(LoggingLevel.AUTO_FLUSH, LoggingLevel.get())

        self.debugger.HandleCommand('fmtlog enable')
        self.assertEqual(LoggingLevel.AUTO_FLUSH, LoggingLevel.get())

        self.debugger.HandleCommand('fmtlog enable --level caller-info')
        self.assertEqual(LoggingLevel.CALLER_INFO, LoggingLevel.get())

        self.debugger.HandleCommand('fmtlog enable')
        self.assertEqual(LoggingLevel.CALLER_INFO, LoggingLevel.get())
        self.assertIsNone(LoggingOutput.get())

    def test_fmtlog_enable_with_empty_level(self):
        self.debugger.HandleCommand('fmtlog enable --level')
        self.assertEqual(
            '''stderr:
usage: fmtlog enable [-h] [-l <level>] [-o <file>]
fmtlog enable: error: argument -l/--level: expected one argument
''', self.combined_output)

    def test_fmtlog_enable_with_bad_level(self):
        self.debugger.HandleCommand('fmtlog enable --level none')
        self.assertEqual(
            '''stderr:
usage: fmtlog enable [-h] [-l <level>] [-o <file>]
fmtlog enable: error: argument -l/--level: invalid choice: 'none' \
(choose from 'fast', 'auto-flush', 'caller-info')
''', self.combined_output)

    def test_fmtlog_enable_with_output(self):
        for output_name in ('foo', '../bar', '~/baz'):
            output = Path(output_name)
            self.debugger.HandleCommand(f'fmtlog enable --output {output}')
            self.assertEqual(LoggingLevel.FAST, LoggingLevel.get())
            output = output.expanduser().resolve()
            self.assertEqual(output, LoggingOutput.get())

    def test_fmtlog_disable_help(self):
        self.debugger.HandleCommand('fmtlog disable --help')
        self.assertEqual(
            '''stdout:
usage: fmtlog disable [-h]

Disable logging.

Optional arguments:
  -h, --help  Show this help message and exit.
''', self.combined_output)

    def test_fmtlog_disable(self):
        LoggingLevel.set(LoggingLevel.FAST)
        self.debugger.HandleCommand('fmtlog disable')
        self.assertEqual(LoggingLevel.NONE, LoggingLevel.get())
        self.assertIsNone(LoggingOutput.get())

    def test_fmtlog_state_help(self):
        self.debugger.HandleCommand('fmtlog state --help')
        self.assertEqual(
            '''stdout:
usage: fmtlog state [-h]

Show the state of the logging facility.

Optional arguments:
  -h, --help  Show this help message and exit.
''', self.combined_output)

    def test_fmtlog_state(self):
        self.debugger.HandleCommand('fmtlog state')
        self.assertEqual('''stdout:
level:  none
output: -
''', self.combined_output)

    def test_fmtlog_state_modified(self):
        output = Path('foo')
        LoggingLevel.set(LoggingLevel.AUTO_FLUSH)
        LoggingOutput.set(output)

        self.debugger.HandleCommand('fmtlog state')
        self.assertEqual(
            f'''stdout:
level:  auto-flush
output: {output.resolve()}
''', self.combined_output)

    def eval_script(self, script: str) -> None:
        self.debugger.HandleCommand(f'script {script}')

    def test_fmtlog_output_to_file_auto_flush(self):
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir).joinpath('formatters.log')
            self.debugger.HandleCommand(
                f'fmtlog enable --level=auto-flush --output={output}')
            self.eval_script('logger = lldb.formatters.Logger.Logger()')
            self.eval_script('logger.write("something logged")')
            self.assertEqual('something logged\n', output.read_text())
            self.assertEqual('', self.combined_output)


if __name__ == '__main__':
    unittest.main()
