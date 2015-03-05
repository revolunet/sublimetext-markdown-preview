# -*- coding: utf-8 -*-
"""
    pygments.lexers.web
    ~~~~~~~~~~~~~~~~~~~

    Just export previously exported lexers.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
from ..lexers.html import HtmlLexer, DtdLexer, XmlLexer, XsltLexer, \
    HamlLexer, ScamlLexer, JadeLexer
from ..lexers.css import CssLexer, SassLexer, ScssLexer
from ..lexers.javascript import JavascriptLexer, LiveScriptLexer, \
    DartLexer, TypeScriptLexer, LassoLexer, ObjectiveJLexer, CoffeeScriptLexer
from ..lexers.actionscript import ActionScriptLexer, \
    ActionScript3Lexer, MxmlLexer
from ..lexers.php import PhpLexer
from ..lexers.webmisc import DuelLexer, XQueryLexer, SlimLexer, QmlLexer
from ..lexers.data import JsonLexer
JSONLexer = JsonLexer  # for backwards compatibility with Pygments 1.5

__all__ = []
