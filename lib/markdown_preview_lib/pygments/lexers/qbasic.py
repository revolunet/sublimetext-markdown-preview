# -*- coding: utf-8 -*-
"""
    pygments.lexers.qbasic
    ~~~~~~~~~~~~~~~~~~~~~~

    Simple lexer for Microsoft QBasic source code.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
import re

from ..lexer import RegexLexer, include, bygroups
from ..token import Text, Name, Comment, String, Keyword, Punctuation, \
    Number, Operator

__all__ = ['QBasicLexer']


class QBasicLexer(RegexLexer):
    """
    For
    `QBasic <http://en.wikipedia.org/wiki/QBasic>`_
    source code.
    """

    name = 'QBasic'
    aliases = ['qbasic', 'basic']
    filenames = ['*.BAS', '*.bas']
    mimetypes = ['text/basic']

    declarations = ['DATA', 'LET']

    functions = [
        'ABS', 'ASC', 'ATN', 'CDBL', 'CHR$', 'CINT', 'CLNG',
        'COMMAND$', 'COS', 'CSNG', 'CSRLIN', 'CVD', 'CVDMBF', 'CVI',
        'CVL', 'CVS', 'CVSMBF', 'DATE$', 'ENVIRON$', 'EOF', 'ERDEV',
        'ERDEV$', 'ERL', 'ERR', 'EXP', 'FILEATTR', 'FIX', 'FRE',
        'FREEFILE', 'HEX$', 'INKEY$', 'INP', 'INPUT$', 'INSTR', 'INT',
        'IOCTL$', 'LBOUND', 'LCASE$', 'LEFT$', 'LEN', 'LOC', 'LOF',
        'LOG', 'LPOS', 'LTRIM$', 'MID$', 'MKD$', 'MKDMBF$', 'MKI$',
        'MKL$', 'MKS$', 'MKSMBF$', 'OCT$', 'PEEK', 'PEN', 'PLAY',
        'PMAP', 'POINT', 'POS', 'RIGHT$', 'RND', 'RTRIM$', 'SADD',
        'SCREEN', 'SEEK', 'SETMEM', 'SGN', 'SIN', 'SPACE$', 'SPC',
        'SQR', 'STICK', 'STR$', 'STRIG', 'STRING$', 'TAB', 'TAN',
        'TIME$', 'TIMER', 'UBOUND', 'UCASE$', 'VAL', 'VARPTR',
        'VARPTR$', 'VARSEG'
    ]

    metacommands = ['$DYNAMIC', '$INCLUDE', '$STATIC']

    operators = ['AND', 'EQV', 'IMP', 'NOT', 'OR', 'XOR']

    statements = [
        'BEEP', 'BLOAD', 'BSAVE', 'CALL', 'CALL ABSOLUTE',
        'CALL INTERRUPT', 'CALLS', 'CHAIN', 'CHDIR', 'CIRCLE', 'CLEAR',
        'CLOSE', 'CLS', 'COLOR', 'COM', 'COMMON', 'CONST', 'DATA',
        'DATE$', 'DECLARE', 'DEF FN', 'DEF SEG', 'DEFDBL', 'DEFINT',
        'DEFLNG', 'DEFSNG', 'DEFSTR', 'DEF', 'DIM', 'DO', 'LOOP',
        'DRAW', 'END', 'ENVIRON', 'ERASE', 'ERROR', 'EXIT', 'FIELD',
        'FILES', 'FOR', 'NEXT', 'FUNCTION', 'GET', 'GOSUB', 'GOTO',
        'IF', 'THEN', 'INPUT', 'INPUT #', 'IOCTL', 'KEY', 'KEY',
        'KILL', 'LET', 'LINE', 'LINE INPUT', 'LINE INPUT #', 'LOCATE',
        'LOCK', 'UNLOCK', 'LPRINT', 'LSET', 'MID$', 'MKDIR', 'NAME',
        'ON COM', 'ON ERROR', 'ON KEY', 'ON PEN', 'ON PLAY',
        'ON STRIG', 'ON TIMER', 'ON UEVENT', 'ON', 'OPEN', 'OPEN COM',
        'OPTION BASE', 'OUT', 'PAINT', 'PALETTE', 'PCOPY', 'PEN',
        'PLAY', 'POKE', 'PRESET', 'PRINT', 'PRINT #', 'PRINT USING',
        'PSET', 'PUT', 'PUT', 'RANDOMIZE', 'READ', 'REDIM', 'REM',
        'RESET', 'RESTORE', 'RESUME', 'RETURN', 'RMDIR', 'RSET', 'RUN',
        'SCREEN', 'SEEK', 'SELECT CASE', 'SHARED', 'SHELL', 'SLEEP',
        'SOUND', 'STATIC', 'STOP', 'STRIG', 'SUB', 'SWAP', 'SYSTEM',
        'TIME$', 'TIMER', 'TROFF', 'TRON', 'TYPE', 'UEVENT', 'UNLOCK',
        'VIEW', 'WAIT', 'WHILE', 'WEND', 'WIDTH', 'WINDOW', 'WRITE'
    ]

    keywords = [
        'ACCESS', 'ALIAS', 'ANY', 'APPEND', 'AS', 'BASE', 'BINARY',
        'BYVAL', 'CASE', 'CDECL', 'DOUBLE', 'ELSE', 'ELSEIF', 'ENDIF',
        'INTEGER', 'IS', 'LIST', 'LOCAL', 'LONG', 'LOOP', 'MOD',
        'NEXT', 'OFF', 'ON', 'OUTPUT', 'RANDOM', 'SIGNAL', 'SINGLE',
        'STEP', 'STRING', 'THEN', 'TO', 'UNTIL', 'USING', 'WEND'
    ]

    tokens = {
        'root': [
            (r'\n+', Text),
            (r'\s+', Text.Whitespace),
            (r'^(\s*)(\d*)(\s*)(REM .*)$',
             bygroups(Text.Whitespace, Name.Label, Text.Whitespace,
             Comment.Single)),
            (r'^(\s*)(\d+)(\s*)',
             bygroups(Text.Whitespace, Name.Label, Text.Whitespace)),
            (r'(?=[\s]*)(\w+)(?=[\s]*=)', Name.Variable.Global),
            (r'(?=[^"]*)\'.*$', Comment.Single),
            (r'"[^\n\"]*"', String.Double),
            (r'(END)(\s+)(FUNCTION|IF|SELECT|SUB)',
             bygroups(Keyword.Reserved, Text.Whitespace, Keyword.Reserved)),
            (r'(DECLARE)(\s+)([A-Z]+)(\s+)(\S+)',
             bygroups(Keyword.Declaration, Text.Whitespace, Name.Variable,
             Text.Whitespace, Name)),
            (r'(DIM)(\s+)(SHARED)(\s+)([^\s\(]+)',
             bygroups(Keyword.Declaration, Text.Whitespace, Name.Variable,
             Text.Whitespace, Name.Variable.Global)),
            (r'(DIM)(\s+)([^\s\(]+)',
             bygroups(Keyword.Declaration, Text.Whitespace, Name.Variable.Global)),
            (r'^(\s*)([a-zA-Z_]+)(\s*)(\=)',
             bygroups(Text.Whitespace, Name.Variable.Global, Text.Whitespace,
             Operator)),
            (r'(GOTO|GOSUB)(\s+)(\w+\:?)',
             bygroups(Keyword.Reserved, Text.Whitespace, Name.Label)),
            (r'(SUB)(\s+)(\w+\:?)',
             bygroups(Keyword.Reserved, Text.Whitespace, Name.Label)),
            include('declarations'),
            include('functions'),
            include('metacommands'),
            include('operators'),
            include('statements'),
            include('keywords'),
            (r'[a-zA-Z_]\w*[\$@#&!]', Name.Variable.Global),
            (r'[a-zA-Z_]\w*\:', Name.Label),
            (r'\-?\d*\.\d+[@|#]?', Number.Float),
            (r'\-?\d+[@|#]', Number.Float),
            (r'\-?\d+#?', Number.Integer.Long),
            (r'\-?\d+#?', Number.Integer),
            (r'!=|==|:=|\.=|<<|>>|[-~+/\\*%=<>&^|?:!.]', Operator),
            (r'[\[\]{}(),;]', Punctuation),
            (r'[\w]+', Name.Variable.Global),
        ],
        # can't use regular \b because of X$()
        'declarations': [
            (r'\b(%s)(?=\(|\b)' % '|'.join(map(re.escape, declarations)),
             Keyword.Declaration),
        ],
        'functions': [
            (r'\b(%s)(?=\(|\b)' % '|'.join(map(re.escape, functions)),
             Keyword.Reserved),
        ],
        'metacommands': [
            (r'\b(%s)(?=\(|\b)' % '|'.join(map(re.escape, metacommands)),
             Keyword.Constant),
        ],
        'operators': [
            (r'\b(%s)(?=\(|\b)' % '|'.join(map(re.escape, operators)), Operator.Word),
        ],
        'statements': [
            (r'\b(%s)\b' % '|'.join(map(re.escape, statements)),
             Keyword.Reserved),
        ],
        'keywords': [
            (r'\b(%s)\b' % '|'.join(keywords), Keyword),
        ],
    }

    def analyse_text(text):
        return 0.2
