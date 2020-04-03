"""
Helpers for formatting reviews to HTML.
Functions for writing indexed reviews lists in HTML format.
(Dummy arguments to respect standard formatter definition.)
"""

import colorsys
import json
import os
import re

import click
from powerspot.operations import get_album

from ..ui import style_info
from . import utils


def markdown_to_html(string):
    """Translates the string from markdown format to HTML."""
    string = utils.replace_enclosed_text_tags(string, r"\*\*", "<b>", "</b>")
    string = utils.replace_enclosed_text_tags(string, r"\*", "<i>", "</i>")
    string = re.sub("\n\n", "</p><p>", string)
    return string


def rating_to_rbg_color(rating):
    """Convert integer rating to HTML RBG color tuple.

    Red if rating <= 30, else gradient from red to green.
    """
    limit = 30
    if rating <= limit:
        rating = 0
    return tuple(
        color * 100
        for color in colorsys.hsv_to_rgb((rating - limit) / (100 - limit) / 3, 1, 1)
    )


def get_cover_url(root, artist_tag, album_tag, uri):
    """Return URL to album cover using Spotify data.

    If data has already retrieved, use it, else retrieve it from Spotify.
    """
    directory = os.path.join(root, artist_tag)
    data_path = os.path.join(directory, album_tag + ".json")
    if os.path.exists(data_path):
        with open(data_path, "r") as file_content:
            album_data = json.load(file_content)
    else:
        click.echo(style_info("Album data not retrieved yet, retrieving from Spotify"))
        album_data = get_album(uri)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(data_path, "w") as file_content:
            file_content.write(json.dumps(album_data))
    url = album_data["images"][0]["url"]
    return url


def parse_list(data, formatter, index_shift=1):
    """Parses each element in data using a formatter function.
    Data is a list of dicts.
    """
    output = "<ol>\n" + utils.parse_list(data, formatter) + "</ol>\n"
    return output


def parse_categorised_lists(data, header_formatter, formatter, sorted_keys=None):
    """Parses each element in data using a formatter function.
    Data is a dict, each key is a category and each value is a list of dicts.
    Adds a header for each category.
    """
    output = utils.parse_categorised_lists(
        data, header_formatter, formatter, parse_list, sorted_keys
    )
    return output


def format_header(string):
    """Returns the string as a header in HTML format."""
    return "<h1>{}</h1>\n".format(string)


def format_artist(__, data):
    """Returns a formatted HTML line describing the artist."""
    return "<li>{artist} - {rating:.1f}</li>\n".format(**data)


def format_album(__, data):
    """Returns a formatted HTML line describing the album."""
    return (
        "<li>{artist} - {album} - {year} - {rating} - "
        "<a href='{artist_tag}/{album_tag}.html'>review</a></li>\n"
    ).format(**data)


def format_track(__, data):
    """Returns a formatted HTML line describing the track."""
    return (
        "<li><a href='{artist_tag}/{album_tag}.html'>{artist} - {album}</a>"
        " - {track}</li>\n"
    ).format(**data)


def format_review(__, data):
    """Returns a formatted line showing the review state and its reference tags."""
    return (
        "<li>[{state}] <a href='{artist_tag}/{album_tag}.html'>"
        "{artist} - {album}</a></li>\n"
    ).format(**data)
