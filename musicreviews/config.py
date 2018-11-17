import os
from configparser import ConfigParser

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)
)

CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config', 'config.cfg')

CONFIG = ConfigParser()
CONFIG.read(CONFIG_PATH)
