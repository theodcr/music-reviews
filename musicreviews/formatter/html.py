"""
Helpers for formatting reviews to HTML.
"""

import colorsys
import re

from .utils import replace_enclosed_text_tags


def wiki_to_html(string):
    """Translates the string from vimwiki format to HTML."""
    string = replace_enclosed_text_tags(string, '\*', '<b>', '</b>')
    string = replace_enclosed_text_tags(string, '_', '<i>', '</i>')
    string = re.sub('\n\n', '</p><p>', string)
    return string


def rating_to_rbg_color(rating):
    """Convert integer rating to HTML RBG color tuple.

    Red if rating <= 30, else gradient from red to green.
    """
    limit = 30
    if rating <= limit:
        rating = 0
    return tuple(
        color*100 for color in colorsys.hsv_to_rgb(
            (rating - limit) / (100 - limit) / 3, 1, 1
        )
    )
