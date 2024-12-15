"""
Helpers for CLI UI and specific prompts.
"""

import re

import click

try:
    import readline

    readline_available = True
except ImportError:
    readline_available = False


GREET = r"""
    __  ___           _      ____            _
   /  |/  /_  _______(_)____/ __ \___ _   __(_)__ _      _______
  / /|_/ / / / / ___/ / ___/ /_/ / _ \ | / / / _ \ | /| / / ___/
 / /  / / /_/ (__  ) / /__/ _, _/  __/ |/ / /  __/ |/ |/ (__  )
/_/  /_/\__,_/____/_/\___/_/ |_|\___/|___/_/\___/|__/|__/____/
"""


def style_prompt(message):
    """Returns a unified style for click prompts."""
    return click.style(message, fg="cyan")


def style_info(message):
    """Returns a unified style for general echos about program state."""
    return click.style(message, fg="blue")


def style_error(message):
    """Returns a unified style for error echos."""
    return click.style(message, fg="red")


def style_enumerate(i, val):
    """Returns a unified style for enumerate items."""
    return click.style(f"{i:2d}", fg="magenta") + " " + click.style(val, fg="blue")


def style_album(artist, album, year):
    """Returns a unified style for albums."""
    return (
        click.style(str(artist), fg="magenta", bold=True)
        + click.style(" - ", fg="white")
        + click.style(str(album), fg="blue", bold=True)
        + click.style(" - ", fg="white")
        + click.style(str(year), fg="white", bold=True)
    )


def style_info_path(message, path):
    """Returns a unified style for information about a path."""
    return (
        style_info(message) + " " + click.style(click.format_filename(path), fg="white")
    )


def check_integer_known(value, possibles):
    """Converts and checks if the integer from the prompt is in gives possibilities."""
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"{value} is not a valid integer", param=value)
    if value in possibles:
        return value
    raise click.BadParameter(f"{value} is not known")


def check_integer_range(value, min_value, max_value):
    """Converts and checks if the integer from the click prompt is in given range."""
    try:
        value = int(value)
    except ValueError:
        raise click.BadParameter(f"{value} is not a valid integer", param=value)
    if min_value <= value <= max_value:
        return value
    raise click.BadParameter(f"{value} is not between {min_value} and {max_value}")


def list_integers_range(string, min_value, max_value):
    """Converts and checks a string containing a list of integers."""
    indices = re.split(r"\W+", string)
    clean_indices = [check_integer_range(idx, min_value, max_value) for idx in indices if idx != ""]
    return clean_indices


def list_strings_input(string):
    """Converts and checks a string containing a list of strings."""
    strings = re.split(r"\W+", string)
    strings = [i for i in strings if i != ""]
    return strings


def completion_input(prompt_text, commands, **kwargs):
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
    return click.prompt(prompt_text, **kwargs)
