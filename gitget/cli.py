#!/usr/bin/env python3

"""Gitget.

Package manager for git repositories.

Usage:
    gitget [options] install (batch <file_name> | <package_url> [<package_name>])
    gitget [options] track <package_path>
    gitget [options] untrack <package_name>
    gitget [options] [--soft] remove <package_name>
    gitget [options] update
    gitget [options] move <package_name> <location>
    gitget [options] rename <package_name> <new_name>
    gitget [options] [--format=<tabulate-format>] [--no-wrap] [--width=<table width>] list
    gitget [options] edit
    gitget [options] doctor
    gitget [options] setup
    gitget [options] config (list | get <key> | set <key> <value> | unset <key>)
    gitget help <command>
    gitget -h | --help
    gitget --version

Options:
    --debug    Increases verbosity of the output
    --nocolor  Logs will not have colors in them
    --git-clone-args=<additional-arguments>
               Additional arguments to pass to git clone commands
    --git-pull-args=<additional-arguments>
               Additional arguments to pass to git pull commands
    --github-auth-token=<auth-token>
               Auth token to use for authenticating with the GitHub API
    --gitlab-auth-token=<auth-token>
               Auth token to use for authenticating with the GitLab API
    --format=<tabluate-format>
               Table format to pass to tabulate (default: mixed_grid)
    --no-wrap  Do not wrap lines in the table
    --width=<table width>
               Width of the table (default: 188)

Examples:
    gitget setup
    gitget config set editor vim
    gitget config set "--git-clone-args" "--recurse-submodules --jobs 8"
    gitget install awesmubarak/git-get
    gitget remove awesmubarak_git-get
    gitget install awesmubarak/git-get
    gitget rename awesmubarak_git-get gitget
    gitget remove gitget
    gitget install awesmubarak/git-get
    gitget move awesmubarak_git-get dev
    gitget remove awesmubarak_git-get
    gitget track dev/my-git-get
    gitget remove dev/my-git-get
    gitget track dev/*
    gitget list
    gitget untrack dev/my-git-get
    gitget --format tsv list
    gitget update

Help:
    For help using this tool, please open an issue on the GitHub repository:
    https://github.com/richard-sim/gitget

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
    elif arguments["track"]:
        commands.track.Track(arguments).run()
    elif arguments["untrack"]:
        commands.untrack.Untrack(arguments).run()
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
