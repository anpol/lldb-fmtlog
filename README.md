<!-- vim:spell -->

# lldb-fmtlog

LLDB Commands for manipulating formatters logging facility.

## Installation

This repository is meant to be a submodule of
[lldb-bundle](//github.com/anpol/lldb-bundle), look there for installation instructions.

You also have an option to clone this repository and add the following line
into your `~/.lldbinit` file:
```
command script import <path-to-repository>/lldb_fmtlog
```

## Formatters Logging Facility

LLDB custom type formatters normally use logging, as demonstrated in the
following example:
```python
logger = lldb.formatters.Logger.Logger()
logger.write('something interesting')
```

By default, such logging messages are discarded.

If you are either developing an LLDB formatter for a type, or analyzing a
behavior of an existing formatter, you may find it helpful to quickly enable
logging output with a provided command.

## Commands

```sh
help fmtlog
```
Display a list of subcommands.

```sh
fmtlog enable [-h] [-l <level>] [-o <file>]
```
Enable formatters logging at the specified `level`, and write logging messages
to the specified `file`.

Possible `level` values are:

- `fast`: use buffered logging.
- `auto-flush`: use unbuffered logging; slow but more reliable.
- `caller-info`: use unbuffered logging, and output a name of a caller function.

```sh
fmtlog disable [-h]
```
Disable formatters logging.

```sh
fmtlog state [-h]
```
Display the state of the logging facility.


## Contributing

Feel free to file an issue, or send a pull request.

Before making your changes, you need to establish a development environment.
As this repository is meant to be a submodule of
[lldb-bundle](//github.com/anpol/lldb-bundle), look there for creating the
Python virtual environment suitable for developing with LLDB.

Once you activated the virtual environment, run:
```sh
make init
```
to install the required development tools.

Use your editor or IDE to make your changes.  Add relevant tests.  To prepare
for a submission, run:
```sh
make format
make lint
make test
```

Fix lint issues and test failures.

Repeat until everything is OK, then open a pull request.

Thanks!
