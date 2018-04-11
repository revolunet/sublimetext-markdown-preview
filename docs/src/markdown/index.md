# Overview

Preview and build your markdown files quickly in your web browser.

You can use the builtin [Python Markdown][pymd] parser (offline) or use the [GitHub Markdown API][gfm-api] (online) for the conversion.

!!! note
    If you choose the GitHub API for conversion (set `parser` to `github` in your settings), your code will be sent through HTTPS to GitHub for live conversion. You'll have [Github Flavored Markdown][gfm-help], syntax highlighting and EMOJI support for free :heart: :gift:. If you make more than 60 calls a day, be sure to set your GitHub API key in the settings :smile:.

## Features

- Markdown preview using the [python-markdown][pymd] with syntax highlighting via Pygments and optional 3rd party extensions ([pymdown-extensions][pymdownx-docs] included by default).
- Markdown previews via the Github API.
- Ability use other external Markdown parsers.
- Build markdown file using Sublime Text build system.
- Browser preview auto reload on save if you have the [LiveReload plugin][live-reload] installed.
- Configurable CSS and JavaScript assets with overriding if needed.
- YAML support thanks to [@tommi][tommi].
- Clipboard selection and copy to clipboard thanks to [@hexatrope][hexatrope].
- MathJax support : $\frac{\pi}{2}$ thanks to [@bps10][bps10].
- HTML template customization thanks to [@hozaka][hozaka].
- Embed images as base64.
- Strip out MultiMarkdown CriticMarkup.

## Support

- Any bugs about Markdown Preview please feel free to report [here][issue].
- And you are welcome to fork and submit pull requests.

## Attribution

Markdown Preview contains a stripped down version of font awesome that is included in the default non-GitHub CSS.  It contains only the icons we currently use.

https://fontawesome.com/license

## License

The code is available at [GitHub][home] under the [MIT license][license].

--8<-- "refs.md"
--8<-- "mathjax.md"
