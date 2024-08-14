from os import path, getcwd
from loguru import logger
import yaml
import semver
from gitget.version import __version__


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        self.configuration = None

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
    def generate_name_from_url(url, include_owner=True, owner_first=True):
        """Split the url and get the last part(s).
        i.e. awesmubarak/gitget -> owner: awesmubarak, repo: gitget
        
        Returns the owner and repo name in the format specified by the arguments.
        """
        if include_owner:
            if owner_first:
                # owner_repo
                return "_".join(url.split("/")[-2:])
            else:
                # repo_owner
                return "_".join(url.split("/")[-2:].reverse())
        else:
            # repo
            return url.split("/")[-1]

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

    @staticmethod
    def merge(dict_1, dict_2):
        """Merge two dictionaries.

        Values that evaluate to true take priority over falsy values.
        `dict_1` takes priority over `dict_2`.

        """
        return dict((str(key), dict_1.get(key) or dict_2.get(key))
                    for key in set(dict_2) | set(dict_1))

    def get_package_list(self):
        """Returns the list of packages from the package file and updates self.options with any defaults."""
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
                f"Package file is a directory, please remove `{package_list_filepath}` and run `gitget setup`"
            )
            exit(1)
        elif package_list_file_valid == 0:
            logger.debug(f"Package file found: {package_list_filepath}")

        # try loading the file
        logger.debug("Attempting to load file")
        try:
            with open(package_list_filepath) as file:
                package_document = yaml.safe_load(file)
        except Exception as ex:
            logger.error("Could not load package list due to the following error:")
            logger.error(ex)
            exit(1)
        logger.debug("Package list loaded")

        # if the list is NONE, set to an empty dictionary to prevent iteration errors
        logger.debug("Checking if package list is None")
        if package_document is None:
            package_list = {}
            self.configuration = { "version": __version__, "options": {} }
            logger.debug("Package list has no content, set to empty dict")
        else:
            if "packages" in package_document and "configuration" in package_document and "version" in package_document["configuration"]:
                package_list = package_document["packages"]
                self.configuration = package_document["configuration"]
                logger.debug(f"Configuration: {yaml.dump(self.configuration, default_flow_style=True)}")
                if semver.compare(self.configuration["version"], __version__) < 0:
                    logger.debug(f"Old package list version loaded: {self.configuration['version']} < {__version__}")

                    # Perform any necessary updates here

                    self.configuration["version"] = __version__
                    self.write_package_list(package_list)
            else:
                logger.debug("Old package list format detected")
                # Old format
                package_list = package_document
                self.configuration = { "version": __version__, "options": {} }
                
                # Perform any necessary updates here

                self.write_package_list(package_list)

        # Apply the options from the configuration, if any
        default_options = self.configuration.get("options", {})
        # Specified options will take precedence over the default options
        self.options = Base.merge(self.options, default_options)

        return package_list

    def write_package_list(self, package_list):
        """Writes the package information to the package file."""
        logger.debug("Attempting to write package list")
        try:
            package_document = { "packages": package_list, "configuration": self.configuration }
            with open(Base.get_package_list_filepath(), "w") as file:
                yaml.dump(package_document, file, sort_keys=True, default_flow_style=False)
        except:
            logger.exception("Could not write package list")
            exit(1)
        logger.debug(f"Packages written to file: {Base.get_package_list_filepath()}")
