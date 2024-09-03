# Gitget

Package manager for git repositories.

[![asciicast](https://asciinema.org/a/270298.svg)](https://asciinema.org/a/270298)

## Installation

To install from pypi run:

```sh
pip3 install gitget
```

## Usage

Gitget allows you to manage repositories download from git hosts like github or
gitlab. The repositories are treated like software 'packages', and basic tasks
such as downloading and saving information about repositories, updating
repository, and removing them once they aren't needed anymore. The contents of
the git repositories is not changed; installation scripts are not run and
dependencies are not installed (yet).

### Help

```sh
gitget -h
gitget --help
gitget help <command>
```

Displays a help menu. If the `help` command is used, a help menu for a specific
command is displayed.

### Setup

```sh
gitget setup
```

Creates a `.gitget.yaml` package file in the current directory, where all
the package information is saved.

If you do not manually create a `.gitget.yaml` in the current or a parent
directory before running `gitget install ...`, the default `~/.gitget.yaml`
will be created and used (i.e. in your home directory).

### Configuration

```sh
gitget config list
gitget config get <key>
gitget config set <key> <value>
gitget config unset <key>
```

Creates a `.gitget.yaml` package file in the current directory, where all
the package information is saved.

If you do not manually create a `.gitget.yaml` in the current or a parent
directory before running `gitget install ...`, the default `~/.gitget.yaml`
will be created and used (i.e. in your home directory).

### Install

```sh
gitget install <package>
gitget install <package> <package_name>
```

Downloads a repository from github and saves information about it.
Optionally, a name for the package can be specified. This name will also
be used as the directory name. Otherwise, the package name is set to
`username/repository`.

### Remove

```sh
gitget remove <repository_name>
gitget remove <repository_name> --soft
```

Removes a repository from the package list and also deletes the files locally.
If the `--soft` flag is passed, the local files will not be deleted.

### Track

```sh
gitget track <repository_name>
gitget track *
```

Adds an existing repository to the package list.

### Untrack

```sh
gitget untrack <repository_name>
```

Removes a repository from the package list without deleting the local files.

### Update

```sh
gitget update
```

Runs `git-pull` on all packages in the package list to update them.

### Move

```sh
gitget move <package_name> <location>
```

Moves a package from location to another and updates the information about it.

### Doctor

```sh
gitget doctor
```

Verifies integrity of files and packages. Any errors are then reported
and need to be fixed.

### List

```sh
gitget list
```

Lists all packages and install locations.

### Edit

```sh
gitget edit
```

Opens the default editor (run `echo $EDITOR`) to edit the package file.

## Development

```shell
conda activate py3.10

pip uninstall gitget

python setup.py build
python setup.py install

gitget --version
```
