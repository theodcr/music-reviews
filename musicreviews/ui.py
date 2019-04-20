"""
Helpers for CLI appearence and UI.
"""

import click

GREET = """
    __  ___           _      ____            _
   /  |/  /_  _______(_)____/ __ \___ _   __(_)__ _      _______
  / /|_/ / / / / ___/ / ___/ /_/ / _ \ | / / / _ \ | /| / / ___/
 / /  / / /_/ (__  ) / /__/ _, _/  __/ |/ / /  __/ |/ |/ (__  )
/_/  /_/\__,_/____/_/\___/_/ |_|\___/|___/_/\___/|__/|__/____/
"""


def style_prompt(message):
    """Returns a unified style for click prompts."""
    return click.style(message, fg='cyan')


def style_info(message):
    """Returns a unified style for general echos about program state."""
    return click.style(message, fg='blue')


def style_error(message):
    """Returns a unified style for error echos."""
    return click.style(message, fg='red')


def style_enumerate(i, val):
    """Returns a unified style for enumerate items."""
    return click.style(f'{i:2d}', fg='magenta') + ' ' + click.style(val, fg='blue')


def style_album(artist, album, year):
    """Returns a unified style for albums."""
    return (
        click.style(artist, fg='magenta', bold=True)
        + click.style(' - ', fg='white')
        + click.style(album, fg='blue', bold=True)
        + click.style(' - ', fg='white')
        + click.style(year, fg='white', bold=True)
    )


def style_info_path(message, path):
    """Returns a unified style for information about a path."""
    return style_info(message) + ' ' + click.style(click.format_filename(path), fg='white')
