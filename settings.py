from __future__ import unicode_literals
import sublime
import os
import sys
import re

BUILTIN_KEYS = ('basepath', 'references', 'destination')

ST3 = int(sublime.version()) >= 3000
if ST3:
    unicode_str = str
else:
    unicode_str = unicode


class Settings(object):
    def __init__(self, settings_file, file_name):
        self.file_name = file_name
        self._sub_settings = sublime.load_settings(settings_file)
        self._overrides = {
            "builtin": {
                "references": [],
                "basepath": self.get_base_path(None)
            },
            "meta": {}
        }

    def get(self, key, default=None):
        if key in self._overrides:
            return self._overrides[key]
        else:
            return self._sub_settings.get(key, default)

    def set(self, key, value):
        self._overrides[key] = value

    def has(self, key):
        found = key in self._overrides
        if not found:
            found = self._sub_settings.has(key)
        return found

    def is_abs(self, pth):
        absolute = False
        if pth is not None:
            if sys.platform.startswith('win'):
                re_win_drive = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")
                if re_win_drive.match(pth) is not None or pth.startswith("//"):
                    absolute = True
            elif pth.startswith('/'):
                absolute = True
        return absolute

    def resolve_meta_path(self, target):
        """
        Resolve the path returned in the meta data.
        1. See if path is defined as absolute and if so see
           if it exists
        2. If relative, use the file's current directory
           (if available) as the base and see if the file
           can be found
        3. If relative, and the file's current directory
           as the base proved fruitless, use the defined
           basepath (if available)
        """
        basepath = self._overrides["builtin"].get("basepath")
        current_dir = None if self.file_name is None else os.path.dirname(self.file_name)
        if target is not None:
            target = os.path.expanduser(target)
            if not self.is_abs(target):
                for base in (current_dir, basepath):
                    if base is not None:
                        temp = os.path.join(base, target)
                        if os.path.exists(temp):
                            target = temp
                            break
            elif not os.path.exists(target):
                target = None
        return target

    def get_base_path(self, basepath):
        """ Get the base path to use when resolving basepath paths if possible """
        if basepath is not None:
            basepath = os.path.expanduser(basepath)

        if (
            basepath is not None and os.path.exists(basepath) and
            self.is_abs(basepath) and os.path.isdir(basepath)
        ):
            # A valid path was fed in
            path = basepath
            basepath = path
        elif self.file_name is not None and os.path.exists(self.file_name):
            basepath = os.path.dirname(self.file_name)
        else:
            # Okay, there is no way to tell the orign.
            # We are probably a stream that has no specified
            # physical location.
            basepath = None

        return basepath

    def add_meta(self, meta):
        meta = dict(list(meta.items()) + list(self._overrides.get("meta", {}).items()))
        self._overrides["meta"] = meta

    def apply_frontmatter(self, frontmatter):
        # Handle basepath first

        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            self._overrides["builtin"]["basepath"] = self.get_base_path(value)
            del frontmatter["basepath"]

        for key, value in frontmatter.items():
            if key == "settings" and isinstance(value, dict):
                for subkey, subvalue in value.items():
                    self._overrides[subkey] = subvalue
            elif key in BUILTIN_KEYS:
                if key == "references":
                    if not isinstance(value, list):
                        value = [value]
                    refs = []
                    for ref in value:
                        file_name = self.resolve_meta_path(ref)
                        if file_name is not None and not os.path.isdir(file_name):
                            refs.append(os.path.normpath(file_name))
                    self._overrides["builtin"][key] = refs
                if key == "destination":
                    if value is not None:
                        file_name = value
                        if file_name is not None:
                            directory = os.path.dirname(file_name)
                            directory = self.resolve_meta_path(directory)
                        else:
                            directory = None
                        if directory is not None:
                            file_name = os.path.join(directory, os.path.basename(file_name))
                        if (
                            file_name is not None and
                            (not os.path.exists(file_name) or not os.path.isdir(file_name))
                        ):
                            self._overrides["builtin"][key] = file_name
            else:
                if isinstance(value, list):
                    value = [unicode_str(v) for v in value]
                else:
                    value = unicode_str(value)
                self._overrides["meta"][unicode_str(key)] = value
