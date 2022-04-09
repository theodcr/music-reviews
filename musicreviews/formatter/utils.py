"""
Helpers for review and index formatting.
- Parsers format and combine lists of dictionaries using formatters.
"""

import re


def parse_list(data, formatter, index_shift=1):
    """Parses each element in data using a formatter function.
    Data is a list of dicts.
    """
    output = "".join([formatter(i + index_shift, item) for i, item in enumerate(data)])
    return output


def parse_categorised_lists(
    data,
    header_formatter,
    formatter,
    list_parser,
    descriptions=None,
    description_formatter=None,
    sorted_keys=None,
):
    """Parses each element in data using a formatter function.
    Data is a dict, each key is a category and each value is a list of dicts.
    Adds a header for each category.
    """
    if sorted_keys is None:
        sorted_keys = sorted(data.keys(), reverse=True)
    if descriptions is not None and description_formatter is not None:
        output = "".join(
            [
                header_formatter(key)
                + description_formatter(descriptions[key])
                + list_parser(data[key], formatter)
                for key in sorted_keys
            ]
        )
    else:
        output = "".join(
            [
                header_formatter(key) + list_parser(data[key], formatter)
                for key in sorted_keys
            ]
        )
    return output


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out.
    """
    return re.sub("[^a-zA-Z0-9]", "", string).lower()


def replace_enclosed_text_tags(string, tag_to_sub, opening_tag, closing_tag=None):
    """Replaces tags around enclosed text.
    For example _test_ -> **test** or <b>test</b>
    """
    closing_tag = closing_tag or opening_tag
    string = re.sub(
        "{0}([^{0}]+){0}".format(tag_to_sub), f"{opening_tag}\\1{closing_tag}", string
    )
    return string


def replace_track_tags(content):
    """Replaces tags like {4} to formatting compatible tags like {tracks[4]}."""
    return re.sub(r"{(\d+)}", "<i>{tracks[\\1]}</i>", content)


def escape_yaml_specials(string):
    """Surrounds the given string with quotes if it is not conform to YAML syntax."""
    alpha_string = alphanumeric_lowercase(string)
    if alpha_string == "yes" or alpha_string == "no":
        return '"' + string + '"'
    elif bool(re.search('^"', string)):
        return "'" + string + "'"
    elif bool(
        re.search(r"^'|^\? |: |^,|^&|^%|^@|^!|^\||^\*|^#|^- |^[|^]|^{|^}|^>", string)
    ):
        return '"' + string + '"'
    else:
        return string
