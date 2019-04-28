"""
Helpers for reading and writing various files to disk.
"""

import os


def read_file(root, filename):
    """Reads the file and returns its content as a string."""
    with open(os.path.join(root, filename)) as file_content:
        template = file_content.read()
    return template


def write_file(content, path, newline=False):
    """Writes the given content in a file, with an optional newline at the end."""
    with open(path, 'w') as file_content:
        file_content.write(content)
        if newline:
            file_content.write("\n")
