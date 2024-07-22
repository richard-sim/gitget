from os import path, getcwd
from loguru import logger
import yaml


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        pass

    @staticmethod
    def find_in_dir_tree(curr_dir, filename):
        filepath = path.join(curr_dir, filename)
        if path.isfile(filepath):
            return filepath
        parent_dir = path.dirname(curr_dir)
        if parent_dir == "" or parent_dir == curr_dir:
            return None
        return Base.find_in_dir_tree(parent_dir, filename)

    @staticmethod
    def get_package_list_filepath():
        """Returns the filepath of the file containing the package info."""
        logger.debug("Getting the package file filepath")
        filepath = Base.find_in_dir_tree(getcwd(), ".gitget.yaml")
        if filepath is None:
            filepath = path.expanduser(path.join("~", ".gitget.yaml"))
        logger.debug(f"Package file: {filepath}")
        return filepath

    @staticmethod
    def get_new_package_list_filepath():
        """Returns the filepath of the file containing the package info."""
        logger.debug("Getting the package file filepath")
        filepath = path.abspath(".gitget.yaml")
        logger.debug(f"Package file: {filepath}")
        return filepath

    @staticmethod
    def check_package_list_file(package_list_path):
        """Verifies the package list file exists.

        Returns (int):
            0: valid
            1: not found
            2: a folder instead of a file
        """
        logger.debug("Checking file status")
        path_exists = path.exists(package_list_path)
        path_is_dir = path.isdir(package_list_path)

        logger.debug("File status found, returning value")
        if not path_exists:
            return 1
        elif path_exists and path_is_dir:
            return 2
        else:
            return 3

    def get_package_list(self):
        """Returns the extracted yaml data from the package file."""
        logger.debug("Loading package list")
        package_list_filepath = Base.get_package_list_filepath()

        # check package list file is valid
        logger.debug("Checking filepath")
        package_list_file_valid = Base.check_package_list_file(package_list_filepath)
        if package_list_file_valid == 1:
            logger.error("Package file missing, please run `gitget setup`")
            exit(1)
        elif package_list_file_valid == 2:
            logger.error(
                "Package file is a directory, please remove `.gitget.yaml` and run `gitget setup`"
            )
            exit(1)
        elif package_list_file_valid == 0:
            logger.debug("Package file found")

        # try loading the file
        logger.debug("Attempting to load file")
        try:
            with open(package_list_filepath) as file:
                package_list = yaml.safe_load(file)
        except Exception as ex:
            logger.error("Could not load package list due to the following error:")
            logger.error(ex)
            exit(1)
        logger.debug("Package list loaded")

        # if the list is NONE, set to an empty dictionary to prevent iteration errors
        logger.debug("Checking if package list is None")
        if package_list is None:
            package_list = {}
            logger.debug("Package list has no content, set to empty dict")
        return package_list

    def write_package_list(self, package_list):
        """Writes the package information to the package file."""
        logger.debug("Attempting to write package list")
        try:
            with open(Base.get_package_list_filepath(), "w") as file:
                yaml.dump(package_list, file, sort_keys=True)
        except:
            logger.exception("Could not write package list")
            exit(1)
        logger.debug("Packages written to file")
