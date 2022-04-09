"""
Functions for writing indexed reviews lists in markdown format.
Formatters take an integer index and a dictionary as inputs.
"""

from . import utils

parse_list = utils.parse_list


def parse_categorised_lists(
    data,
    header_formatter,
    formatter,
    descriptions=None,
    description_formatter=None,
    sorted_keys=None,
):
    """Parses each element in data using a formatter function.
    Data is a dict, each key is a category and each value is a list of dicts.
    Adds a header for each category.
    """
    output = utils.parse_categorised_lists(
        data,
        header_formatter,
        formatter,
        parse_list,
        descriptions,
        description_formatter,
        sorted_keys,
    )
    return output


def format_header(string):
    """Returns the string as a header."""
    return "\n# {}\n\n".format(string)


def format_description(string):
    """Returns the string as a basic text."""
    return f"{string}\n\n"


def format_artist(index, data):
    """Returns a formatted line of text describing the artist."""
    return "{}. {artist}\n".format(index, **data)


def format_artist_rating(index, data):
    """Returns a formatted line of text describing the artist and its rating."""
    return "{}. {artist} - {rating:.1f}\n".format(index, **data)


def format_album(index, data):
    """Returns a formatted line of text describing the album."""
    return "{}. {artist} - {album} - {year} - {rating}\n".format(index, **data)


def format_track(index, data):
    """Returns a formatted line of text describing the track."""
    return "{}. {artist} - {album} - {track}\n".format(index, **data)


def format_rating(album):
    """Format the album rating in a short note."""
    output = f"\n**Note :** {album['rating']}/100"
    if album["rating"] % 10 != 0:
        output += f", arrondi à {round(album['rating']/10)}/10"
    output += "\n"
    return output
