Sublime Text 2/3 Markdown Previews
=================================

Preview and build your markdown files quickly in your web browser from sublime text 2/3. 

You can use builtin [python-markdown][10] parser or use the [github markdown API][5] for the conversion.

**NOTE:** If you choose the GitHub API for conversion (set parser: github in your settings), your code will be sent through https to github for live conversion. You'll have [Github flavored markdown][6], syntax highlighting and EMOJI support for free :heart: :octocat: :gift:. If you make more than 60 calls a day, be sure to set your GitHub API key in the settings :). You can also get most of this in the default Markdown parser with by enabling certain extensions; see "[Parsing Github Flavored Markdown](#parsing-github-flavored-markdown-)"" below for more information.

**LINUX users:** If you want to use GitHub API for conversion, you'll need to have a custom Python install that includes python-ssl as its not built in the Sublime Text 2 Linux package. see [@dusteye][dusteye] [comment][8]. If you use a custom window manager, also be sure to set a `BROWSER` environment variable. see [@PPvG][PPvg] comments][9]

## Features

 - Markdown preview using the [python-markdown][10] or the Github API. Just select the build commands.
 - Syntax highlighting via Pygments. See "[Configuring Pygments](#configuring-pygments)" for more info.
 - Build markdown file using Sublime Text build system. The build parser are configured via the `"parser"` config.
 - Browser preview auto reload on save if you have the [ST2 LiveReload plugin][7] installed.
 - Builtin parser : supports `abbr`, `attr_list`, `def_list`, `fenced_code`, `footnotes`, `tables`, `smart_strong`, `smarty`,  `wikilinks`, `meta`, `sane_lists`, `codehilite`, `nl2br`, and `toc` markdown extensions.
 - CSS search path for local and build-in CSS files (always enabled) and/or CSS overriding if you need
 - YAML support thanks to [@tommi][tommi]
 - Clipboard selection and copy to clipboard thanks to [@hexatrope][hexatrope]
 - MathJax support : \\\\(\frac{\pi}{2}\\\\) thanks to [@bps10][bps10].
 - HTML template customisation thanks to [@hozaka][hozaka]
 - Embed images as base64 (see [settings][settings] file for more info)
 - Strip out multimarkdown critic marks from either Githubs or Python Markdown input source (see [settings][settings] file for more info)
 - Supports 3rd party Python Markdown extensions.  [PyMdown Extensions][1] are included via Package Control dependencies, but others can be included as well. Usage of some extensions may require additional JavaScript or CSS. See the desired extension's documentation to learn how to configure them.

    When configuring PyMdown Extensions, please read its [Usage Notes][13] to learn about extension conflicts and which ones cannot be included together.

## Installation

### Using [Package Control][3] (*Recommended*)

For all Sublime Text 2/3 users we recommend install via [Package Control][3].

1. [Install][11] Package Control if you haven't yet.
2. Use <kbd>cmd</kbd>+<kbd>shift</kbd>+<kbd>P</kbd> then `Package Control: Install Package`
3. Look for `Markdown Preview` and install it.

## Usage

When referring to settings, we are referring to the settings found at `Preferences`->`Package Settings`->`Markdown Preview`.

 - `Settings - User` is where you change your settings for Markdown Preview.
 - `Settings - Default` is a good reference with detailed descriptions for each setting.

### To preview

 - optionally select some of your markdown for conversion
 - use <kbd>cmd</kbd>+<kbd>shift</kbd>+<kbd>P</kbd> then `Markdown Preview` to show the follow commands (you will be prompted to select which parser you prefer):
    - Markdown Preview: Preview in Browser
    - Markdown Preview: Export HTML in Sublime Text
    - Markdown Preview: Copy to Clipboard
    - Markdown Preview: Open Markdown Cheat sheet
        ![Usage Demo](sublimetext-markdown-preview.gif)
 - or bind some key in your user key binding, using a line like this one:
   `{ "keys": ["alt+m"], "command": "markdown_preview", "args": {"target": "browser", "parser":"markdown"} },` for a specific parser and target or `{ "keys": ["alt+m"], "command": "markdown_preview_select", "args": {"target": "browser"} },` to bring up the quick panel to select enabled parsers for a given target.

If you want to control which browser the preview is opened in, you can edit the `browser` option in the settings file:

```js
    /*
        Sets the default opener for HTML files

        default - Use the system default HTML viewer
        other - Set a full path to any executable. ex: /Applications/Google Chrome Canary.app or /Applications/Firefox.app
    */
    "browser": "default",
```

### Custom Templates

By default, Markdown Preview uses a simple template, but you can use your own custom template with the setting `html_template`. If you wish to not include the default stylesheets, and instead only use what is specified in your template, or what you've explicitly included in the `css` setting, then set `skip_default_stylesheet` to `true`.

```js
    /*
        Specify a HTML template file to render your markdown within.

        Available place holders in HTML template:
        {{ HEAD }} - would be replaced by generated stylesheets, javascripts enabled above
        {{ BODY }} - would be replaced by HTML converted from markdown

        By setting "skip_default_stylesheet" to true you can use the styles only in your HTML
        template. In most cases you should turn this setting on to have a full-featured design.

        Refer to 'customized-template-sample.html' as a show case.
    */
    "html_template": "/ABS_PATH_TO_A_HTML_FILE",
    "skip_default_stylesheet": true,
```

### LiveReload

To get live updates while editing a file after preview, you need to do the following:

 1. Enable the `enable_autoreload` setting in `MarkdownPreview.sublime-settings`.
    ```js
         /*
            Enable auto-reloaded on save. Will not work if GitHub parser is used without oauth key specified.
        */
        "enable_autoreload": true,
    ```
 2. Install [LiveReload][7] package from Package Control.
 3. Restart.
 4. Open the command palette and select the command `LiveReload: Enable/disable plug-ins`.
 5. Select `Simple Reload with delay (400ms)`.  It is possible you can get away with `Simple Reload`, but some experience an issue where they are one rev behind when using `Simple Reload`.
 6. Edit document and enjoy live reload.

You don't need to enable `Simple Reload` on every file as it is done globally; it can be turned on or off as needed.  From now on, files should auto-reload when you open them in the browser unless you disable `Simple Reload`.

### Preview Path Conversion

In the generated previews, paths are converted so that images and other links work properly. By default, paths are converted to absolute paths, but you can use relative if desired as well.  Image paths can also be changed to inject embedded base 64 images (only for local images). Path handling is controlled by the following two settings:

```js
    /*
        Sets how image paths are handled.
        Setting is a string value: (absolute | relative | base64 | none)
            absolute: converts relative local paths to absolute
            relative: converts relative local paths to a path relative to the
                        HTML output
            base64: coverts the local file to base64 and embeds it in the HTML
            none: does nothing
    */
    "image_path_conversion": "absolute",

    /*
        Sets how file paths are handled.
        Setting is a string value: (absolute | relative | none)
            absolute: converts relative local paths to absolute
            relative: converts relative local paths to a path relative to the
                        HTML output
            none: does nothing
    */
    "file_path_conversions": "absolute",
```

### Preview Temp Location

By default, previews are generated in the OSs default temp location, but you can specify your own custom temp location via the `path_tempfile` option:

```js
    /*
        Sets a custom temporary folder for MarkdownPreview-generated HTML files. Useful if you're
        using LiveReload and don't want to use the OS default. The directory will be created if it
        doesn't exist. Relative paths are supported, and are checked against `os.path.isabs`, see
        doc: http://docs.python.org/3/library/os.path.html#os.path.isabs

        Examples: /tmp/custom_folder   (Linux/OSX - absolute path)
                    C:/TEMP/MYNOTES
                    C:\\TEMP\\MYNOTES    (Windows - absolute path, forward slash or escaped back slash)
                    build                (All OS - relative path, current dir)
                    ../build             (Linux/OSX - relative path, in parent dir)
                    ..\\build            (Windows - relative path, in parent dir)
    */
    "path_tempfile": "/tmp/my_notes",
```

### Enabling Other External Markdown Parsers

External parser commands and arguments should first be mapped to a name.  Each binary value must be an array with the path to the binary being first, followed by flags and options as individual indexes in the array.

```js
    "markdown_binary_map": {
        "multimarkdown": ["/usr/local/bin/multimarkdown", "--some-option", "some-value"]
    },
```

Then the name can be placed in `enabled_parsers` to enable use of the new parser.

```js
    "enabled_parsers": ["markdown", "github", "multimarkdown"],
```

### Configuring Python Markdown Extensions

Python Markdown comes with a number of extensions and can also use a number of 3rd party extensions.  To configure Markdown Preview with extensions, use the `markdown_extensions` setting.

`markdown_extensions` is a setting that contains an array of extensions in the format of their import path. For instance, the Toc (Table of Contents) extension is found in the Markdown Package at `markdown.extensions.toc`.  This is according to Python Markdown [documentation][2].  All extensions must be specified this way.

```js
    "markdown_extensions": [
        "markdown.extensions.toc"
    ]
```

To configure an extension, make the entry a dictionary.  In this example, we want to turn on Toc's permalink feature:

```js
    "markdown_extensions": [
        {
            "markdown.extensions.toc": {
                "permalink": true
            }
        }
    ]
```

You can configure extension options with strings, booleans, integers, floats, etc.  But sometimes, an extension can take a function.  Functions are not part of the JSON spec. Luckily, support has been added with the following syntax:

To specify a function, create an object whose key is named `!!python/name`, and whose value is the import path of the function.  This syntax was picked to be similar to PyYaml's syntax which is used for the Markdown frontmatter.

So let's pretend we didn't like Toc's default slugify `markdown.extensions.headerid.slugify`, and instead wanted to use PyMdown Extensions' slugify `pymdownx.slugs.uslugify`.  We could specify the new slugify function with the following syntax:

```js
    "markdown_extensions": [
        {
            "markdown.extensions.toc": {
                "slugify": {"!!python/name", "pymdownx.slugs.uslugify"}
            }
        }
    ]
```

Compare to the PyYaml format:

```yml
markdown_extensions:
  - markdown.extensions.toc:
      slugify: !!python/name:pymdownx.slugs.uslugify
```

### To build

Just use <kbd>ctrl</kbd>+<kbd>B</kbd> (Windows/Linux) or <kbd>cmd</kbd>+<kbd>B</kbd> (Mac) to build current file.

You can configure the build action by using the `build_action` setting.

```js
    /*
        By default, Markdown Preview builds the HTML in the source directory.
        It expects the file to exist on disk.  It pops up the build output panel etc.

        If you wish to override this behavior, you can change "build_action"

        build - The default build behavior.
        browser - Preview the file in your browser.
        clipboard - Copy the HTML output to the clipboard.
        sublime - Export the HTML to a Sublime tab.
        save - Run the normal save command that outputs to the source directory.
            It will also prompt for "save as" if the file does not exit on disk.

        All the build options use the default parser defined above in "parser"
    */
    "build_action": "build",
```

And the parser that is used when building is set in the `parser` setting:

```js
    /*
        Sets the parser used for building markdown to HTML.

        NOTE: The parser setting is not for the preview commands now.
        The previews have separate commands for each parser markdown.

        Warning for github API: if you have a ST2 linux build, Python is not built with SSL so it may not work

        default - The current default parser is python-markdown parser.
        markdown - Use the built-in python-markdown parser
        github - Use the github API to convert markdown, so you can use GitHub flavored Markdown, see https://help.github.com/articles/github-flavored-markdown/
    */
    "parser": "markdown",
```

When building, a panel will be opened showing build information. This can be disabled by setting `show_panel_on_build` to `false`:

```js
    /* do we show the panel when building with CMD+B */
    "show_panel_on_build": true,
```

### Configuring Pygments
If you add the codehilite extension manually in the enabled extensions, you can override some of the default settings.

* Turn language guessing *on* or *off* (*on* will highlight fenced blocks even if you don't specify a language):

    ```js
    "markdown_extensions": [
        "codehilite": {
            "guess_lang": false
        }
    ]
    ```

* Show line numbers:

    ```js
    "markdown_extensions": [
        "codehilite": {
            "linenums": false
        }
    ]
    ```

* Change the higlight theme:

    ```js
    "markdown_extensions": [
        "codehilite": {
            "pygments_style": "emacs"
        }
    ]
    ```

* Inline the CSS:

    ```js
    "markdown_extensions": [
        "codehilite": {
            "noclasses": true
        }
    ]
    ```

* Use multiple:
    ```js
    "markdown_extensions": [
        "codehilite": {
            "linenums": true,
            "pygments_style": "emacs"
        }
    ]
    ```

The `codehiite` extension's `pygments_style` option is only useful if you are using `noclasses` which writes the styles directly to the HTML tags via the `style` attribute. Normally, we just inject CSS generated by Pygments which is the default behavior. Whether the CSS injection occurs, the Pygments' style that is used, and the CSS class that is used for code blocks can all be controlled with the following options:

```js
    /*
        If Pygments is being used, you may want to inject one of the Pygment styles provided into the HTML.
        If so, enable this.
    */
    "pygments_inject_css": true,

    /*
        Name of the Pygments style to inject. Available styles are the styles provided by pygments
        plus "github" and "github2014".
    */
    "pygments_style": "github",

    /*
        This is the class to prepend to the pygments CSS styles. Make sure it matches whatever class(es)
        you've specified in the extension that controls Pygments highlighting.  CodeHilite's default is
        "codehilite".
    */
    "pygments_css_class": "codehilite",
```

See [codehilte page](https://python-markdown.github.io/extensions/code_hilite) for more info.

### Meta Data Support

When the `meta` extension is enabled (https://python-markdown.github.io/extensions/meta_data), the results will be written to the HTML head in the form `<meta name="key" content="value1,value2">`.  `title` is the one exception, and its content will be written to the title tag in the HTML head.

### YAML Frontmatter Support

YAML frontmatter can be stripped out and read when `strip_yaml_front_matter` is set to  `true` in the settings file.  In general the, the frontmatter is handled the same as [meta data](#meta-data-support), but if both exist in a file, the YAML keys will override the `meta` extension keys.  There are a few special key names that won't be handled as HTML meta data.

```js
    /*
        Strips the YAML front matter header and converts title to a heading
    */
    "strip_yaml_front_matter": false,
```

#### Special YAML Key Names

YAML frontmatter has a few special key names that are used that will not be handled as meta data:

 - **basepath**: An absolute path to configure the relative paths for images etc. (for when the markdown is supposed to reference images in a different location.)
 - **references**: Can take a file path or an array of file paths for separate markdown files containing references, footnotes, etc.  Can be an absolute path or relative path.  Relative paths first use the source file's directory, and if the file cannot be found, it will use the `basepath` setting.
 - **destination**: This is an absolute file path or relative file path for when the markdown is saved to html via the build command or the `Save to HTML` command.  Relative paths first use the source file's directory, and if the file cannot be found, it will use the `basepath` setting.
 - **settings**: This is a dictionary where you can override settings that are in the settings file.

```yaml
---
    # Builtin values
    references:
        - references.md
        - abbreviations.md
        - footnotes.md

    destination: destination.html

    # Meta Data
    title: Test Page
    author:
        - John Doe
        - Jane Doe

    # Settings overrides
    settings:
        enable_uml: true
        markdown_extensions:
          - markdown.extensions.footnotes
          - markdown.extensions.attr_list
          - markdown.extensions.def_list
          - markdown.extensions.tables
          - markdown.extensions.abbr
          - markdown.extensions.toc
          - markdown.extensions.smarty
          - markdown.extensions.meta
          - markdown.extensions.wikilinks
          - markdown.extensions.admonition
          - markdown.extensions.codehilite:
              guess_lang: false
              pygments_style: github
          - pymdownx.extrarawhtml
          - pymdownx.progressbar
          - pymdownx.github
          - pymdownx.caret:
              superscript: false
---
```

### Parsing Github Flavored Markdown

Github Flavored Mardown (GFM) is a very popular markdown.  Markdown Preview can actually handle them in a couple of ways: online and offline.

#### Online

Parsing GFM using the online method requires using the Github API as the parser.  It may also require setting `github_mode` to `gfm` to get things like tasklists to render properly.

```js
    /*
        Default mode for the github Markdown parser : markdown (documents) or gfm (comments)
        see http://developer.github.com/v3/markdown/#render-an-arbitrary-markdown-document
    */
    "github_mode": "markdown",
```

Using the GitHub API without an oauth key is limited to so many calls.  After the limit is reached, the GitHub API will deny further calls until after a set limit of time. To avoid this issue, you can set your API key in the settings as follows:

```js
    /*
        Uses an OAuth token when parsing markdown with GitHub API. To create one for Markdown Preview, see https://help.github.com/articles/creating-an-oauth-token-for-command-line-use.
        Warn: this secret *must not be shared* with anyone and at least you should create it with minimal scopes for security reasons.
    */
    "github_oauth_token": "secret",
```

The GitHub API only inserts IDs for headers when `github_mode` is `markdown`, but it doesn't quite generate the way that GitHub does in your project's readmes on the site. This makes it so the GitHub CSS doesn't create the clickable anchors. So when `github_mode` is `markdown`, you can have Markdown Preview insert the ids properly so the CSS works with the following option:

```js
    /*
        Enables a post process to inject header ids to ensure hrefs to headers work
    */
    "github_inject_header_ids": true,
```

#### Offline

By default almost all extensions are enabled to help with a GitHub-ish feel, but there are some tweaks needed to get the full experience.

GFM does not auto guess language in fenced blocks, but Markdown Preview does this by default.  You can fix this in one of two ways:

1. Disable auto language guessing in the settings file `"guess_language": false,`
2. Or if you are manually defining extensions:

    ```js
    "markdown_extensions": [
        "codehilite": {
            "guess_lang": false,
            "pygments_style": "github"
        }
    ]
    ```

As mentioned earlier, a number of extensions are included by default. You can remove ones that are not part of GFM.

### Including CSS

By default Markdown Preview includes a default CSS via the `css` setting.  It uses the special keyword `default` to represent the default CSS.

```js
    "css": ["default"],
```

You can include whatever CSS you want, and even remove the `default` if you like.  It can take URLs or file paths.

#### Override CSS by File Type

You can also override the default CSS with special file specific CSS. This CSS does not replace the default, but will append CSS for a supported file type after the conventional CSS.

So assuming the following configuration:

```js
    "css": ["default"],
    // File must be of one type below
    "markdown_filetypes": [".md", ".markdown", ".mdown"],
```

We could enable the following:

```js
    "allow_css_overrides": true,
```

Then if we have a file `filename.md` and a CSS in the same directory `filename.css`, that CSS will be applied to that file.

#### Embedding CSS

In previews, the CSS is embedded by default.  This is controlled by the setting `embed_css_for_sublime_output`.

```js
    /* do we include the CSS when outputting HTML into a new sublime view ? */
    "embed_css_for_sublime_output": true
```

### Including JavaScript

JavaScript files can be included via the `js` setting.  It is a list and can take file paths or URLs.

```js
    "js": ["default"],
```

### CriticMarkup

Python Markdown can strip/apply out [CriticMarkup][14] syntax if desired.  Simply enable the following option:

```js
    /*
        Sets how multimarkdown critic marks are handled.
        Setting is a string value: (accept | reject | none)
            accept: Accepts the proposed inserts and deletions (comments etc. are discarded)
            reject: Rejects the proposed inserts and deletions (comments etc. are discarded)
            none: does nothing

        Critic marks only affects "github" and "markdown" (Python Markdown).
    */
    "strip_critic_marks": "none",
```

### MathJax Support

To render Tex style math in Markdown, you can use the default MathJax setup that is available via the setting `enable_mathjax` setting. This will include HTML that will include MathJax via the MathJax CDN.  It is advised to use a Markdown extension (if using  Python Markdown; the `markdown` parser) to preserve the Tex style format.  You can check out [Arithmatex][15] which can do the preservation.

```js
    /*
        Enable or not mathjax support.
    */
    "enable_mathjax": false,
```

### UML Support

If you are using the extension [SuperFences extension](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/), it has an option to create special, custom fences. By default, it specifies `flow` and `sequence` languages to generate special code blocks that JavaScript can be applied to later to create UML diagrams: see https://facelessuser.github.io/pymdown-extensions/extensions/superfences/#custom-fences. By enabling the Markdown Preview setting `enable_uml`, the necessary CSS and JavaScript code will be included to transform `sequence` and `flow` blocks using https://bramp.github.io/js-sequence-diagrams/ and https://flowchart.js.org/ respectively.

```js
    /*
        Enable uml support scripts: flowchart.js and sequence-diagram.js.
    */
    "enable_uml": false,
```

### Simple HTML Output

Some people may desire a stripped down output on occasions that does not include HTML headers, inline styles, and IDs. Markdown Preview has a mode that will strip out these things and omit using a template.  This mode can be enabled via the the `html_simple` option:

```js
    /*
        Sets HTML output to a simple form:
            - No head
            - No body tags
            - ids, classes, and style are stripped out
            - Just bare minimum HTML tags and attributes
            - extension modifications included
    */
    "html_simple": false,
```

## Support

- Any bugs about Markdown Preview please feel free to report [here][issue].
- And you are welcome to fork and submit pull requests.

## License

The code is available at github [project][home] under [MIT license][4].

 [home]: https://github.com/revolunet/sublimetext-markdown-preview
 [1]: http://facelessuser.github.io/pymdown-extensions/
 [2]: https://pythonhosted.org/Markdown/extensions/toc.html#usage
 [3]: https://packagecontrol.io/
 [4]: http://revolunet.mit-license.org
 [5]: https://developer.github.com/v3/markdown/
 [6]: https://help.github.com/articles/github-flavored-markdown/
 [7]: https://packagecontrol.io/packages/LiveReload
 [8]: https://github.com/revolunet/sublimetext-markdown-preview/issues/27#issuecomment-11772098
 [9]: https://github.com/revolunet/sublimetext-markdown-preview/issues/78#issuecomment-15644727
 [10]: https://github.com/Python-Markdown/markdown
 [11]: https://packagecontrol.io/installation
 [12]: https://github.com/revolunet/sublimetext-markdown-preview/archive/master.zip
 [13]: http://facelessuser.github.io/pymdown-extensions/usage_notes/
 [14]: http://criticmarkup.com/
 [15]: https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/
 [issue]: https://github.com/revolunet/sublimetext-markdown-preview/issues
 [settings]: https://github.com/revolunet/sublimetext-markdown-preview/blob/master/MarkdownPreview.sublime-settings
 [hozaka]: https://github.com/hozaka
 [tommi]: https://github.com/tommi
 [bps10]: https://github.com/bps10
 [dusteye]: https://github.com/dusteye
 [PPvG]: https://github.com/PPvG
 [hexatrope]: https://github.com/hexatrope
