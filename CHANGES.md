Changes in Markdown Preview
===========================
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
