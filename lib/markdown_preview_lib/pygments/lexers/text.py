# -*- coding: utf-8 -*-
"""
    pygments.lexers.text
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for non-source code file types.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
from ..lexers.configs import ApacheConfLexer, NginxConfLexer, \
    SquidConfLexer, LighttpdConfLexer, IniLexer, RegeditLexer, PropertiesLexer
from ..lexers.console import PyPyLogLexer
from ..lexers.textedit import VimLexer
from ..lexers.markup import BBCodeLexer, MoinWikiLexer, RstLexer, \
    TexLexer, GroffLexer
from ..lexers.installers import DebianControlLexer, SourcesListLexer
from ..lexers.make import MakefileLexer, BaseMakefileLexer, CMakeLexer
from ..lexers.haxe import HxmlLexer
from ..lexers.diff import DiffLexer, DarcsPatchLexer
from ..lexers.data import YamlLexer
from ..lexers.textfmts import IrcLogsLexer, GettextLexer, HttpLexer

__all__ = []
