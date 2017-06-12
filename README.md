# Git-get

Package manager for git repositories. Nothing is ready yet.

## Usage

The basic script is invoked using `python3 git-get.py`. An alias should be
added to your bashrc or zshrc toaccess the program from anywhere. The following
is a non-comprehensive list of commands are available:

### Install

`git-get install octocat/Hello-World`

Github repositories can be installed. The username of the owner and the
repository name should be passed as command line arguments, seperated by a
forward slash. The repository will be download to the directory where called.

### Remove

`git-get remove octocat/Hello-World`

Remove a repository.


### Upgrade

`git-get upgrade`

Run `git-pull` on all packagesin the package list.

### List

`git-get list`

List all packages and install location.
