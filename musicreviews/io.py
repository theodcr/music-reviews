"""
Helpers for reading and writing various files to disk.
"""

import os

import click


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


def write_review(
    content,
    folder,
    filename,
    root=os.getcwd(),
    extension='wiki',
    overwrite=False
):
    """Writes the review file using the given data.
    Returns True to confirm review creation (or if review already exists).
    Set overwrite to True if review is not created but exported in a different format.
    """
    if not os.path.exists(os.path.join(root, folder)):
        os.makedirs(os.path.join(root, folder))
        click.echo(click.style("Artist not known yet, created folder", fg='cyan'))

    filepath = os.path.join(root, folder, filename + "." + extension)

    if os.path.exists(filepath) and not overwrite:
        click.echo(style_error("File exists, operation aborted"))
        return True

    write_file(content, filepath)
    return True
