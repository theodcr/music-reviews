"""
Functions for writing indexed reviews lists in vimwiki format
"""


def write_file(content, path, newline=False):
    """Writes the given content in a file, with an optional newline at the end"""
    with open(path, 'w') as file_content:
        file_content.write(content)
        if newline:
            file_content.write("\n")


def parse_list(data, formatter, index_shift=1):
    """Parses each element in data using a formatter
    Data is a list of dicts
    """
    output = ''.join([formatter(i + index_shift, item) for i, item in enumerate(data)])
    return output


def parse_categorised_lists(data, formatter, index_shift=1, sorted_keys=None):
    """Parses each element in data using a formatter
    Data is a dict, each key is a category and each value is a list of dicts
    Title formatting for each category
    """
    if sorted_keys is None:
        sorted_keys = sorted(data.keys(), reverse=True)
    output = ''.join(
        [
            format_header(key) + parse_list(data[key], formatter, index_shift)
            for key in sorted_keys
        ]
    )
    return output


def format_header(string):
    """Returns the string as a header in the vimwiki format"""
    return "\n= {} =\n\n".format(string)


def format_artist(index, data):
    """Returns a formatted line of text describing the artist"""
    return "{}. [[{artist_tag}/|{artist}]] - {rating:.1f}\n".format(index, **data)


def format_album(index, data):
    """Returns a formatted line of text describing the album"""
    return (
        "{}. {artist} - {album} - {year} - {rating} - "
        + "[[{artist_tag}/{album_tag}|review]]\n"
    ).format(index, **data)


def format_track(index, data):
    """Returns a formatted line of text describing the track"""
    return ("{}. {artist} - {album} - {track}\n").format(index, **data)


def format_review(__, data):
    """Returns a formatted line showing the review state and its reference
    Dummy argument to respect standard formatter definition
    """
    return "- [{state}] [[{artist_tag}/{album_tag}]]\n".format(**data)
