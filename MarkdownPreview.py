import sublime, sublime_plugin
import webbrowser
import tempfile
import markdown


class MarkdownPreviewCommand(sublime_plugin.TextCommand):
    """ preview file contents with python-markdown and your web browser"""
    def run(self, edit):
        region = sublime.Region(0, self.view.size())
        contents = self.view.substr(region)
        tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        html = markdown.markdown(contents)
        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        tmp_html.write('<meta charset="%s">' % self.view.encoding())
        tmp_html.write('<link href="https://raw.github.com/revolunet/Markdown-CSS/master/markdown.css" rel="stylesheet"></link>')
        tmp_html.write(html.encode(encoding))
        tmp_html.close()
        webbrowser.open_new_tab(tmp_html.name)
