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
import traceback


if sublime.version() >= '3000':
    from . import desktop
    from . import markdown2
    from . import markdown
    from .helper import INSTALLED_DIRECTORY
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    
    def Request(url, data, headers):
        ''' Adapter for urllib2 used in ST2 '''
        import urllib.request
        return urllib.request.Request(url, data=data, headers=headers, method='POST')

else: # ST2
    import desktop
    import markdown2
    import markdown
    from helper import INSTALLED_DIRECTORY
    from urllib2 import Request, urlopen, HTTPError, URLError

_CANNOT_CONVERT = u'cannot convert markdown'


def getTempMarkdownPreviewPath(view):
    ''' return a permanent full path of the temp markdown preview file '''

    settings = sublime.load_settings('MarkdownPreview.sublime-settings')

    tmp_filename = '%s.html' % view.id()
    if settings.get('path_tempfile'):
        tmp_fullpath = os.path.join(settings.get('path_tempfile'), tmp_filename)
    else:
        tmp_fullpath = os.path.join(tempfile.gettempdir(), tmp_filename)
    return tmp_fullpath

def save_utf8(filename, text):
    v = sublime.version()
    if v >= '3000':
        f = open(filename, 'w', encoding='utf-8')
        f.write(text)
        f.close()
    else: # 2.x
        f = open(filename, 'w')
        f.write(text.encode('utf-8'))
        f.close()

def load_utf8(filename):
    v = sublime.version()
    if v >= '3000':
        return open(filename, 'r', encoding='utf-8').read()
    else: # 2.x
        return open(filename, 'r').read().decode('utf-8')

def load_resource(name):
    ''' return file contents for files within the package root folder '''
    v = sublime.version()
    if v >= '3000':
        filename = '/'.join(['Packages', INSTALLED_DIRECTORY, name])
        try:
            return sublime.load_resource(filename)
        except:
            print("Error while load_resource('%s')" % filename)
            traceback.print_exc()
            return ''
            
    else: # 2.x
        filename = os.path.join(sublime.packages_path(), INSTALLED_DIRECTORY, name)

        if not os.path.isfile(filename):
            print('Error while lookup resources file: %s', name)
            return ''

        try:
            return open(filename, 'r').read().decode('utf-8')
        except:
            print("Error while load_resource('%s')" % filename)
            traceback.print_exc()
            return ''

def exists_resource(resource_file_path):
    if sublime.version() >= '3000':
        try:
            sublime.load_resource(resource_file_path)
            return True
        except:
            return False
    else:
        filename = os.path.join(os.path.dirname(sublime.packages_path()), resource_file_path)
        return os.path.isfile(filename)

def new_scratch_view(window, text):
    ''' create a new scratch view and paste text content
        return the new view
    '''

    new_view = window.new_file()
    new_view.set_scratch(True)
    if sublime.version() >= '3000':
        new_view.run_command('append', {
            'characters': text,
        })
    else: # 2.x
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
                break # Done if any syntax is set.

        sublime.status_message('Markdown cheat sheet opened')



class MarkdownCompiler():
    ''' Do the markdown converting '''

    def isurl(self, css_name):
        match = re.match(r'https?://', css_name)
        if match:
            return True
        return False

    def get_search_path_css(self, parser):
        css_name = self.settings.get('css', 'default')

        if self.isurl(css_name) or os.path.isabs(css_name):
            return u"<link href='%s' rel='stylesheet' type='text/css'>" % css_name

        if css_name == 'default':
            css_name = 'github.css' if parser == 'github' else 'markdown.css'

        # Try the local folder for css file.
        mdfile = self.view.file_name()
        if mdfile is not None:
            css_path = os.path.join(os.path.dirname(mdfile), css_name)
            if os.path.isfile(css_path):
                return u"<style>%s</style>" % load_utf8(css_path)

        # Try the build-in css files.
        return u"<style>%s</style>" % load_resource(css_name)

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
        return self.get_search_path_css(parser) + self.get_override_css()

    def get_javascript(self):
        js_files = self.settings.get('js')
        scripts = ''

        if js_files is not None:
            # Ensure string values become a list.
            if isinstance(js_files, str) or isinstance(js_files, unicode):
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
            highlight += "<script>hljs.initHighlightingOnLoad();</script>"
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
        if self.settings.get('strip_yaml_front_matter') and contents.startswith('---'):
            title = ''
            title_match = re.search('(?:title:)(.+)', contents, flags=re.IGNORECASE)
            if title_match:
                stripped_title = title_match.group(1).strip()
                title = '%s\n%s\n\n' % (stripped_title, '=' * len(stripped_title))
            contents_without_front_matter = re.sub(r'(?s)^---.*---\n', '', contents)
            contents = '%s%s' % (title, contents_without_front_matter)
        return contents

    def postprocessor(self, html):
        ''' fix relative paths in images, scripts, and links for the internal parser '''
        def tag_fix(match):
            tag, src = match.groups()
            filename = self.view.file_name()
            if filename:
                if not src.startswith(('file://', 'https://', 'http://', '/', '#')):
                    abs_path = u'file://%s/%s' % (os.path.dirname(filename), src)
                    tag = tag.replace(src, abs_path)
            return tag
        RE_SOURCES = re.compile("""(?P<tag><(?:img|script|a)[^>]+(?:src|href)=["'](?P<src>[^"']+)[^>]*>)""")
        html = RE_SOURCES.sub(tag_fix, html)
        return html

    def get_config_extensions(self, default_extensions):
        config_extensions = self.settings.get('enabled_extensions')
        if not config_extensions or config_extensions == 'default':
            return default_extensions
        if 'default' in config_extensions:
            config_extensions.remove( 'default' )
            config_extensions.extend( default_extensions )
        return config_extensions

    def curl_convert(self, data):
        try:
            import subprocess
            shell_safe_json = data.decode('utf-8').replace('\"', '\\"').replace("`", "\\`")
            curl_args = [
                'curl',
                '-H',
                '"Content-Type: application/json"',
                '-d',
                '"' + shell_safe_json + '"',
                'https://api.github.com/markdown'
            ]
            markdown_html = subprocess.Popen(curl_args, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
            return markdown_html
        except subprocess.CalledProcessError as e:
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

            # postprocess the html from internal parser
            markdown_html = self.postprocessor(markdown_html)
        else:
            sublime.status_message('converting markdown with Python markdown...')
            config_extensions = self.get_config_extensions(['extra', 'toc'])
            markdown_html = markdown.markdown(markdown_text, extensions=config_extensions)
            markdown_html = self.postprocessor(markdown_html)            

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
                html += '<script>document.write(\'<script src="http://\' + (location.host || \'localhost\').split(\':\')[0] + \':35729/livereload.js?snipver=1"></\' + \'script>\')</script>'
            # update output html file
            tmp_fullpath = getTempMarkdownPreviewPath(self.view)
            save_utf8(tmp_fullpath, html)
            # now opens in browser if needed
            if target == 'browser':
                config_browser = settings.get('browser')
                if config_browser and config_browser != 'default':
                    cmd = '"%s" %s' % (config_browser, tmp_fullpath)
                    if sys.platform == 'darwin':
                        cmd = "open -a %s" % cmd
                    elif sys.platform == 'linux2':
                        cmd += ' &'
                    result = os.system(cmd)
                    if result != 0:
                        sublime.error_message('cannot execute "%s" Please check your Markdown Preview settings' % config_browser)
                    else:
                        sublime.status_message('Markdown preview launched in %s' % config_browser)
                else:
                    desktop.open(tmp_fullpath)
                    sublime.status_message('Markdown preview launched in default html viewer')
        elif target == 'sublime':
            # create a new buffer and paste the output HTML
            new_scratch_view(self.view.window(), body)
            sublime.status_message('Markdown preview launched in sublime')
        elif target == 'clipboard':
            # clipboard copy the full HTML
            sublime.set_clipboard(html)
            sublime.status_message('Markdown export copied to clipboard')


class MarkdownBuildCommand(sublime_plugin.WindowCommand):
    def init_panel(self):
        if not hasattr(self, 'output_view'):
            if sublime.version() >= '3000':
                self.output_view = self.window.create_output_panel("markdown")
            else:
                self.output_view = self.window.get_output_panel("markdown")

    def puts(self, message):
        message = message + '\n'
        if sublime.version() >= '3000':
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
        
        show_panel_on_build = sublime.load_settings("Preferences.sublime-settings").get("show_panel_on_build", True)
        if show_panel_on_build:
            self.window.run_command("show_panel", {"panel": "output.markdown"})
        
        mdfile = view.file_name()
        if mdfile is None:
            self.puts("Can't build a unsaved markdown file.")
            return

        self.puts("Compiling %s..." % mdfile)

        html, body = compiler.run(view, 'markdown', True)

        htmlfile = os.path.splitext(mdfile)[0]+'.html'
        self.puts("        ->"+htmlfile)
        save_utf8(htmlfile, html)

        elapsed = time.time() - start_time
        if body == _CANNOT_CONVERT:
            self.puts(_CANNOT_CONVERT)
        self.puts("[Finished in %.1fs]" % (elapsed))
        sublime.status_message("Build finished")
