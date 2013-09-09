Sublime Text 2/3 Markdown Preview
=================================

Preview and build your markdown files quickly in your web browser from sublime text 2/3. 

You can use builtin [python-markdown][10] parser or use the [github markdown API][5] for the conversion.

**NOTE:** If you choose the GitHub API for conversion (set parser: github in your settings), your code will be sent through https to github for live conversion. You'll have [Github flavored markdown][6], syntax highlighting and EMOJI support for free :heart: :octocat: :gift:. If you make more than 60 calls a day, be sure to set your GitHub API key in the settings :)

**LINUX users:** If you want to use GitHub API for conversion, you'll need to have a custom Python install that includes python-ssl as its not built in the Sublime Text 2 Linux package. see [@dusteye comment][8]. If you use a custom window manager, also be sure to set a `BROWSER` environment variable. see [@PPvG comments][9]

## Features :

 - Markdown preview using the [Python-markdown][10] or the Github API just choose select the build commands.
 - Build markdown file using Sublime Text build system. The build parser are config via the `"parser"` config.
 - Browser preview auto reload on save if you have the [ST2 LiveReload plugin][7] installed.
 - Builtin parser : supports `abbr`, `attr_list`, `def_list`, `fenced_code`, `footnotes`, `tables`, `smart_strong` and `toc` markdown extensions.
 - CSS search path for local and build-in CSS files (always enabled) and/or CSS overriding if you need
 - YAML support thanks to @tommi
 - Clipboard selection and copy to clipboard thanks to @hexatrope
 - MathJax support : \\(\frac{\pi}{2}\\) thanks to @bps10

## Installation :

### Using [Package Control][3] (*Recommended*)

For all Sublime Text 2/3 users we recommend install via [Package Control][3].

1. [Install][11] Package Control if you haven't yet.
2. Use `cmd+shift+P` then `Package Control: Install Package`
3. Look for `Markdown Preview` and install it.

### Manual Install

1. Click the `Preferences > Browse Packages…` menu
2. Browse up a folder and then into the `Installed Packages/` folder
3. Download [zip package][12] rename it to `Markdown Preview.sublime-package` and copy it into the `Installed Packages/` directory
4. Restart Sublime Text

## Usage :

### To preview :

 - optionally select some of your markdown for conversion
 - use `cmd+shift+P` then `Markdown Preview` to show the follow commands:
	- Markdown Preview: Python Markdown: Preview in Browser
	- Markdown Preview: Python Markdown: Export HTML in Sublime Text
	- Markdown Preview: Python Markdown: Copy to Clipboard
	- Markdown Preview: Github Flavored Markdown: Preview in Browser
	- Markdown Preview: Github Flavored Markdown: Export HTML in Sublime Text
	- Markdown Preview: Github Flavored Markdown: Copy to Clipboard
	- Markdown Preview: Open Markdown Cheat sheet
 - or bind some key in your user key binding, using a line like this one:
   `{ "keys": ["alt+m"], "command": "markdown_preview", "args": {"target": "browser", "parser":"markdown"} },`
 - once converted a first time, the output HTML will be updated on each file save (with LiveReload plugin)

### To build :

 - Just use `Ctrl+B` (Windows/Linux) or `cmd+B` (Mac) to build current file.

### To config :

Using Sublime Text menu: `Preferences`->`Package Settings`->`Markdown Preview`

- `Settings - User` is where you change your settings for Markdown Preview.
- `Settings - Default` is a good reference with detailed descriptions for each setting.


## Support :

- Any bugs about Markdown Preview please fell free to report [here][issue].
- And you are welcome to fork and submit pullrequests.


## License :

The code is available at github [project][home] under [MIT licence][4].

 [0]: https://github.com/trentm/python-markdown2
 [home]: https://github.com/revolunet/sublimetext-markdown-preview
 [3]: https://sublime.wbond.net/
 [4]: http://revolunet.mit-license.org
 [5]: http://developer.github.com/v3/markdown
 [6]: http://github.github.com/github-flavored-markdown/
 [7]: https://github.com/dz0ny/LiveReload-sublimetext2
 [8]: https://github.com/revolunet/sublimetext-markdown-preview/issues/27#issuecomment-11772098
 [9]: https://github.com/revolunet/sublimetext-markdown-preview/issues/78#issuecomment-15644727
 [10]: https://github.com/waylan/Python-Markdown
 [11]: https://sublime.wbond.net/installation
 [12]: https://github.com/revolunet/sublimetext-markdown-preview/archive/master.zip
 [issue]: https://github.com/revolunet/sublimetext-markdown-preview/issues
