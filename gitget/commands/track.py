from ._base import Base
from loguru import logger
from os import path
from glob import glob

class Track(Base):
    """Track.

    Tracks an exsiting package so it can be managed by gitget.

    Usage: gitget [global options] track <package_path>

    Examples:
        gitget track 'dev/git-get'
    """

    def run(self):
        package_list = self.get_package_list()
        inv_package_list = { package["path"]: package for package_name, package in package_list.items() }
        package_path = self.options["<package_path>"]

        # verify the package path
        logger.debug("Verifying package")
        package_path = path.abspath(package_path)
        path_exists = path.exists(package_path)
        path_is_dir = path.isdir(package_path)
        if path_exists and path_is_dir:
            logger.debug("Package path is valid")
            package_paths = [package_path]
        else:
            matching_paths = glob(package_path)
            if not matching_paths:
                logger.error(f"Package path '{package_path}' is not valid")
                exit(1)
            matching_paths = [path.abspath(p) for p in matching_paths]
            package_paths = [p for p in matching_paths if path.exists(p) and path.isdir(p)]
            if not package_paths:
                logger.error(f"No packages found matching '{package_path}'")
                exit(1)

        modified = False
        for package_path in package_paths:
            package_name = path.basename(package_path)
            # verify that the package doesn't already exist in the package list
            logger.debug("Checking if {package_name} ({package_path}) exists in package list")
            if package_name in package_list:
                existing_path = package_list[package_name]["path"]
                logger.warning(f"Package {package_name} ({package_path}) already exists: ({existing_path})")
                continue
            if package_path in inv_package_list:
                existing_name = inv_package_list[package_path]["name"]
                logger.warning(f"Package {package_name} ({package_path}) already exists as: ({existing_name})")
                continue
            package = self.get_package_for_path(package_name, package_path)
            package_list[package_name] = package
            inv_package_list[package_path] = package
            modified = True
            logger.info(f"Tracked package {package_name} ({package_path})")

        # update package list
        if modified:
            logger.debug("Updating package list")
            self.write_package_list(package_list)
            logger.info("Saved package information")
        else:
            logger.warning("No new packages were tracked")
