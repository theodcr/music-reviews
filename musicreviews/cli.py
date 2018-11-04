"""
CLI of the package to access functions
"""

import click

from musicreviews import generation


GREET = """
    __  ___           _      ____            _
   /  |/  /_  _______(_)____/ __ \___ _   __(_)__ _      _______
  / /|_/ / / / / ___/ / ___/ /_/ / _ \ | / / / _ \ | /| / / ___/
 / /  / / /_/ (__  ) / /__/ _, _/  __/ |/ / /  __/ |/ |/ (__  )
/_/  /_/\__,_/____/_/\___/_/ |_|\___/|___/_/\___/|__/|__/____/
"""


@click.group(chain=True)
@click.pass_context
def main(ctx, username):
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


if __name__ == '__main__':
    main()
