"""
Helpers for generating a review file using album data
"""

import datetime
import os

import click


def import_template(root=os.getcwd(), filename="template.wiki"):
    """Returns the review template as a string"""
    with open(os.path.join(root, filename)) as file_content:
        template = file_content.read()
    return template


def fill_template(template, artist, album, year, rating):
    """Fills the template review with the input"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return template.format(
        date=today, artist=artist, album=album, year=year, rating=rating
    )


def write_review(content, folder, filename, root=os.getcwd(), ext='wiki'):
    """Writes the review file using the given data"""
    if not os.path.exists(os.path.join(root, folder)):
        os.makedirs(os.path.join(root, folder))
        click.echo(click.style("Artist not known yet, created folder"), fg='cyan')
    filepath = os.path.join(root, folder, filename + "." + ext)
    if os.path.exists(filepath):
        click.echo(click.style("File exists, operation aborted"), fg='red')
    else:
        with open(filepath, 'w') as file_content:
            file_content.write(content)
