# -*- encoding: UTF-8 -*-
"""Mardown Preview main."""
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
import yaml
import textwrap
from collections import OrderedDict
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from pygments.formatters import get_formatter_by_name
from . import desktop
from .markdown_settings import Settings
from .markdown_wrapper import StMarkdown as Markdown

_CANNOT_CONVERT = 'cannot convert markdown'
_EXT_CONFIG = "Packages/Markdown Preview/markdown_preview.yml"

PYGMENTS_LOCAL = {
    'github': 'css/pygments/github.css',
    'github2014': 'css/pygments/github2014.css'
}

RELOAD_JS = """<script async>
document.write(
  '<script src="http://' +
  (location.host || 'localhost').split(':')[0] +
  ':%d/livereload.js?snipver=1"></' +
  'script>')
</script>
"""


def yaml_load(stream, loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Custom yaml loader.

    Make all YAML dictionaries load as ordered Dicts.
    http://stackoverflow.com/a/21912744/3609487
    Load all strings as unicode.
    http://stackoverflow.com/a/2967461/3609487
    """

    def construct_mapping(loader, node):
        """Convert to ordered dict."""

        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    def construct_yaml_str(self, node):
        """Override the default string handling function to always return unicode objects."""

        return self.construct_scalar(node)

    class Loader(loader):
        """Custom Loader."""

    Loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )

    Loader.add_constructor(
        'tag:yaml.org,2002:str',
        construct_yaml_str
    )

    return yaml.load(stream, Loader)


def request_url(url, data, headers):
    """Request URL."""
    import urllib.request
    return urllib.request.Request(url, data=data, headers=headers, method='POST')


def get_temp_preview_path(view):
    """Return a permanent full path of the temp markdown preview file."""
    settings = sublime.load_settings('MarkdownPreview.sublime-settings')

    tmp_filename = '%s.html' % view.id()
    if settings.get('path_tempfile'):
        if os.path.isabs(settings.get('path_tempfile')):  # absolute path or not
            tmp_dir = settings.get('path_tempfile')
        else:
            tmp_dir = os.path.join(os.path.dirname(view.file_name()), settings.get('path_tempfile'))
    else:
        tmp_dir = tempfile.gettempdir()

    if not os.path.isdir(tmp_dir):  # create dir if not exsits
        os.makedirs(tmp_dir)

    tmp_fullpath = os.path.join(tmp_dir, tmp_filename)
    return tmp_fullpath


def save_utf8(filename, text):
    """Save to UTF8 file."""
    with codecs.open(filename, 'w', encoding='utf-8')as f:
        f.write(text)


def load_utf8(filename):
    """Load UTF8 file."""
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def load_resource(name):
    """Return file contents for files within the package root folder."""
    try:
        return sublime.load_resource('Packages/Markdown Preview/{0}'.format(name))
    except Exception:
        print("Error while load_resource('%s')" % name)
        traceback.print_exc()
        return ''


def exists_resource(resource_file_path):
    """Check if resource exists."""
    filename = os.path.join(os.path.dirname(sublime.packages_path()), resource_file_path)
    return os.path.isfile(filename)


def new_view(window, text, scratch=False):
    """
    Create a new view and paste text content.

    Return the new view that can optionally can be set as scratch.
    """

    new_view = window.new_file()
    if scratch:
        new_view.set_scratch(True)
    new_view.run_command('append', {
        'characters': text,
    })
    return new_view


def get_references(file_name, encoding="utf-8"):
    """Get footnote and general references from outside source."""
    text = ''
    if file_name is not None:
        if os.path.exists(file_name):
            try:
                with codecs.open(file_name, "r", encoding=encoding) as f:
                    text = f.read()
            except Exception:
                print(traceback.format_exc())
        else:
            print("Could not find reference file %s!", file_name)
    return text


class MarkdownPreviewListener(sublime_plugin.EventListener):
    """Auto update the output html if markdown file has already been converted once."""

    def on_post_save(self, view):
        """Handle auto-reload on save."""
        settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        if settings.get('enable_autoreload', True):
            filetypes = settings.get('markdown_filetypes')
            file_name = view.file_name()
            if filetypes and file_name is not None and file_name.endswith(tuple(filetypes)):
                temp_file = get_temp_preview_path(view)
                if os.path.isfile(temp_file):
                    # reexec markdown conversion
                    # todo : check if browser still opened and reopen it if needed
                    view.run_command('markdown_preview', {
                        'target': 'disk',
                        'parser': view.settings().get('parser')
                    })
                    sublime.status_message('Markdown preview file updated')


class MarkdownCheatsheetCommand(sublime_plugin.TextCommand):
    """Open our markdown cheat sheet."""

    def run(self, edit):
        """Execute command."""
        lines = '\n'.join(load_resource('samples/sample.md').splitlines())
        view = new_view(self.view.window(), lines, scratch=True)
        view.set_name("Markdown Cheatsheet")

        # Set syntax file
        syntax_files = [
            "Packages/Markdown Extended/Syntaxes/Markdown Extended.tmLanguage",
            "Packages/Markdown/Markdown.tmLanguage"
        ]
        for file in syntax_files:
            if exists_resource(file):
                view.set_syntax_file(file)
                break  # Done if any syntax is set.

        sublime.status_message('Markdown cheat sheet opened')


class Compiler(object):
    """Base compiler that does the markdown converting."""

    default_css = "css/markdown.css"

    def isurl(self, css_name):
        """Check if URL."""
        match = re.match(r'https?://', css_name)
        if match:
            return True
        return False

    def get_default_css(self):
        """Locate the correct CSS with the 'css' setting."""
        css_list = self.settings.get('css', ['default'])

        if not isinstance(css_list, list):
            css_list = [css_list]

        css_text = []
        for css_name in css_list:
            if css_name.startswith('res://'):
                internal_file = os.path.join(sublime.packages_path(), os.path.normpath(css_name[6:]))
                if os.path.exists(internal_file):
                    css_text.append("<style>%s</style>" % load_utf8(internal_file))
                else:
                    css_text.append("<style>%s</style>" % sublime.load_resource('Packages/' + css_name[6:]))
            elif self.isurl(css_name):
                # link to remote URL
                css_text.append("<link href='%s' rel='stylesheet' type='text/css'>" % css_name)
            elif os.path.isfile(os.path.expanduser(css_name)):
                # use custom CSS file
                css_text.append("<style>%s</style>" % load_utf8(os.path.expanduser(css_name)))
            elif css_name == 'default':
                # use parser CSS file
                css_text.append("<style>%s</style>" % load_resource(self.default_css))

        return '\n'.join(css_text)

    def get_override_css(self):
        """Handles allow_css_overrides setting."""

        if self.settings.get('allow_css_overrides'):
            filename = self.view.file_name()
            filetypes = self.settings.get('markdown_filetypes')

            if filename and filetypes:
                for filetype in filetypes:
                    if filename.endswith(filetype):
                        css_filename = filename.rpartition(filetype)[0] + '.css'
                        if (os.path.isfile(css_filename)):
                            return "<style>%s</style>" % load_utf8(css_filename)
        return ''

    def get_stylesheet(self):
        """Return the correct CSS file based on parser and settings."""
        return self.get_default_css() + self.get_override_css()

    def get_javascript(self):
        """Return JavaScript."""
        js_files = self.settings.get('js')
        scripts = ''

        if js_files is not None:
            # Ensure string values become a list.
            if isinstance(js_files, str) or isinstance(js_files, str):
                js_files = [js_files]
            # Only load scripts if we have a list.
            if isinstance(js_files, list):
                for js_file in js_files:
                    if js_file.startswith('res://'):
                        internal_file = os.path.join(sublime.packages_path(), os.path.normpath(js_file[6:]))
                        if os.path.exists(internal_file):
                            scripts += "<script>%s</script>" % load_utf8(internal_file)
                        else:
                            scripts += "<script>%s</script>" % sublime.load_resource('Packages/' + js_file[6:])
                    elif os.path.isabs(js_file):
                        # Load the script inline to avoid cross-origin.
                        scripts += "<script>%s</script>" % load_utf8(js_file)
                    else:
                        scripts += "<script type='text/javascript' src='%s'></script>" % js_file
        return scripts

    def get_highlight(self):
        """Base highlight method."""
        return ''

    def get_contents(self, wholefile=False):
        """Get contents or selection from view and optionally strip the YAML front matter."""
        region = sublime.Region(0, self.view.size())
        contents = self.view.substr(region)
        if not wholefile:
            # use selection if any
            selection = self.view.substr(self.view.sel()[0])
            if selection.strip() != '':
                contents = selection

        # Remove yaml front matter
        if self.settings.get('strip_yaml_front_matter'):
            frontmatter, contents = self.preprocessor_yaml_frontmatter(contents)
            self.settings.apply_frontmatter(frontmatter)

        references = self.settings.get('builtin').get('references', [])
        for ref in references:
            contents += get_references(ref)

        # Striip CriticMarkup
        if self.settings.get("strip_critic_marks", "accept") in ("accept", "reject"):
            contents = self.preprocessor_criticmarkup(
                contents, self.settings.get("strip_critic_marks", "accept") == "accept"
            )

        contents = self.parser_specific_preprocess(contents)

        return contents

    def parser_specific_preprocess(self, text):
        """Base parser specific preprocess method."""
        return text

    def preprocessor_yaml_frontmatter(self, text):
        """Get frontmatter from string."""

        frontmatter = OrderedDict()

        if text.startswith("---"):
            m = re.search(r'^(-{3}\r?\n(?!\r?\n)(.*?)(?<=\n)(?:-{3}|\.{3})\r?\n)', text, re.DOTALL)
            if m:
                yaml_okay = True
                try:
                    frontmatter = yaml_load(m.group(2))
                    if frontmatter is None:
                        frontmatter = OrderedDict()
                    # If we didn't get a dictionary, we don't want this as it isn't frontmatter.
                    assert isinstance(frontmatter, (dict, OrderedDict)), TypeError
                except Exception:
                    # We had a parsing error. This is not the YAML we are looking for.
                    yaml_okay = False
                    frontmatter = OrderedDict()
                    traceback.format_exc()
                if yaml_okay:
                    text = text[m.end(1):]

        return frontmatter, text

    def parser_specific_postprocess(self, text):
        """
        Parser specific post process.

        Override this to add parser specific post processing.
        """
        return text

    def postprocessor_pathconverter(self, source, image_convert, file_convert, absolute=False):
        """Convert paths to absolute or relative paths."""
        from pymdownx.pathconverter import PathConverterPostprocessor

        relative_path = ''
        if not absolute:
            if self.preview:
                relative_path = get_temp_preview_path(self.view)
            else:
                relative_path = self.settings.get('builtin').get("destination")
                if not relative_path:
                    mdfile = self.view.file_name()
                    if mdfile is not None and os.path.exists(mdfile):
                        relative_path = os.path.splitext(mdfile)[0] + '.html'
            if relative_path:
                relative_path = os.path.dirname(relative_path)

        tags = []
        if file_convert:
            tags.extend(["script", "a", "link"])
        if image_convert:
            tags.append('img')

        pathconv = PathConverterPostprocessor()
        pathconv.config = {
            "base_path": self.settings.get('builtin').get("basepath"),
            "relative_path": relative_path,
            "absolute": absolute,
            "tags": ' '.join(tags)
        }

        return pathconv.run(source)

    def postprocessor_base64(self, source):
        """Convert resources (currently images only) to base64."""
        from pymdownx.b64 import B64Postprocessor

        b64proc = B64Postprocessor()
        b64proc.config = {'base_path': self.settings.get('builtin').get("basepath")}
        return b64proc.run(source)

    def postprocessor_simple(self, source):
        """Strip out ids and classes for a simplified HTML output."""
        from pymdownx.striphtml import StripHtmlPostprocessor

        strip_comments = True,
        strip_js_on_attributes = True
        strip_attributes = ["id", "class", "style"]
        striphtml = StripHtmlPostprocessor(strip_comments, strip_js_on_attributes, strip_attributes, None)
        return striphtml.run(source)

    def preprocessor_criticmarkup(self, source, accept):
        """Stip out multi-markdown critic marks.  Accept changes by default."""
        from pymdownx.critic import CriticViewPreprocessor, CriticStash, CRITIC_KEY

        text = ''
        mode = 'accept' if accept else 'reject'
        critic_stash = CriticStash(CRITIC_KEY)
        critic = CriticViewPreprocessor(critic_stash)
        critic.config = {'mode': mode}
        text = '\n'.join(critic.run(source.split('\n')))

        return text

    def convert_markdown(self, markdown_text):
        """Convert input markdown to HTML, with github or builtin parser."""
        markdown_html = self.parser_specific_convert(markdown_text)

        image_convert = self.settings.get("image_path_conversion", "absolute")
        file_convert = self.settings.get("file_path_conversions", "absolute")

        markdown_html = self.parser_specific_postprocess(markdown_html)

        if "absolute" in (image_convert, file_convert):
            markdown_html = self.postprocessor_pathconverter(
                markdown_html,
                image_convert == 'absolute',
                file_convert == 'absolute',
                True
            )

        if "relative" in (image_convert, file_convert):
            markdown_html = self.postprocessor_pathconverter(
                markdown_html,
                image_convert == 'relative',
                file_convert == 'relative',
                False
            )

        if image_convert == "base64":
            markdown_html = self.postprocessor_base64(markdown_html)

        if self.settings.get("html_simple", False):
            markdown_html = self.postprocessor_simple(markdown_html)

        return markdown_html

    def get_title(self):
        """Get HTML title."""
        if self.meta_title is not None:
            title = self.meta_title
        else:
            title = self.view.name()
        if not title:
            fn = self.view.file_name()
            title = 'untitled' if not fn else os.path.splitext(os.path.basename(fn))[0]
        return '<title>%s</title>' % cgi.escape(title)

    def get_meta(self):
        """Get meta data."""
        self.meta_title = None
        meta = []
        for k, v in self.settings.get("meta", {}).items():
            if k == "title":
                if isinstance(v, list):
                    if len(v) == 0:
                        v = ""
                    else:
                        v = v[0]
                self.meta_title = str(v)
                continue
            if isinstance(v, list):
                v = ','.join(v)
            if v is not None:
                meta.append(
                    '<meta name="%s" content="%s">' % (cgi.escape(k, True), cgi.escape(v, True))
                )
        return '\n'.join(meta)

    def run(self, view, wholefile=False, preview=False):
        """Return full HTML and body HTML for view."""
        self.settings = Settings('MarkdownPreview.sublime-settings', view.file_name())
        self.preview = preview
        self.view = view

        contents = self.get_contents(wholefile)

        body = self.convert_markdown(contents)

        html_template = self.settings.get('html_template')

        if html_template:
            html_template = os.path.abspath(os.path.expanduser(html_template))

        # use customized html template if given
        if self.settings.get('html_simple', False):
            html = body
        elif html_template and os.path.exists(html_template):
            head = ''
            head += self.get_meta()
            head += self.get_stylesheet()
            head += self.get_javascript()
            head += self.get_highlight()
            head += self.get_title()

            html = load_utf8(html_template)
            html = html.replace('{{ HEAD }}', head, 1)
            html = html.replace('{{ BODY }}', body, 1)
        else:
            html = '<!DOCTYPE html>'
            html += '<html><head><meta charset="utf-8">'
            html += self.get_meta()
            html += self.get_stylesheet()
            html += self.get_javascript()
            html += self.get_highlight()
            html += self.get_title()
            html += '</head><body>'
            html += '<article class="markdown-body">'
            html += body
            html += '</article>'
            html += '</body>'
            html += '</html>'

        return html, body


class GithubCompiler(Compiler):
    """GitHub compiler."""

    default_css = "css/github.css"

    def curl_convert(self, data):
        """Use curl to send Markdown content through GitHub API."""
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
            sublime.error_message(
                textwrap.dedent(
                    """\
                    Cannot use github API to convert markdown. SSL is not included in your Python installation. \
                    And using curl didn't work either
                    """
                )
            )
        return None

    def parser_specific_postprocess(self, html):
        """Run GitHub specific postprocesses."""
        if self.settings.get("github_inject_header_ids", False):
            html = self.postprocess_inject_header_id(html)
        return html

    def postprocess_inject_header_id(self, html):
        """Insert header ids when no anchors are present."""
        from pymdownx.slugs import uslugify
        unique = {}
        re_header = re.compile(r'(?P<open><h([1-6])>)(?P<text>.*?)(?P<close></h\2>)', re.DOTALL)

        def inject_id(m):
            id = uslugify(m.group('text'), '-')
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

        return re_header.sub(inject_id, html)

    def get_github_response_from_exception(self, e):
        """Convert GitHub Response."""
        body = json.loads(e.read().decode('utf-8'))
        return 'GitHub\'s original response: (HTTP Status Code %s) "%s"' % (e.code, body['message'])

    def parser_specific_convert(self, markdown_text):
        """Convert input markdown to HTML with github parser."""
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
            request = request_url(url, data, headers)
            markdown_html = urlopen(request).read().decode('utf-8')
        except HTTPError as e:
            if e.code == 401:
                sublime.error_message(
                    "GitHub API authentication failed. Please check your OAuth token.\n\n" +
                    self.get_github_response_from_exception(e)
                )
            elif e.code == 403:  # Forbidden
                sublime.error_message(
                    textwrap.dedent(
                        """\
                        It seems like you have exceeded GitHub's API rate limit.

                        To continue using GitHub's markdown format with this package, log in to \
                        GitHub, then go to Settings > Personal access tokens > Generate new token, \
                        copy the token's value, and paste it in this package's user settings under the key \
                        'github_oauth_token'. Example:

                        {
                            "github_oauth_token": "xxxx...."
                        }

                        """
                    ) + self.get_github_response_from_exception(e)
                )
            else:
                sublime.error_message(
                    "GitHub API responded in an unfriendly way!\n\n" +
                    self.get_github_response_from_exception(e)
                )
        except URLError:
            # Maybe this is a Linux-install of ST which doesn't bundle with SSL support
            # So let's try wrapping curl instead
            markdown_html = self.curl_convert(data)
        except Exception:
            e = sys.exc_info()[1]
            print(e)
            traceback.print_exc()
            sublime.error_message(
                "Cannot use GitHub's API to convert Markdown. Please check your settings.\n\n" +
                self.get_github_response_from_exception(e)
            )
        else:
            sublime.status_message('converted markdown with github API successfully')

        return markdown_html


class ExternalMarkdownCompiler(Compiler):
    """Compiler for other, external Markdown parsers."""

    default_css = "css/markdown.css"

    def __init__(self, parser):
        """Initialize."""

        self.parser = parser
        super(ExternalMarkdownCompiler, self).__init__()

    def parser_specific_convert(self, markdown_text):
        """Convert Markdown with external parser."""
        import subprocess
        settings = sublime.load_settings("MarkdownPreview.sublime-settings")
        binary = settings.get('markdown_binary_map', {})[self.parser]

        if len(binary) and os.path.exists(binary[0]):
            cmd = binary
            sublime.status_message('converting markdown with %s...' % self.parser)
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
            sublime.error_message("Cannot find % binary!" % self.binary)
            markdown_html = _CANNOT_CONVERT
        return markdown_html


class MarkdownCompiler(Compiler):
    """Python Markdown compiler."""

    default_css = "css/markdown.css"

    def set_highlight(self, pygments_style, css_class):
        """Set the Pygments css."""
        if pygments_style:
            style = None
            if pygments_style not in PYGMENTS_LOCAL:
                try:
                    style = get_formatter_by_name('html', style=pygments_style).get_style_defs(
                        ''.join(['.' + x for x in css_class.split(' ') if x])
                    )
                except Exception:
                    traceback.print_exc()
                    pygments_style = 'github'
            if style is None:
                style = load_resource(PYGMENTS_LOCAL[pygments_style]) % {
                    'css_class': ''.join(['.' + x for x in css_class.split(' ') if x])
                }

            self.pygments_style = '<style>%s</style>' % style
        return pygments_style

    def get_highlight(self):
        """Return the Pygments css if enabled."""
        return self.pygments_style if self.pygments_style else ''

    def preprocessor_critic(self, source):
        """
        Stip out multi-markdown critic marks.

        Accept changes by default.
        """
        from pymdownx.critic import CriticViewPreprocessor, CriticStash, CRITIC_KEY

        text = ''
        mode = 'accept' if self.settings.get("strip_critic_marks", "accept") == "accept" else 'reject'
        critic_stash = CriticStash(CRITIC_KEY)
        critic = CriticViewPreprocessor(critic_stash)
        critic.config = {'mode': mode}
        text = '\n'.join(critic.run(source.split('\n')))

        return text

    def process_extensions(self, extensions):
        """Process extensions and related settings."""
        # See if we need to inject CSS for pygments.
        self.pygments_style = None
        style = self.settings.get('pygments_style', 'github')
        if self.settings.get('pygments_inject_css', True):
            # Check if the desired style exists internally
            self.set_highlight(style, self.settings.get('pygments_css_class', 'codehilite'))

        # Get the base path of source file if available
        base_path = self.settings.get('builtin').get("basepath")
        if base_path is None:
            base_path = ""

        names = []
        settings = {}
        for e in extensions:
            # Ensure extension is in correct format and separate config from extension
            if isinstance(e, str):
                ext = e
                config = OrderedDict()
            elif isinstance(e, (dict, OrderedDict)):
                ext = list(e.keys())[0]
                config = list(e.values())[0]
                if config is None:
                    config = OrderedDict()
            else:
                continue

            names.append(ext)
            settings[ext] = config

            for k, v in config.items():
                if isinstance(v, str):
                    config[k] = v.replace("${BASE_PATH}", base_path)

        return names, settings

    def get_config_extensions(self):
        """Get the extensions to include from the settings."""
        ext_config = self.settings.get('markdown_extensions')
        return self.process_extensions(ext_config)

    def parser_specific_convert(self, markdown_text):
        """Parse Markdown with Python Markdown."""
        sublime.status_message('converting markdown with Python markdown...')
        extensions, extension_configs = self.get_config_extensions()
        md = Markdown(extensions=extensions, extension_configs=extension_configs)
        html_text = md.convert(markdown_text)
        # Retrieve the meta data returned from the "meta" extension
        self.settings.add_meta(md.Meta)
        return html_text


class MarkdownPreviewSelectCommand(sublime_plugin.TextCommand):
    """Allow selection of parser to use."""

    selected = 0

    def run(self, edit, target='browser'):
        """Show menu of parsers to select from."""
        settings = sublime.load_settings("MarkdownPreview.sublime-settings")
        md_map = settings.get('markdown_binary_map', {})
        parsers = [
            "markdown",
            "github"
        ]

        # Add external markdown binaries.
        for k in md_map.keys():
            parsers.append(k)

        self.target = target

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
                window.show_quick_panel(
                    self.user_parsers, self.run_command, 0, self.selected
                )

    def run_command(self, value):
        """Run the selected parser."""
        if value > -1:
            self.selected = value
            self.view.run_command(
                "markdown_preview",
                {
                    "parser": self.user_parsers[value],
                    "target": self.target
                }
            )


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    """Initiate a Markdown preview/conversion."""

    def run(self, edit, parser='markdown', target='browser'):
        """Run the conversion with the specified parser and output to the specified target."""
        self.settings = sublime.load_settings('MarkdownPreview.sublime-settings')

        # backup parser+target for later saves
        self.view.settings().set('parser', parser)
        self.view.settings().set('target', target)
        self.parser = parser
        self.target = target

        if parser == "github":
            compiler = GithubCompiler()
        elif parser == 'markdown':
            compiler = MarkdownCompiler()
        elif parser in self.settings.get("enabled_parsers", ("markdown", "github")):
            compiler = ExternalMarkdownCompiler(parser)
        else:
            # Fallback to Python Markdown
            compiler = MarkdownCompiler()

        html, body = compiler.run(self.view, preview=(target in ['disk', 'browser']))

        temp_target = 'browser' if target == 'disk' else target
        if temp_target in self.settings.get('include_head', ['build', 'browser', 'sublime', 'clipboard', 'save']):
            content = html
        else:
            content = body

        if target in ['disk', 'browser']:
            self.to_disk(content, self.target == 'browser')
        elif target == 'sublime':
            self.to_sublime(content)
        elif target == 'clipboard':
            self.to_clipboard(content)
        elif target == 'save':
            self.save(compiler, content)

    def to_disk(self, html, open_in_browser):
        """Save to disk and open in browser if desired."""
        # do not use LiveReload unless autoreload is enabled
        github_auth_provided = self.settings.get('github_oauth_token') is not None
        if self.settings.get('enable_autoreload', True) and (self.parser != 'github' or github_auth_provided):
            # check if LiveReload ST2 extension installed and add its script to the resulting HTML
            if 'LiveReload' in os.listdir(sublime.packages_path()):
                port = sublime.load_settings('LiveReload.sublime-settings').get('port', 35729)
                html += RELOAD_JS % port
        # update output html file
        tmp_fullpath = get_temp_preview_path(self.view)
        save_utf8(tmp_fullpath, html)
        # now opens in browser if needed
        if open_in_browser:
            self.__class__.open_in_browser(tmp_fullpath, self.settings.get('browser', 'default'))

    def to_sublime(self, html):
        """Output to Sublime view."""
        # create a new buffer and paste the output HTML
        new_view(self.view.window(), html, scratch=True)
        sublime.status_message('Markdown preview launched in sublime')

    def to_clipboard(self, html):
        """Save to clipboard."""

        # clipboard copy the full HTML
        sublime.set_clipboard(html)
        sublime.status_message('Markdown export copied to clipboard')

    def save(self, compiler, html):
        """Save output."""
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
        """Open in browser for the appropriate platform."""
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
    """Build command for Markdown."""

    def init_panel(self):
        """Initialize the output panel."""
        if not hasattr(self, 'output_view'):
            self.output_view = self.window.create_output_panel("markdown")

    def puts(self, message):
        """Output to panel."""
        message = message + '\n'
        self.output_view.run_command('append', {'characters': message, 'force': True, 'scroll_to_end': True})

    def run(self):
        """Run the build and convert the Markdown."""
        view = self.window.active_view()
        if not view:
            return
        start_time = time.time()

        self.init_panel()

        settings = sublime.load_settings('MarkdownPreview.sublime-settings')
        parser = settings.get('parser', 'markdown')
        if parser == 'default':
            print(
                'Markdown Preview: The use of "default" as a parser is now deprecated,'
                ' please specify a valid parser name.'
            )
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
        elif parser == 'markdown':
            compiler = MarkdownCompiler()
        elif parser in settings.get("enabled_parsers", ("markdown", "github")):
            compiler = ExternalMarkdownCompiler(parser)
        else:
            compiler = MarkdownCompiler()

        html, body = compiler.run(view, True, preview=False)

        if 'build' in self.settings.get('include_head', ['build', 'browser', 'sublime', 'clipboard', 'save']):
            content = html
        else:
            content = body

        htmlfile = compiler.settings.get('builtin').get('destination', None)

        if htmlfile is None:
            htmlfile = os.path.splitext(mdfile)[0] + '.html'
        self.puts("        ->" + htmlfile)
        save_utf8(htmlfile, content)

        elapsed = time.time() - start_time
        if body == _CANNOT_CONVERT:
            self.puts(_CANNOT_CONVERT)
        self.puts("[Finished in %.1fs]" % (elapsed))
        sublime.status_message("Build finished")
