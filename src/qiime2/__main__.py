# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

import rachis_cli.commands


ROOT_COMMAND_HELP = """\
QIIME 2 command-line interface (via rachis-cli)
-----------------------------------------------

To get help with QIIME 2, visit https://qiime2.org.

Tab completion is enabled automatically when this environment is \
activated. To enable it in the current shell, run:

    source tab-rachis

"""


# Entry point for CLI
@click.command(cls=rachis_cli.commands.RootCommand,
               invoke_without_command=True,
               no_args_is_help=True, help=ROOT_COMMAND_HELP)
@click.version_option(prog_name='rachis-cli',
                      message='%(prog)s version %(version)s\nRun `qiime info` '
                              'for more version details.')
def qiime():
    pass


if __name__ == '__main__':
    qiime()
