from configparser import ConfigParser
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)
)

CONFIG = ConfigParser()
CONFIG.read(os.path.join(PROJECT_ROOT, 'config', 'config.cfg'))
