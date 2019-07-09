"""
Helpers for formatting reviews to HTML.
"""

import colorsys
import json
import os
import re

from powerspot.operations import get_album

from ..ui import style_info
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


def get_cover_url(root, artist_tag, album_tag, uri):
    """Return URL to album cover using Spotify data.

    If data has already retrieved, use it, else retrieve it from Spotify.
    """
    data_path = os.path.join(root, artist_tag, album_tag + '.json')
    if os.path.exists(data_path):
        with open(data_path, 'r') as file_content:
            album_data = json.load(file_content)
    else:
        style_info("Album data not retrieved yet, retrieving from Spotify")
        album_data = get_album(uri)
        with open(data_path, 'w') as file_content:
            file_content.write(json.dumps(album_data))
    url = album_data['images'][0]['url']
    return url
