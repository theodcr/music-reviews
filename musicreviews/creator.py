"""
Helpers for creating a review file using given album data.
"""

import datetime
import os
import re

import click

from .ui import style_info, style_error
from .utils import escape_yaml_specials, write_file


def import_template(root=os.getcwd(), filename="template.wiki"):
    """Returns the review template as a string."""
    with open(os.path.join(root, filename)) as file_content:
        template = file_content.read()
    return template


def fill_template(
    template,
    artist,
    album,
    year,
    rating,
    uri=None,
    picks=None,
    tracks=None,
    state=None,
    content=None,
):
    """Converts the fields and fills the template review."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    uri = uri or ''
    state = state or '.'
    content = content or ''
    if picks is not None:
        picks_string = '\n'.join([f'- {pick}' for pick in picks])
    else:
        picks_string = ''
    if tracks is not None:
        # indent track list
        track = ''
        tracks_string = '\n'.join(
            [
                f'    {i+1}: {escape_yaml_specials(track)}'
                for i, track in enumerate(tracks)
            ]
        )
    else:
        tracks_string = ''
    return template.format(
        date=today,
        artist=escape_yaml_specials(artist),
        album=escape_yaml_specials(album),
        year=year,
        uri=uri,
        rating=rating,
        picks=picks_string,
        tracks=tracks_string,
        state=state,
        content=content,
    )


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
