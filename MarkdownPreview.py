import sublime, sublime_plugin
import desktop
import tempfile
import markdown
import os


def getTempMarkdownPreviewPath(view):
    # return a permanent full path of the temp markdown preview file
    tmp_filename = '%s.html' % view.id()
    tmp_fullpath = os.path.join(tempfile.gettempdir(), tmp_filename)
    return tmp_fullpath


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

        # build the html
        html_contents = u'<html><head><meta charset="%s">' % encoding
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
