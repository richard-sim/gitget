from ._base import Base
from distutils.util import strtobool
from git import Repo
from loguru import logger
import os


class Untrack(Base):
    """Untrack

    Untracks a repository from the package list (does not delete the files
    locally).

    Usage: gitget untrack <package_name> [global options]

    Examples:
        gitget untrack awesmubarak/gitget
    """

    def run(self):
        package_list = self.get_package_list()
        inv_package_list = { package["path"]: package for package_name, package in package_list.items() }
        package_name = self.options["<package_name>"]

        # check if package exists
        logger.debug("Checking if package in package list")
        if not package_name in package_list:
            # The user may have provided the path instead of the name
            package_path = os.path.abspath(package_name)
            if package_path in inv_package_list:
                package_name = inv_package_list[package_path]["name"]
            else:
                logger.error("Package name not in package list")
                exit(1)
        else:
            logger.debug("Package in package list")
        package = package_list[package_name]
        package_location = package["path"]

        # remove package from package list
        logger.debug("Updating package list")
        package_list.pop(package_name, None)
        self.write_package_list(package_list)
        logger.info(f"No longer tracking package {package_name}. Files still exist at: {package_location}")
