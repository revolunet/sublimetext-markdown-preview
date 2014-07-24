"""
Mdownx.delete
An extension for Python Markdown.
Adds support for ~~strike~~ => <del>strike</del>

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


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
        md.ESCAPED_CHARS.append('~')
        md.inlinePatterns.add("del", SimpleTagPattern(RE_DEL, "del"), "<not_strong")


def makeExtension(configs={}):
    return DeleteExtension(configs=dict(configs))
