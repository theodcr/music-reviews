"""
Functions for generating various sorted lists and indexes of the reviews and ratings.
Each indexer function returns:
- sorted data as a dictionary
- parsed data as a formatted string in wanted format (markdown or HTML)
"""

import os

from .reader import read_file
from .writer import write_file

SORTED_STATES = ["P", "X", "O", "o", ".", " "]
STATES_DESCRIPTION = {
    "P": "Publié",
    "X": "Terminé (relire)",
    "O": "En écriture",
    "o": "Débuté",
    ".": "Noté et idées",
    " ": "Non noté ou inconnu",
}


def sort_artists(formatter, albums):
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
    sorted_artists = sorted(artists, key=lambda x: x["rating"], reverse=True)
    return (
        sorted_artists,
        formatter.parse_list(sorted_artists, formatter.format_artist),
    )


def sort_ratings(formatter, albums):
    """Returns the rated albums sorted by decreasing rating."""
    sorted_albums = sorted(albums, key=lambda x: x["rating"], reverse=True)
    return (sorted_albums, formatter.parse_list(sorted_albums, formatter.format_album))


def sort_ratings_by_year(formatter, albums):
    """Returns the rated albums sorted by decreasing year and rating."""
    years = set([album["year"] for album in albums])
    sorted_albums = {}
    for year in sorted(years, reverse=True):
        sorted_albums[year] = sorted(
            [x for x in albums if x["year"] == year],
            key=lambda x: x["rating"],
            reverse=True,
        )
    return (
        sorted_albums,
        formatter.parse_categorised_lists(
            sorted_albums, formatter.format_header, formatter.format_album
        ),
    )


def sort_ratings_by_decade(formatter, albums):
    """Returns the rated albums sorted by decreasing decade and rating."""
    for album in albums:
        album["decade"] = compute_decade(album["year"])
    decades = set([album["decade"] for album in albums])
    sorted_albums = {}
    for decade in sorted(decades, reverse=True):
        sorted_albums[decade] = sorted(
            [x for x in albums if x["decade"] == decade],
            key=lambda x: x["rating"],
            reverse=True,
        )
    return (
        sorted_albums,
        formatter.parse_categorised_lists(
            sorted_albums, formatter.format_header, formatter.format_album
        ),
    )


def all_reviews(formatter, albums):
    """Returns a list of all album reviews and their state."""
    sorted_albums = sorted(albums, key=lambda x: (x["artist_tag"], x["year"]))
    return (sorted_albums, formatter.parse_list(sorted_albums, formatter.format_review))


def sort_reviews_date(formatter, albums):
    """Returns the reviews sorted by generation date."""
    sorted_albums = sorted(albums, key=lambda x: x["date"], reverse=True)
    return (sorted_albums, formatter.parse_list(sorted_albums, formatter.format_review))


def sort_reviews_state(formatter, albums):
    """Returns the reviews sorted by state."""
    sorted_albums = sorted(albums, key=lambda x: (x["artist_tag"], x["year"]))
    filtered_albums = {}
    for state in SORTED_STATES:
        # title formatting for each state
        state_description = STATES_DESCRIPTION[state]
        filtered_albums[state_description] = [
            x for x in sorted_albums if x["state"] == state
        ]
    return (
        sorted_albums,
        formatter.parse_categorised_lists(
            filtered_albums,
            formatter.format_header,
            formatter.format_review,
            sorted_keys=(STATES_DESCRIPTION[state] for state in SORTED_STATES),
        ),
    )


def playlists_by_year(formatter, albums):
    """Returns yearly playlists of favorite tracks from albums
    sorted by decreasing year and decreasing rating.
    """
    years = set([album["year"] for album in albums])
    sorted_tracks = {}
    for year in sorted(years, reverse=True):
        sorted_tracks[year] = []
        sorted_albums = sorted(
            [x for x in albums if x["year"] == year],
            key=lambda x: x["rating"],
            reverse=True,
        )
        for album in sorted_albums:
            if album["picks"] is None:
                continue
            tracks = [
                {
                    "artist_tag": album["artist_tag"],
                    "album_tag": album["album_tag"],
                    "artist": album["artist"],
                    "album": album["album"],
                    "track": album["tracks"][p],
                }
                for p in album["picks"]
            ]
            sorted_tracks[year].extend(tracks)
    return (
        sorted_tracks,
        formatter.parse_categorised_lists(
            sorted_tracks, formatter.format_header, formatter.format_track
        ),
    )


def compute_artist_rating(ratings):
    """Returns an artist rating based on the ratings of its albums."""
    return float(sum(ratings)) / max(len(ratings), 1)


def compute_decade(year):
    """Returns the decade of the given year."""
    return 10 * (year // 10)


def generate_all_indexes(albums, root_dir, extension="md"):
    """Writes all possible indexes format."""
    if extension == "html":
        formatter = __import__("musicreviews").formatter.html
    else:
        formatter = __import__("musicreviews").formatter.markdown
    pipelines = (
        (sort_ratings, "sorted_albums"),
        (sort_ratings_by_year, "sorted_by_year"),
        (sort_ratings_by_decade, "sorted_by_decade"),
        (all_reviews, "reviews"),
        (sort_reviews_state, "reviews_state"),
        (sort_reviews_date, "reviews_date"),
        (sort_artists, "sorted_artists"),
        (playlists_by_year, "playlists_by_year"),
    )
    for function, index_name in pipelines:
        content = function(formatter, albums)[1]
        # specific case for html: fill an html template
        if extension == "html":
            index_template = read_file(root_dir, "template_index.html")
            title = index_name.replace("_", " ").title()
            content = index_template.format(title=title, content=content)
        write_file(content, os.path.join(root_dir, f"{index_name}.{extension}"))
