"""
Helpers for creating a review file or exporting a written review
to different formats.
"""

import datetime
import os

import click

from .formatter import html, utils
from .reader import read_file
from .ui import style_error


def fill_review_template(
    template,
    artist,
    album,
    year,
    rating,
    uri=None,
    cover=None,
    picks=None,
    tags=None,
    tracks=None,
    state=None,
    content=None,
    date=None,
):
    """Converts the fields and fills the template review."""
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    uri = uri or ""
    cover = cover or ""
    state = state or "."
    content = content or ""
    if picks is not None:
        picks_string = "\n".join([f"- {pick}" for pick in picks])
    else:
        picks_string = ""
    if tags is not None:
        if isinstance(tags, str):
            tags_string = f"- {tags}"
        else:
            tags_string = "\n".join([f"- {tag}" for tag in tags])
    else:
        tags_string = ""
    if tracks is not None:
        # indent track list
        tracks_string = "\n".join(
            [
                f"    {i+1}: {utils.escape_yaml_specials(track)}"
                for i, track in enumerate(tracks)
            ]
        )
    else:
        tracks_string = ""
    return template.format(
        date=date,
        artist=utils.escape_yaml_specials(artist),
        album=utils.escape_yaml_specials(album),
        year=year,
        uri=uri,
        cover=cover,
        rating=rating,
        picks=picks_string,
        tags=tags_string,
        tracks=tracks_string,
        state=state,
        content=content,
    )


def export_review(data, root, base_url=None):
    """Exports review(s) to HTML. Formats metadata and content."""
    template = read_file(root, "template.html")
    data["content"] = utils.replace_track_tags(data["content"]).format(**data)
    data["content"] = html.markdown_to_html(data["content"])
    data["tracks"] = html.format_tracks_picks(data["tracks"], data["picks"])
    if data["tags"] is None:
        # tags are optional -> may be None
        data["tags"] = []
    # ref to tags index
    data["tags"] = html.format_tags(data["tags"])
    data["rating_color"] = html.rating_to_rbg_color(data["rating"])
    if base_url is not None:
        data["base_url"] = base_url
    formatted_review = template.format(**data)
    write_review(
        content=formatted_review,
        folder=data["artist_tag"],
        filename=data["album_tag"],
        root=root,
        extension="html",
        overwrite=True,
    )


def write_file(content, path, newline=False):
    """Writes the given content in a file, with an optional newline at the end."""
    with open(path, "w", encoding="utf8") as file_content:
        file_content.write(content)
        if newline:
            file_content.write("\n")


def write_review(
    content, folder, filename, root=os.getcwd(), extension="md", overwrite=False
):
    """Writes the review file using the given data.
    Returns True to confirm review creation (or if review already exists).
    Set overwrite to True if review is not created but exported in a different format.
    """
    if not os.path.exists(os.path.join(root, folder)):
        os.makedirs(os.path.join(root, folder))
        click.echo(click.style("Artist not known yet, created folder", fg="cyan"))

    filepath = os.path.join(root, folder, filename + "." + extension)

    if os.path.exists(filepath) and not overwrite:
        click.echo(style_error("File exists, operation aborted"))
        return True

    write_file(content, filepath)
    return True
