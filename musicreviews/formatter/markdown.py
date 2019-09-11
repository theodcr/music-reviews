"""
Helpers for formatting reviews to markdown.
"""

from .utils import replace_enclosed_text_tags


def wiki_to_markdown(string):
    """Translates the string from vimwiki format to markdown."""
    string = replace_enclosed_text_tags(string, r"\*", "**")
    string = replace_enclosed_text_tags(string, "_", "*")
    return string
