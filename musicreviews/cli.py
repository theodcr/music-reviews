"""
CLI of the package to access functions
"""

import os
from functools import partial

import click
from musicreviews import creation, generation, helpers
from musicreviews.config import CONFIG
from powerspot.operations import get_artist_albums, search_artist

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
@click.option('--uri', '-u', prompt="Album URI (skip to use search)", default="")
@click.pass_context
def create(ctx, uri):
    if uri == "":
        known_artists = [x['artist'] for x in ctx.obj['albums']]
        artist_query = helpers.completion_input(
            style_prompt("Artist search"), known_artists
        )
        res_artists = search_artist(artist_query)['items']
        artists = [res_artists[i]['name'] for i in range(len(res_artists))]
        for i, artist in enumerate(artists):
            click.echo(style_enumerate(i, artist))
        artist_id = click.prompt(
            style_prompt("Choose artist index"),
            value_proc=partial(
                helpers.check_integer_input, min_value=0, max_value=len(artists) - 1
            ),
            default=0,
        )
        artist_uri = res_artists[artist_id]['uri']
        res_albums = get_artist_albums(artist_uri)['items']
        albums = [res_albums[i]['name'] for i in range(len(res_albums))]
        for i, album in enumerate(albums):
            click.echo(style_enumerate(i, album))
        album_id = click.prompt(
            style_prompt("Choose album index"),
            value_proc=partial(
                helpers.check_integer_input, min_value=0, max_value=len(albums) - 1
            ),
            default=0,
        )
        album_data = res_albums[album_id]
        album_uri = album_data['uri']
    click.prompt(
        style_prompt("Rating"),
        value_proc=partial(
            helpers.check_integer_input, min_value=MIN_RATING, max_value=MAX_RATING
        ),
    )
    # artist, album, year = creation.get_spotify_info(uri)
    # creation.create_review(root_dir)
    # # update albums database
    # ctx.obj['albums'] = generation.build_database(root_dir)


def style_prompt(message):
    """Returns a unified style for click prompts"""
    return click.style(message, fg='cyan')


def style_enumerate(i, val):
    """Returns a unified style for enumerate items"""
    return click.style(str(i), fg='magenta') + ' ' + click.style(val, fg='blue')


if __name__ == '__main__':
    main()
