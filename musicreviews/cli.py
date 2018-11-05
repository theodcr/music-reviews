"""
CLI of the package to access functions
"""

import os
from functools import partial

import click
from musicreviews import creation, generation
from musicreviews.config import CONFIG
from musicreviews.helpers import check_integer_input

MIN_RATING = int(CONFIG['creation']['min_rating'])
MAX_RATING = int(CONFIG['creation']['max_rating'])

GREET = """
    __  ___           _      ____            _
   /  |/  /_  _______(_)____/ __ \___ _   __(_)__ _      _______
  / /|_/ / / / / ___/ / ___/ /_/ / _ \ | / / / _ \ | /| / / ___/
 / /  / / /_/ (__  ) / /__/ _, _/  __/ |/ / /  __/ |/ |/ (__  )
/_/  /_/\__,_/____/_/\___/_/ |_|\___/|___/_/\___/|__/|__/____/
"""


@click.group(chain=True)
@click.pass_context
def main(ctx):
    """CLI for music reviews management"""
    click.echo(click.style(GREET, fg='magenta', bold=True))
    root_dir = os.path.abspath(CONFIG['path']['reviews_directory'])
    albums = generation.build_database(root_dir)
    ctx.obj = {}
    ctx.obj['root_dir'] = root_dir
    ctx.obj['albums'] = albums


@main.command()
@click.pass_context
def generate(ctx):
    generation.generate_all_lists(ctx.obj['albums'], ctx.obj['root_dir'])


@main.command()
@click.option('--uri', '-u')
@click.pass_context
def create(ctx, uri):
    click.prompt(
        "Rating",
        value_proc=partial(
            check_integer_input, min_value=MIN_RATING, max_value=MAX_RATING
        ),
    )
    # if uri is not None:
    # else:
    #     uri =
    # artist, album, year = creation.get_spotify_info(uri)
    # rating = prompt_rating()
    # creation.create_review(root_dir)
    # # update albums database
    # ctx.obj['albums'] = generation.build_database(root_dir)
    generation.generate_all_lists(ctx.obj['albums'], ctx.obj['root_dir'])


if __name__ == '__main__':
    main()
