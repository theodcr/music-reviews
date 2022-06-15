"""
Helpers for reading files from disk, and building the database of reviews.
"""

import glob
import os

import frontmatter

START_HEADER = r"---\n"
END_HEADER = r"\n---\n"


def read_file(root, filename):
    """Reads the file and returns its content as a string."""
    with open(os.path.join(root, filename), encoding="utf8") as file_content:
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
        "producers": "",
        "rating": 0,
        "uri": None,
        "cover": None,
        "tracks": None,
        "picks": None,
        "content": "",
        "tags": None,
        "decade": 0,
    }


def compute_decade(year):
    """Returns the decade of the given year."""
    return 10 * (year // 10)


def build_album(artist_tag, file_path):
    album = empty_album()
    with open(file_path, "r", encoding="utf8") as f:
        post = frontmatter.load(f)
    album.update(post.to_dict())
    album["artist_tag"] = artist_tag
    album["album_tag"] = os.path.splitext(os.path.basename(file_path))[0]
    album["decade"] = compute_decade(album["year"])
    return album


def build_database(root_dir=os.getcwd()):
    """Finds reviews and builds a database using their header and content."""
    albums = []
    # find reviews in folders
    artist_tags = [
        f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))
    ]
    for artist_tag in artist_tags:
        for file_path in glob.glob(os.path.join(root_dir, artist_tag, "*.md")):
            albums.append(build_album(artist_tag, file_path))
    return albums
