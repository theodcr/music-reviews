"""
CLI of the package to access functions
Note: queue subcommands should be associeted to a queue group, but nesting chain
commands is not possible in click yet
"""

import datetime
import json
import os
from functools import partial

import click

from musicreviews import creator, indexer, ui, utils
from musicreviews.config import CONFIG
from powerspot.helpers import get_username
from powerspot.operations import (
    get_album,
    get_artist_albums,
    get_saved_albums,
    search_artist,
)

MIN_RATING = int(CONFIG['creation']['min_rating'])
MAX_RATING = int(CONFIG['creation']['max_rating'])
MIN_YEAR = int(CONFIG['creation']['min_year'])
MAX_YEAR = datetime.datetime.now().year


@click.group(chain=True)
@click.pass_context
@click.option('--username', default=lambda: os.getenv('SPOTIFY_USER'))
def main(ctx, username):
    """CLI for music reviews management"""
    click.echo(click.style(ui.GREET, fg='magenta', bold=True))
    root_dir = os.path.abspath(CONFIG['path']['reviews_directory'])
    click.echo(ui.style_info(f"Review library in directory {root_dir}"))
    albums = indexer.build_database(root_dir)

    if username is None:
        username = get_username()
    click.echo(ui.style_info(f"Welcome {username}\n"))

    ctx.obj = {}
    ctx.obj['root_dir'] = root_dir
    ctx.obj['albums'] = albums
    ctx.obj['username'] = username


@main.command()
@click.pass_context
def generate(ctx):
    """Generate lists of reviews indexes"""
    indexer.generate_all_lists(ctx.obj['albums'], ctx.obj['root_dir'])
    click.echo(ui.style_info("Lists generated"))


@main.command()
@click.pass_context
def queue(ctx):
    """Manage the queue of album to review"""
    queue_path = os.path.abspath(CONFIG['path']['queue'])
    click.echo(ui.style_info(f"Managing queue stored in {queue_path}"))

    # retrieve queue
    if os.path.exists(queue_path):
        with open(queue_path, 'r') as file_content:
            queue = json.load(file_content)
    else:
        queue = []
    click.echo(ui.style_info(f"Queue contains {len(queue)} albums"))

    # update queue with user library albums
    if click.confirm(ui.style_prompt("Update queue with library albums")):
        saved_albums = get_saved_albums(ctx.obj['username'])
        saved_uris = set([album['album']['uri'] for album in saved_albums])
        known_uris = set([album['uri'] for album in ctx.obj['albums']])
        queue_uris = set([album['uri'] for album in queue])
        for uri in saved_uris - known_uris - queue_uris:
            album_data = get_album(uri)
            queue.append({
                'artist': album_data['artists'][0]['name'],
                'album': album_data['name'],
                'year': album_data['release_date'][:4],
                'uri': uri,
            })
        click.echo(ui.style_info(f"Queue contains {len(queue)} albums"))
    # save updated queue
    with open(queue_path, 'w') as file_content:
        file_content.write(json.dumps(queue))

    # update queue with user library albums
    idx = 0
    length = len(queue)
    uris_to_pop = []
    for album in queue:
        idx += 1
        click.echo(
            click.style(f"Item {idx}/{length}: ", fg='white')
            + click.style(album['artist'], fg='magenta', bold=True)
            + click.style(' - ', fg='white')
            + click.style(album['album'], fg='blue', bold=True)
        )
        if click.confirm(ui.style_prompt("Review this album")):
            if ctx.invoke(create, uri=album['uri']):
                uris_to_pop.append(album['uri'])
    updated_queue = [album for album in queue if album['uri'] not in uris_to_pop]

    # save updated queue
    with open(queue_path, 'w') as file_content:
        file_content.write(json.dumps(updated_queue))


@main.command()
@click.option('--uri', '-u', help="direct input of album URI")
@click.option('--manual', '-m', is_flag=True, help="manual input of album data")
@click.option('-y', is_flag=True, help="confirm review creation")
@click.pass_context
def create(ctx, uri, manual, y):
    """Create a review using data retrieved from Spotify or manually entered"""
    known_artists = [x['artist'] for x in ctx.obj['albums']]
    if manual:
        # manual input of data
        artist = utils.completion_input(ui.style_prompt("Artist"), known_artists)
        album = click.prompt(ui.style_prompt("Album"))
        year = click.prompt(
            ui.style_prompt("Year"),
            value_proc=partial(
                utils.check_integer_input, min_value=MIN_YEAR, max_value=MAX_YEAR
            ),
        )
        # arbitrary maximum number of tracks
        tracks_idx = click.prompt(
            ui.style_prompt("Favorite tracks numbers"),
            value_proc=partial(utils.list_integers_input, min_value=1, max_value=100),
        )
        tracks = None
    else:
        if uri is None:
            # incremental search to select album in Spotify collection
            artist_query = utils.completion_input(
                ui.style_prompt("Artist search"), known_artists
            )

            res_artists = search_artist(artist_query)['items']
            artists = [artist['name'] for artist in res_artists]
            for i, artist in enumerate(artists):
                click.echo(ui.style_enumerate(i, artist))
            artist_idx = click.prompt(
                ui.style_prompt("Choose artist index"),
                value_proc=partial(
                    utils.check_integer_input, min_value=0, max_value=len(artists) - 1
                ),
                default=0,
            )
            artist_uri = res_artists[artist_idx]['uri']

            res_albums = get_artist_albums(artist_uri)['items']
            albums = [album['name'] for album in res_albums]
            for i, album in enumerate(albums):
                click.echo(ui.style_enumerate(i, album))
            album_idx = click.prompt(
                ui.style_prompt("Choose album index"),
                value_proc=partial(
                    utils.check_integer_input, min_value=0, max_value=len(albums) - 1
                ),
                default=0,
            )
            uri = res_albums[album_idx]['uri']
        album_data = get_album(uri)
        # retrieve useful fields from Spotify data
        artist = album_data['artists'][0]['name']
        album = album_data['name']
        year = album_data['release_date'][:4]
        tracks = [track['name'] for track in album_data['tracks']['items']]
        # list tracks, starting at index 1
        for i, track in enumerate(tracks):
            click.echo(ui.style_enumerate(i + 1, track))

        tracks_idx = click.prompt(
            ui.style_prompt("Favorite tracks numbers"),
            value_proc=partial(
                utils.list_integers_input, min_value=1, max_value=len(tracks)
            ),
        )

    rating = click.prompt(
        ui.style_prompt("Rating"),
        value_proc=partial(
            utils.check_integer_input, min_value=MIN_RATING, max_value=MAX_RATING
        ),
    )

    root_dir = ctx.obj['root_dir']
    folder = utils.alphanumeric_lowercase(artist)
    filename = utils.alphanumeric_lowercase(album)
    click.echo(
        '\n'
        + click.style("Creating review for album:", fg='cyan')
        + '\n'
        + click.style(artist, fg='magenta', bold=True)
        + click.style(' - ', fg='white')
        + click.style(album, fg='blue', bold=True)
        + '\n'
        + click.style("Filename: ", fg='cyan')
        + click.style(root_dir + '/', fg='white')
        + click.style(folder, fg='magenta', bold=True)
        + click.style('/', fg='white')
        + click.style(filename, fg='blue', bold=True)
        + '\n'
    )
    if click.confirm(ui.style_prompt("Confirm creation of review")):
        template = creator.import_template(root=root_dir)
        review = creator.fill_template(
            template, artist, album, year, rating, uri, picks=tracks_idx, tracks=tracks
        )
        creator.write_review(review, folder, filename, root=root_dir)
        click.echo(ui.style_info("Review created"))
        return True
    return False


if __name__ == '__main__':
    main()
