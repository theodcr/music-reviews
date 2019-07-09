"""
Helpers for review and index formatting.
- Parsers format and combine lists of dictionaries using formatters.
"""

import re


def parse_list(data, formatter, tag='', index_shift=1):
    """Parses each element in data using a formatter function.
    Data is a list of dicts.
    Optional tag, mainly for HTML.
    """
    output = ''.join([formatter(i + index_shift, item) for i, item in enumerate(data)])
    if tag:
        output = f'<{tag}>\n' + output + f'</{tag}>\n'
    return output


def parse_categorised_lists(
    data,
    header_formatter,
    formatter,
    sorted_keys=None,
    **kwargs
):
    """Parses each element in data using a formatter function.
    Data is a dict, each key is a category and each value is a list of dicts.
    Adds a header for each category.
    """
    if sorted_keys is None:
        sorted_keys = sorted(data.keys(), reverse=True)
    output = ''.join(
        [
            header_formatter(key) + parse_list(data[key], formatter, **kwargs)
            for key in sorted_keys
        ]
    )
    return output


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out.
    """
    return re.sub('[^a-zA-Z0-9]', '', string).lower()


def replace_enclosed_text_tags(string, tag_to_sub, opening_tag, closing_tag=None):
    """Replaces tags around enclosed text.
    For example _test_ -> **test** or <b>test</b>
    """
    closing_tag = closing_tag or opening_tag
    string = re.sub(
        '{0}([^{0}]+){0}'.format(tag_to_sub),
        f'{opening_tag}\\1{closing_tag}',
        string
    )
    return string


def replace_track_tags(content):
    """Replaces tags like {4} to formatting compatible tags like {tracks[4]}."""
    return re.sub('{(\d+)}', '{tracks[\\1]}', content)
