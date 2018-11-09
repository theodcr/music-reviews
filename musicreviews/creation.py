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


def fill_template(template, artist, album, year, rating, uri=None, picks=None, tracks=None):
    """Converts the fiels and fills the template review"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    uri = uri or ''
    if picks is not None:
        picks_string = '\n'.join([f'- {pick}' for pick in picks])
    else:
        picks_string = ''
    if tracks is not None:
        length_digits = max(str(len(tracks)))
        tracks_string = '\n'.join(
            [f'{i+1:{length_digits}d}: {track}' for i, track in enumerate(tracks)]
        )
    else:
        tracks_string = ''
    return template.format(
        date=today, artist=artist, album=album, year=year, uri=uri,
        rating=rating, picks=picks_string, tracks=tracks_string,
    )


def write_review(content, folder, filename, root=os.getcwd(), ext='wiki'):
    """Writes the review file using the given data"""
    if not os.path.exists(os.path.join(root, folder)):
        os.makedirs(os.path.join(root, folder))
        click.echo(click.style("Artist not known yet, created folder", fg='cyan'))
    filepath = os.path.join(root, folder, filename + "." + ext)
    if os.path.exists(filepath):
        click.echo(click.style("File exists, operation aborted", fg='red'))
    else:
        with open(filepath, 'w') as file_content:
            file_content.write(content)
