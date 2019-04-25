"""
Helpers for exporting a written to different formats review.
"""

import os
import re

import click

from .creator import fill_template, import_template, write_review


def export_review(data, root=os.getcwd(), extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = import_template(root, 'template.' + extension)
    content = replace_track_tags(data['content']).format(**data)
    # ensure tracks are sorted
    tracks = [data['tracks'][i] for i in sorted(data['tracks'])]
    formatted_review = fill_template(
        template=template,
        artist=data['artist'],
        album=data['album'],
        year=data['year'],
        rating=data['rating'],
        uri=data['uri'],
        picks=data['picks'],
        tracks=tracks,
        state=data['state'],
        content=content,
    )
    write_review(
        content=formatted_review,
        folder=data['artist_tag'],
        filename=data['album_tag'],
        root=root,
        extension=extension,
        overwrite=True
    )


def replace_track_tags(content):
    """Replaces tags like {4} to formatting compatible tags like {tracks[4]}."""
    return re.sub('{(\d+)}', '{tracks[\\1]}', content)
