"""
Helpers for creating a review file or exporting a written review
to different formats.
"""

import datetime
import os

import click

from .formatter import html, markdown, utils, yaml
from .reader import read_file


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
                f'    {i+1}: {yaml.escape_yaml_specials(track)}'
                for i, track in enumerate(tracks)
            ]
        )
    else:
        tracks_string = ''
    return template.format(
        date=date,
        artist=yaml.escape_yaml_specials(artist),
        album=yaml.escape_yaml_specials(album),
        year=year,
        uri=uri,
        rating=rating,
        picks=picks_string,
        tracks=tracks_string,
        state=state,
        content=content,
    )


def export_review(data, root, extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = read_file(root, 'template.' + extension)
    data['content'] = utils.replace_track_tags(data['content']).format(**data)

    if extension == 'md':
        data['content'] = markdown.wiki_to_markdown(data['content'])
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
        data['content'] = html.wiki_to_html(data['content'])
        formatted_review = html.fill_html(template, data)
    write_review(
        content=formatted_review,
        folder=data['artist_tag'],
        filename=data['album_tag'],
        root=root,
        extension=extension,
        overwrite=True
    )


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