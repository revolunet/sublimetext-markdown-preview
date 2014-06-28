"""
Mdownx.b64
An extension for Python Markdown.
Given an absolute base path, this extension searches for img tags,
and if the images are local, will embed the images in base64.

Modified to work with Sublime Markdown Preview
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..markdown.extensions import Extension
from ..markdown.treeprocessors import Treeprocessor
from os.path import abspath, exists, normpath, splitext, join
import sys
import base64

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

    # Format the link
    if path.startswith('file://'):
        path = path.replace('file://', '', 1)
        if _PLATFORM == "windows":
            path = path.lstrip("/")
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
                    link += str(e)
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
