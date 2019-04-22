import os
from configparser import ConfigParser
from pkg_resources import Requirement, resource_filename

import click


APP_NAME = 'musicreviews'
CONFIG_FILENAME = 'config.cfg'
TEMPLATE_FILENAME = 'config.template.cfg'


def write_config(config):
    """Writes config object in local config path and returns this path."""
    directory = config_directory()
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = config_path()
    with open(path, 'w') as configfile:
        config.write(configfile)
    return path


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
    return resource_filename(Requirement.parse("music-reviews"), TEMPLATE_FILENAME)


def config_path():
    """Returns path to local package configuration."""
    return os.path.join(config_directory(), CONFIG_FILENAME)


def config_directory():
    """Returns local package configuration directory."""
    return os.path.join(click.get_app_dir(APP_NAME))
