Changes in Markdown Preview
===========================
## 2.0.0

Please read documentation as there have been big changes in this version which may require updates to your personal settings.

* Do not vendor Python Markdown. Python Markdown will be acquired via the current markdown dependency.

* Python Markdown configuration changes:

    * No more defining settings as `extension(option1=a,option2=b)`. Options will be defined as a dictionary.
    * You will have to define the full extension name: `markdown.extensions.codehilite`. This will allow you to import any extension you want outside of Markdown Preview.
    * New line to `<br>` conversion has been dropped from GitHub emulation as GitHub no longer does this. Ref issue #374.

* Originally a couple pymdownx-extension extensions were ported over to this plugin to give a GitHub-ish feel to Markdown, these are no longer be included directly, but are included as a dependency. This will provide the latest versions, and also provide new extensions previously not included. Ref issue #378.

* Drop ST2 so we no longer have to provide specially crafted Python Markdown versions when we try to upgrade.

* Improve yaml front matter parsing: see issue #392.

* Better UML JavaScript injection.

* Link contributors in readme.

* Remove "magic" Pygments configuration. User will now explicitly configure Pygments CSS injection separately.

* Require explicit parser name moving forward instead of default, but provide a deprecation path for the short term.

* Fix GitHub header ID generation. GitHub only lowercases ASCII chars.

* Ensure default parser is Python Markdown, and enable auto-reload by default.

* Hopefully better documentation.

* Make flake8 compatible. I'd put it up on travis for continuous integration, but I don't have that kind of control.

* Fix outdated links.

## 1.4.3

* Fix issue where Chrome prevents live reload.

## 1.4.0

* `css` setting can now be an array and contain multiple CSS files (see settings file for more info).
* Updated Github style to latest.

## 1.3.0

* Now supports any markdown parser through a generalized method.  Now you can map a binary to parser name via `markdown_binary_map`.  Then use the parser name in `enabled_parsers` to use it.
* Multimarkdown specific settings have been removed.  Multimarkdown should now be configured via `markdown_binary_map` and `enabled_parsers`.
* Upgraded to Python Markdown 2.6.4.
* Removed internal PyYaml and Pygments.  Markdown Preview now uses Package Control dependencies to obtain PyYaml and Pygments.
* Update kbd CSS for Github.

## 1.0.3

* The `messages.json` should OK for this time.

## 1.0.2

* Fixes messages.json and changelog versions.

## 1.0.1

* Removed markdown2 parser for its not well maintained and buggy.
* Make Python Markdown parser as default.
* Split the preview commands for *Python Markdown* parser and *Github Flavored Markdown* parser.
* Add markdown file build support, build parser are config via the origin `"parser"` settings.
* Add this changlog file for both developpers and users.
* Add messages.json which make display of `README.md` and `CHANGES.md`
* Try use `Markdown Extended.tmLanguage` for cheat sheet if you installed `Markdown Extended`.

## 1.0.0

* Support for ST3.
* Added Python Markdown parser.
* CSS search first in markdown file directory and the the build-in.
