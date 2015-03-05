"""
---
pymdownx.superfences
Neseted Fenced Code Blocks

This is a modification of the original Fenced Code Extension.
Algorithm has been rewritten to allow for fenced blocks in blockquotes,
lists, etc.  And also , allow for special UML fences like 'flow' for flowcharts
and `sequence` for sequence diagrams.

Modified: 2014 Isaac Muse <isaacmuse@gmail.com>
---

Fenced Code Extension for Python Markdown
=========================================

This extension adds Fenced Code Blocks to Python-Markdown.

See <https://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html>
for documentation.

Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).


All changes Copyright 2008-2014 The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from ..extensions import Extension
from ..preprocessors import Preprocessor
from ..blockprocessors import CodeBlockProcessor
from ..extensions.codehilite import CodeHilite, CodeHiliteExtension, parse_hl_lines
from .. import util
import re

NESTED_FENCE_START = r'''(?x)
(?:^(?P<ws>[\> ]*)(?P<fence>~{3,}|`{3,}))[ ]*           # Fence opening
(\{?                                                    # Language opening
\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*                      # Language
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]* # highlight lines
}?[ ]*$                                                 # Language closing
'''
NESTED_FENCE_END = r'^[\> ]*%s[ ]*$'

WS = r'^([\> ]{0,%d})(.*)'

RE_FENCE = re.compile(
    r'''(?xsm)
    (?P<fence>^(?:~{3,}|`{3,}))[ ]*                          # Opening
    (\{?\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*                   # Optional {, and lang
    (hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*  # Optional highlight lines option
    }?[ ]*\n                                                 # Optional closing }
    (?P<code>.*?)(?<=\n)                                     # Code
    (?P=fence)[ ]*$                                          # Closing
    '''
)


def _escape(txt):
    """ basic html escaping """
    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def extendSuperFences(md, name, language, formatter):
    if not hasattr(md, "superfences"):
        md.superfences = []
    md.superfences.append(
        {
            "name": name,
            "test": lambda l, language=language: language == l,
            "formatter": formatter
        }
    )


class CodeStash(object):
    """
    Store original fenced code here in case we were
    too greedy and need to restore in an indented code
    block.
    """

    def __init__(self):
        self.stash = {}

    def __len__(self):
        return len(self.stash)

    def get(self, key, default=None):
        code = self.stash.get(key, default)
        return code

    def remove(self, key):
        del self.stash[key]

    def store(self, key, code, indent_level):
        self.stash[key] = (code, indent_level)

    def clear_stash(self):
        self.stash = {}


def uml_format(source, language, css_class):
    return '<pre class="%s"><code>%s</code></pre>' % (css_class, _escape(source))


class SuperFencesCodeExtension(Extension):

    def __init__(self, *args, **kwargs):
        self.config = {
            'disable_indented_code_blocks': [False, "Disable indented code blocks - Default: False"],
            'nested': [True, "Use nested fences - Default: True"],
            'uml_flow': [True, "Enable flowcharts - Default: True"],
            'uml_sequence': [True, "Enable sequence diagrams - Default: True"]
        }
        self.configured = False
        super(SuperFencesCodeExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        config = self.getConfigs()
        sf_entry = {
            "name": "superfences",
            "test": lambda language: True,
            "formatter": None
        }
        if not hasattr(md, "superfences"):
            md.superfences = []
        md.superfences.insert(0, sf_entry)
        if config.get("uml_flow", True):
            extendSuperFences(md, "flow", "flow", lambda s, l, c="uml-flowchart": uml_format(s, l, c))
        if config.get("uml_sequence", True):
            extendSuperFences(md, "sequence", "sequence", lambda s, l, c="uml-sequence-diagram": uml_format(s, l, c))
        self.markdown = md

    def patch_fenced_rule(self):
        config = self.getConfigs()
        fenced = SuperFencesBlockPreprocessor(self.markdown)
        indented_code = SuperFencesCodeBlockProcessor(self)
        fenced.config = config
        indented_code.config = config
        indented_code.markdown = self.markdown
        self.markdown.superfences[0]["formatter"] = fenced.highlight
        self.markdown.parser.blockprocessors['code'] = indented_code
        if 'fenced_code_block' in self.markdown.preprocessors.keys():
            self.markdown.preprocessors['fenced_code_block'] = fenced
        else:
            pos = ">critic" if ['critic'] in self.markdown.preprocessors.keys() else ">normalize_whitespace"
            self.markdown.preprocessors.add('fenced_code_block', fenced, pos)

    def reset(self):
        # People should use superfences **or** fenced_code,
        # but to make it easy on people who include all of
        # "extra", we will patch fenced_code after fenced_code
        # has been loaded.
        if not self.configured:
            self.patch_fenced_rule()
            self.configured = True
            for entry in self.markdown.superfences:
                entry["stash"] = CodeStash()
        else:
            for entry in self.markdown.superfences:
                entry["stash"].clear_stash()


class SuperFencesBlockPreprocessor(Preprocessor):
    fence_start = re.compile(NESTED_FENCE_START)
    CODE_WRAP = '<pre><code%s>%s</code></pre>'
    CLASS_ATTR = ' class="%s"'

    def __init__(self, md):
        super(SuperFencesBlockPreprocessor, self).__init__(md)
        self.markdown = md
        self.checked_for_codehilite = False
        self.codehilite_conf = {}

    def rebuild_block(self, lines):
        """ Deindent the fenced block lines """
        return '\n'.join([line[self.ws_len:] for line in lines]) + '\n'

    def check_codehilite(self):
        """ Check for code hilite extension """
        if not self.checked_for_codehilite:
            for ext in self.markdown.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break
            self.checked_for_codehilite = True

    def clear(self):
        """ Reset the class variables. """
        self.ws = None
        self.ws_len = 0
        self.fence = None
        self.lang = None
        self.hl_lines = None
        self.quote_level = 0
        self.code = []
        self.empty_lines = 0
        self.whitespace = None
        self.fence_end = None

    def eval(self, m, start, end):
        """ Evaluate a normal fence """
        if m.group(0).strip() == '':
            # Empty line is okay
            self.empty_lines += 1
            self.code.append(m.group(0))
        elif len(m.group(1)) != self.ws_len and m.group(2) != '':
            # Not indented enough
            self.clear()
        elif self.fence_end.match(m.group(0)) is not None:
            # End of fence
            self.process_nested_block(m, start, end)
        else:
            # Content line
            self.empty_lines = 0
            self.code.append(m.group(0))

    def eval_quoted(self, m, quote_level, start, end):
        """ Evaluate fence inside a blockquote """
        if quote_level > self.quote_level:
            # Quote level exceeds the starting quote level
            self.clear()
        elif quote_level <= self.quote_level:
            if m.group(2) == '':
                # Empty line is okay
                self.code.append(m.group(0))
                self.empty_lines += 1
            elif len(m.group(1)) < self.ws_len:
                # Not indented enough
                self.clear()
            elif self.empty_lines and quote_level < self.quote_level:
                # Quote levels don't match and we are signified
                # the end of the block with an empty line
                self.clear()
            elif self.fence_end.match(m.group(0)) is not None:
                # End of fence
                self.process_nested_block(m, start, end)
            else:
                # Content line
                self.empty_lines = 0
                self.code.append(m.group(0))

    def process_nested_block(self, m, start, end):
        """ Process the contents of the nested block """
        self.last = m.group(0)
        code = None
        for entry in reversed(self.markdown.superfences):
            if entry["test"](self.lang):
                code = entry["formatter"](self.rebuild_block(self.code), self.lang)
                break

        if code is not None:
            self._store('\n'.join(self.code) + '\n', code, start, end, entry)
        self.clear()

    def search(self, lines):
        """ Search for non-nested fenced blocks """
        text = "\n".join(lines)
        while 1:
            m = RE_FENCE.search(text)
            if m:
                self.lang = m.group('lang')
                self.hl_lines = m.group('hl_lines')
                for entry in reversed(self.markdown.superfences):
                    if entry["test"](self.lang):
                        code = entry["formatter"](m.group('code'), self.lang)
                        break
                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()], placeholder, text[m.end():])
            else:
                break
        return text.split("\n")

    def search_nested(self, lines):
        """ Search for nested fenced blocks """
        count = 0
        for line in lines:
            if self.fence is None:
                # Found the start of a fenced block.
                m = self.fence_start.match(line)
                if m is not None:
                    start = count
                    self.first = m.group(0)
                    self.ws = m.group('ws') if m.group('ws') else ''
                    self.ws_len = len(self.ws)
                    self.quote_level = self.ws.count(">")
                    self.empty_lines = 0
                    self.fence = m.group('fence')
                    self.lang = m.group('lang')
                    self.hl_lines = m.group('hl_lines')
                    self.fence_end = re.compile(NESTED_FENCE_END % self.fence)
                    self.whitespace = re.compile(WS % self.ws_len)
            else:
                # Evaluate lines
                # - Determine if it is the ending line or content line
                # - If is a content line, make sure it is all indentend
                #   with the opening and closing lines (lines with just
                #   whitespace will be stripped so those don't matter).
                # - When content lines are inside blockquotes, make sure
                #   the nested block quote levels make sense according to
                #   blockquote rules.
                m = self.whitespace.match(line)
                if m:
                    end = count + 1
                    quote_level = m.group(1).count(">")

                    if self.quote_level:
                        # Handle blockquotes
                        self.eval_quoted(m, quote_level, start, end)
                    elif quote_level == 0:
                        # Handle all other cases
                        self.eval(m, start, end)
                    else:
                        # Looks like we got a blockquote line
                        # when not in a blockquote.
                        self.clear()
                else:
                    self.clear()
            count += 1

        # Now that we are done iterating the lines,
        # let's replace the original content with the
        # fenced blocks.
        while len(self.stack):
            fenced, start, end = self.stack.pop()
            lines = lines[:start] + [fenced] + lines[end:]
        return lines

    def highlight(self, source, language):
        """
        If config is not empty, then the codehlite extension
        is enabled, so we call into to highlight the code.
        """
        if self.codehilite_conf:
            code = CodeHilite(
                source,
                linenums=self.codehilite_conf['linenums'][0],
                guess_lang=self.codehilite_conf['guess_lang'][0],
                css_class=self.codehilite_conf['css_class'][0],
                style=self.codehilite_conf['pygments_style'][0],
                lang=language,
                noclasses=self.codehilite_conf['noclasses'][0],
                hl_lines=parse_hl_lines(self.hl_lines)
            ).hilite()
        else:
            lang = self.CLASS_ATTR % language if language else ''
            code = self.CODE_WRAP % (lang, _escape(source))
        return code

    def _store(self, source, code, start, end, obj):
        """
        Store the fenced blocks in teh stack to be replaced when done iterating.
        Store the original text in case we need to restore if we are too greedy.
        """
        # Save the fenced blocks to add once we are done iterating the lines
        placeholder = self.markdown.htmlStash.store(code, safe=True)
        self.stack.append(('%s%s' % (self.ws, placeholder), start, end))
        if not self.disabled_indented:
            # If an indented block consumes this placeholder,
            # we can restore the original source
            obj["stash"].store(
                placeholder[1:-1],
                "%s\n%s%s" % (self.first, source, self.last),
                self.ws_len
            )

    def run(self, lines):
        """ Search for fenced blocks """
        self.check_codehilite()
        self.clear()
        self.stack = []
        self.disabled_indented = self.config.get("disable_indented_code_blocks", False)
        self.uml_flow = self.config.get("uml_flow", True)
        self.uml_sequence = self.config.get("uml_sequence", True)

        if self.config.get("nested", True):
            lines = self.search_nested(lines)
        else:
            lines = self.search(lines)

        return lines


class SuperFencesCodeBlockProcessor(CodeBlockProcessor):
    """ Process code blocks. """
    FENCED_BLOCK_RE = re.compile(
        r'^([\> ]*)%s(%s)%s$' % (
            util.HTML_PLACEHOLDER[0],
            util.HTML_PLACEHOLDER[1:-1] % r'([0-9]+)',
            util.HTML_PLACEHOLDER[-1]
        )
    )

    def test(self, parent, block):
        """ Test method that is one day to be deprecated """
        return True

    def reindent(self, text, pos, level):
        """ Reindent the code to where it is supposed to be """
        if text is None:
            return None
        indented = []
        for line in text.split('\n'):
            index = pos - level
            indented.append(line[index:])
        return '\n'.join(indented)

    def revert_greedy_fences(self, block):
        """ Revert a prematurely converted fenced block """
        new_block = []
        for line in block.split('\n'):
            m = self.FENCED_BLOCK_RE.match(line)
            if m:
                key = m.group(2)
                indent_level = len(m.group(1))
                original = None
                for entry in self.markdown.superfences:
                    stash = entry["stash"]
                    original, pos = stash.get(key)
                    if original is not None:
                        code = self.reindent(original, pos, indent_level)
                        new_block.append(code)
                        stash.remove(key)
                        break
                if original is None:
                    new_block.append(line)
            else:
                new_block.append(line)
        return '\n'.join(new_block)

    def run(self, parent, blocks):
        """ Look for and parse code block """
        handled = False

        if not self.config.get("disable_indented_code_blocks", False):
            handled = CodeBlockProcessor.test(self, parent, blocks[0])
            if handled:
                if self.config.get("nested", True):
                    blocks[0] = self.revert_greedy_fences(blocks[0])
                handled = CodeBlockProcessor.run(self, parent, blocks) is not False
        return handled


def makeExtension(*args, **kwargs):
    return SuperFencesCodeExtension(*args, **kwargs)
