from ._base import Base
from loguru import logger
from tabulate import tabulate


class List(Base):
    """List.

    Lists all packages and install locations.

    Usage: gitget list [global options]

    Examples:
        gitget list
    """

    def run(self):

        package_list = self.get_package_list()

        # print message if no content in package List
        logger.debug("Checking if package list is empty")
        if not package_list:
            logger.info("Package list is empty")
            return 0

        # create the table, trimming each section
        logger.debug("Creating table for printing")
        table = []
        for package_name, package in package_list.items():
            path = package["path"]
            url = package["url"] if package["url"] else ""
            description = package["description"] if package["description"] else ""
            last_commit = package["last_commit_at"].strftime("%A, %d. %B %Y %I:%M%p %Z") if package["last_commit_at"] else ""
            topics = ", ".join(package["topics"]) if package["topics"] else ""
            license = package["license"]["name"] if package["license"] else ""
            table.append([package_name, path, last_commit, url, description, topics, license])

        logger.debug("Printing table")
        number_str = f"{len(package_list)} packages:"
        table = tabulate(table, headers=["Package name", "Path", "Last Commit", "URL", "Description", "Topics", "License"], tablefmt="simple_outline")
        logger.info(f"{number_str}\n\n{table}\n")
