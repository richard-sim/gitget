from ._base import Base
from git import Repo
from loguru import logger
from os import path, makedirs
import shlex
from pprint import pformat
import http.client as httplib
from ._updateprogress import UpdateProgress


class Install(Base):
    """Install.

    Downloads a repository from github and saves information about it.
    Optionally, a name for the package can be specified. This name will also
    be used as the directory name. Otherwise, the package name is set to
    `username/repository`.

    Usage: gitget install (batch <file_name> | <package_url> [<package_name>]) [global options] [--git-args=<additional-arguments>]

    Examples:
        gitget install 'https://github.com/awesmubarak/gitget'
        gitget install 'https://github.com/awesmubarak/gitget' 'gitget-download'
        gitget install 'https://github.com/awesmubarak/gitget' --git-args="--recurse-submodules --jobs 8"
        gitget install batch some_packages.txt
        gitget install batch some_packages.txt --git-args="--filter=tree:0 --also-filter-submodules --recurse-submodules --jobs 8"
    """

    def run(self):
        if self.options["batch"]:
            logger.debug("Batch mode")
            
            package_urls = []
            file_name = self.options["<file_name>"]
            with open(file_name, "r") as f:
                for line in f:
                    package_url = line.strip()
                    package_urls.append(package_url)

            num_packages = len(package_urls)
            packages_installed = 0
            failed_packages = []
            while len(package_urls) > 0:
                package_line = package_urls.pop(0)
                package_name = None
                if "=" in package_line:
                    package_name, package_url = package_line.split("=")
                else:
                    package_url = package_line

                logger.info(f"Batch install: Installing package {package_url} [{packages_installed+len(failed_packages)+1}/{num_packages}]")
                if self.install_package(package_url, package_name):
                    packages_installed = packages_installed + 1
                else:
                    logger.error(f"Batch install: Failed to install package {packages_installed+len(failed_packages)+1} ({package_url})")
                    failed_packages.append(package_line)

                with open(f"{file_name}.remaining", "w") as f:
                    f.write('\n'.join(package_urls) + '\n')
            with open(f"{file_name}.failed", "w") as f:
                f.write('\n'.join(failed_packages) + '\n')
            if len(failed_packages) > 0:
                logger.error(f"Failed to install {len(failed_packages)} packages (see {file_name}.failed). {packages_installed} packages installed successfully")
                exit(1)
            else:
                logger.info(f"{packages_installed} packages installed successfully")
        else:
            package_url = self.options["<package_url>"]
            package_name = self.options["<package_name>"]
            
            if not self.install_package(package_url, package_name):
                exit(1)

    def install_package(self, package_url, package_name=None):
        # sort out package name
        logger.debug("Deciding on package name")
        if package_name is not None:
            # use argument
            logger.debug(f"Using the provided name: {package_name}")
        else:
            # use the last part(s) of the url
            package_name = Base.generate_name_from_url(package_url, include_owner=True, owner_first=True)
            logger.debug(f"Using the URL to generate a name: {package_name}")

        # check if the package is in the package list already
        logger.debug("Checking if the package name already exists")
        package_list = self.get_package_list()
        if package_name in package_list:
            logger.error(f"Package name {package_name} already exists")
            return False

        # figure out the package location
        logger.debug("Deciding package location")
        package_location = path.abspath(package_name)

        # check if directory already exists
        logger.debug("Checking if the directory name already exists")
        if path.isdir(package_location):
            logger.error(f"Directory already exists: {package_location}")
            return False

        logger.info(f"Package {package_name} ({package_location})")

        # make any required parent directories
        parent_dir = path.dirname(package_location)
        logger.debug(f"Creating parent directories: {parent_dir}")
        if not path.exists(parent_dir):
            makedirs(parent_dir)
        elif not path.isdir(parent_dir):
            logger.error(f"Path already exists but isn't a directory: {parent_dir}")
            return False

        # check if the repository can be reached
        logger.debug("Checking if repository can be reached")
        trimmed_package_url = package_url.replace("https://", "").replace("http://", "")
        trimmed_package_url = trimmed_package_url.split("/")[0]
        connection = httplib.HTTPConnection(trimmed_package_url, timeout=5)
        try:
            connection.request("HEAD", "/")
            connection.close()
            logger.debug("Connection made succesfully")
        except:
            connection.close()
            logger.exception(
                "Could not connect to the URL, check the URL and your internet"
            )
            return False

        git_args = {}
        if self.options["--git-args"] is not None:
            args = shlex.split(self.options["--git-args"])
            for i, arg in enumerate(args):
                if arg.startswith("-"):
                    if arg.startswith("--"):
                        arg = arg[2:]
                    elif arg.startswith("-"):
                        arg = arg[1:]
                    if "=" in arg:
                        # --foo=bar
                        git_arg = arg.split("=")
                        git_args[git_arg[0]] = git_arg[1]
                    else:
                        if i+1 < len(args) and not args[i+1].startswith("-"):
                            # --foo bar
                            git_args[arg] = args[i+1]
                        else:
                            # --foo
                            git_args[arg] = True
                else:
                    # item is a parameter to the previous argument, not an argument itself
                    pass
            logger.debug(f"Git arguments: {pformat(git_args)}")

        # clone repository
        logger.info(f"Cloning repository {package_name}")
        try:
            Repo.clone_from(package_url, package_location, progress=UpdateProgress(), **git_args)
        except:
            logger.exception("Could not clone the repository")
            return False
        UpdateProgress.clear_line()
        logger.debug("Clone successful")

        # add package to package list
        logger.debug("Adding package to package list")
        package_list[package_name] = package_location
        self.write_package_list(package_list)
        logger.info("Saved package information")
        
        return True
