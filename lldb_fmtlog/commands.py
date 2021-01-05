#!/usr/bin/env python
"""Argument parser for a command."""

import argparse
import collections
import pathlib
from gettext import gettext as _
from typing import Type, Optional, Dict

import lldb

from lldb_script_utils import lldb_commands
from lldb_script_utils import debugger_utils
from lldb_fmtlog.core import LoggingLevel, LoggingOutput


def _lowercase_hyphenated(name: str) -> str:
    return name.lower().replace('_', '-')


def _uppercase_underscored(name: str) -> str:
    return name.upper().replace('-', '_')


LOGGING_LEVELS: Dict[str, int] = collections.OrderedDict(
    (_lowercase_hyphenated(x.name), x.value) for x in LoggingLevel)

POSITIVE_LOGGING_LEVEL_NAMES = [
    name for name, value in LOGGING_LEVELS.items() if value > 0
]


def _logging_level(str_value: str) -> int:
    int_value = LOGGING_LEVELS.get(str_value.lower())
    return int_value if int_value else int(str_value)


def _logging_level_str(int_value: int) -> str:
    for name, value in LOGGING_LEVELS.items():
        if value == int_value:
            return name
    return str(int_value)


def lldb_init_submodule(debugger: lldb.SBDebugger) -> None:
    FormattersLoggerCommand.lldb_init_class(debugger)


class FormattersLoggerCommand(lldb_commands.LLDBCommand):
    """Argument parser for the `fmtlog` command with subcommands."""
    NAME = 'fmtlog'
    HELP = _('Commands for manipulating formatters logging facility.')

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger_utils.handle_command_script_add(debugger, cls.NAME, cls)

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> lldb_commands.LLDBArgumentParser:
        parser = lldb_commands.LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_subcommands(
            (self.EnableSubcommand, self._on_enable),
            (self.DisableSubcommand, self._on_disable),
            (self.StateSubcommand, self._on_state),
        )
        return parser

    class EnableSubcommand(lldb_commands.LLDBSubcommand):
        """Argument parser for the `fmtlog enable` subcommand."""
        NAME = 'enable'
        HELP = _('Enable logging.')

        @classmethod
        def create_args_subparser(
            cls, add_subparser: Type[argparse.ArgumentParser]
        ) -> argparse.ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            subparser.add_argument(
                '-l',
                '--level',
                metavar=_('<level>'),
                choices=POSITIVE_LOGGING_LEVEL_NAMES,
                help=_('Logging level. Values: {}').format(
                    ' | '.join(POSITIVE_LOGGING_LEVEL_NAMES)))
            subparser.add_argument('-o',
                                   '--output',
                                   metavar=_('<file>'),
                                   type=pathlib.Path,
                                   help=_('Output file path.'))
            return subparser

    @staticmethod
    def _on_enable(level: Optional[str], output: Optional[pathlib.Path], **_):
        if level is not None:
            LoggingLevel.set(LoggingLevel[_uppercase_underscored(level)])
        elif LoggingLevel.get() == LoggingLevel.NONE:
            LoggingLevel.set(LoggingLevel.FAST)

        if output is not None:
            LoggingOutput.set(None if str(output) == '-' else output)

    class DisableSubcommand(lldb_commands.LLDBSubcommand):
        """Argument parser for the `fmtlog disable` subcommand."""
        NAME = 'disable'
        HELP = _('Disable logging.')

        @classmethod
        def create_args_subparser(
            cls, add_subparser: Type[argparse.ArgumentParser]
        ) -> argparse.ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    @staticmethod
    def _on_disable(**_):
        LoggingLevel.set(LoggingLevel.NONE)

    class StateSubcommand(lldb_commands.LLDBSubcommand):
        """Argument parser for the `fmtlog state` subcommand."""
        NAME = 'state'
        HELP = _('Show the state of the logging facility.')

        @classmethod
        def create_args_subparser(
            cls, add_subparser: Type[argparse.ArgumentParser]
        ) -> argparse.ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    @staticmethod
    def _on_state(command_return: lldb.SBCommandReturnObject, **_):
        level = LoggingLevel.get()
        output = LoggingOutput.get()
        print(f'''
level:  {_lowercase_hyphenated(level.name)}
output: {'-' if output is None else output.resolve()}
'''[1:],
              file=command_return,
              end='')
