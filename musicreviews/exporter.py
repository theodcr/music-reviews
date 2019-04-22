"""
Helpers for exporting a written to different formats review.
"""

import os

import click

from .creator import fill_template, import_template, write_review


def export_review(data, root=os.getcwd(), extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = import_template(root, 'template.' + extension)
    # TODO resolve tracks formatting
    content = data['content'].format(**data)
    # unsure tracks are sorted
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
