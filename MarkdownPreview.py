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

ABS_EXCLUDE = tuple(
    [
        'file://', 'https://', 'http://', '/', '#',
        "data:image/jpeg;base64,", "data:image/png;base64,", "data:image/gif;base64,"
    ] + ['\\'] if sys.platform.startswith('win') else []
)


def is_ST3():
    ''' check if ST3 based on python version '''
    version = sys.version_info
    if isinstance(version, tuple):
        version = version[0]
    elif getattr(version, 'major', None):
        version = version.major
    return (version >= 3)

if is_ST3():
    from . import desktop
    from . import markdown2
    from . import markdown_wrapper as markdown
    from .helper import INSTALLED_DIRECTORY
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError

    def Request(url, data, headers):
        ''' Adapter for urllib2 used in ST2 '''
        import urllib.request
        return urllib.request.Request(url, data=data, headers=headers, method='POST')

    unicode_str = str

else:
    import desktop
    import markdown2
    import markdown_wrapper as markdown
    from helper import INSTALLED_DIRECTORY
    from urllib2 import Request, urlopen, HTTPError, URLError

    unicode_str = unicode

_CANNOT_CONVERT = u'cannot convert markdown'


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
        print("Error while load_resource('%s')" % filename)
        traceback.print_exc()
        return ''


def exists_resource(resource_file_path):
    filename = os.path.join(os.path.dirname(sublime.packages_path()), resource_file_path)
    return os.path.isfile(filename)


def new_scratch_view(window, text):
    ''' create a new scratch view and paste text content
        return the new view
    '''

    new_view = window.new_file()
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


class MarkdownPreviewListener(sublime_plugin.EventListener):
    ''' auto update the output html if markdown file has already been converted once '''

    def on_post_save(self, view):
        settings = sublime.load_settings('MarkdownPreview.sublime-settings')
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
        view = new_scratch_view(self.view.window(), lines)
        view.set_name("Markdown Cheatsheet")

        # Set syntax file
        syntax_files = ["Packages/Markdown Extended/Syntaxes/Markdown Extended.tmLanguage", "Packages/Markdown/Markdown.tmLanguage"]
        for file in syntax_files:
            if exists_resource(file):
                view.set_syntax_file(file)
                break  # Done if any syntax is set.

        sublime.status_message('Markdown cheat sheet opened')


class MarkdownCompiler():
    ''' Do the markdown converting '''

    def isurl(self, css_name):
        match = re.match(r'https?://', css_name)
        if match:
            return True
        return False

    def get_default_css(self, parser):
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
            return u"<style>%s</style>" % load_resource('github.css' if parser == 'github' else 'markdown.css')

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

    def get_stylesheet(self, parser):
        ''' return the correct CSS file based on parser and settings '''
        return self.get_default_css(parser) + self.get_override_css()

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
        ''' return the Highlight.js and css if enabled '''

        highlight = ''
        if self.settings.get('enable_highlight') is True and self.settings.get('parser') == 'default':
            highlight += "<style>%s</style>" % load_resource('highlight.css')
            highlight += "<script>%s</script>" % load_resource('highlight.js')
            if self.settings.get("highlight_js_guess", True):
                highlight += "<script>%s</script>" % load_resource("highlight.guess.js")
            else:
                highlight += "<script>%s</script>" % load_resource("highlight.noguess.js")
        return highlight

    def get_contents(self, wholefile=False):
        ''' Get contents or selection from view and optionally strip the YAML front matter '''
        region = sublime.Region(0, self.view.size())
        contents = self.view.substr(region)
        if not wholefile:
            # use selection if any
            selection = self.view.substr(self.view.sel()[0])
            if selection.strip() != '':
                contents = selection

        # Strip out multi-markdown critic marks as first task
        if self.settings.get("strip_critic_marks", "accept") in ["accept", "reject"]:
            contents = self.preprocessor_critic(contents)

        # Remove yaml front matter
        if self.settings.get('strip_yaml_front_matter') and contents.startswith('---'):
            title = ''
            title_match = re.search('(?:title:)(.+)', contents, flags=re.IGNORECASE)
            if title_match:
                stripped_title = title_match.group(1).strip()
                title = '%s\n%s\n\n' % (stripped_title, '=' * len(stripped_title))
            contents_without_front_matter = re.sub(r'(?s)^---.*---\n', '', contents)
            contents = '%s%s' % (title, contents_without_front_matter)
        return contents

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
        html = RE_SOURCES.sub(tag_fix, html)
        return html

    def preprocessor_critic(self, text):
        ''' Stip out multi-markdown critic marks.  Accept changes by default '''
        return CriticDump().dump(text, self.settings.get("strip_critic_marks", "accept") == "accept")

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
            data = src
            filename = self.view.file_name()
            base_path = ""
            if filename and os.path.exists(filename):
                base_path = os.path.dirname(filename)

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
        html = RE_SOURCES.sub(b64, html)
        return html

    def process_extensions(self, extensions):
        filename = self.view.file_name()
        base_path = ""
        if filename and os.path.exists(filename):
            base_path = os.path.dirname(filename)

        if self.settings.get("get_highlight") and self.settings.get("parser") == "default":
            found = False
            for e in extensions:
                if e.startswith("codehilite"):
                    found = True
                    break
            if not found:
                extensions.append("codehilite")

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

    def convert_markdown(self, markdown_text, parser):
        ''' convert input markdown to HTML, with github or builtin parser '''

        markdown_html = _CANNOT_CONVERT
        if parser == 'github':
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

        elif parser == 'markdown2':
            # convert the markdown
            enabled_extras = set(self.get_config_extensions(['footnotes', 'toc', 'fenced-code-blocks', 'cuddled-lists']))
            if self.settings.get("enable_mathjax") is True or self.settings.get("enable_highlight") is True:
                enabled_extras.add('code-friendly')
            markdown_html = markdown2.markdown(markdown_text, extras=list(enabled_extras))
            toc_html = markdown_html.toc_html
            if toc_html:
                toc_markers = ['[toc]', '[TOC]', '<!--TOC-->']
                for marker in toc_markers:
                    markdown_html = markdown_html.replace(marker, toc_html)

        else:
            sublime.status_message('converting markdown with Python markdown...')
            config_extensions = self.get_config_extensions(['extra', 'toc'])
            markdown_html = markdown.markdown(markdown_text, extensions=config_extensions)

        image_convert = self.settings.get("image_path_conversion", "absolute")
        file_convert = self.settings.get("file_path_conversions", "absolute")

        if "absolute" in (image_convert, file_convert):
            markdown_html = self.postprocessor_absolute(markdown_html, image_convert, file_convert)

        if image_convert == "base64":
            markdown_html = self.postprocessor_base64(markdown_html)

        return markdown_html

    def get_title(self):
        title = self.view.name()
        if not title:
            fn = self.view.file_name()
            title = 'untitled' if not fn else os.path.splitext(os.path.basename(fn))[0]
        return '<title>%s</title>' % title

    def run(self, view, parser, wholefile=False):
        ''' return full html and body html for view. '''
        self.settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        self.view = view

        contents = self.get_contents(wholefile)

        body = self.convert_markdown(contents, parser)

        html_template = self.settings.get('html_template')

        # use customized html template if given
        if html_template and os.path.exists(html_template):
            head = u''
            if not self.settings.get('skip_default_stylesheet'):
                head += self.get_stylesheet(parser)
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
            html += self.get_stylesheet(parser)
            html += self.get_javascript()
            html += self.get_highlight()
            html += self.get_mathjax()
            html += self.get_title()
            html += '</head><body>'
            html += body
            html += '</body>'
            html += '</html>'

        return html, body


compiler = MarkdownCompiler()


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    def run(self, edit, parser='markdown', target='browser'):
        settings = sublime.load_settings('MarkdownPreview.sublime-settings')

        # backup parser+target for later saves
        self.view.settings().set('parser', parser)
        self.view.settings().set('target', target)

        html, body = compiler.run(self.view, parser)

        if target in ['disk', 'browser']:
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
                new_scratch_view(self.view.window(), html)
            else:
                new_scratch_view(self.view.window(), body)
            sublime.status_message('Markdown preview launched in sublime')
        elif target == 'clipboard':
            # clipboard copy the full HTML
            sublime.set_clipboard(html)
            sublime.status_message('Markdown export copied to clipboard')

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

        show_panel_on_build = settings.get("show_panel_on_build", True)
        if show_panel_on_build:
            self.window.run_command("show_panel", {"panel": "output.markdown"})

        mdfile = view.file_name()
        if mdfile is None:
            self.puts("Can't build a unsaved markdown file.")
            return

        self.puts("Compiling %s..." % mdfile)

        html, body = compiler.run(view, parser, True)

        htmlfile = os.path.splitext(mdfile)[0] + '.html'
        self.puts("        ->" + htmlfile)
        save_utf8(htmlfile, html)

        elapsed = time.time() - start_time
        if body == _CANNOT_CONVERT:
            self.puts(_CANNOT_CONVERT)
        self.puts("[Finished in %.1fs]" % (elapsed))
        sublime.status_message("Build finished")
