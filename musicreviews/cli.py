"""
CLI of the package to access functions
"""

import click


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
    ctx.obj = {}


if __name__ == '__main__':
    main()
