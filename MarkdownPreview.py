import sublime, sublime_plugin
import webbrowser
import tempfile
import markdown
import os


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    """ preview file contents with python-markdown and your web browser"""
    def run(self, edit):
        region = sublime.Region(0, self.view.size())
        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        contents = self.view.substr(region)
        tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        html = markdown.markdown(contents)
        tmp_html.write('<meta charset="%s">' % self.view.encoding())
        styles = open(os.path.join(sublime.packages_path(), 'Markdown Preview', 'markdown.css'), 'r').read()
        tmp_html.write('<style>%s</style>' % styles)
        tmp_html.write(html.encode(encoding))
        tmp_html.close()
        webbrowser.open_new_tab(tmp_html.name)
