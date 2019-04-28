"""
Helpers for formatting reviews to HTML.
"""

from jinja2 import Template

from .utils import replace_enclosed_text_tags


def wiki_to_html(string):
    """Translates the string from vimwiki format to HTML."""
    string = replace_enclosed_text_tags(string, '\*', '<b>', '</b>')
    string = replace_enclosed_text_tags(string, '_', '<i>', '</i>')
    return string


def fill_html(template, data):
    """Fills Jinja template with data to generate a HTML string."""
    template = Template(template)
    return template.render(**data)
