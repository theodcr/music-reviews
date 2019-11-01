import os
from configparser import ConfigParser

import click
from pkg_resources import Requirement, resource_filename

CONFIG_FILENAME = "config.cfg"
TEMPLATE_FILENAME = "templates/config.template.cfg"


def write_config(config):
    """Writes config object in local config path and returns this path."""
    directory = config_directory()
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(config_path(), "w") as file_content:
        config.write(file_content)
    return config_path()


def load_config(load_template=False):
    """Loads configuration and returns path and configuration object."""
    config = ConfigParser()
    path = template_config_path() if load_template else config_path()
    if os.path.exists(path):
        config.read(path)
    else:
        config = None
    return path, config


def template_config_path():
    """Returns path to package template configuration."""
    return resource_filename(Requirement.parse(__package__), TEMPLATE_FILENAME)


def config_path():
    """Returns path to local package configuration."""
    return os.path.join(config_directory(), CONFIG_FILENAME)


def config_directory():
    """Returns local package configuration directory."""
    return click.get_app_dir(__package__)
