"""
Helpers for exporting a written to different formats review.
"""

import os
import re

import click
from jinja2 import Template

from .creator import fill_template, write_review
from .io import read_file
from .formatter.utils import replace_enclosed_text_tags


def export_review(data, root=os.getcwd(), extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = read_file(root, 'template.' + extension)
    data['content'] = replace_track_tags(data['content']).format(**data)

    if extension == 'md':
        data['content'] = wiki_to_markdown(data['content'])
        # ensure tracks are sorted
        tracks = [data['tracks'][i] for i in sorted(data['tracks'])]
        # use general review template
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
            content=data['content'],
            date=data['date']
        )
    else:
        data['content'] = wiki_to_html(data['content'])
        formatted_review = fill_html(template, data)
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


def wiki_to_markdown(string):
    """Translates the string from vimwiki format to markdown."""
    string = replace_enclosed_text_tags(string, '\*', '**')
    string = replace_enclosed_text_tags(string, '_', '*')
    return string


def wiki_to_html(string):
    """Translates the string from vimwiki format to HTML."""
    string = replace_enclosed_text_tags(string, '\*', '<b>', '</b>')
    string = replace_enclosed_text_tags(string, '_', '<i>', '</i>')
    return string


def fill_html(template, data):
    """Fills Jinja template with data to generate a HTML string."""
    template = Template(template)
    return template.render(**data)
