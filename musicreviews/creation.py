#!/usr/bin/env python3
"""Generates a review file using user input"""

import os
import datetime
import re
import readline

from .config import CONFIG
from . import generation


MIN_YEAR = int(CONFIG['creation']['min_year'])
MAX_YEAR = datetime.datetime.now().year
MIN_RATING = int(CONFIG['creation']['min_rating'])
MAX_RATING = int(CONFIG['creation']['max_rating'])


def import_template(filename="template.wiki"):
    """Returns the review template as a string"""
    with open(filename) as file_content:
        template = file_content.read()
    return template


def check_integer_input(prompt_text, min_value, max_value):
    """Prompts for an integer and checks if it is in the given range"""
    while True:
        value = input(prompt_text)
        if min_value <= int(value) <= max_value:
            break
        print(
            "Error, please enter a number between {} and {}".format(
                min_value, max_value
            )
        )
    return value


def completion_input(prompt_text, commands):
    """Prompts and allows tab-complete on the given list of commands"""

    def complete(text, state):
        """Completion function for readline"""
        for cmd in commands:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1

    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
    # tab completion on commands will stay enabled outside this scope
    return input(prompt_text)


def prompt_info(albums):
    """Prompts for album info input and returns the fields as strings"""
    known_artists = [x['artist'] for x in albums]
    artist = completion_input("Artist: ", known_artists)
    album = input("Album: ")
    year = check_integer_input("Year: ", MIN_YEAR, MAX_YEAR)
    rating = check_integer_input("Rating: ", MIN_RATING, MAX_RATING)
    return artist, album, year, rating


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out"""
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub('', string).lower()


def fill_template(template, artist, album, year, rating):
    """Fills the template review with the input"""
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    return template.format(
        date=day, artist=artist, album=album, year=year, rating=rating
    )


def write_review(content, folder, filename, root=os.getcwd(), ext='wiki'):
    """Writes the review file using the given data"""
    confirmation = input(
        "Confirm creation of review (y/N) {}/{}? ".format(folder, filename)
    )
    if confirmation == 'y':
        if not os.path.exists(os.path.join(root, folder)):
            os.makedirs(os.path.join(root, folder))
            print("Artist not known yet, created folder")
        filepath = os.path.join(root, folder, filename + "." + ext)
        if os.path.exists(filepath):
            print("File exists, operation aborted")
        else:
            with open(filepath, 'w') as file_content:
                file_content.write(content)


def create_review(albums):
    """Conducts the full procedure to create a review"""
    template = import_template()
    artist, album, year, rating = prompt_info(albums)
    review = fill_template(template, artist, album, year, rating)
    folder = alphanumeric_lowercase(artist)
    filename = alphanumeric_lowercase(album)
    write_review(review, folder, filename)


if __name__ == '__main__':
    ALBUMS = generation.build_database()
    create_review(ALBUMS)
    generation.main()
