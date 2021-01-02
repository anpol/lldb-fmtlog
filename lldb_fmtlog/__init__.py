#!/usr/bin/env python
"""LLDB Commands for manipulating formatters logging facility."""

import lldb

from . import commands


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    commands.lldb_init_submodule(debugger)
