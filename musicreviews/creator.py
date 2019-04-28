"""
Helpers for creating a review file using given album data.
"""

import datetime
import os
import re

import click

from .formatter.yaml import escape_yaml_specials
from .io import write_file
from .ui import style_info, style_error


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
    date=None
):
    """Converts the fields and fills the template review."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
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
        date=date,
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
