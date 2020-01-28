"""
Helpers for reading files from disk, and building the database of reviews.
"""

import glob
import os
import re

import yaml

START_HEADER = r"---\n"
END_HEADER = r"\n---\n"


def read_file(root, filename):
    """Reads the file and returns its content as a string."""
    with open(os.path.join(root, filename)) as file_content:
        content = file_content.read()
    return content


def empty_album():
    """Returns an empty dictionary to store album data."""
    return {
        "artist_tag": "",
        "album_tag": "",
        "artist": "",
        "album": "",
        "year": 0,
        "rating": 0,
        "uri": None,
        "tracks": None,
        "picks": None,
        "state": " ",
        "content": "",
    }


def build_database(root_dir=os.getcwd()):
    """Finds reviews and builds a database using their tags and content.
    By default decodes the yaml header to decode tags.
    """
    albums = []
    # find reviews in folders
    artist_tags = [
        f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))
    ]
    for artist_tag in artist_tags:
        for file_path in glob.glob(os.path.join(root_dir, artist_tag, "*.md")):
            album = empty_album()
            with open(file_path, "r") as file_content:
                album = read_review_with_header(file_content, album)
            album["artist_tag"] = artist_tag
            album["album_tag"] = os.path.splitext(os.path.basename(file_path))[0]
            albums.append(album)
    return albums


def read_review_with_header(file_content, album):
    """Read the content of a review to find the album tags written in a YAML header."""
    review = file_content.read()
    __, header, album["content"] = re.split(
        f"{START_HEADER}|{END_HEADER}", review, maxsplit=2
    )
    for key, value in yaml.safe_load(header).items():
        album[key] = value
    return album
