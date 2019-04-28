"""
Functions for writing indexed reviews lists in vimwiki format.
Formatters take an integer index and a dictionary as inputs.
"""


def format_header(string):
    """Returns the string as a header in the vimwiki format."""
    return "\n= {} =\n\n".format(string)


def format_artist(index, data):
    """Returns a formatted line of text describing the artist."""
    return "{}. [[{artist_tag}/|{artist}]] - {rating:.1f}\n".format(index, **data)


def format_album(index, data):
    """Returns a formatted line of text describing the album."""
    return (
        "{}. {artist} - {album} - {year} - {rating} - "
        + "[[{artist_tag}/{album_tag}|review]]\n"
    ).format(index, **data)


def format_track(index, data):
    """Returns a formatted line of text describing the track."""
    return ("{}. {artist} - {album} - {track}\n").format(index, **data)


def format_review(__, data):
    """Returns a formatted line showing the review state and its reference tags.
    Dummy argument to respect standard formatter definition.
    """
    return "- [{state}] [[{artist_tag}/{album_tag}]]\n".format(**data)


def format_rating(album):
    """Format the album rating in a short note in vimwiki syntax."""
    output = f"\n*Note :* {album['rating']}/100"
    if album['rating'] % 10 != 0:
        output += f", arrondi à {round(album['rating']/10)}/10"
    output += "\n"
    return output
