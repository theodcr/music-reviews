"""
Functions for writing header of reviews in YAML format.
"""

import re


def escape_yaml_specials(string):
    """Surrounds the given string with quotes if it is not conform to YAML syntax."""
    alpha_string = alphanumeric_lowercase(string)
    if alpha_string == 'yes' or alpha_string == 'no':
        return '"' + string + '"'
    elif bool(re.search('^"', string)):
        return "'" + string + "'"
    elif bool(
        re.search("^'|^\? |: |^,|^&|^%|^@|^!|^\||^\*|^#|^- |^[|^]|^{|^}|^>", string)
    ):
        return '"' + string + '"'
    else:
        return string
