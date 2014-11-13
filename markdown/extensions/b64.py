"""
pymdown.b64
An extension for Python Markdown.
Given an absolute base path, this extension searches for img tags,
and if the images are local, will embed the images in base64.

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..postprocessors import Postprocessor
from os.path import exists, normpath, splitext, join
import sys
import base64
import re
# import traceback

PY3 = sys.version_info >= (3, 0)
if PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

file_types = {
    (".png",): "image/png",
    (".jpg", ".jpeg"): "image/jpeg",
    (".gif",): "image/gif"
}

exclusion_list = tuple(
    ['https://', 'http://', '#'] +
    ["data:%s;base64," % ft for ft in file_types.values()]
)

RE_TAG_HTML = re.compile(
    r'''(?xus)
    (?:
        (?P<comments>(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)|
        (?P<open><(?P<tag>img))
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    '''
)

RE_TAG_LINK_ATTR = re.compile(
    r'''(?xus)
    (?P<attr>
        (?:
            (?P<name>\s+src\s*=\s*)
            (?P<path>"[^"]*"|'[^']*')
        )
    )
    '''
)


def repl_path(m, base_path):
    """ Replace path with b64 encoded data """

    path = unquote(m.group('path')[1:-1])
    link = m.group(0)
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
            for b64_ext in file_types:
                if ext in b64_ext:
                    try:
                        with open(file_name, "rb") as f:
                            link = " src=\"data:%s;base64,%s\"" % (
                                file_types[b64_ext],
                                base64.b64encode(f.read()).decode('ascii')
                            )
                    except:
                        pass
                    break
    return link


def repl(m, base_path):
    if m.group('comments'):
        tag = m.group('comments')
    else:
        tag = m.group('open')
        tag += RE_TAG_LINK_ATTR.sub(lambda m2: repl_path(m2, base_path), m.group('attr'))
        tag += m.group('close')
    return tag


class B64Postprocessor(Postprocessor):
    def run(self, text):
        """ Find and replace paths with base64 encoded file. """

        basepath = self.config['base_path']
        if basepath:
            text = RE_TAG_HTML.sub(lambda m: repl(m, basepath), text)
        return text


class B64Extension(Extension):
    def __init__(self, configs):
        self.config = {
            'base_path': ["", "Base path for b64 to use to resolve paths Default: \"\""]
        }

        for key, value in configs:
            if key == "base_path" and exists(value):
                self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """Add B64Treeprocessor to Markdown instance"""

        b64 = B64Postprocessor(md)
        b64.config = self.getConfigs()
        md.postprocessors.add("b64", b64, "_end")
        md.registerExtension(self)


def makeExtension(configs={}):
    return B64Extension(configs=configs)
