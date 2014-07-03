"""
Mdownx.b64
An extension for Python Markdown.
Given an absolute base path, this extension searches for img tags,
and if the images are local, will embed the images in base64.

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
from ..treeprocessors import Treeprocessor
from os.path import exists, normpath, splitext, join
import sys
import base64
import re

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

file_types = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif"
}

exclusion_list = tuple(
    ['https://', 'http://', '#'] +
    ["data:%s;base64," % ft for ft in file_types.values()]
)


def repl(path, base_path):
    """ Replace path with b64 encoded data """

    link = path
    absolute = False
    re_win_drive = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")

    # Format the link
    if path.startswith('file://'):
        path = path.replace('file://', '', 1)
        if _PLATFORM == "windows" and not path.startswith('//'):
            path = path.lstrip("/")
        absolute = True
    elif _PLATFORM == "windows" and re_win_drive.match(path) is not None:
        absolute = True

    if not path.startswith(exclusion_list):
        if absolute:
            file_name = normpath(path)
        else:
            file_name = normpath(join(base_path, path))

        if exists(file_name):
            ext = splitext(file_name)[1].lower()
            if ext in file_types:
                try:
                    with open(file_name, "rb") as f:
                        link = "data:%s;base64,%s" % (file_types[ext], base64.b64encode(f.read()).decode('ascii'))
                except Exception as e:
                    pass
    return link


class B64Treeprocessor(Treeprocessor):
    def run(self, root):
        """Replace resource with b64 encoded data"""
        if self.config['base_path'] is None:
            return root

        links = root.getiterator('img')
        for link in links:
            src = link.attrib.get("src")
            if src is not None:
                link.attrib["src"] = repl(src, self.config['base_path'])
        return root


class B64Extension(Extension):
    def __init__(self, configs):
        self.config = {
            'base_path': [None, "Base path for b64 to use to resolve paths Default: None"]
        }

        for key, value in configs:
            if key == "base_path" and exists(value):
                self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """Add B64Treeprocessor to Markdown instance"""

        b64 = B64Treeprocessor(md)
        b64.config = self.getConfigs()
        md.treeprocessors.add("b64", b64, "_end")
        md.registerExtension(self)


def makeExtension(configs={}):
    return B64Extension(configs=configs)
