"""
pymdownx.magiclink
An extension for Python Markdown.
Find http|ftp links and email address and turn them to actual links

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..inlinepatterns import LinkPattern
from .. import util

RE_MAIL = r'''(?x)(?i)
(
    (?:[\-+\w]([\w\-+]|\.(?!\.))+)    # Local part
    @(?:[\w\-]+\.)                    # @domain part start
    (([\w\-]|(?<!\.)\.(?!\.))*)[a-z]  # @domain.end (allow multiple dot names)
    (?![\d\-_@])                      # Don't allow last char to be followed by these
)
'''

RE_LINK = r'''(?x)(?i)
(
    \b(?:
        (?:ht|f)tps?://(?:(?:[a-z\d\-_]+(?:\.[a-z\d\-._]+)+)|localhost)|  # (http|ftp)://
        (?P<www>w{3}\.)[a-z\d\-_]+(?:\.[a-z\d\-._]+)+                     # www.
    )
    /?[a-z\d\-._?,!'(){}\[\]/+&@%$#=:"|~;]*                               # url path, fragments, and query stuff
    [a-z\d\-_~:/#@$*+=]                                                   # allowed end chars
)
'''


class MagiclinkPattern(LinkPattern):
    def handleMatch(self, m):
        el = util.etree.Element("a")
        if m.group("www"):
            href = "http://%s" % m.group(2)
        else:
            href = m.group(2)
        el.text = m.group(2)
        el.set("href", self.sanitize_url(self.unescape(href.strip())))

        return el


class MagicMailPattern(LinkPattern):
    def handleMatch(self, m):
        el = util.etree.Element("a")
        href = "mailto:%s" % m.group(2)
        el.text = m.group(2)
        el.set("href", self.sanitize_url(self.unescape(href.strip())))

        return el


class MagiclinkExtension(Extension):
    """Adds Easylink extension to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Adds support for turning html links to link tags"""

        md.inlinePatterns.add("magic-link", MagiclinkPattern(RE_LINK, md), "<not_strong")
        md.inlinePatterns.add("magic-mail", MagicMailPattern(RE_MAIL, md), "<not_strong")


def makeExtension(*args, **kwargs):
    return MagiclinkExtension(*args, **kwargs)
