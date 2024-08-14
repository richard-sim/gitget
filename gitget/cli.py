#!/usr/bin/env python3

"""Gitget.

Package manager for git repositories.

Usage:
    gitget [options] install (batch <file_name> | <package_url> [<package_name>])
    gitget [options] import <package_path>
    gitget [options] remove <package_name>
    gitget [options] update
    gitget [options] move <package_name> <location>
    gitget [options] rename <package_name> <new_name>
    gitget [options] list
    gitget [options] edit
    gitget [options] doctor
    gitget [options] setup
    gitget [options] config (list | get <key> | set <key> <value> | unset <key>)
    gitget help <command>
    gitget -h | --help
    gitget --version

Global options:
    --debug    Increases verbosity of the output
    --nocolor  Logs will not have colors in them
    --git-args=<additional-arguments>
               Additional arguments to pass to git commands
    --soft     Do not delete the package files when removing a package

Examples:
    gitget setup
    gitget config set editor vim
    gitget config set "--git-args" "--recurse-submodules --jobs 8"
    gitget install awesmubarak/git-get
    gitget remove awesmubarak_git-get
    gitget install awesmubarak/git-get
    gitget rename awesmubarak_git-get gitget
    gitget remove gitget
    gitget install awesmubarak/git-get
    gitget move awesmubarak_git-get dev
    gitget remove awesmubarak_git-get
    gitget import dev/my-git-get
    gitget remove dev/my-git-get
    gitget import dev/*
    gitget update

Help:
    For help using this tool, please open an issue on the Github repository:
    https://github.com/awesmubarak/gitget

"""

from . import commands
from .version import __version__
from docopt import docopt
from inspect import getmembers, isclass
from loguru import logger
from sys import stderr


def setup_logging(debug_level, colorize):
    """Sets up the format for logging, based on the debug level (info/dbug)."""
    logger.remove()

    if debug_level == "info":
        logger_format = "<green>{time:HH:mm:ss}</green> <level>{message}</level>"
        logger.add(
            stderr,
            colorize=colorize,
            format=logger_format,
            level="INFO",
            backtrace=False,
            diagnose=False,
        )
    else:
        logger_format = "<green>{time:HH:mm:ss}</green> {file: <12} <level>{level: <8} {message}</level>"
        logger.add(
            stderr,
            colorize=colorize,
            format=logger_format,
            level="DEBUG",
            backtrace=True,
            diagnose=True,
        )
    logger.debug("Set up logging")


def main():
    # setup the argument parser with the docstring and imported version number
    arguments = docopt(__doc__, version=f"Gitget {__version__}", options_first=True)

    # set up the logger
    debug_level = "debug" if arguments["--debug"] else "info"
    colorize = False if arguments["--nocolor"] else True
    setup_logging(debug_level, colorize)

    # call the right command, based on the argument
    logger.debug("Calling the function based on the command sent")
    if arguments["doctor"]:
        commands.doctor.Doctor(arguments).run()
    elif arguments["config"]:
        commands.config.Config(arguments).run()
    elif arguments["edit"]:
        commands.edit.Edit(arguments).run()
    elif arguments["install"]:
        commands.install.Install(arguments).run()
    elif arguments["import"]:
        commands.importCmd.Import(arguments).run()
    elif arguments["list"]:
        commands.list.List(arguments).run()
    elif arguments["move"]:
        commands.move.Move(arguments).run()
    elif arguments["remove"]:
        commands.remove.Remove(arguments).run()
    elif arguments["setup"]:
        commands.setup.Setup(arguments).run()
    elif arguments["update"]:
        commands.update.Update(arguments).run()
    elif arguments["help"]:
        commands.help.Help(arguments).run()


if __name__ == "__main__":
    main()
