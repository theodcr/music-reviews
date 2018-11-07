"""Generates a review file using user input"""

import datetime
import os

from .helpers import alphanumeric_lowercase


def import_template(root=os.getcwd(), filename="template.wiki"):
    """Returns the review template as a string"""
    with open(os.path.join(root, filename)) as file_content:
        template = file_content.read()
    return template


def fill_template(template, artist, album, year, rating):
    """Fills the template review with the input"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return template.format(
        date=today, artist=artist, album=album, year=year, rating=rating
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


def create_review(root_dir, artist, album, year, rating):
    """Create a review file using provided fields"""
    template = import_template()
    review = fill_template(template, artist, album, year, rating)
    folder = alphanumeric_lowercase(artist)
    filename = alphanumeric_lowercase(album)
    write_review(review, folder, filename, root=root_dir)
