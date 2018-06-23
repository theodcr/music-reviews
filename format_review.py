#!/usr/bin/env python3
"""Formats and exports a review file"""

import os
import re
import sys


def find_review():
    """Returns the relative path to the review"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            return path
        else:
            print(f"File {path} doesn't exist")


if __name__ == '__main__':
    find_review()

