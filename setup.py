import os
import shutil

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

if not os.path.exists(os.path.join(here, 'config', 'config.cfg')):
    shutil.copy(
        os.path.join(here, 'config', 'config.template.cfg'),
        os.path.join(here, 'config', 'config.cfg'),
    )

setup(
    name='music-reviews',
    version='0.1',
    author='theolamayo',
    description='CLI for music reviews management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6.0',
    url='https://github.com/theolamayo/music-reviews',
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        musicreviews=musicreviews.cli:main
    ''',
    install_requires=['Click', 'PyYAML'],
    include_package_data=True,
    licence='MIT',
)
