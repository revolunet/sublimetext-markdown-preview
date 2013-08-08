import sublime, os, pkgutil
import os.path
import re

'''
INSTALLED_DIRECTORY - The install directory name for this plugin.

For ST3
    As descriped in http://www.sublimetext.com/docs/3/packages.html this script locations is one of
    Zipped: 
        "<executable_path>/Packages/Markdown Preview.sublime-package/Markdown Preview.MarkdownPreview"
        "<data_path>/Installed Packages/Markdown Preview.sublime-package/Markdown Preview.MarkdownPreview"
    Not Zipped:
        "<data_path>/Packages/Markdown Preview/MarkdownPreview.py"

    All passable path for ST3 are abspath (tested on windows)

For ST2
    The __file__ will be '.\MarkdownPreview.pyc' that means when this script is loaded,
    Sublime Text entered the directoy of this script. So we make use of os.path.abspath()
'''
try:
    INSTALLED_DIRECTORY = re.search("[ \\\\/]Packages[\\\\/]([^\\\\/\.]+)", os.path.abspath(__file__)).group(1)
except:
    print('Warning failed to detect the install directory, defaulting to: "Markdown Preview"')
    INSTALLED_DIRECTORY = "Markdown Preview"




"""
Preload all python-markdown extensions (ST2 only)
"""

# By default sublime 2 only imports python packages from the top level of the plugin directory.
# Trying to import packages from subdirectories dynamically at a later time is NOT possible.

# This package automatically imports all packages from the extension directory
# so they are available when we need them.

if sublime.version() < '3000':
    packages_path = sublime.packages_path()
    extension_module = "markdown.extensions"


    for  _, package, _ in pkgutil.walk_packages("."):
        if package.startswith(extension_module):
            print ("Reloading plugin extension " + os.path.join(packages_path, INSTALLED_DIRECTORY, *package.split(".")) + ".py")
            __import__(package)
