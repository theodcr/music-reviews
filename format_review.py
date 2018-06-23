#!/usr/bin/env python3
"""Formats and exports a review file"""

import os
import re
import sys
import generate_lists


def read_file(filename):
    """Returns the review as a string"""
    with open(filename, 'r') as file_content:
        output = file_content.read()
    return output


def write_file(content, filename):
    """Writes the given content in a file"""
    with open(filename, 'w') as file_content:
        file_content.write(content)


def find_review():
    """Returns the relative path to the review"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            return path
        else:
            print(f"File {path} doesn't exist")


def strip_review(string):
    """Returns the body of the review, strips the header and footer"""
    lines = string.split("\n")
    body = ""
    for line in lines:
        if len(line) > 0 and line[0] == "%":
            continue
        if len(line) > 4 and line[:5] == "Picks":
            body += line
            break
        body += line
    return body


def format_rating(album):
    """Format the album rating in a short note in Wiki syntax"""
    output = f"\n*Note :* {album['rating']}/100"
    if album['rating'] % 10 != 0:
        output += f", arrondi à {round(album['rating']/10)}/10"
    output += "\n"
    return output


def markdown_wiki_to_markdown(string):
    """Translates the strin from Wiki format to Markdown"""
    string = re.sub('\*', '**', string)
    string = re.sub('_', '*', string)
    return string


if __name__ == '__main__':
    filename = find_review()
    content = read_file(filename)
    #os.path.basename(os.path.dirname(b)) # for artist
    # for album: see generate_lists
