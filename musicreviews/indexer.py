"""
Functions for generating various sorted lists and indexes of the reviews and ratings.
Each indexer function returns parsed data as a formatted string in wanted format
(markdown or HTML).
"""

import os
from datetime import date, timedelta
from itertools import chain

from .configuration import load_config
from .reader import read_file
from .writer import write_file


def compute_artist_rating(ratings):
    """Returns an artist rating based on the ratings of its albums."""
    return float(sum(ratings)) / max(len(ratings), 1)


def artists_by_name(formatter, albums):
    """Returns the artists sorted by name."""
    artist_tags = set([album["artist_tag"] for album in albums])
    artists = []
    for artist_tag in sorted(artist_tags):
        specific_albums = [x for x in albums if x["artist_tag"] == artist_tag]
        artists.append(
            {
                "artist_tag": artist_tag,
                "artist": specific_albums[0]["artist"],
            }
        )
    return formatter.parse_list(artists, formatter.format_artist)


def artists_by_rating(formatter, albums):
    """Returns the artists sorted by decreasing mean album rating.
    Only artists with more than 1 reviewed albums are considered.
    """
    artist_tags = set([album["artist_tag"] for album in albums])
    artists = []
    # build the list of artists and compute their ratings
    for artist_tag in artist_tags:
        specific_albums = [x for x in albums if x["artist_tag"] == artist_tag]
        if len(specific_albums) > 1:
            rating = compute_artist_rating([x["rating"] for x in specific_albums])
            artists.append(
                {
                    "artist_tag": artist_tag,
                    "artist": specific_albums[0]["artist"],
                    "rating": rating,
                }
            )
    sorted_artists = sorted(
        artists, key=lambda x: (x["rating"], x["artist_tag"]), reverse=True
    )
    return formatter.parse_list(sorted_artists, formatter.format_artist_rating)


def albums_by_rating(formatter, albums):
    """Returns the rated albums sorted by decreasing rating."""
    sorted_albums = sorted(
        albums,
        key=lambda x: (x["rating"], x["artist_tag"], x["album_tag"]),
        reverse=True,
    )
    return formatter.parse_list(sorted_albums, formatter.format_album)


def albums_by_year(formatter, albums):
    """Returns the rated albums sorted by decreasing year and rating."""
    years = set([album["year"] for album in albums])
    sorted_albums = {}
    for year in sorted(years, reverse=True):
        sorted_albums[year] = sorted(
            [x for x in albums if x["year"] == year],
            key=lambda x: (x["rating"], x["artist_tag"], x["album_tag"]),
            reverse=True,
        )
    return formatter.parse_categorised_lists(
        sorted_albums, formatter.format_header, formatter.format_album
    )


def albums_by_decade(formatter, albums):
    """Returns the rated albums sorted by decreasing decade and rating."""
    decades = set([album["decade"] for album in albums])
    sorted_albums = {}
    for decade in sorted(decades, reverse=True):
        sorted_albums[decade] = sorted(
            [x for x in albums if x["decade"] == decade],
            key=lambda x: (x["rating"], x["artist_tag"], x["album_tag"]),
            reverse=True,
        )
    return formatter.parse_categorised_lists(
        sorted_albums, formatter.format_header, formatter.format_album
    )


def albums_by_name(formatter, albums):
    """Returns a list of all album reviews sorted by artist and name."""
    sorted_albums = sorted(albums, key=lambda x: (x["artist_tag"], x["album_tag"]))
    return formatter.parse_list(sorted_albums, formatter.format_album)


def albums_by_date(formatter, albums):
    """Returns the reviews sorted by generation date."""
    sorted_albums = sorted(
        albums, key=lambda x: (x["date"], x["artist_tag"], x["album_tag"]), reverse=True
    )
    return formatter.parse_list(sorted_albums, formatter.format_album)


def albums_by_length(formatter, albums):
    """Returns the reviews sorted by content length."""
    sorted_albums = sorted(
        albums,
        key=lambda x: (len(x["content"]), x["artist_tag"], x["album_tag"]),
        reverse=True,
    )
    return formatter.parse_list(sorted_albums, formatter.format_album)


def tags_by_name(formatter, albums):
    """Returns for each tag's albums sorted by decreasing rating."""
    tags = sorted(
        set(
            chain.from_iterable(
                [album["tags"] for album in albums if album["tags"] is not None]
            )
        )
    )
    sorted_albums = {}
    descriptions = {}
    __, config = load_config()
    for tag in tags:
        descriptions[tag] = config["tags"].get(tag, "")
        sorted_albums[tag] = sorted(
            [x for x in albums if x["tags"] is not None and tag in x["tags"]],
            key=lambda x: (x["artist_tag"], x["album_tag"]),
        )
    return formatter.parse_categorised_lists(
        sorted_albums,
        formatter.format_header,
        formatter.format_album,
        descriptions=descriptions,
        description_formatter=formatter.format_description,
        sorted_keys=tags,
    )


def producers_by_name(formatter, albums):
    """Returns for each producer's albums sorted by decreasing rating."""
    producers = sorted(
        set(
            chain.from_iterable(
                [
                    album["producers"]
                    for album in albums
                    if album["producers"] is not None
                ]
            )
        )
    )
    sorted_albums = {}
    for producer in producers:
        sorted_albums[producer] = sorted(
            [
                x
                for x in albums
                if x["producers"] is not None and producer in x["producers"]
            ],
            key=lambda x: (x["artist_tag"], x["album_tag"]),
        )
    return formatter.parse_categorised_lists(
        sorted_albums,
        formatter.format_header,
        formatter.format_album,
        sorted_keys=producers,
    )


def labels_by_name(formatter, albums):
    """Returns for each label's albums sorted by decreasing rating."""
    labels = sorted(
        set(
            chain.from_iterable(
                [album["labels"] for album in albums if album["labels"] is not None]
            )
        )
    )
    sorted_albums = {}
    for label in labels:
        sorted_albums[label] = sorted(
            [x for x in albums if x["labels"] is not None and label in x["labels"]],
            key=lambda x: (x["artist_tag"], x["album_tag"]),
        )
    return formatter.parse_categorised_lists(
        sorted_albums,
        formatter.format_header,
        formatter.format_album,
        sorted_keys=labels,
    )


def shopping_list(formatter, albums):
    """Returns classics and favorites not physically owned."""
    filtered_albums = [
        x
        for x in albums
        if ("fav" in x["tags"] or "classic" in x["tags"])
        and not ("cd" in x["tags"] or "vinyl" in x["tags"] or "bandcamp" in x["tags"])
    ]
    sorted_albums = sorted(
        filtered_albums,
        key=lambda x: (x["date"], x["artist_tag"], x["album_tag"]),
        reverse=True
    )
    return formatter.parse_list(sorted_albums, formatter.format_album)


def recent_albums(formatter, albums):
    """Returns albums reviewed over the last 6 months sorted by decreasing rating."""
    filtered_albums = [
        x for x in albums if x["date"] > date.today() - timedelta(days=183)
    ]
    sorted_albums = sorted(
        filtered_albums,
        key=lambda x: (x["rating"], x["artist_tag"], x["album_tag"]),
        reverse=True,
    )
    return formatter.parse_list(sorted_albums, formatter.format_album)


def generate_all_indexes(albums, root_dir, extension="md", base_url=None):
    """Writes all possible indexes format."""
    if extension == "html":
        formatter = __import__("musicreviews").formatter.html
    else:
        formatter = __import__("musicreviews").formatter.markdown
    pipelines = (
        (albums_by_rating, "albumsrating"),
        (albums_by_year, "years"),
        (albums_by_decade, "decades"),
        (albums_by_name, "albums"),
        (albums_by_date, "albumsdate"),
        (albums_by_length, "albumslength"),
        (producers_by_name, "producers"),
        (labels_by_name, "labels"),
        (tags_by_name, "tags"),
        (artists_by_name, "artists"),
        (artists_by_rating, "artistsrating"),
        (shopping_list, "shopping_list"),
        (recent_albums, "recent_albums"),
    )
    for function, index_name in pipelines:
        content = function(formatter, albums)
        # specific case for html: fill an html template
        if extension == "html":
            index_template = read_file(root_dir, "template_index.html")
            title = index_name.replace("_", " ").title()
            content = index_template.format(
                title=title, base_url=base_url, content=content
            )
        write_file(content, os.path.join(root_dir, f"{index_name}.{extension}"))
