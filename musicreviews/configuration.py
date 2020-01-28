import os
from configparser import ConfigParser

import click
from pkg_resources import Requirement, resource_filename

from .writer import write_file


def write_config(config):
    """Writes config object in local config path and returns this path."""
    directory = config_directory()
    os.makedirs(directory, exist_ok=True)
    path = config_path()
    with open(path, "w") as file_content:
        config.write(file_content)
    return path


def copy_template_review(root_dir):
    """Copies the template review to the reviews library directory."""
    template_path = resource_filename(
        Requirement.parse(__package__), "templates/template.md"
    )
    with open(template_path) as file_content:
        template = file_content.read()
    write_path = os.path.join(root_dir, "template.md")
    write_file(template, write_path)
    return write_path


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
    return resource_filename(
        Requirement.parse(__package__), "templates/config.template.cfg"
    )


def config_path():
    """Returns path to local package configuration."""
    return os.path.join(config_directory(), "config.cfg")


def config_directory():
    """Returns local package configuration directory."""
    return click.get_app_dir(__package__)
