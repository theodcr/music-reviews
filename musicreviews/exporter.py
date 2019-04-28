"""
Helpers for exporting a written to different formats review.
"""

from .creator import fill_template
from .io import read_file, write_review
from .formatter import html, markdown, utils
from .formatter.utils import replace_track_tags


def export_review(data, root, extension='md'):
    """Exports review in given format. Formats metadata and content."""
    template = read_file(root, 'template.' + extension)
    data['content'] = utils.replace_track_tags(data['content']).format(**data)

    if extension == 'md':
        data['content'] = markdown.wiki_to_markdown(data['content'])
        # ensure tracks are sorted
        tracks = [data['tracks'][i] for i in sorted(data['tracks'])]
        # use general review template
        formatted_review = fill_template(
            template=template,
            artist=data['artist'],
            album=data['album'],
            year=data['year'],
            rating=data['rating'],
            uri=data['uri'],
            picks=data['picks'],
            tracks=tracks,
            state=data['state'],
            content=data['content'],
            date=data['date']
        )
    else:
        data['content'] = html.wiki_to_html(data['content'])
        formatted_review = html.fill_html(template, data)
    write_review(
        content=formatted_review,
        folder=data['artist_tag'],
        filename=data['album_tag'],
        root=root,
        extension=extension,
        overwrite=True
    )
