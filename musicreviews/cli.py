"""
CLI of the package to access functions.
"""

import datetime
import json
import os
from functools import partial

import click
from powerspot.cli import get_username
from powerspot.operations import (
    create_playlist,
    get_album,
    get_artist_albums,
    get_playing_track,
    get_playlists,
    get_saved_albums,
    replace_playlist_tracks,
    search_artist,
)

from musicreviews import configuration, formatter, indexer, reader, ui, writer


@click.group(chain=True)
@click.pass_context
@click.option("--username", default=lambda: os.getenv("SPOTIFY_USER"))
def main(ctx, username):
    """CLI for album reviews management."""
    click.echo(click.style(ui.GREET, fg="magenta", bold=True))
    ctx.obj = {}

    config_path, config_content = configuration.load_config()
    click.echo(ui.style_info_path("Loading configuration at", config_path))
    if config_content is None:
        click.echo(ui.style_error("Configuration not found, running setup command"))
        config_content = ctx.invoke(setup)

    root_dir = os.path.abspath(config_content["path"]["reviews_directory"])
    click.echo(ui.style_info_path("Loading review library from directory", root_dir))
    albums = reader.build_database(root_dir)

    if username is None:
        username = get_username()
    click.echo(ui.style_info(f"Welcome {username}\n"))

    ctx.obj["root_dir"] = root_dir
    ctx.obj["albums"] = albums
    ctx.obj["username"] = username
    ctx.obj["config"] = config_content


@main.command()
@click.pass_context
def index(ctx):
    """Generate various reviews indexes and lists."""
    indexer.generate_all_indexes(ctx.obj["albums"], ctx.obj["root_dir"], extension="md")
    click.echo(ui.style_info("Indexes generated"))


@main.command()
@click.pass_context
def queue(ctx):
    """Manage the queue of albums to review."""
    queue_path = os.path.abspath(ctx.obj["config"]["path"]["queue"])
    click.echo(ui.style_info_path("Managing queue stored in", queue_path))

    # retrieve queue
    if os.path.exists(queue_path):
        with open(queue_path, "r") as file_content:
            queue = json.load(file_content)
    else:
        queue = []
    click.echo(ui.style_info(f"Queue contains {len(queue)} albums"))

    # update queue with user library albums
    if click.confirm(ui.style_prompt("Update queue with library albums")):
        saved_albums = get_saved_albums(ctx.obj["username"])
        saved_uris = set([album["album"]["uri"] for album in saved_albums])
        known_uris = set([album["uri"] for album in ctx.obj["albums"]])
        queue_uris = set([album["uri"] for album in queue])
        # prompt for unreviewed albums that were removed from library
        for uri in queue_uris - saved_uris:
            album = next(album for album in queue if album["uri"] == uri)
            click.echo(
                click.style("Unreviewed album was removed from library: ", fg="white")
                + ui.style_album(album["artist"], album["album"], album["year"])
            )
            if click.confirm(ui.style_prompt("Remove from queue"), default=True):
                queue_uris.remove(uri)
                queue.remove(album)
        # add new uris to queue
        for uri in saved_uris - known_uris - queue_uris:
            album_data = get_album(uri)
            queue.append(
                {
                    "artist": album_data["artists"][0]["name"],
                    "album": album_data["name"],
                    "year": album_data["release_date"][:4],
                    "uri": uri,
                }
            )
        click.echo(ui.style_info(f"Queue contains {len(queue)} albums"))
        # save current queue
        writer.write_file(json.dumps(queue), queue_path)

    # show artists in queue
    artists_in_queue = sorted(set([album["artist"] for album in queue]))
    click.echo(ui.style_info("Artists in queue:"))
    for i, artist in enumerate(artists_in_queue):
        click.echo(ui.style_enumerate(i, artist))

    # prompt the user for a direct artist search
    artist = ui.completion_input(
        ui.style_prompt("Search artist in queue"), artists_in_queue
    )
    matches = [album for album in queue if album["artist"] == artist]

    # if no matches, prompt the user for each album in the queue
    if len(matches) == 0:
        click.echo(ui.style_info("No matches found, going over the whole queue"))
        matches = queue

    # prompt for review creation and delete reviewed albums from queue
    idx = 0
    length = len(matches)
    for match in matches:
        idx += 1
        click.echo(
            click.style(f"Item {idx}/{length}: ", fg="white")
            + ui.style_album(match["artist"], match["album"], match["year"])
        )
        if click.confirm(ui.style_prompt("Review this album")):
            # pop album from queue only if review creation is confirmed
            if ctx.invoke(create, uri=match["uri"]):
                queue = [album for album in queue if album["uri"] != match["uri"]]
                # rewrite queue in case procedure is cancelled later
                writer.write_file(json.dumps(queue), queue_path)


@main.command()
@click.option("--uri", "-u", help="direct input of album URI")
@click.option("--playing", "-p", is_flag=True, help="use currently playing album")
@click.option("--manual", "-m", is_flag=True, help="manual input of album data")
@click.option("-y", is_flag=True, help="confirm review creation")
@click.pass_context
def create(ctx, uri, playing, manual, y):
    """Create a review using data retrieved from Spotify or manually entered."""
    known_artists = [x["artist"] for x in ctx.obj["albums"]]
    if manual:
        # manual input of data
        artist = ui.completion_input(ui.style_prompt("Artist"), known_artists)
        album = click.prompt(ui.style_prompt("Album"))
        if artist in known_artists:
            artist_albums = [
                x["album"] for x in ctx.obj["albums"] if x["artist"] == artist
            ]
            if album in artist_albums:
                click.echo(ui.style_error("Review already exists, operation aborted"))
                return False
        year = click.prompt(
            ui.style_prompt("Year"),
            value_proc=partial(
                ui.check_integer_range,
                min_value=int(ctx.obj["config"]["creation"]["min_year"]),
                max_value=datetime.datetime.now().year,
            ),
        )
        # arbitrary maximum number of tracks
        tracks_idx = click.prompt(
            ui.style_prompt("Favorite tracks numbers"),
            value_proc=partial(ui.list_integers_range, min_value=1, max_value=100),
        )
        tracks = None
        cover = None
    else:
        if playing:
            # album from currently playing track
            track = get_playing_track(ctx.obj["username"])
            if track is not None:
                uri = track["item"]["album"]["uri"]

        if uri is None:
            # incremental search to select album in Spotify collection
            artist_query = ui.completion_input(
                ui.style_prompt("Artist search"), known_artists
            )

            res_artists = search_artist(artist_query)["items"]
            artists = [artist["name"] for artist in res_artists]
            for i, artist in enumerate(artists):
                click.echo(ui.style_enumerate(i, artist))
            artist_idx = click.prompt(
                ui.style_prompt("Choose artist index"),
                value_proc=partial(
                    ui.check_integer_range, min_value=0, max_value=len(artists) - 1
                ),
                default=0,
            )
            artist_uri = res_artists[artist_idx]["uri"]

            res_albums = get_artist_albums(
                artist_uri, country=ctx.obj["config"]["spotify"]["country"]
            )
            albums = [album["name"] for album in res_albums]
            for i, album in enumerate(albums):
                click.echo(ui.style_enumerate(i, album))
            album_idx = click.prompt(
                ui.style_prompt("Choose album index"),
                value_proc=partial(
                    ui.check_integer_range, min_value=0, max_value=len(albums) - 1
                ),
                default=0,
            )
            uri = res_albums[album_idx]["uri"]
        album_data = get_album(uri)
        # retrieve useful fields from Spotify data
        artist = album_data["artists"][0]["name"]
        album = album_data["name"]
        if artist in known_artists:
            artist_albums = [
                x["album"] for x in ctx.obj["albums"] if x["artist"] == artist
            ]
            if album in artist_albums:
                click.echo(ui.style_error("Review already exists, operation aborted"))
                return False
        year = album_data["release_date"][:4]
        tracks = [track["name"] for track in album_data["tracks"]["items"]]
        cover = album_data["images"][0]["url"]

        click.echo(
            "\n"
            + click.style("Creating review for album: ", fg="cyan")
            + ui.style_album(artist, album, year)
        )

        # list tracks, starting at index 1
        for i, track in enumerate(tracks):
            click.echo(ui.style_enumerate(i + 1, track))

        tracks_idx = click.prompt(
            ui.style_prompt("Favorite tracks numbers (comma separated)"),
            value_proc=partial(
                ui.list_integers_range, min_value=1, max_value=len(tracks)
            ),
        )

    rating = click.prompt(
        ui.style_prompt("Rating"),
        value_proc=partial(
            ui.check_integer_range,
            min_value=int(ctx.obj["config"]["creation"]["min_rating"]),
            max_value=int(ctx.obj["config"]["creation"]["max_rating"]),
        ),
    )

    tags = click.prompt(
        ui.style_prompt("Tags (comma separated)"), value_proc=ui.list_strings_input
    )

    root_dir = ctx.obj["root_dir"]
    folder = formatter.utils.alphanumeric_lowercase(artist)
    filename = formatter.utils.alphanumeric_lowercase(album)
    click.echo(
        click.style("Creating review at: ", fg="cyan")
        + click.style(root_dir + "/", fg="white")
        + click.style(folder, fg="magenta", bold=True)
        + click.style("/", fg="white")
        + click.style(filename, fg="blue", bold=True)
    )
    if click.confirm(ui.style_prompt("Confirm creation of review"), default=True) or y:
        template = reader.read_file(root_dir, "template.md")
        review = writer.fill_review_template(
            template,
            artist,
            album,
            year,
            rating,
            uri,
            cover,
            picks=tracks_idx,
            tracks=tracks,
            tags=tags,
        )
        writer.write_review(review, folder, filename, root=root_dir)
        click.echo(ui.style_info("Review created"))
        return True
    return False


@main.command()
@click.pass_context
def setup(ctx):
    """Configure review library settings."""
    __, template_config = configuration.load_config(load_template=True)
    __, config = configuration.load_config()
    if config is None:
        config = template_config

    click.echo(ui.style_info("Setting configuration fields:"))
    for category_name, category in config.items():
        for field, value in category.items():
            new_value = click.prompt(ui.style_prompt(field), default=value)
            if category_name == "path":
                new_value = os.path.abspath(new_value)
                click.echo(ui.style_info_path("Absolute path is", new_value))
            config[category_name][field] = new_value

    click.echo(ui.style_info("Checking configuration:"))
    for category_name, category in template_config.items():
        if category_name not in config:
            click.echo(
                ui.style_error(f"Category {category_name} not in config, creating")
            )
            config[category_name] = {}
        for field, value in category.items():
            if field not in config[category_name]:
                click.echo(ui.style_error(f"Field {field} not in config, creating"))
                new_value = click.prompt(ui.style_prompt(field), default=value)
                if category_name == "path":
                    new_value = os.path.abspath(new_value)
                    click.echo(ui.style_info_path("Absolute path is", new_value))
                config[category_name][field] = new_value

    click.echo(
        ui.style_info_path("Saved configuration at", configuration.write_config(config))
    )
    click.echo(
        ui.style_info_path(
            "Copied review template to",
            configuration.copy_template_review(
                os.path.abspath(config["path"]["reviews_directory"])
            ),
        )
    )
    click.echo(
        ui.style_info_path(
            "Copied HTML/CSS export templates to",
            configuration.copy_template_html(config["path"]["export_directory"]),
        )
    )
    return config


@main.command()
@click.pass_context
@click.option(
    "--all", "-a", is_flag=True, help="export all reviews and indexes in library"
)
@click.option("--index", "-i", is_flag=True, help="export indexes")
def export(ctx, all, index):
    """Exports a review or all reviews to HTML."""
    export_dir = ctx.obj["config"]["path"]["export_directory"]
    base_url = ctx.obj["config"]["web"]["base_url"]
    click.echo(ui.style_info_path("Exporting to directory", export_dir))

    if all or index:
        indexer.generate_all_indexes(
            ctx.obj["albums"], export_dir, extension="html", base_url=base_url
        )
        click.echo(ui.style_info("Indexes generated"))
    if index:
        return

    if all:
        albums_to_export = ctx.obj["albums"]
    else:
        # prompt to choose artist then album to export
        artist_tags = [x["artist_tag"] for x in ctx.obj["albums"]]
        artist_tag = ui.completion_input(
            ui.style_prompt("Artist tag of review to export"),
            artist_tags,
            type=click.Choice(artist_tags),
            show_choices=False,
        )

        artist_albums = [
            album for album in ctx.obj["albums"] if album["artist_tag"] == artist_tag
        ]
        album_tags = [album["album_tag"] for album in artist_albums]
        click.echo(ui.style_info("Album reviews tags:"))
        for i, tag in enumerate(album_tags):
            click.echo(ui.style_enumerate(i, tag))
        album_tag = ui.completion_input(
            ui.style_prompt("Album tag of review to export"),
            album_tags,
            type=click.Choice(album_tags),
            show_choices=False,
        )

        albums_to_export = [
            album for album in artist_albums if album["album_tag"] == album_tag
        ]

    for album in albums_to_export:
        click.echo(ui.style_info(f"{album['artist_tag']}/{album['album_tag']}"))
        writer.export_review(album, root=export_dir, base_url=base_url)
    click.echo(ui.style_info("Reviews exported"))

    # build artist indexes
    artist_tags = set([album["artist_tag"] for album in albums_to_export])
    for artist_tag in artist_tags:
        specific_albums = sorted(
            [x for x in albums_to_export if x["artist_tag"] == artist_tag],
            key=lambda x: (x["year"], x["rating"]),
            reverse=True,
        )
        content = formatter.html.parse_list(
            specific_albums, formatter.html.format_album
        )
        index_template = reader.read_file(export_dir, "template_index.html")
        title = specific_albums[0]["artist"]
        content = index_template.format(title=title, base_url=base_url, content=content)
        writer.write_file(content, os.path.join(export_dir, artist_tag, "index.html"))
    click.echo(ui.style_info("Artist indexes generated"))


@main.command()
@click.option("--all", "-a", is_flag=True, help="create playlists for all years")
@click.pass_context
def playlists(ctx, all):
    """Upload/update playlists of yearly favorite tracks to Spotify account."""
    years = set([album["year"] for album in ctx.obj["albums"]])
    if not all:
        year = click.prompt(
            ui.style_prompt("Year to upload"),
            value_proc=partial(ui.check_integer_known, possibles=years),
        )
        years = [year]

    playlists = get_playlists(ctx.obj["username"])
    for year in years:
        name = f"{year} favorite tracks"
        try:
            playlist_id = next(pl["id"] for pl in playlists if pl["name"] == name)
        except StopIteration:
            # playlist does not exist
            res = create_playlist(username=ctx.obj["username"], name=name, public=False)
            playlist_id = res["id"]
        sorted_albums = sorted(
            [x for x in ctx.obj["albums"] if x["year"] == year],
            key=lambda x: x["rating"],
            reverse=True,
        )
        year_tracks = []
        for album in sorted_albums:
            if album["picks"] is None:
                continue
            album_data = get_album(album["uri"])
            track_ids = [track["uri"] for track in album_data["tracks"]["items"]]
            year_tracks += [track_ids[i - 1] for i in album["picks"]]
        replace_playlist_tracks(
            username=ctx.obj["username"], playlist_id=playlist_id, track_ids=year_tracks
        )


@main.command()
@click.option("--year", "-y", help="years filter, for example 2016, +2010, -1990")
@click.option("--rating", "-r", help="rating filter, for example 82, +80, -60")
@click.option("--tags", "-t", help="tags filter, for example rock,electro")
@click.option("--sort", "-s", help="sorting fields, for example rating")
@click.option("--ascending", "-a", is_flag=True, help="sort by ascending value")
@click.pass_context
def query(ctx, year, rating, tags, sort, ascending):
    """Query, filter and sort reviews."""
    albums = ctx.obj["albums"]

    if year is not None:
        if "=" in year:
            albums = [x for x in albums if x["year"] == int(year.replace("=", ""))]
        elif "+" in year:
            albums = [x for x in albums if x["year"] >= int(year.replace("+", ""))]
        elif "-" in year:
            albums = [x for x in albums if x["year"] <= int(year.replace("-", ""))]

    if rating is not None:
        albums = [x for x in albums if x["rating"] == int(rating)]
        if "=" in rating:
            albums = [x for x in albums if x["rating"] == int(rating.replace("=", ""))]
        elif "+" in rating:
            albums = [x for x in albums if x["rating"] >= int(rating.replace("+", ""))]
        elif "-" in rating:
            albums = [x for x in albums if x["rating"] <= int(rating.replace("-", ""))]

    if tags is not None:
        query_tags = set(tags.split(","))
        albums = [x for x in albums if query_tags.issubset(set(x["tags"]))]

    if sort is not None:
        reverse = not ascending if ascending is not None else True
        albums = sorted(albums, key=lambda x: x[sort], reverse=reverse)

    for album in albums:
        click.echo(ui.style_album(album["artist"], album["album"], album["year"]))


if __name__ == "__main__":
    main()
