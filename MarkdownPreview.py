# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin

import os
import sys
import traceback
import tempfile
import re
import json
import time
import codecs
import cgi


def is_ST3():
    ''' check if ST3 based on python version '''
    return sys.version_info >= (3, 0)

if is_ST3():
    from . import desktop
    from . import yaml
    from .markdown_settings import Settings
    from .markdown_wrapper import StMarkdown as Markdown
    from .lib.markdown_preview_lib.pygments.formatters import HtmlFormatter
    from .helper import INSTALLED_DIRECTORY
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote

    def Request(url, data, headers):
        ''' Adapter for urllib2 used in ST2 '''
        import urllib.request
        return urllib.request.Request(url, data=data, headers=headers, method='POST')

    unicode_str = str

else:
    import desktop
    import yaml
    from markdown_settings import Settings
    from markdown_wrapper import StMarkdown as Markdown
    from lib.markdown_preview_lib.pygments.formatters import HtmlFormatter
    from helper import INSTALLED_DIRECTORY
    from urllib2 import Request, urlopen, HTTPError, URLError
    from urllib import quote

    unicode_str = unicode

_CANNOT_CONVERT = u'cannot convert markdown'
ABS_EXCLUDE = tuple(
    [
        'file://', 'https://', 'http://', '/', '#',
        "data:image/jpeg;base64,", "data:image/png;base64,", "data:image/gif;base64,"
    ] + ['\\'] if sys.platform.startswith('win') else []
)
DEFAULT_EXT = [
    "extra", "github", "toc", "headerid",
    "meta", "sane_lists", "smarty", "wikilinks",
    "admonition"
]


def getTempMarkdownPreviewPath(view):
    ''' return a permanent full path of the temp markdown preview file '''

    settings = sublime.load_settings('MarkdownPreview.sublime-settings')

    tmp_filename = '%s.html' % view.id()
    tmp_dir = tempfile.gettempdir()
    if settings.get('path_tempfile'):
        if os.path.isabs(settings.get('path_tempfile')):  # absolute path or not
            tmp_dir = settings.get('path_tempfile')
        else:
            tmp_dir = os.path.join(os.path.dirname(view.file_name()), settings.get('path_tempfile'))

    if not os.path.isdir(tmp_dir):  # create dir if not exsits
        os.makedirs(tmp_dir)

    tmp_fullpath = os.path.join(tmp_dir, tmp_filename)
    return tmp_fullpath


def save_utf8(filename, text):
    with codecs.open(filename, 'w', encoding='utf-8')as f:
        f.write(text)


def load_utf8(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def load_resource(name):
    ''' return file contents for files within the package root folder '''

    try:
        if is_ST3():
            return sublime.load_resource('Packages/Markdown Preview/{0}'.format(name))
        else:
            filename = os.path.join(sublime.packages_path(), INSTALLED_DIRECTORY, name)
            return load_utf8(filename)
    except:
        print("Error while load_resource('%s')" % name)
        traceback.print_exc()
        return ''


def exists_resource(resource_file_path):
    filename = os.path.join(os.path.dirname(sublime.packages_path()), resource_file_path)
    return os.path.isfile(filename)


def new_view(window, text, scratch=False):
    ''' create a new view and paste text content
        return the new view.
        Optionally can be set as scratch.
    '''

    new_view = window.new_file()
    if scratch:
        new_view.set_scratch(True)
    if is_ST3():
        new_view.run_command('append', {
            'characters': text,
        })
    else:  # 2.x
        new_edit = new_view.begin_edit()
        new_view.insert(new_edit, 0, text)
        new_view.end_edit(new_edit)
    return new_view


def get_references(file_name, encoding="utf-8"):
    """ Get footnote and general references from outside source """
    text = ''
    if file_name is not None:
        if os.path.exists(file_name):
            try:
                with codecs.open(file_name, "r", encoding=encoding) as f:
                    text = f.read()
            except:
                print(traceback.format_exc())
        else:
            print("Could not find reference file %s!", file_name)
    return text


class CriticDump(object):
    RE_CRITIC = re.compile(
        r'''
            ((?P<open>\{)
                (?:
                    (?P<ins_open>\+{2})(?P<ins_text>.*?)(?P<ins_close>\+{2})
                  | (?P<del_open>\-{2})(?P<del_text>.*?)(?P<del_close>\-{2})
                  | (?P<mark_open>\={2})(?P<mark_text>.*?)(?P<mark_close>\={2})
                  | (?P<comment>(?P<com_open>\>{2})(?P<com_text>.*?)(?P<com_close>\<{2}))
                  | (?P<sub_open>\~{2})(?P<sub_del_text>.*?)(?P<sub_mid>\~\>)(?P<sub_ins_text>.*?)(?P<sub_close>\~{2})
                )
            (?P<close>\})|.)
        ''',
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def process(self, m):
        if self.accept:
            if m.group('ins_open'):
                return m.group('ins_text')
            elif m.group('del_open'):
                return ''
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_ins_text')
            else:
                return m.group(0)
        else:
            if m.group('ins_open'):
                return ''
            elif m.group('del_open'):
                return m.group('del_text')
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_del_text')
            else:
                return m.group(0)

    def dump(self, source, accept):
        text = ''
        self.accept = accept
        for m in self.RE_CRITIC.finditer(source):
            text += self.process(m)
        return text


class MarkdownPreviewListener(sublime_plugin.EventListener):
    ''' auto update the output html if markdown file has already been converted once '''

    def on_post_save(self, view):
        settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        if settings.get('enable_autoreload', True):
            filetypes = settings.get('markdown_filetypes')
            if filetypes and view.file_name().endswith(tuple(filetypes)):
                temp_file = getTempMarkdownPreviewPath(view)
                if os.path.isfile(temp_file):
                    # reexec markdown conversion
                    # todo : check if browser still opened and reopen it if needed
                    view.run_command('markdown_preview', {
                        'target': 'disk',
                        'parser': view.settings().get('parser')
                    })
                    sublime.status_message('Markdown preview file updated')


class MarkdownCheatsheetCommand(sublime_plugin.TextCommand):
    ''' open our markdown cheat sheet in ST2 '''
    def run(self, edit):
        lines = '\n'.join(load_resource('sample.md').splitlines())
        view = new_view(self.view.window(), lines, scratch=True)
        view.set_name("Markdown Cheatsheet")

        # Set syntax file
        syntax_files = ["Packages/Markdown Extended/Syntaxes/Markdown Extended.tmLanguage", "Packages/Markdown/Markdown.tmLanguage"]
        for file in syntax_files:
            if exists_resource(file):
                view.set_syntax_file(file)
                break  # Done if any syntax is set.

        sublime.status_message('Markdown cheat sheet opened')


class Compiler(object):
    ''' Do the markdown converting '''
    default_css = "markdown.css"

    def isurl(self, css_name):
        match = re.match(r'https?://', css_name)
        if match:
            return True
        return False

    def get_default_css(self):
        ''' locate the correct CSS with the 'css' setting '''
        css_name = self.settings.get('css', 'default')

        if self.isurl(css_name):
            # link to remote URL
            return u"<link href='%s' rel='stylesheet' type='text/css'>" % css_name
        elif os.path.isfile(os.path.expanduser(css_name)):
            # use custom CSS file
            return u"<style>%s</style>" % load_utf8(os.path.expanduser(css_name))
        elif css_name == 'default':
            # use parser CSS file
            return u"<style>%s</style>" % load_resource(self.default_css)

        return ''

    def get_override_css(self):
        ''' handls allow_css_overrides setting. '''

        if self.settings.get('allow_css_overrides'):
            filename = self.view.file_name()
            filetypes = self.settings.get('markdown_filetypes')

            if filename and filetypes:
                for filetype in filetypes:
                    if filename.endswith(filetype):
                        css_filename = filename.rpartition(filetype)[0] + '.css'
                        if (os.path.isfile(css_filename)):
                            return u"<style>%s</style>" % load_utf8(css_filename)
        return ''

    def get_stylesheet(self):
        ''' return the correct CSS file based on parser and settings '''
        return self.get_default_css() + self.get_override_css()

    def get_javascript(self):
        js_files = self.settings.get('js')
        scripts = ''

        if js_files is not None:
            # Ensure string values become a list.
            if isinstance(js_files, str) or isinstance(js_files, unicode_str):
                js_files = [js_files]
            # Only load scripts if we have a list.
            if isinstance(js_files, list):
                for js_file in js_files:
                    if os.path.isabs(js_file):
                        # Load the script inline to avoid cross-origin.
                        scripts += u"<script>%s</script>" % load_utf8(js_file)
                    else:
                        scripts += u"<script type='text/javascript' src='%s'></script>" % js_file
        return scripts

    def get_mathjax(self):
        ''' return the MathJax script if enabled '''

        if self.settings.get('enable_mathjax') is True:
            return load_resource('mathjax.html')
        return ''

    def get_highlight(self):
        return ''

    def get_contents(self, wholefile=False):
        ''' Get contents or selection from view and optionally strip the YAML front matter '''
        region = sublime.Region(0, self.view.size())
        contents = self.view.substr(region)
        if not wholefile:
            # use selection if any
            selection = self.view.substr(self.view.sel()[0])
            if selection.strip() != '':
                contents = selection

        # Remove yaml front matter
        if self.settings.get('strip_yaml_front_matter') and contents.startswith('---'):
            frontmatter, contents = self.preprocessor_yaml_frontmatter(contents)
            self.settings.apply_frontmatter(frontmatter)

        references = self.settings.get('builtin').get('references', [])
        for ref in references:
            contents += get_references(ref)

        contents = self.parser_specific_preprocess(contents)

        return contents

    def parser_specific_preprocess(self, text):
        return text

    def preprocessor_yaml_frontmatter(self, text):
        """ Get frontmatter from string """
        frontmatter = {}

        if text.startswith("---"):
            m = re.search(r'^(---(.*?)---\r?\n)', text, re.DOTALL)
            if m:
                try:
                    frontmatter = yaml.load(m.group(2))
                except:
                    print(traceback.format_exc())
                text = text[m.end(1):]

        return frontmatter, text

    def parser_specific_postprocess(self, text):
        return text

    def postprocessor_absolute(self, html, image_convert, file_convert):
        ''' fix relative paths in images, scripts, and links for the internal parser '''
        def tag_fix(m):
            tag = m.group('tag')
            src = m.group('src')
            filename = self.view.file_name()
            if filename:
                if (
                    not src.startswith(ABS_EXCLUDE) and
                    not (sublime.platform() == "windows" and RE_WIN_DRIVE.match(src) is not None)
                ):
                    # Don't explicitly add file:// prefix,
                    # But don't remove them either
                    abs_path = u'%s/%s' % (os.path.dirname(filename), src)
                    # Don't replace just the first instance,
                    # but explicitly place it where it was before
                    # to ensure a file name 'img' dosen't replace
                    # the tag name etc.
                    if os.path.exists(abs_path):
                        tag = m.group('begin') + abs_path + m.group('end')
            return tag
        # Compile the appropriate regex to find images and/or files
        RE_WIN_DRIVE = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")
        RE_SOURCES = re.compile(
            r"""(?P<tag>(?P<begin><(?:%s%s%s)[^>]+(?:src%s)=["'])(?P<src>[^"']+)(?P<end>[^>]*>))""" % (
                r"img" if image_convert else "",
                r"|" if image_convert and file_convert else "",
                r"script|a" if file_convert else "",
                r"|href" if file_convert else ""
            )
        )
        return RE_SOURCES.sub(tag_fix, html)

    def postprocessor_base64(self, html):
        ''' convert resources (currently images only) to base64 '''

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

        def b64(m):
            import base64
            src = m.group('src')
            data = m.group('tag')
            base_path = self.settings.get("basepath")
            if base_path is None:
                base_path = ""

            # Format the link
            absolute = False
            if src.startswith('file://'):
                src = src.replace('file://', '', 1)
                if sublime.platform() == "windows" and not src.startswith('//'):
                    src = src.lstrip("/")
                absolute = True
            elif sublime.platform() == "windows" and RE_WIN_DRIVE.match(src) is not None:
                absolute = True

            # Make sure we are working with an absolute path
            if not src.startswith(exclusion_list):
                if absolute:
                    src = os.path.normpath(src)
                else:
                    src = os.path.normpath(os.path.join(base_path, src))

                if os.path.exists(src):
                    ext = os.path.splitext(src)[1].lower()
                    if ext in file_types:
                        try:
                            with open(src, "rb") as f:
                                data = m.group('begin') + "data:%s;base64,%s" % (
                                    file_types[ext],
                                    base64.b64encode(f.read()).decode('ascii')
                                ) + m.group('end')
                        except Exception:
                            pass
            return data
        RE_WIN_DRIVE = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")
        RE_SOURCES = re.compile(r"""(?P<tag>(?P<begin><(?:img)[^>]+(?:src)=["'])(?P<src>[^"']+)(?P<end>[^>]*>))""")
        return RE_SOURCES.sub(b64, html)

    def postprocessor_simple(self, html):
        ''' Strip out ids and classes for a simplified HTML output '''
        def strip_html(m):
            tag = m.group('open')
            if m.group('attr1'):
                tag += m.group('attr1')
            if m.group('attr2'):
                tag += m.group('attr2')
            if m.group('attr3'):
                tag += m.group('attr3')
            if m.group('attr4'):
                tag += m.group('attr4')
            if m.group('attr5'):
                tag += m.group('attr5')
            if m.group('attr6'):
                tag += m.group('attr6')
            tag += m.group('close')
            return tag

        # Strip out id, class and style attributes for a simple html output
        # Since we are stripping out two attributes, we need to set up the groups in such
        # a way so we can retrieve the data we don't want to throw away
        # up to these worst case scenarios:
        #
        # <tag attr=""... (id|class|style)=""... attr=""... (id|class|style)=""... attr=""... (id|class|style)=""...>
        # <tag (id|class|style)=""... attr=""... (id|class|style)=""... attr=""... (id|class|style)=""... attr=""...>
        STRIP_HTML = re.compile(
            r'''
                (?P<open><[\w\:\.\-]+)                                                      # Tag open
                (?:
                    (?P<attr1>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target1>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )
                (?:
                    (?P<attr2>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target2>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )?
                (?:
                    (?P<attr3>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target3>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )?
                (?:
                    (?P<attr4>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target4>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )?
                (?:
                    (?P<attr5>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target5>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )?
                (?:
                    (?P<attr6>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
                  | (?P<target6>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
                )?
                (?P<close>\s*(?:\/?)>)                                                      # Tag end
            ''',
            re.MULTILINE | re.DOTALL | re.VERBOSE
        )
        return STRIP_HTML.sub(strip_html, html)

    def convert_markdown(self, markdown_text):
        ''' convert input markdown to HTML, with github or builtin parser '''

        markdown_html = self.parser_specific_convert(markdown_text)

        image_convert = self.settings.get("image_path_conversion", "absolute")
        file_convert = self.settings.get("file_path_conversions", "absolute")

        markdown_html = self.parser_specific_postprocess(markdown_html)

        if "absolute" in (image_convert, file_convert):
            markdown_html = self.postprocessor_absolute(markdown_html, image_convert, file_convert)

        if image_convert == "base64":
            markdown_html = self.postprocessor_base64(markdown_html)

        if self.settings.get("html_simple", False):
            markdown_html = self.postprocessor_simple(markdown_html)

        return markdown_html

    def get_title(self):
        if self.meta_title is not None:
            title = self.meta_title
        else:
            title = self.view.name()
        if not title:
            fn = self.view.file_name()
            title = 'untitled' if not fn else os.path.splitext(os.path.basename(fn))[0]
        return '<title>%s</title>' % cgi.escape(title)

    def get_meta(self):
        self.meta_title = None
        meta = []
        for k, v in self.settings.get("meta", {}).items():
            if k == "title":
                if isinstance(v, list):
                    if len(v) == 0:
                        v = ""
                    else:
                        v = v[0]
                self.meta_title = unicode_str(v)
                continue
            if isinstance(v, list):
                v = ','.join(v)
            if v is not None:
                meta.append(
                    '<meta name="%s" content="%s">' % (cgi.escape(k, True), cgi.escape(v, True))
                )
        return '\n'.join(meta)

    def run(self, view, wholefile=False):
        ''' return full html and body html for view. '''
        self.settings = Settings('MarkdownPreview.sublime-settings', view.file_name())
        self.view = view

        contents = self.get_contents(wholefile)

        body = self.convert_markdown(contents)

        html_template = self.settings.get('html_template')

        # use customized html template if given
        if self.settings.get('html_simple', False):
            html = body
        elif html_template and os.path.exists(html_template):
            head = u''
            head += self.get_meta()
            if not self.settings.get('skip_default_stylesheet'):
                head += self.get_stylesheet()
            head += self.get_javascript()
            head += self.get_highlight()
            head += self.get_mathjax()
            head += self.get_title()

            html = load_utf8(html_template)
            html = html.replace('{{ HEAD }}', head, 1)
            html = html.replace('{{ BODY }}', body, 1)
        else:
            html = u'<!DOCTYPE html>'
            html += '<html><head><meta charset="utf-8">'
            html += self.get_meta()
            html += self.get_stylesheet()
            html += self.get_javascript()
            html += self.get_highlight()
            html += self.get_mathjax()
            html += self.get_title()
            html += '</head><body>'
            html += '<article class="markdown-body">'
            html += body
            html += '</article>'
            html += '</body>'
            html += '</html>'

        return html, body


class GithubCompiler(Compiler):
    default_css = "github.css"

    def curl_convert(self, data):
        try:
            import subprocess

            # It looks like the text does NOT need to be escaped and
            # surrounded with double quotes.
            # Tested in ubuntu 13.10, python 2.7.5+
            shell_safe_json = data.decode('utf-8')
            curl_args = [
                'curl',
                '-H',
                'Content-Type: application/json',
                '-d',
                shell_safe_json,
                'https://api.github.com/markdown'
            ]

            github_oauth_token = self.settings.get('github_oauth_token')
            if github_oauth_token:
                curl_args[1:1] = [
                    '-u',
                    github_oauth_token
                ]

            markdown_html = subprocess.Popen(curl_args, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
            return markdown_html
        except subprocess.CalledProcessError:
            sublime.error_message('cannot use github API to convert markdown. SSL is not included in your Python installation. And using curl didn\'t work either')
        return None

    def preprocessor_critic(self, text):
        ''' Stip out multi-markdown critic marks.  Accept changes by default '''
        return CriticDump().dump(text, self.settings.get("strip_critic_marks", "accept") == "accept")

    def parser_specific_preprocess(self, text):
        if self.settings.get("strip_critic_marks", "accept") in ["accept", "reject"]:
            text = self.preprocessor_critic(text)
        return text

    def parser_specific_postprocess(self, html):
        ''' Post-processing for github API '''

        if self.settings.get("github_inject_header_ids", False):
            html = self.postprocess_inject_header_id(html)
        return html

    def postprocess_inject_header_id(self, html):
        ''' Insert header ids when no anchors are present '''
        unique = {}

        def header_to_id(text):
            if text is None:
                return ''
            # Strip html tags and lower
            id = RE_TAGS.sub('', text).lower()
            # Remove non word characters or non spaces and dashes
            # Then convert spaces to dashes
            id = RE_WORD.sub('', id).replace(' ', '-')
            # Encode anything that needs to be
            return quote(id)

        def inject_id(m):
            id = header_to_id(m.group('text'))
            if id == '':
                return m.group(0)
            # Append a dash and number for uniqueness if needed
            value = unique.get(id, None)
            if value is None:
                unique[id] = 1
            else:
                unique[id] += 1
                id += "-%d" % value
            return m.group('open')[:-1] + (' id="%s">' % id) + m.group('text') + m.group('close')

        RE_TAGS = re.compile(r'''</?[^>]*>''')
        RE_WORD = re.compile(r'''[^\w\- ]''')
        RE_HEADER = re.compile(r'''(?P<open><h([1-6])>)(?P<text>.*?)(?P<close></h\2>)''', re.DOTALL)
        return RE_HEADER.sub(inject_id, html)

    def parser_specific_convert(self, markdown_text):
        ''' convert input markdown to HTML, with github or builtin parser '''

        markdown_html = _CANNOT_CONVERT
        github_oauth_token = self.settings.get('github_oauth_token')

        # use the github API
        sublime.status_message('converting markdown with github API...')
        github_mode = self.settings.get('github_mode', 'gfm')
        data = {
            "text": markdown_text,
            "mode": github_mode
        }
        data = json.dumps(data).encode('utf-8')

        try:
            headers = {
                'Content-Type': 'application/json'
            }
            if github_oauth_token:
                headers['Authorization'] = "token %s" % github_oauth_token
            url = "https://api.github.com/markdown"
            sublime.status_message(url)
            request = Request(url, data, headers)
            markdown_html = urlopen(request).read().decode('utf-8')
        except HTTPError:
            e = sys.exc_info()[1]
            if e.code == 401:
                sublime.error_message('github API auth failed. Please check your OAuth token.')
            else:
                sublime.error_message('github API responded in an unfashion way :/')
        except URLError:
            # Maybe this is a Linux-install of ST which doesn't bundle with SSL support
            # So let's try wrapping curl instead
            markdown_html = self.curl_convert(data)
        except:
            e = sys.exc_info()[1]
            print(e)
            traceback.print_exc()
            sublime.error_message('cannot use github API to convert markdown. Please check your settings.')
        else:
            sublime.status_message('converted markdown with github API successfully')

        return markdown_html


class MultiMarkdownCompiler(Compiler):
    default_css = "markdown.css"

    def parser_specific_convert(self, markdown_text):
        import subprocess
        binary = self.settings.get("multimarkdown_binary", "")
        if os.path.exists(binary):
            cmd = [binary]
            critic_mode = self.settings.get("strip_critic_marks", "accept")
            if critic_mode in ("accept", "reject"):
                cmd.append('-a' if critic_mode == "accept" else '-r')
            sublime.status_message('converting markdown with multimarkdown...')
            if sublime.platform() == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(
                    cmd, startupinfo=startupinfo,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            else:
                p = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            for line in markdown_text.split('\n'):
                p.stdin.write((line + '\n').encode('utf-8'))
            markdown_html = p.communicate()[0].decode("utf-8")
            if p.returncode:
                # Log info to console
                sublime.error_message("Could not convert file! See console for more info.")
                print(markdown_html)
                markdown_html = _CANNOT_CONVERT
        else:
            sublime.error_message("Cannot find multimarkdown binary!")
            markdown_html = _CANNOT_CONVERT
        return markdown_html


class MarkdownCompiler(Compiler):
    default_css = "markdown.css"

    def get_highlight(self):
        ''' return the Pygments css if enabled '''

        highlight = ''
        if self.pygments_style and not self.noclasses:
            highlight += '<style>%s</style>' % HtmlFormatter(style=self.pygments_style).get_style_defs('.codehilite pre')

        return highlight

    def preprocessor_critic(self, text):
        ''' Stip out multi-markdown critic marks.  Accept changes by default '''
        return CriticDump().dump(text, self.settings.get("strip_critic_marks", "accept") == "accept")

    def parser_specific_preprocess(self, text):
        if self.settings.get("strip_critic_marks", "accept") in ["accept", "reject"]:
            text = self.preprocessor_critic(text)
        return text

    def process_extensions(self, extensions):
        re_pygments = re.compile(r"pygments_style\s*=\s*([a-zA-Z][a-zA-Z_\d]*)")
        re_insert_pygment = re.compile(r"(?P<bracket_start>codehilite\([^)]+?)(?P<bracket_end>\s*\)$)|(?P<start>codehilite)")
        re_no_classes = re.compile(r"noclasses\s*=\s*(True|False)")
        # First search if pygments has manually been set,
        # and if so, read what the desired color scheme to use is
        self.pygments_style = None
        self.noclasses = False
        count = 0
        for e in extensions:
            if e.startswith("codehilite"):
                pygments_style = re_pygments.search(e)
                if pygments_style is None:
                    self.pygments_style = "github"
                    m = re_insert_pygment.match(e)
                    if m is not None:
                        if m.group('bracket_start'):
                            start = m.group('bracket_start') + ',pygments_style='
                            end = ")"
                        else:
                            start = m.group('start') + "(pygments_style="
                            end = ')'

                        extensions[count] = start + self.pygments_style + end
                else:
                    self.pygments_style = pygments_style.group(1)
                noclasses = re_no_classes.search(e)
                if noclasses is not None and noclasses.group(1) == "True":
                    self.noclasses = True
            count += 1

        # Second, if nothing manual was set, see if "enable_highlight" is enabled with pygment support
        # If no style has been set, setup the default
        if (
            self.pygments_style is None and
            self.settings.get("enable_highlight") is True
        ):
            guess_lang = str(bool(self.settings.get("guess_language", True)))
            extensions.append("codehilite(guess_lang=%s,pygments_style=github)" % guess_lang)
            self.pygments_style = "github"

        # Get the base path of source file if available
        base_path = self.settings.get("basepath")
        if base_path is None:
            base_path = ""

        # Replace BASE_PATH keyword with the actual base_path
        return [e.replace("${BASE_PATH}", base_path) for e in extensions]

    def get_config_extensions(self, default_extensions):
        config_extensions = self.settings.get('enabled_extensions')
        if not config_extensions or config_extensions == 'default':
            return self.process_extensions(default_extensions)
        if 'default' in config_extensions:
            config_extensions.remove('default')
            config_extensions.extend(default_extensions)
        return self.process_extensions(config_extensions)

    def parser_specific_convert(self, markdown_text):
        sublime.status_message('converting markdown with Python markdown...')
        config_extensions = self.get_config_extensions(DEFAULT_EXT)
        md = Markdown(extensions=config_extensions)
        html_text = md.convert(markdown_text)
        # Retrieve the meta data returned from the "meta" extension
        self.settings.add_meta(md.Meta)
        return html_text


class MarkdownPreviewSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit, target='browser'):
        parsers = [
            "markdown",
            "github",
            "multimarkdown"
        ]

        self.target = target

        settings = sublime.load_settings("MarkdownPreview.sublime-settings")
        enabled_parsers = set()
        for p in settings.get("enabled_parsers", ["markdown", "github"]):
            if p in parsers:
                enabled_parsers.add(p)

        self.user_parsers = list(enabled_parsers)
        self.user_parsers.sort()

        window = self.view.window()
        length = len(self.user_parsers)
        if window is not None and length:
            if length == 1:
                self.view.run_command(
                    "markdown_preview",
                    {
                        "parser": self.user_parsers[0],
                        "target": self.target
                    }
                )
            else:
                window.show_quick_panel(self.user_parsers, self.run_command)

    def run_command(self, value):
        if value > -1:
            self.view.run_command(
                "markdown_preview",
                {
                    "parser": self.user_parsers[value],
                    "target": self.target
                }
            )


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    def run(self, edit, parser='markdown', target='browser'):
        settings = sublime.load_settings('MarkdownPreview.sublime-settings')

        # backup parser+target for later saves
        self.view.settings().set('parser', parser)
        self.view.settings().set('target', target)

        if parser == "github":
            compiler = GithubCompiler()
        elif parser == "multimarkdown":
            compiler = MultiMarkdownCompiler()
        else:
            compiler = MarkdownCompiler()

        html, body = compiler.run(self.view)

        if target in ['disk', 'browser']:
            # do not use LiveReload unless autoreload is enabled
            if settings.get('enable_autoreload', True):
                # check if LiveReload ST2 extension installed and add its script to the resulting HTML
                livereload_installed = ('LiveReload' in os.listdir(sublime.packages_path()))
                # build the html
                if livereload_installed:
                    port = sublime.load_settings('LiveReload.sublime-settings').get('port', 35729)
                    html += '<script>document.write(\'<script src="http://\' + (location.host || \'localhost\').split(\':\')[0] + \':%d/livereload.js?snipver=1"></\' + \'script>\')</script>' % port
            # update output html file
            tmp_fullpath = getTempMarkdownPreviewPath(self.view)
            save_utf8(tmp_fullpath, html)
            # now opens in browser if needed
            if target == 'browser':
                self.__class__.open_in_browser(tmp_fullpath, settings.get('browser', 'default'))
        elif target == 'sublime':
            # create a new buffer and paste the output HTML
            embed_css = settings.get('embed_css_for_sublime_output', True)
            if embed_css:
                new_view(self.view.window(), html, scratch=True)
            else:
                new_view(self.view.window(), body, scratch=True)
            sublime.status_message('Markdown preview launched in sublime')
        elif target == 'clipboard':
            # clipboard copy the full HTML
            sublime.set_clipboard(html)
            sublime.status_message('Markdown export copied to clipboard')
        elif target == 'save':
            save_location = compiler.settings.get('builtin').get('destination', None)
            if save_location is None:
                save_location = self.view.file_name()
                if save_location is None or not os.path.exists(save_location):
                    # Save as...
                    v = new_view(self.view.window(), html)
                    if v is not None:
                        v.run_command('save')
                else:
                    # Save
                    htmlfile = os.path.splitext(save_location)[0] + '.html'
                    save_utf8(htmlfile, html)
            else:
                save_utf8(save_location, html)

    @classmethod
    def open_in_browser(cls, path, browser='default'):
        if browser == 'default':
            if sys.platform == 'darwin':
                # To open HTML files, Mac OS the open command uses the file
                # associated with .html. For many developers this is Sublime,
                # not the default browser. Getting the right value is
                # embarrassingly difficult.
                import shlex
                import subprocess
                env = {'VERSIONER_PERL_PREFER_32_BIT': 'true'}
                raw = """perl -MMac::InternetConfig -le 'print +(GetICHelper "http")[1]'"""
                process = subprocess.Popen(shlex.split(raw), env=env, stdout=subprocess.PIPE)
                out, err = process.communicate()
                default_browser = out.strip().decode('utf-8')
                cmd = "open -a '%s' %s" % (default_browser, path)
                os.system(cmd)
            else:
                desktop.open(path)
            sublime.status_message('Markdown preview launched in default browser')
        else:
            cmd = '"%s" %s' % (browser, path)
            if sys.platform == 'darwin':
                cmd = "open -a %s" % cmd
            elif sys.platform == 'linux2':
                cmd += ' &'
            elif sys.platform == 'win32':
                cmd = 'start "" %s' % cmd
            result = os.system(cmd)
            if result != 0:
                sublime.error_message('cannot execute "%s" Please check your Markdown Preview settings' % browser)
            else:
                sublime.status_message('Markdown preview launched in %s' % browser)


class MarkdownBuildCommand(sublime_plugin.WindowCommand):
    def init_panel(self):
        if not hasattr(self, 'output_view'):
            if is_ST3():
                self.output_view = self.window.create_output_panel("markdown")
            else:
                self.output_view = self.window.get_output_panel("markdown")

    def puts(self, message):
        message = message + '\n'
        if is_ST3():
            self.output_view.run_command('append', {'characters': message, 'force': True, 'scroll_to_end': True})
        else:
            selection_was_at_end = (len(self.output_view.sel()) == 1
                                    and self.output_view.sel()[0]
                                    == sublime.Region(self.output_view.size()))
            self.output_view.set_read_only(False)
            edit = self.output_view.begin_edit()
            self.output_view.insert(edit, self.output_view.size(), message)
            if selection_was_at_end:
                self.output_view.show(self.output_view.size())
            self.output_view.end_edit(edit)
            self.output_view.set_read_only(True)

    def run(self):
        view = self.window.active_view()
        if not view:
            return
        start_time = time.time()

        self.init_panel()

        settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        parser = settings.get('parser', 'markdown')
        if parser == 'default':
            parser = 'markdown'

        target = settings.get('build_action', 'build')
        if target in ('browser', 'sublime', 'clipboard', 'save'):
            view.run_command("markdown_preview", {"parser": parser, "target": target})
            return

        show_panel_on_build = settings.get("show_panel_on_build", True)
        if show_panel_on_build:
            self.window.run_command("show_panel", {"panel": "output.markdown"})

        mdfile = view.file_name()
        if mdfile is None or not os.path.exists(mdfile):
            self.puts("Can't build an unsaved markdown file.")
            return

        self.puts("Compiling %s..." % mdfile)

        if parser == "github":
            compiler = GithubCompiler()
        elif parser == "multimarkdown":
            compiler = MultiMarkdownCompiler()
        else:
            compiler = MarkdownCompiler()

        html, body = compiler.run(view, True)

        htmlfile = compiler.settings.get('builtin').get('destination', None)

        if htmlfile is None:
            htmlfile = os.path.splitext(mdfile)[0] + '.html'
        self.puts("        ->" + htmlfile)
        save_utf8(htmlfile, html)

        elapsed = time.time() - start_time
        if body == _CANNOT_CONVERT:
            self.puts(_CANNOT_CONVERT)
        self.puts("[Finished in %.1fs]" % (elapsed))
        sublime.status_message("Build finished")
