from os import path, getcwd
from datetime import datetime
from urllib.parse import urlparse
from loguru import logger
import yaml
import semver
from github import Github
from github import Auth
from gitlab import Gitlab
from git import Repo
from gitget.version import __version__

class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        self.configuration = None
        self.github = None
        self.github_rate_limit = None
        self.github_rate_limit_core = None
        self.github_rate_limit_graphql = None
        self.gitlab = None

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
        return 0

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

                # Apply the options from the configuration, if any
                default_options = self.configuration.get("options", {})
                # Specified options will take precedence over the default options
                self.options = Base.merge(self.options, default_options)

                if semver.compare(self.configuration["version"], __version__) < 0:
                    logger.debug(f"Old package list version loaded: {self.configuration['version']} < {__version__}")

                    # Perform any necessary updates here
                    if semver.compare(self.configuration["version"], "4.0.0") < 0:
                        new_package_list = {}
                        for package_name, package_path in package_list.items():
                            logger.debug(f"Updating package {package_name} ({package_path})")
                            new_package_list[package_name] = self.get_package_for_path(package_name, package_path)
                        package_list = new_package_list

                    self.configuration["version"] = __version__
                    self.write_package_list(package_list)
            else:
                logger.debug("Old package list format detected")
                # Old format
                package_list = package_document
                self.configuration = { "version": __version__, "options": {} }
                
                # Perform any necessary updates here

                self.write_package_list(package_list)

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

    def get_package_for_path(self, package_name, package_path):
        """Returns the package information from the path. package_path must be an existing git repo."""
        logger.debug(f"Getting package information for {package_name} ({package_path})")
        url = self.get_remote_url(package_path)

        return self.get_package_for_url(url, package_name, package_path)

    def get_package_for_url(self, url, package_name, package_path):
        """Returns the package information for the url. package_path may not exist yet."""
        logger.debug(f"Getting package information for {package_name} ({package_path}, {url})")
        owner_name, repo_name = Base.get_owner_and_repo(url)

        url_parts = urlparse(url)
        if "gist.github.com" in url_parts.netloc:
            gist = self.get_github_gist(url)
            package = {
                "name": package_name,
                "path": package_path,
                "owner": owner_name,
                "repo": repo_name,
                "url": url,
                "description": gist.description,
                "homepage": None,
                "languages": [],
                "size_kb": 0,
                "stars": 0,
                "watchers": 0,
                "forks": len(gist.forks) if gist.forks is not None else 0,
                "topics": [],
                "license": None,
                "created_at": gist.created_at,
                "updated_at": gist.last_modified_datetime,
                "last_commit_at": gist.updated_at,
            }
            return package
        elif "github.com" in url_parts.netloc:
            repo = self.get_github_repo(url)
            license = repo.license
            if license is not None:
                license = {
                    "name": license.name,
                    "key": license.spdx_id,
                    "url": license.url,
                }
            package = {
                "name": package_name,
                "path": package_path,
                "owner": owner_name,
                "repo": repo_name,
                "url": url,
                "description": repo.description,
                "homepage": repo.homepage,
                "languages": [repo.language] if repo.language is not None else [],
                "size_kb": repo.size,
                "stars": repo.stargazers_count,
                "watchers": repo.subscribers_count,
                "forks": repo.forks_count,
                "topics": repo.get_topics(),
                "license": license,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "last_commit_at": repo.pushed_at,
            }
            return package
        elif "gitlab.com" in url_parts.netloc:
            repo = self.get_gitlab_repo(url)
            license = repo.license
            if license is not None:
                license = {
                    "name": license['name'],
                    "key": license['key'],
                    "url": license['html_url'],
                }
            package = {
                "name": package_name,
                "path": package_path,
                "owner": owner_name,
                "repo": repo_name,
                "url": url,
                "description": repo.description,
                "homepage": None,
                "languages": list(repo.languages().keys()) if repo.languages() is not None else [],
                "size_kb": 0,
                "stars": repo.star_count,
                "watchers": 0,
                "forks": repo.forks_count,
                "topics": repo.topics,
                "license": license,
                "created_at": Base.datetime_from_utc_iso_string(repo.created_at),
                "updated_at": Base.datetime_from_utc_iso_string(repo.updated_at),
                "last_commit_at": Base.datetime_from_utc_iso_string(repo.last_activity_at),
            }
            return package
        logger.warning(f"Full details are only supported for GitHub and GitLab repositories: {url}")
        package = {
            "name": package_name,
            "path": package_path,
            "owner": owner_name,
            "repo": repo_name,
            "url": url,
            "description": None,
            "homepage": None,
            "languages": [],
            "size_kb": 0,
            "stars": 0,
            "watchers": 0,
            "forks": 0,
            "topics": [],
            "license": None,
            "created_at": None,
            "updated_at": None,
            "last_commit_at": None,
        }
        return package

    @staticmethod
    def datetime_from_utc_iso_string(date_string):
        """Converts a UTC ISO date string to a datetime object."""
        if date_string.endswith("Z"):
            date_string = date_string[:-1]
        return datetime.fromisoformat(f"{date_string}+00:00")

    @staticmethod
    def get_owner_and_repo(url):
        """Split the url and get the owner and repo part(s) as a single string.
        i.e. awesmubarak/gitget -> owner: awesmubarak, repo: gitget
        
        Returns the owner and repo name in the format specified by the arguments.
        """
        url_parts = urlparse(url)
        url_path = url_parts.path
        # Trim the .git extension, if it exists
        if url_path.endswith(".git"):
            url_path = url_path[:-4]
        path_parts = list(filter(None, url_path.split("/")))
        # NOTE: If the URL was copied from the address bar of a bitbucket repo, the
        # path will be /owner/repo/src/branch, so we need to use 0/1, not -2/-1.
        owner = path_parts[0]
        repo = path_parts[1]
        return owner, repo

    @staticmethod
    def generate_name_from_url(url, include_owner=True, owner_first=True):
        """Split the url and get the owner and repo part(s) as a single string.
        i.e. awesmubarak/gitget -> owner: awesmubarak, repo: gitget
        
        Returns the owner and repo name in the format specified by the arguments.
        """
        owner, repo = Base.get_owner_and_repo(url)
        if include_owner:
            if owner_first:
                # owner_repo
                return f"{owner}_{repo}"
            else:
                # repo_owner
                return f"{repo}_{owner}"
        else:
            # repo
            return repo

    def init_github_client(self):
        """Initializes the GitHub client."""
        if self.github is not None:
            self.close_github_client()
        logger.debug("Creating GitHub client")
        try:
            if self.options["--github-auth-token"]:
                logger.debug("Accessing the GitHub API with an auth token")
                auth = Auth.Token(self.options["--github-auth-token"])
                self.github = Github(auth=auth)
                self.update_github_rate_limit()
            else:
                logger.debug("Accessing the GitHub API anonymously")
                self.github = Github()
                self.update_github_rate_limit()
        except Exception as ex:
            logger.error("Could not create GitHub client:")
            logger.error(ex)
            exit(1)

    def close_github_client(self):
        """Closes the GitHub client."""
        if self.github is not None:
            logger.debug("Closing GitHub client")
            try:
                self.github.close()
                self.github = None
            except Exception as ex:
                logger.error("Could not close GitHub client:")
                logger.error(ex)
                exit(1)

    def update_github_rate_limit(self):
        """Updates the GitHub rate limit."""
        if self.github is None:
            self.init_github_client()
        logger.debug("Updating GitHub rate limit")
        try:
            self.github_rate_limit = self.github.get_rate_limit()
            core_rl = self.github_rate_limit.core.raw_data
            core_rl["reset"] = self.github_rate_limit.core.reset
            core_rl["reset_str"] = core_rl["reset"].strftime("%A, %d. %B %Y %I:%M%p %Z")
            graphql_rl = self.github_rate_limit.graphql.raw_data
            graphql_rl["reset"] = self.github_rate_limit.graphql.reset
            graphql_rl["reset_str"] = graphql_rl["reset"].strftime("%A, %d. %B %Y %I:%M%p %Z")
            self.github_rate_limit_core = core_rl
            self.github_rate_limit_graphql = graphql_rl
            logger.debug(f"GitHub core rate limit: {core_rl['used']}/{core_rl['limit']}, {core_rl['remaining']} remaining (reset: {core_rl['reset_str']})")
            logger.debug(f"GitHub graphql rate limit: {graphql_rl['used']}/{graphql_rl['limit']}, {graphql_rl['remaining']} remaining (reset: {graphql_rl['reset_str']})")
        except Exception as ex:
            logger.error("Could not update GitHub rate limit:")
            logger.error(ex)
            exit(1)

    def get_github_repo(self, package_url):
        """Returns the GitHub repository object."""
        if self.github is None:
            self.init_github_client()
        logger.debug(f"Getting GitHub repo for {package_url}")
        try:
            owner, repo = Base.get_owner_and_repo(package_url)
            repo = self.github.get_repo(f"{owner}/{repo}")
            self.update_github_rate_limit()
            return repo
        except Exception as ex:
            logger.error("Could not get GitHub repo:")
            logger.error(ex)
            exit(1)

    def get_github_gist(self, package_url):
        """Returns the GitHub gist object."""
        if self.github is None:
            self.init_github_client()
        logger.debug(f"Getting GitHub gist for {package_url}")
        try:
            owner, gist = Base.get_owner_and_repo(package_url)
            gist = self.github.get_gist(f"{gist}")
            self.update_github_rate_limit()
            return gist
        except Exception as ex:
            logger.error("Could not get GitHub repo:")
            logger.error(ex)
            exit(1)

    def init_gitlab_client(self):
        """Initializes the GitLab client."""
        if self.gitlab is not None:
            self.close_gitlab_client()
        logger.debug("Creating GitLab client")
        try:
            if self.options["--gitlab-auth-token"]:
                logger.debug("Accessing the GitLab API with an auth token")
                self.gitlab = Gitlab("https://gitlab.com", private_token=self.options["--gitlab-auth-token"])
            else:
                logger.debug("Accessing the GitLab API anonymously")
                self.gitlab = Gitlab("https://gitlab.com")
            self.gitlab.auth()
        except Exception as ex:
            logger.error("Could not create GitLab client:")
            logger.error(ex)
            exit(1)

    def close_gitlab_client(self):
        """Closes the GitLab client."""
        if self.gitlab is not None:
            logger.debug("Closing GitLab client")
            try:
                # There is no close method for the GitLab client
                self.gitlab = None
            except Exception as ex:
                logger.error("Could not close GitLab client:")
                logger.error(ex)
                exit(1)

    def get_gitlab_repo(self, package_url):
        """Returns the GitLab repository object."""
        if self.gitlab is None:
            self.init_gitlab_client()
        logger.debug(f"Getting GitLab repo for {package_url}")
        try:
            owner, repo = Base.get_owner_and_repo(package_url)
            repo = self.gitlab.projects.get(f"{owner}/{repo}", license=True)
            return repo
        except Exception as ex:
            logger.error("Could not get GitLab repo:")
            logger.error(ex)
            exit(1)

    def get_remote_url(self, package_path):
        """Returns the remote URL of the repository."""
        logger.debug(f"Getting remote URL for {package_path}")
        try:
            repo = Repo(package_path)
            try:
                remote = repo.remotes.origin
            except AttributeError:
                # Named something other than origin?
                remote = repo.remotes[0]
            return remote.url
        except Exception as ex:
            logger.error("Could not get remote URL:")
            logger.error(ex)
            exit(1)
