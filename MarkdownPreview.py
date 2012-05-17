import sublime, sublime_plugin
import desktop
import tempfile
import markdown
import os
import re


def getTempMarkdownPreviewPath(view):
    " return a permanent full path of the temp markdown preview file "
    tmp_filename = '%s.html' % view.id()
    tmp_fullpath = os.path.join(tempfile.gettempdir(), tmp_filename)
    return tmp_fullpath


class MarkdownPreviewListener(sublime_plugin.EventListener):
    """ update the output html when markdown file has already been converted once """

    def on_post_save(self, view):
        if view.file_name().endswith(('.md', '.markdown', '.mdown')):
            temp_file = getTempMarkdownPreviewPath(view)
            if os.path.isfile(temp_file):
                # reexec markdown conversion
                view.run_command('markdown_preview', {'target': 'browser'})


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    """ preview file contents with python-markdown and your web browser"""

    def getCSS(self):
        css_filename = 'markdown.css'
        # path via package manager
        css_path = os.path.join(sublime.packages_path(), 'Markdown Preview', css_filename)
        if not os.path.isfile(css_path):
            # path via git repo
            css_path = os.path.join(sublime.packages_path(), 'sublimetext-markdown-preview', css_filename)
            if not os.path.isfile(css_path):
                raise Exception("markdown.css file not found!")

        return open(css_path, 'r').read().decode('utf-8')

    def postprocessor(self, html):
        # fix relative images paths
        def img_fix(match):
            img, src = match.groups()
            filename = self.view.file_name()
            if filename:
                if not src.startswith(('file://', 'http://', '/')):
                    abs_path = u'file://%s/%s' % (os.path.dirname(filename), src)
                    img = img.replace(src, abs_path)
            return img
        RE_IMGS = re.compile("""(?P<img><img[^>]+src=["'](?P<src>[^"']+)[^>]*>)""")
        html = RE_IMGS.sub(img_fix, html)
        return html

    def run(self, edit, target='browser'):
        region = sublime.Region(0, self.view.size())
        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'utf-8'
        elif encoding == 'Western (Windows 1252)':
            encoding = 'windows-1252'
        contents = self.view.substr(region)

        # convert the markdown
        markdown_html = markdown.markdown(contents)

        # postprocess the html
        markdown_html = self.postprocessor(markdown_html)

        # build the html
        html_contents = u'<!DOCTYPE html>'
        html_contents += '<html><head><meta charset="%s">' % encoding
        styles = self.getCSS()
        html_contents += '<style>%s</style>' % styles
        html_contents += '</head><body>'
        html_contents += markdown_html
        html_contents += '</body>'

        if target in ['disk', 'browser']:
            # update output html file
            tmp_fullpath = getTempMarkdownPreviewPath(self.view)
            tmp_html = open(tmp_fullpath, 'w')
            tmp_html.write(html_contents.encode(encoding))
            tmp_html.close()
            # todo : livereload ?
            if target == 'browser':
                desktop.open(tmp_fullpath)
        elif target == 'sublime':
            new_view = self.view.window().new_file()
            new_edit = new_view.begin_edit()
            new_view.insert(new_edit, 0, html_contents)
            new_view.end_edit(new_edit)
        print 'markdown converted'
