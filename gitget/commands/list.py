from ._base import Base
from loguru import logger
from tabulate import tabulate


class List(Base):
    """List.

    Lists all packages and install locations.

    Usage: gitget [global options] [options] list

    Options:
        --format   Table format to pass to tabulate (default: mixed_grid)
        --no-wrap  Do not wrap lines in the table
        --width    Width of the table (default: 188)

    Examples:
        gitget list
        gitget --format tsv --no-wrap list
        gitget --format html list
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

        table_format = self.options["--format"]
        if not table_format:
            table_format = "mixed_grid"

        width = 188
        if self.options["--width"]:
            width = int(self.options["--width"])

        maxcolwidths = [30*width/188, 30*width/188, 18*width/188, 30*width/188, 40*width/188, 20*width/188, 20*width/188]
        if self.options["--no-wrap"]:
            maxcolwidths = [None] * 7

        logger.debug("Printing table")
        number_str = f"{len(package_list)} packages:"
        table = tabulate(table,
                         headers=["Package Name", "Path", "Last Commit", "URL", "Description", "Topics", "License"],
                         maxcolwidths=maxcolwidths,
                         tablefmt=table_format)
        logger.info(f"{number_str}\n\n{table}\n")
