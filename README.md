# Markdown Preview

Preview and build your markdown files quickly in your web browser.

You can use the builtin [Python Markdown][pymd] parser (offline) or use the [GitHub Markdown API][gfm-api] (online) for the conversion.

## Features

- Markdown preview using the [python-markdown][pymd] with syntax highlighting via Pygments and optional 3rd party extensions ([pymdown-extensions][pymdownx-docs] included by default).
- Markdown previews via the Github API.
- Ability use other external Markdown parsers.
- Build markdown file using Sublime Text build system.
- Browser preview auto reload on save if you have the [LiveReload plugin][live-reload] installed.
- Configurable CSS and JavaScript assets with overriding if needed.
- YAML support thanks to [@tommi][tommi].
- Clipboard selection and copy to clipboard thanks to [@hexatrope][hexatrope].
- MathJax support : `\(\frac{\pi}{2}\)` thanks to [@bps10][bps10].
- HTML template customization thanks to [@hozaka][hozaka].
- Embed images as base64.
- Strip out MultiMarkdown CriticMarkup.

## Documentation

Current Documentation: https://github.com/revolunet/sublimetext-markdown-preview/blob/st2/README.md

Future 2.0 Documentation: https://revolunet.github.io/sublimetext-markdown-preview/

## Support

- Any bugs about Markdown Preview please feel free to report [here][issue].
- And you are welcome to fork and submit pull requests.

## Attribution

Markdown Preview contains a stripped down version of font awesome that is included in the default non-GitHub CSS.  It contains only the icons we currently use.

https://fontawesome.com/license

## License

The code is available at [GitHub][home] under the [MIT license][license].

[bps10]: https://github.com/bps10
[gfm-api]: https://developer.github.com/v3/markdown/
[hexatrope]: https://github.com/hexatrope
[home]: https://github.com/revolunet/sublimetext-markdown-preview
[hozaka]: https://github.com/hozaka
[issue]: https://github.com/revolunet/sublimetext-markdown-preview/issues
[license]: http://revolunet.mit-license.org
[live-reload]: https://packagecontrol.io/packages/LiveReload
[pymd]: https://github.com/Python-Markdown/markdown
[pymdownx-docs]: http://facelessuser.github.io/pymdown-extensions/usage_notes/
[tommi]: https://github.com/tommi
