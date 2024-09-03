from ._base import Base
from loguru import logger
from os import path
from shutil import move as mmove  # can't be called move, causes issues


class Rename(Base):
    """Rename.

    Renames a package from location to another and updates the information about
    it.

    Usage: gitget [global options] rename <package_name> <new_name>

    Examples:
        gitget rename 'awesmubarak/gitget' ..
    """

    def run(self):
        package_list = self.get_package_list()
        package_name = self.options["<package_name>"]
        new_name = self.options["<new_name>"]

        # verify that the package exists in the package list
        logger.debug("Checking if package in package list")
        if not package_name in package_list:
            logger.error(f"Package name is not valid: {package_name}")
            exit(1)

        # verify that the new name does not exist in the package list
        logger.debug("Checking if new name in package list")
        if new_name in package_list:
            logger.error(f"Package name is not valid: {new_name}")
            exit(1)

        # verify new name
        logger.debug(f"Verifying the new name: {new_name}")
        package = package_list[package_name]
        package_path = package["path"]
        base_location = path.basename(package_path)
        location = path.join(base_location, new_name)
        location = path.abspath(location)
        path_exists = path.exists(location)
        if not path_exists:
            logger.debug("New package name is valid")
        else:
            logger.error(f"New package name is not valid: {new_name}")
            exit(1)

        # move the package to the location
        logger.debug("Attempting to move package")
        try:
            mmove(package_path, location)
            logger.info(f"Moved package to {location}")
        except:
            logger.error(f"Could not move the package from {package_path} to {location}")
            exit(1)

        # update package list
        logger.debug("Updating package list")
        package_list.pop(package_name, None)
        package["name"] = new_name
        package["path"] = location
        package_list[new_name] = package
        self.write_package_list(package_list)
        logger.info("Saved package information")
