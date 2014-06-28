"""
Mdownx.delete
An extension for Python Markdown.
Adds support for ~~strike~~ => <del>strike</del>

Modified to work with Sublime Markdown Preview
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..inlinepatterns import SimpleTagPattern

RE_DEL = r"(\~{2})(.+?)\2"


class DeleteExtension(Extension):
    """Adds delete extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """Add support for <del>test</del> tags as ~~test~~"""

        md.inlinePatterns.add("del", SimpleTagPattern(RE_DEL, "del"), "<not_strong")


def makeExtension(configs={}):
    return DeleteExtension(configs=dict(configs))
