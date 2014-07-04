"""
mdownx.headeranchor
An extension for Python Markdown.
Github header anchors

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..treeprocessors import Treeprocessor
from .headerid import slugify, stashedHTML2text, itertext

LINK = '<a name="user-content-%(id)s" href="#%(id)s" class="headeranchor-link"  aria-hidden="true"><span class="headeranchor"></span></a>'


class HeaderAnchorTreeprocessor(Treeprocessor):
    def run(self, root):
        """ Add header anchors """

        for tag in root.getiterator():
            if tag.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                if "id" in tag.attrib:
                    id = tag.get('id')
                else:
                    id = stashedHTML2text(''.join(itertext(tag)), self.md)
                    id = slugify(id, '-')
                    tag.set('id', id)
                tag.text = self.markdown.htmlStash.store(
                    LINK % {"id": id},
                    safe=True
                ) + tag.text
        return root


class HeaderAnchorExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        """Add HeaderAnchorTreeprocessor to Markdown instance"""

        self.processor = HeaderAnchorTreeprocessor(md)
        self.processor.md = md
        if 'toc' in md.treeprocessors.keys():
            insertion = ">toc"
        else:
            insertion = ">_end"
        md.treeprocessors.add("headeranchor", self.processor, insertion)
        md.registerExtension(self)


def makeExtension(configs={}):
    return HeaderAnchorExtension(configs=configs)
