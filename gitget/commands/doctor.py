from ._base import Base
from importlib import import_module


class Doctor(Base):
    """Doctor.

    Verifies integrity of files and packages. Any errors are then reported
    and need to be fixed.

    Usage: gitget [global options] doctor

    Examples:
        gitget doctor
    """

    def run(self):
        # Core modules required in this script
        try:
            from loguru import logger
            from yaml import safe_load
            from os import path
        except ModuleNotFoundError as ex:
            logger.error(f"Could not import one or more modules: {ex}")
            exit(1)

        # Modules required elsewhere (provides more details when failing)
        failed_modules = []
        for module in ("docopt", "git", "yaml", "tabulate"):
            try:
                import_module(module)
            except ModuleNotFoundError as ex:
                failed_modules.append(str(ex)[17:-1])
        if failed_modules:
            failed_modules_str = ", ".join(failed_modules)
            logger.error(
                f"Could not import the following modules: {failed_modules_str}"
            )

        # Check if package file exists
        logger.debug("Checking if package file exists")
        package_list_path = Base.get_package_list_filepath()
        package_list_file_valid = Base.check_package_list_file(package_list_path)
        if package_list_file_valid == 1:
            logger.error("Package file missing, please run `gitget setup`")
            exit(1)
        elif package_list_file_valid == 2:
            logger.error(
                f"Package file is a directory, please remove `{package_list_path}` and run `gitget setup`"
            )
            exit(1)
        elif package_list_file_valid == 0:
            logger.info(f"Package file found: {package_list_path}")

        # Verify that the file is valid yaml
        logger.debug("Verifying that the package file is valid yaml")
        try:
            with open(package_list_path) as file:
                package_list = safe_load(file)
            logger.info("Package file is valid yaml")
        except ValueError as e:
            logger.error("Package file is invalid yaml:")
            logger.error(e)
            exit(1)
        except Exception as e:
            logger.error("Could not load package file:")
            logger.error(e)
            exit(1)

        # Check if all packages exist
        logger.debug("Checking each package")
        package_list = self.get_package_list()
        invalid_packages = 0
        for package_name in package_list:
            package = package_list[package_name]
            package_path = package["path"]
            package_path_exists = path.exists(package_path)
            package_path_is_dir = path.isdir(package_path)
            if not package_path_exists:
                logger.warning(f"The path for the package {package_name} was not found")
                invalid_packages = invalid_packages + 1
            elif package_path_exists and not package_path_is_dir:
                logger.warning(f"The path for the package {package_name} is a file")
                invalid_packages = invalid_packages + 1
            else:
                logger.debug(f"Package {package_name} found")

        if not invalid_packages:
            logger.info("All packages are valid")
        else:
            logger.info(f"{invalid_packages} invalid package{'s' if invalid_packages > 1 else ''} found")
