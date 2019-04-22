"""
Helpers for exporting a written to different formats review.
"""

import os

import click

from .creator import import_template, write_review


def export_review(data, root=os.getcwd(), extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = import_template(root, 'template.' + extension)
    content = data['content'].format(**data)
