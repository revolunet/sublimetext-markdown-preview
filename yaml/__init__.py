from __future__ import absolute_import
import sublime

ST3 = int(sublime.version()) >= 3000

if ST3:
    from .lib3 import *
else:
    from .lib import *
