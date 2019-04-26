"""
CLI helpers for specific prompts, and various helper functions.
"""

import re
try:
    import readline
    readline_available = True
except ImportError:
    readline_available = False

import click


def write_file(content, path, newline=False):
    """Writes the given content in a file, with an optional newline at the end."""
    with open(path, 'w') as file_content:
        file_content.write(content)
        if newline:
            file_content.write("\n")


def check_integer_input(value, min_value, max_value):
    """Converts and checks if the integer from the click prompt is in the given range."""
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"{value} is not a valid integer", param=value)
    if min_value <= value <= max_value:
        return value
    raise click.BadParameter(f"{value} is not between {min_value} and {max_value}")


def list_integers_input(string, min_value, max_value):
    """Converts and checks a string containing a list of integers."""
    indices = set(re.split('\W+', string))
    indices.discard('')
    clean_indices = [check_integer_input(idx, min_value, max_value) for idx in indices]
    return clean_indices


def completion_input(prompt_text, commands):
    """Returns a click prompt with tab-completion on the given list of commands."""

    def complete(text, state):
        """Completion function for readline."""
        for cmd in commands:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1

    if readline_available:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
        # tab completion on commands will stay enabled outside this scope
    return click.prompt(prompt_text)


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out.
    """
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub('', string).lower()


def escape_yaml_specials(string):
    """Surrounds the given string with quotes if it is not conform to YAML syntax."""
    alpha_string = alphanumeric_lowercase(string)
    if alpha_string == 'yes' or alpha_string == 'no':
        return '"' + string + '"'
    elif bool(re.search('^"', string)):
        return "'" + string + "'"
    elif bool(
        re.search("^'|^\? |: |^,|^&|^%|^@|^!|^\||^\*|^#|^- |^[|^]|^{|^}|^>", string)
    ):
        return '"' + string + '"'
    else:
        return string


def replace_enclosed_text_tags(string, tag_to_sub, opening_tag, closing_tag=None):
    """Replaces tags around enclosed text.
    For example _test_ -> **test** or <b>test</b>
    """
    closing_tag = closing_tag or opening_tag
    string = re.sub(
        '{0}([^{0}]+){0}'.format(tag_to_sub),
        f'{opening_tag}\\1{closing_tag}',
        string
    )
    return string
