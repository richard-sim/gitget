from ._base import Base
from loguru import logger
from os import getcwd
import shlex
from pprint import pformat
import git
from ._updateprogress import UpdateProgress


class Update(Base):
    """Update.

    Runs `git-pull` on all packages in the package list to update them.

    Usage: gitget [global options] [--git-pull-args=<additional-arguments>] update

    Examples:
        gitget update
    """

    def run(self):
        package_list = self.get_package_list()
        number_of_packages = len(package_list)

        logger.debug("Making sure there are some packages to update")
        if number_of_packages == 0:
            logger.info("No packages to update")
            exit(0)

        git_args = {}
        if self.options["--git-pull-args"] is not None:
            args = shlex.split(self.options["--git-pull-args"])
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

        logger.debug("Going through each package")
        packages_succeeded = 0
        packages_failed = 0
        for package_number, package_name in enumerate(package_list):
            package = package_list[package_name]
            package_path = package["path"]

            progress = f"[{package_number+1}/{number_of_packages}]"
            logger.info(f"Updating {package_name}  {progress}")

            try:
                package = self.get_package_for_path(package_name, package_path)
                package_list[package_name] = package

                repo = git.Repo(package_path)
                origins = repo.remotes.origin
                origins.pull(progress=UpdateProgress(), **git_args)
                packages_succeeded += 1
                logger.debug("Package updated successfully")
            except Exception:
                packages_failed += 1
                logger.exception(f"Package {package_name} could not be updated")
        logger.info(f"{packages_succeeded}/{number_of_packages} packages updated, {packages_failed} failed.")
        self.write_package_list(package_list)
