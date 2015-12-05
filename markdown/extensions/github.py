from __future__ import unicode_literals
from ..extensions import Extension

extensions = [
    'delete',
    'githubemoji',
    'magiclink',
    'tasklist',
    'headeranchor',
    'superfences',
    'nl2br'
]

extension_configs = {}


class GithubExtension(Extension):
    """Add various extensions to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """Register extension instances."""

        md.registerExtensions(extensions, extension_configs)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return GithubExtension(*args, **kwargs)
