import os
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


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
    install_requires=['Click', 'powerspot', 'PyYAML'],
    include_package_data=True,
    licence='MIT',
)
