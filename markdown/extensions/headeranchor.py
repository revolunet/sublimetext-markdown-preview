"""
pymdownx.headeranchor
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
from .headerid import slugify, stashedHTML2text, itertext, unique

LINK = (
    '<a '
    'name="user-content-%(id)s" '
    'href="#%(id)s" class="headeranchor-link" '
    'aria-hidden="true">'
    '<span class="headeranchor"></span>'
    '</a>'
)


class HeaderAnchorTreeprocessor(Treeprocessor):
    def run(self, root):
        """ Add header anchors """

        # Get a list of id attributes
        used_ids = set()
        for tag in root.getiterator():
            if "id" in tag.attrib:
                used_ids.add(tag.attrib["id"])

        for tag in root.getiterator():
            if tag.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                if "id" in tag.attrib:
                    id = tag.get('id')
                else:
                    id = stashedHTML2text(''.join(itertext(tag)), self.md)
                    id = unique(self.config['slugify'](id, self.config['sep']), used_ids)
                    tag.set('id', id)
                tag.text = self.markdown.htmlStash.store(
                    LINK % {"id": id},
                    safe=True
                ) + tag.text if tag.text is not None else ''
        return root


class HeaderAnchorExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'sep': ['-', "Separator to use when creating header ids - Default: '-'"],
            'slugify': [slugify, 'Callable to generate anchors']
        }
        self.configured = False
        super(HeaderAnchorExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add HeaderAnchorTreeprocessor to Markdown instance"""

        self.md = md
        processor = HeaderAnchorTreeprocessor(md)
        processor.config = self.getConfigs()
        processor.md = md
        md.treeprocessors.add("header-anchor", processor, "_end")
        md.registerExtension(self)

    def reset(self):
        """ Ensure this is always after toc """
        if not self.configured and 'toc' in self.md.treeprocessors.keys():
            self.configured = True
            processor = self.md.treeprocessors["header-anchor"]
            del self.md.treeprocessors["header-anchor"]
            self.md.treeprocessors.add("header-anchor", processor, ">toc")


def makeExtension(*args, **kwargs):
    return HeaderAnchorExtension(*args, **kwargs)
