"""
CLI of the package to access functions
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


@click.group(chain=True)
@click.pass_context
@click.option('--username', default=lambda: os.getenv('SPOTIFY_USER'))
def main(ctx, username):
    """CLI for music reviews management"""
    click.echo(click.style(ui.GREET, fg='magenta', bold=True))
    root_dir = os.path.abspath(CONFIG['path']['reviews_directory'])
    click.echo(ui.style_info_path("Review library in directory", root_dir))
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
    click.echo(ui.style_info_path("Managing queue stored in", queue_path))

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
            queue.append(
                {
                    'artist': album_data['artists'][0]['name'],
                    'album': album_data['name'],
                    'year': album_data['release_date'][:4],
                    'uri': uri,
                }
            )
        click.echo(ui.style_info(f"Queue contains {len(queue)} albums"))
        # save current queue
        with open(queue_path, 'w') as file_content:
            file_content.write(json.dumps(queue))

    # show artists in queue
    artists_in_queue = sorted(set([album['artist'] for album in queue]))
    click.echo(ui.style_info("Artists in queue:"))
    for i, artist in enumerate(artists_in_queue):
        click.echo(ui.style_enumerate(i, artist))

    # prompt the user for a direct artist search
    artist = utils.completion_input(
        ui.style_prompt("Search artist in queue"), [album['artist'] for album in queue]
    )
    matches = [album for album in queue if album['artist'] == artist]

    # if no matches, prompt the user for each album in the queue
    if len(matches) == 0:
        click.echo(ui.style_info("No matches found, going over the whole queue"))
        matches = queue

    # prompt for review creation and delete reviewed albums from queue
    uris_to_pop = []
    idx = 0
    length = len(matches)
    for album in matches:
        idx += 1
        click.echo(
            click.style(f"Item {idx}/{length}: ", fg='white')
            + ui.style_album(album['artist'], album['album'], album['year'])
        )
        if click.confirm(ui.style_prompt("Review this album")):
            # pop album from queue only if review creation is confirmed
            if ctx.invoke(create, uri=album['uri']):
                uris_to_pop.append(album['uri'])
                # rewrite queue in case procedure is canceled later
                with open(queue_path, 'w') as file_content:
                    file_content.write(
                        json.dumps(
                            [
                                album
                                for album in queue
                                if album['uri'] not in uris_to_pop
                            ]
                        )
                    )


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
                utils.check_integer_input,
                min_value=int(CONFIG['creation']['min_year']),
                max_value=datetime.datetime.now().year,
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
            utils.check_integer_input,
            min_value=int(CONFIG['creation']['min_rating']),
            max_value=int(CONFIG['creation']['max_rating']),
        ),
    )

    root_dir = ctx.obj['root_dir']
    folder = utils.alphanumeric_lowercase(artist)
    filename = utils.alphanumeric_lowercase(album)
    click.echo(
        '\n'
        + click.style("Creating review for album:", fg='cyan')
        + '\n'
        + ui.style_album(artist, album, year)
        + '\n'
        + click.style("Filename: ", fg='cyan')
        + click.style(root_dir + '/', fg='white')
        + click.style(folder, fg='magenta', bold=True)
        + click.style('/', fg='white')
        + click.style(filename, fg='blue', bold=True)
        + '\n'
    )
    if click.confirm(ui.style_prompt("Confirm creation of review"), default=True):
        template = creator.import_template(root=root_dir)
        review = creator.fill_template(
            template, artist, album, year, rating, uri, picks=tracks_idx, tracks=tracks
        )
        creator.write_review(review, folder, filename, root=root_dir)
        return True
    return False


if __name__ == '__main__':
    main()
