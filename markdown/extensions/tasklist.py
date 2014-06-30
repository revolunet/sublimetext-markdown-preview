"""
mdownx.tasklist
An extension for Python Markdown.
Github style tasklists

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from ..extensions import Extension
from ..treeprocessors import Treeprocessor
import re

RE_CHECKBOX = re.compile(r"^(?P<checkbox> *\[(?P<state>x|X| {1})\] +)(?P<line>.*)")


class TasklistTreeprocessor(Treeprocessor):
    def run(self, root):
        """ Replace relative paths with absolute """

        parent_map = dict((c, p) for p in root.getiterator() for c in p)
        task_items = []
        lilinks = root.getiterator('li')
        for li in lilinks:
            if li.text is None:
                continue
            m = RE_CHECKBOX.match(li.text)
            if m is not None:
                checkbox = '<input type="checkbox" disabled%s> ' % (' checked' if m.group('state').lower() == 'x' else '')
                li.text = self.markdown.htmlStash.store(checkbox, safe=True) + m.group('line')
                c = li.attrib.get("class", "")
                classes = [] if c == "" else c.split()
                classes.append("task-list-item")
                li.attrib["class"] = ' '.join(classes)
                task_items.append(li)
        for li in task_items:
            parent = parent_map[li]
            c = parent.attrib.get("class", "")
            classes = [] if c == "" else c.split()
            if "task-list" not in classes:
                classes.append("task-list")
            parent.attrib["class"] = ' '.join(classes)
        return root


class TasklistExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        """Add GithubChecklistsTreeprocessor to Markdown instance"""

        ghckl = TasklistTreeprocessor(md)
        md.treeprocessors.add("githubchecklists", ghckl, ">inline")
        md.registerExtension(self)


def makeExtension(configs={}):
    return TasklistExtension(configs=configs)
