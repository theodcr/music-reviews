"""
Helpers for CLI and UI
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
    """Returns a unified style for click prompts"""
    return click.style(message, fg='cyan')


def style_info(message):
    """Returns a unified style for general echos about program state"""
    return click.style(message, fg='cyan')


def style_enumerate(i, val):
    """Returns a unified style for enumerate items"""
    return click.style(f'{i:2d}', fg='magenta') + ' ' + click.style(val, fg='blue')
