"""
Mdownx.magiclink
An extension for Python Markdown.
Find http|ftp links and turn them to actual links

Modified to work with Sublime Markdown Preview
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..inlinepatterns import LinkPattern
from .. import util

RE_LINK = r"((ht|f)tp(s?)://(([a-zA-Z0-9\-._]+(\.[a-zA-Z0-9\-._]+)+)|localhost)(/?)([a-zA-Z0-9\-.?,'/\\+&%$#_]*)?([\d\w./%+-=&?:\\"',|~;]*)[^.,'"\s<])"


class MagiclinkPattern(LinkPattern):
    def handleMatch(self, m):
        el = util.etree.Element("a")
        el.text = m.group(2)
        el.set("href", self.sanitize_url(self.unescape(m.group(2).strip())))

        return el


class MagiclinkExtension(Extension):
    """Adds Easylink extension to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Adds support for turning html links to link tags"""

        md.inlinePatterns.add("magiclink", MagiclinkPattern(RE_LINK, md), "<not_strong")


def makeExtension(configs={}):
    return MagiclinkExtension(configs=dict(configs))
