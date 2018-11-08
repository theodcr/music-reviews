"""CLI and helper functions"""

import re
import readline

import click


def check_integer_input(value, min_value, max_value):
    """Converts and checks if the integer from the click prompt is in the given range"""
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"{value} is not a valid integer", param=value)
    if min_value <= value <= max_value:
        return value
    raise click.BadParameter(f"{value} is not between {min_value} and {max_value}")


def list_integers_input(string, min_value, max_value):
    """Converts and checks a string containing a list of integers"""
    indices = set(re.split('\W+', string))
    indices.discard('')
    clean_indices = [check_integer_input(idx, min_value, max_value) for idx in indices]
    return clean_indices


def completion_input(prompt_text, commands):
    """Returns a click prompt with tab-completion on the given list of commands"""

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
    return click.prompt(prompt_text)


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out"""
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub('', string).lower()
