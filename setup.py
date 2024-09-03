#!/usr/bin/env python3

from setuptools import setup
from os import path
from gitget.version import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="gitget",
    version=__version__,
    description="A package manager for git repositories.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/richard-sim/gitget",
    author="Richard Sim, Awes Mubarak",
    author_email="richard-sim@users.noreply.github.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Version Control :: Git",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    keywords="git github gitlab package manager packages package-manager packman repo repository repository-manager clone pull manage update doctor install import move remove rename track untrack list edit setup",
    packages=["gitget", "gitget.commands"],
    entry_points={"console_scripts": ["gitget=gitget:main"]},
    install_requires=["docopt", "loguru", "gitpython", "pygithub", "python-gitlab", "pyyaml", "tabulate", "semver"],
)
