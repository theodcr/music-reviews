#!/usr/bin/env python3
"""Searches the reviews and generates various sorted lists of the reviews and
ratings"""

import os
import glob


SORTED_STATES = ['P', 'X', 'O', 'o', '.', ' ']
STATES_DESCRIPTION = {'P': 'Publié',
                      'X': 'Terminé (relire)',
                      'O': 'En écriture',
                      'o': 'Débuté',
                      '.': 'Noté et idées',
                      ' ': 'Non noté ou inconnu'}


def build_database(root_dir=os.getcwd()):
    """Builds the database of ratings"""
    albums = []
    # find reviews in folders
    artist_tags = [f for f in os.listdir(root_dir)
                   if os.path.isdir(os.path.join(root_dir, f))
                   and f != '__pycache__']
    for artist_tag in artist_tags:
        for filename in glob.glob(os.path.join(root_dir, artist_tag,
                                               '*.wiki')):
            album = {'artist_tag': artist_tag,
                     'album_tag': os.path.splitext(os.path.basename(filename))[0],
                     'artist': "",
                     'album': "",
                     'year': 0,
                     'rating': 0,
                     'state': " "}
            path = os.path.join(root_dir, artist_tag, filename)
            # find the fields in the first lines of the file
            with open(path) as file_content:
                i = 0
                while i < 6:
                    words = file_content.readline().split()
                    tag = words[0][1:]
                    album[tag] = " ".join(words[1:])
                    album['year'] = int(album['year'])
                    album['rating'] = int(album['rating'])
                    i += 1
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
            artists.append({'artist_tag': artist_tag,
                            'artist': specific_albums[0]['artist'],
                            'rating': rating})
    sorted_artists = sorted(artists, key=lambda x: x['rating'], reverse=True)
    for i, artist in enumerate(sorted_artists):
        output += format_artist(i+1, artist)
    return output


def sort_ratings(albums):
    """Returns the rated albums sorted by decreasing rating"""
    sorted_albums = sorted(albums, key=lambda x: x['rating'], reverse=True)
    output = ""
    for i, album in enumerate(sorted_albums):
        output += format_album(i+1, album)
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
        sorted_albums = sorted([x for x in albums if x['year'] == year],
                               key=lambda x: x['rating'], reverse=True)
        for i, album in enumerate(sorted_albums):
            output += format_album(i+1, album)
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
        sorted_albums = sorted([x for x in albums if x['decade'] == decade],
                               key=lambda x: x['rating'], reverse=True)
        for i, album in enumerate(sorted_albums):
            output += format_album(i+1, album)
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
    return "{}. [[{}/|{}]] - {}\n".format(
        index, artist['artist_tag'], artist['artist'], artist['rating'])


def format_album(index, album):
    """Returns a formatted line of text describing the album"""
    return "{}. {} - {} - {} - {} - [[{}/{}|review]]\n".format(
        index, album['artist'], album['album'],
        album['year'], album['rating'],
        album['artist_tag'], album['album_tag'])


def format_review(album):
    """Returns a formatted line showing the review state and its reference"""
    return "- [{}] [[{}/{}]]\n".format(
        album['state'], album['artist_tag'], album['album_tag'])


def main():
    """Imports all reviews and writes all possible files"""
    albums = build_database()
    write_file(sort_ratings(albums), 'sorted_albums.wiki')
    write_file(sort_ratings_by_year(albums), 'sorted_by_year.wiki')
    write_file(sort_ratings_by_decade(albums), 'sorted_by_decade.wiki')
    write_file(all_reviews(albums), 'reviews.wiki')
    write_file(sort_reviews_state(albums), 'reviews_state.wiki')
    write_file(sort_reviews_date(albums), 'reviews_date.wiki')
    write_file(sort_artists(albums), 'sorted_artists.wiki')
    return albums

if __name__ == '__main__':
    main()
