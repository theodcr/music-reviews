"""
Functions for building a database of local reviews
and generating various sorted lists of the reviews and ratings
"""

import glob
import os

SORTED_STATES = ['P', 'X', 'O', 'o', '.', ' ']
STATES_DESCRIPTION = {
    'P': 'Publié',
    'X': 'Terminé (relire)',
    'O': 'En écriture',
    'o': 'Débuté',
    '.': 'Noté et idées',
    ' ': 'Non noté ou inconnu',
}


def empty_album():
    """Returns an empty dictionary to store album data"""
    return {
        'artist_tag': "",
        'album_tag': "",
        'artist': "",
        'album': "",
        'year': 0,
        'rating': 0,
        'uri': None,
        'tracks': None,
        'picks': None,
        'state': " ",
        'content': "",
    }


def decode_tags(path, album=None):
    """Read the content of a review to find the album fields"""
    if album is None:
        album = empty_album()
    with open(path, 'r') as file_content:
        for _ in range(6):
            words = file_content.readline().split()
            tag = words[0][1:]
            album[tag] = " ".join(words[1:])
        album['year'] = int(album['year'])
        album['rating'] = int(album['rating'])
        album['content'] = file_content.read()
    return album


def build_database(root_dir=os.getcwd()):
    """Builds the database of ratings"""
    albums = []
    # find reviews in folders
    artist_tags = [
        f
        for f in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, f)) and f != '__pycache__'
    ]
    for artist_tag in artist_tags:
        for filename in glob.glob(os.path.join(root_dir, artist_tag, '*.wiki')):
            path = os.path.join(root_dir, artist_tag, filename)
            album = decode_tags(path)
            # could do something easier using just the path
            album['artist_tag'] = artist_tag
            album['album_tag'] = os.path.splitext(os.path.basename(filename))[0]
            albums.append(album)
    return albums


def write_file(content, filename, newline=False):
    """Writes the given content in a file, with a newline at the end"""
    with open(filename, 'w') as file_content:
        file_content.write(content)
        if newline:
            file_content.write("\n")


def sort_artists(albums):
    """Returns the artists sorted by decreasing rating, only artists with more
    than 1 reviewed albums"""
    output = ""
    artist_tags = set([album['artist_tag'] for album in albums])
    artists = []
    # build the list of artists and compute their ratings
    for artist_tag in artist_tags:
        specific_albums = [x for x in albums if x['artist_tag'] == artist_tag]
        if len(specific_albums) > 1:
            rating = compute_artist_rating([x['rating'] for x in specific_albums])
            artists.append(
                {
                    'artist_tag': artist_tag,
                    'artist': specific_albums[0]['artist'],
                    'rating': rating,
                }
            )
    sorted_artists = sorted(artists, key=lambda x: x['rating'], reverse=True)
    for i, artist in enumerate(sorted_artists):
        output += format_artist(i + 1, artist)
    return output


def sort_ratings(albums):
    """Returns the rated albums sorted by decreasing rating"""
    sorted_albums = sorted(albums, key=lambda x: x['rating'], reverse=True)
    output = ""
    for i, album in enumerate(sorted_albums):
        output += format_album(i + 1, album)
    return output


def sort_ratings_by_year(albums):
    """Returns the rated albums sorted by decreasing year and
    decreasing rating"""
    output = ""
    # only work with years present in the database
    years = set([album['year'] for album in albums])
    for year in sorted(years, reverse=True):
        # title formatting for each year
        output += format_header(year)
        sorted_albums = sorted(
            [x for x in albums if x['year'] == year],
            key=lambda x: x['rating'],
            reverse=True,
        )
        for i, album in enumerate(sorted_albums):
            output += format_album(i + 1, album)
    return output


def sort_ratings_by_decade(albums):
    """Returns the rated albums sorted by decreasing decade and
    decreasing rating"""
    output = ""
    for album in albums:
        album['decade'] = compute_decade(album['year'])
    decades = set([album['decade'] for album in albums])
    for decade in sorted(decades, reverse=True):
        output += format_header(decade)
        sorted_albums = sorted(
            [x for x in albums if x['decade'] == decade],
            key=lambda x: x['rating'],
            reverse=True,
        )
        for i, album in enumerate(sorted_albums):
            output += format_album(i + 1, album)
    return output


def all_reviews(albums):
    """Returns a todo list with all reviews and their state"""
    output = ""
    sorted_albums = sorted(albums, key=lambda x: (x['artist_tag'], x['year']))
    for album in sorted_albums:
        output += format_review(album)
    return output


def sort_reviews_date(albums):
    """Returns the reviews sorted by generation date"""
    output = ""
    sorted_albums = sorted(albums, key=lambda x: x['date'], reverse=True)
    for album in sorted_albums:
        output += format_review(album)
    return output


def sort_reviews_state(albums):
    """Returns the reviews sorted by state"""
    output = ""
    sorted_albums = sorted(albums, key=lambda x: (x['artist_tag'], x['year']))
    for state in SORTED_STATES:
        # title formatting for each state
        output += format_header(STATES_DESCRIPTION[state])
        filtered_albums = [x for x in sorted_albums if x['state'] == state]
        for album in filtered_albums:
            output += format_review(album)
    return output


def compute_artist_rating(ratings):
    """Returns an artist rating based on the given ratings of its albums"""
    return float(sum(ratings)) / max(len(ratings), 1)


def compute_decade(year):
    """Returns the decade of the given year"""
    return 10 * (year // 10)


def format_header(string):
    """Returns the string as a header in the vimwiki format"""
    return "\n= {} =\n\n".format(string)


def format_artist(index, artist):
    """Returns a formatted line of text describing the artist"""
    return "{}. [[{artist_tag}/|{artist}]] - {rating}\n".format(index, **artist)


def format_album(index, album):
    """Returns a formatted line of text describing the album"""
    return (
        "{}. {artist} - {album} - {year} - {rating} - "
        + "[[{artist_tag}/{album_tag}|review]]\n"
    ).format(index, **album)


def format_review(album):
    """Returns a formatted line showing the review state and its reference"""
    return "- [{state}] [[{artist_tag}/{album_tag}]]\n".format(**album)


def generate_all_lists(albums, root_dir):
    """Imports reviews and writes all possible files"""
    functions = [
        sort_ratings,
        sort_ratings_by_year,
        sort_ratings_by_decade,
        all_reviews,
        sort_reviews_state,
        sort_reviews_date,
        sort_artists,
    ]
    file_names = [
        'sorted_albums.wiki',
        'sorted_by_year.wiki',
        'sorted_by_decade.wiki',
        'reviews.wiki',
        'reviews_state.wiki',
        'reviews_date.wiki',
        'sorted_artists.wiki',
    ]
    for func, file_name in zip(functions, file_names):
        write_file(func(albums), os.path.join(root_dir, file_name))
    return albums
