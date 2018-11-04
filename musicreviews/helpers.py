"""CLI and helper functions"""

import re
import readline


def check_integer_input(prompt_text, min_value, max_value):
    """Prompts for an integer and checks if it is in the given range"""
    while True:
        value = input(prompt_text)
        if min_value <= int(value) <= max_value:
            break
        print(
            "Error, please enter a number between {} and {}".format(
                min_value, max_value
            )
        )
    return value


def completion_input(prompt_text, commands):
    """Prompts and allows tab-complete on the given list of commands"""

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
    return input(prompt_text)


def alphanumeric_lowercase(string):
    """Returns a lowercase version of the string with non-alphanumeric
    characters stripped out"""
    regex = re.compile('[^a-zA-Z0-9]')
    return regex.sub('', string).lower()
