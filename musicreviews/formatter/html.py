"""
Helpers for formatting reviews to HTML.
Functions for writing indexed reviews lists in HTML format.
(Dummy arguments to respect standard formatter definition.)
"""

import colorsys
import re

from . import utils


def markdown_to_html(string):
    """Translates the string from markdown format to HTML."""
    string = utils.replace_enclosed_text_tags(string, r"\*\*", "<b>", "</b>")
    string = utils.replace_enclosed_text_tags(string, r"\*", "<i>", "</i>")
    string = re.sub("\n\n", "</p><p>", string)
    return string


def rating_to_rbg_color(rating):
    """Converts integer rating to HTML RBG color tuple.

    Red if rating <= 30, else gradient from red to green.
    """
    limit = 30
    if rating <= limit:
        rating = 0
    return tuple(
        color * 100
        for color in colorsys.hsv_to_rgb((rating - limit) / (100 - limit) / 3, 1, 1)
    )


def format_tags(tags):
    """Formats tags as comma-separated list of urls to tags index."""
    return ", ".join(
        [f'<a href="reviews_tags.html#{tag}">{tag}</a>' for tag in tags]
    )


def format_tracks_picks(tracks, picks):
    """Formats tracks as a list, with picks in bold."""
    return "\n".join(
        [
            f"<li><b>{track}</b></li>"
            if picks is not None and index in picks
            else f"<li>{track}</li>"
            for index, track in sorted(tracks.items())
        ]
    )


def parse_list(data, formatter, index_shift=1):
    """Parses each element in data using a formatter function.
    Data is a list of dicts.
    """
    output = "<ul>\n" + utils.parse_list(data, formatter) + "</ul>\n"
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
    return f"<h1 id='{string}'>{string}</h1>\n"


def format_artist(__, data):
    """Returns a formatted HTML line describing the artist."""
    return "<li><a href='{artist_tag}/index.html'>{artist}</a>".format(**data)


def format_artist_rating(__, data):
    """Returns a formatted HTML line describing the artist and its rating."""
    return (
        "<li><a href='{artist_tag}/index.html'>{artist}</a>"
        " - {rating:.1f}</li>\n"
    ).format(**data)


def format_album(__, data):
    """Returns a formatted HTML line describing the album."""
    return (
        "<li><a href='{artist_tag}/{album_tag}.html'>{artist} - {album}</a>"
        " - {year} - {rating}</li>\n"
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
