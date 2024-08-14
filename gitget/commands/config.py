from ._base import Base
from loguru import logger
from os import path
from shutil import move as mmove  # can't be called move, causes issues
import yaml


class Config(Base):
    """Config.

    Query or modify the gitget configuration.

    Usage: gitget config (list | get <key> | set <key> <value> | unset <key>) [global options]

    Examples:
        gitget config set "--git-args" "--recurse-submodules --jobs 8"
    """

    def run(self):
        package_list = self.get_package_list()
        
        if self.options["list"]:
            logger.info("Configuration:")
            editor = self.configuration.get("editor", "")
            options = self.configuration.get("options", {})
            logger.info(f"  editor: {editor}")
            logger.info(f"  options: {yaml.dump(options, default_flow_style=True)}")
            for key, value in options.items():
                logger.info(f"  {key}: {value}")
            exit(0)
        elif self.options["get"]:
            key = self.options["<key>"]
            logger.debug(f"Getting configuration for key: {key}")
            if key in self.configuration["options"]:
                logger.info(f"Value: {self.configuration['options'][key]}")
            elif key in self.configuration:
                logger.info(f"Value: {yaml.dump(self.configuration[key], default_flow_style=False)}")
            else:
                logger.error(f"Key not found: {key}")
                exit(1)
            exit(0)
        elif self.options["set"]:
            key = self.options["<key>"]
            logger.debug(f"Setting configuration for key: {key}")
            if key.startswith("-"):
                value = self.options["<value>"]
                if "options" in self.configuration:
                    self.configuration["options"][key] = value
                else:
                    self.configuration["options"] = {key: value}
            else:
                # Allow multiple options to be specified at once using YAML
                try:
                    value = yaml.safe_load(self.options["<value>"])
                except yaml.YAMLError:
                    value = self.options["<value>"]
                self.configuration[key] = value
            self.write_package_list(package_list)
            logger.info(f"Updated configuration for key: {key}")
            exit(0)
        elif self.options["unset"]:
            key = self.options["<key>"]
            logger.debug(f"Unsetting configuration for key: {key}")
            if key in self.configuration["options"]:
                self.configuration["options"].pop(key, None)
            elif key in self.configuration:
                self.configuration.pop(key, None)
            else:
                logger.error(f"Key not found: {key}")
                exit(1)
            self.write_package_list(package_list)
            logger.info(f"Unset configuration for key: {key}")
            exit(0)
