"""
mdownx.progressbar
Extension to add support for
progress bars

/* No label */
[==30%]

/* Label */
[==30%  MyLabel]

/* Inline adding of classes to html object */
[==50/200  MyLabel]{addclasses="additional classes"}

/* Inline turning off/on level_class */
[==50%  MyLabel]{addclasses="additional classes" levelclass="false"}

New line is required before the progress bar.  Can take percentages and divisions.
Floats are okay.  Numbers must be positive.  This is an experimental extension.
Functionality is subject to change.

Minimum Recommended Styling
(but you could add gloss, candystriping, animation or anything else):

.progress {
  display: block;
  width: 300px;
  margin: 10px 0;
  height: 24px;
  border: 1px solid #ccc;
  -webkit-border-radius: 3px;
  -moz-border-radius: 3px;
  border-radius: 3px;
  background-color: #F8F8F8;
  position: relative;
  box-shadow: inset -1px 1px 3px rgba(0, 0, 0, .1);
}

.progress-label {
  position: absolute;
  text-align: center;
  font-weight: bold;
  width: 100%; margin: 0;
  line-height: 24px;
  color: #333;
  -webkit-font-smoothing: antialiased !important;
  white-space: nowrap;
  overflow: hidden;
}

.progress-bar {
  height: 24px;
  float: left;
  border-right: 1px solid #ccc;
  -webkit-border-radius: 3px;
  -moz-border-radius: 3px;
  border-radius: 3px;
  background-color: #34c2e3;
  box-shadow: inset 0 1px 0px rgba(255, 255, 255, .5);
}

For Level Colors

.progress-100plus .progress-bar {
  background-color: #1ee038;
}

.progress-80plus .progress-bar {
  background-color: #86e01e;
}

.progress-60plus .progress-bar {
  background-color: #f2d31b;
}

.progress-40plus .progress-bar {
  background-color: #f2b01e;
}

.progress-20plus .progress-bar {
  background-color: #f27011;
}

.progress-0plus .progress-bar {
  background-color: #f63a0f;
}

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import unicode_literals
from __future__ import absolute_import
from ..extensions import Extension
from ..inlinepatterns import Pattern, dequote
from .. import util
import re

RE_PROGRESS = r'\[==\s*(?:(100(?:.0+)?|[1-9]?[0-9](?:.\d+)?)%|(?:(\d+(?:.\d+)?)\s*/\s*(\d+(?:.\d+)?)))(\s+(?:[^\]\\]|\\.)*?)?\s*\](?:\{\s*((?:(?<=[\s\{])(?:addclasses|levelclass)="[^"{}]*"\s*)*)\})?'

CLASS_100PLUS = "progress-100plus"
CLASS_80PLUS = "progress-80plus"
CLASS_60PLUS = "progress-60plus"
CLASS_40PLUS = "progress-40plus"
CLASS_20PLUS = "progress-20plus"
CLASS_0PLUS = "progress-0plus"

ATTR = r'\s*(addclasses|levelclass)="([^"{}]+)"\s*'


class ProgressBarPattern(Pattern):
    def __init__(self, pattern):
        Pattern.__init__(self, pattern)

    def create_tag(self, width, label, add_classes):
        # Create list of all classes and remove duplicates
        classes = list(
            set(
                ["progress"] +
                self.config.get('addclasses', '').split() +
                add_classes
            )
        )
        el = util.etree.Element("div")
        el.set('class', ' '.join(classes))
        bar = util.etree.SubElement(el, 'div')
        bar.set('class', "progress-bar")
        bar.set('style', 'width:%s%%' % width)
        p = util.etree.SubElement(bar, 'p')
        p.set('class', 'progress-label')
        p.text = self.markdown.htmlStash.store(label, safe=True)
        return el

    def get_attr(self, string):
        """ Get add_classes (c) or level_class (l) attributes """
        attr = re.compile(ATTR)
        c = []
        l = None
        for m in attr.finditer(string):
            if m.group(1) == "addclasses":
                c += m.group(2).strip().split()
            elif m.group(1) == "levelclass":
                if m.group(2).lower() == "true":
                    l = True
                elif m.group(2).lower() == "false":
                    l = False
                else:
                    l = None
        return c, l

    def handleMatch(self, m):
        label = ""
        level_class = self.config.get('levelclass', False)
        if m.group(5):
            label = dequote(self.unescape(m.group(5).strip()))
        if m.group(6):
            add_classes, lvl_class = self.get_attr(m.group(6))
            if lvl_class is not None:
                level_class = lvl_class
        else:
            add_classes = []
        if m.group(2):
            value = float(m.group(2))
        else:
            try:
                num = float(m.group(3))
            except:
                num = 0.0
            try:
                den = float(m.group(4))
            except:
                den = 1.0
            if den == 0.0:
                den = 1.0

            value = (num / den) * 100.0

            if value > 100.0:
                value = 100.0
            elif value < 0.0:
                value = 0.0

        if level_class:
            if value >= 100.0:
                add_classes.append(CLASS_100PLUS)
            elif value >= 80.0:
                add_classes.append(CLASS_80PLUS)
            elif value >= 60.0:
                add_classes.append(CLASS_60PLUS)
            elif value >= 40.0:
                add_classes.append(CLASS_40PLUS)
            elif value >= 20.0:
                add_classes.append(CLASS_20PLUS)
            else:
                add_classes.append(CLASS_0PLUS)

        return self.create_tag('%.2f' % value, label, add_classes)


class ProgressBarExtension(Extension):
    """Adds progressbar extension to Markdown class."""
    def __init__(self, configs):
        self.config = {
            'levelclass': [True, "Include class that defines progress level in increments of 20 - Default: True"],
            'addclasses': ['', "Add additional classes to the progress tag for styling.  Classes are separated by spaces. - Default: None"]
        }

        for key, value in configs.items():
            if value == 'True':
                value = True
            if value == 'False':
                value = False
            if value == 'None':
                value = None

            if key == 'addclasses':
                value = str(value)

            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """Add for progress bar"""
        progress = ProgressBarPattern(RE_PROGRESS)
        progress.config = self.getConfigs()
        progress.markdown = md
        md.inlinePatterns.add("progressbar", progress, "<not_strong")


def makeExtension(configs={}):
    return ProgressBarExtension(configs=dict(configs))
