# -*- coding: utf-8 -*-
"""
    pygments.lexers.compiled
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for compiled languages.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
import re
from string import Template

from ..lexer import Lexer, RegexLexer, include, bygroups, using, \
     this, combined, inherit, do_insertions, default
from ..util import get_bool_opt, get_list_opt
from ..token import Text, Comment, Operator, Keyword, Name, String, \
     Number, Punctuation, Error, Literal, Generic
from ..scanner import Scanner

# backwards compatibility
from ..lexers.functional import OcamlLexer
from ..lexers.jvm import JavaLexer, ScalaLexer

__all__ = ['CLexer', 'CppLexer', 'DLexer', 'DelphiLexer', 'ECLexer',
           'NesCLexer', 'DylanLexer', 'ObjectiveCLexer', 'ObjectiveCppLexer',
           'FortranLexer', 'GLShaderLexer', 'PrologLexer', 'CythonLexer',
           'ValaLexer', 'OocLexer', 'GoLexer', 'FelixLexer', 'AdaLexer',
           'Modula2Lexer', 'BlitzMaxLexer', 'BlitzBasicLexer', 'NimrodLexer',
           'FantomLexer', 'RustLexer', 'CudaLexer', 'MonkeyLexer', 'SwigLexer',
           'DylanLidLexer', 'DylanConsoleLexer', 'CobolLexer',
           'CobolFreeformatLexer', 'LogosLexer', 'ClayLexer', 'PikeLexer',
           'ChapelLexer', 'EiffelLexer', 'Inform6Lexer', 'Inform7Lexer',
           'Inform6TemplateLexer', 'MqlLexer', 'SwiftLexer']


class CFamilyLexer(RegexLexer):
    """
    For C family source code.  This is used as a base class to avoid repetitious
    definitions.
    """

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'
    #: only one /* */ style comment
    _ws1 = r'\s*(?:/[*].*?[*]/\s*)*'

    tokens = {
        'whitespace': [
            # preprocessor directives: without whitespace
            ('^#if\s+0', Comment.Preproc, 'if0'),
            ('^#', Comment.Preproc, 'macro'),
            # or with whitespace
            ('^(' + _ws1 + r')(#if\s+0)',
             bygroups(using(this), Comment.Preproc), 'if0'),
            ('^(' + _ws1 + ')(#)',
             bygroups(using(this), Comment.Preproc), 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text), # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
        ],
        'statements': [
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[LlUu]*', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[LlUu]*', Number.Hex),
            (r'0[0-7]+[LlUu]*', Number.Oct),
            (r'\d+[LlUu]*', Number.Integer),
            (r'\*/', Error),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[()\[\],.]', Punctuation),
            (r'(auto|break|case|const|continue|default|do|else|enum|extern|'
             r'for|goto|if|register|restricted|return|sizeof|static|struct|'
             r'switch|typedef|union|volatile|while)\b', Keyword),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-z_][a-z0-9_]*_t)\b',
             Keyword.Type),
            (r'(_{0,2}inline|naked|restrict|thread|typename)\b', Keyword.Reserved),
            # Vector intrinsics
            (r'(__(m128i|m128d|m128|m64))\b', Keyword.Reserved),
            # Microsoft-isms
            (r'__(asm|int8|based|except|int16|stdcall|cdecl|fastcall|int32|'
             r'declspec|finally|int64|try|leave|wchar_t|w64|unaligned|'
             r'raise|noop|identifier|forceinline|assume)\b', Keyword.Reserved),
            (r'(true|false|NULL)\b', Name.Builtin),
            (r'([a-zA-Z_]\w*)(\s*)(:)(?!:)', bygroups(Name.Label, Text, Punctuation)),
            ('[a-zA-Z_]\w*', Name),
        ],
        'root': [
            include('whitespace'),
            # functions
            (r'((?:[\w*\s])+?(?:\s|[*]))' # return arguments
             r'([a-zA-Z_]\w*)'            # method name
             r'(\s*\([^;]*?\))'           # signature
             r'(' + _ws + r')?({)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation),
             'function'),
            # function declarations
            (r'((?:[\w*\s])+?(?:\s|[*]))' # return arguments
             r'([a-zA-Z_]\w*)'            # method name
             r'(\s*\([^;]*?\))'           # signature
             r'(' + _ws + r')?(;)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation)),
            default('statement'),
        ],
        'statement' : [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'function': [
            include('whitespace'),
            include('statements'),
            (';', Punctuation),
            ('{', Punctuation, '#push'),
            ('}', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # stray backslash
        ],
        'macro': [
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?\n', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ]
    }

    stdlib_types = ['size_t', 'ssize_t', 'off_t', 'wchar_t', 'ptrdiff_t',
                    'sig_atomic_t', 'fpos_t', 'clock_t', 'time_t', 'va_list',
                    'jmp_buf', 'FILE', 'DIR', 'div_t', 'ldiv_t', 'mbstate_t',
                    'wctrans_t', 'wint_t', 'wctype_t']
    c99_types = ['_Bool', '_Complex', 'int8_t', 'int16_t', 'int32_t', 'int64_t',
                 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int_least8_t',
                 'int_least16_t', 'int_least32_t', 'int_least64_t',
                 'uint_least8_t', 'uint_least16_t', 'uint_least32_t',
                 'uint_least64_t', 'int_fast8_t', 'int_fast16_t', 'int_fast32_t',
                 'int_fast64_t', 'uint_fast8_t', 'uint_fast16_t', 'uint_fast32_t',
                 'uint_fast64_t', 'intptr_t', 'uintptr_t', 'intmax_t',
                 'uintmax_t']

    def __init__(self, **options):
        self.stdlibhighlighting = get_bool_opt(options,
                'stdlibhighlighting', True)
        self.c99highlighting = get_bool_opt(options,
                'c99highlighting', True)
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
            RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name:
                if self.stdlibhighlighting and value in self.stdlib_types:
                    token = Keyword.Type
                elif self.c99highlighting and value in self.c99_types:
                    token = Keyword.Type
            yield index, token, value


class CLexer(CFamilyLexer):
    """
    For C source code with preprocessor directives.
    """
    name = 'C'
    aliases = ['c']
    filenames = ['*.c', '*.h', '*.idc']
    mimetypes = ['text/x-chdr', 'text/x-csrc']
    priority = 0.1

    def analyse_text(text):
        if re.search('#include [<"]', text):
            return 0.1


class CppLexer(CFamilyLexer):
    """
    For C++ source code with preprocessor directives.
    """
    name = 'C++'
    aliases = ['cpp', 'c++']
    filenames = ['*.cpp', '*.hpp', '*.c++', '*.h++',
                 '*.cc', '*.hh', '*.cxx', '*.hxx',
                 '*.C', '*.H', '*.cp', '*.CPP']
    mimetypes = ['text/x-c++hdr', 'text/x-c++src']
    priority = 0.1

    tokens = {
        'statements': [
            (r'(asm|catch|const_cast|delete|dynamic_cast|explicit|'
             r'export|friend|mutable|namespace|new|operator|'
             r'private|protected|public|reinterpret_cast|'
             r'restrict|static_cast|template|this|throw|throws|'
             r'typeid|typename|using|virtual|'
             r'constexpr|nullptr|decltype|thread_local|'
             r'alignas|alignof|static_assert|noexcept|override|final)\b', Keyword),
            (r'(char16_t|char32_t)\b', Keyword.Type),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            inherit,
         ],
        'root': [
            inherit,
            # C++ Microsoft-isms
            (r'__(virtual_inheritance|uuidof|super|single_inheritance|'
             r'multiple_inheritance|interface|event)\b', Keyword.Reserved),
            # Offload C++ extensions, http://offload.codeplay.com/
            (r'(__offload|__blockingoffload|__outer)\b', Keyword.Pseudo),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            # template specification
            (r'\s*(?=>)', Text, '#pop'),
        ],
    }

    def analyse_text(text):
        if re.search('#include <[a-z]+>', text):
            return 0.2
        if re.search('using namespace ', text):
            return 0.4


class PikeLexer(CppLexer):
    """
    For `Pike <http://pike.lysator.liu.se/>`_ source code.

    .. versionadded:: 2.0
    """
    name = 'Pike'
    aliases = ['pike']
    filenames = ['*.pike', '*.pmod']
    mimetypes = ['text/x-pike']

    tokens = {
        'statements': [
            (r'(catch|new|private|protected|public|gauge|'
             r'throw|throws|class|interface|implement|abstract|extends|from|'
             r'this|super|new|constant|final|static|import|use|extern|'
             r'inline|proto|break|continue|if|else|for|'
             r'while|do|switch|case|as|in|version|return|true|false|null|'
             r'__VERSION__|__MAJOR__|__MINOR__|__BUILD__|__REAL_VERSION__|'
             r'__REAL_MAJOR__|__REAL_MINOR__|__REAL_BUILD__|__DATE__|__TIME__|'
             r'__FILE__|__DIR__|__LINE__|__AUTO_BIGNUM__|__NT__|__PIKE__|'
             r'__amigaos__|_Pragma|static_assert|defined|sscanf)\b',
             Keyword),
            (r'(bool|int|long|float|short|double|char|string|object|void|mapping|'
             r'array|multiset|program|function|lambda|mixed|'
             r'[a-z_][a-z0-9_]*_t)\b',
             Keyword.Type),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'[~!%^&*+=|?:<>/-@]', Operator),
            inherit,
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            # template specification
            (r'\s*(?=>)', Text, '#pop'),
        ],
    }


class SwigLexer(CppLexer):
    """
    For `SWIG <http://www.swig.org/>`_ source code.

    .. versionadded:: 2.0
    """
    name = 'SWIG'
    aliases = ['swig']
    filenames = ['*.swg', '*.i']
    mimetypes = ['text/swig']
    priority = 0.04 # Lower than C/C++ and Objective C/C++

    tokens = {
        'statements': [
            # SWIG directives
            (r'(%[a-z_][a-z0-9_]*)', Name.Function),
            # Special variables
            ('\$\**\&?\w+', Name),
            # Stringification / additional preprocessor directives
            (r'##*[a-zA-Z_]\w*', Comment.Preproc),
            inherit,
         ],
    }

    # This is a far from complete set of SWIG directives
    swig_directives = (
        # Most common directives
        '%apply', '%define', '%director', '%enddef', '%exception', '%extend',
        '%feature', '%fragment', '%ignore', '%immutable', '%import', '%include',
        '%inline', '%insert', '%module', '%newobject', '%nspace', '%pragma',
        '%rename', '%shared_ptr', '%template', '%typecheck', '%typemap',
        # Less common directives
        '%arg', '%attribute', '%bang', '%begin', '%callback', '%catches', '%clear',
        '%constant', '%copyctor', '%csconst', '%csconstvalue', '%csenum',
        '%csmethodmodifiers', '%csnothrowexception', '%default', '%defaultctor',
        '%defaultdtor', '%defined', '%delete', '%delobject', '%descriptor',
        '%exceptionclass', '%exceptionvar', '%extend_smart_pointer', '%fragments',
        '%header', '%ifcplusplus', '%ignorewarn', '%implicit', '%implicitconv',
        '%init', '%javaconst', '%javaconstvalue', '%javaenum', '%javaexception',
        '%javamethodmodifiers', '%kwargs', '%luacode', '%mutable', '%naturalvar',
        '%nestedworkaround', '%perlcode', '%pythonabc', '%pythonappend',
        '%pythoncallback', '%pythoncode', '%pythondynamic', '%pythonmaybecall',
        '%pythonnondynamic', '%pythonprepend', '%refobject', '%shadow', '%sizeof',
        '%trackobjects', '%types', '%unrefobject', '%varargs', '%warn', '%warnfilter')

    def analyse_text(text):
        rv = 0
        # Search for SWIG directives, which are conventionally at the beginning of
        # a line. The probability of them being within a line is low, so let another
        # lexer win in this case.
        matches = re.findall(r'^\s*(%[a-z_][a-z0-9_]*)', text, re.M)
        for m in matches:
            if m in SwigLexer.swig_directives:
                rv = 0.98
                break
            else:
                rv = 0.91 # Fraction higher than MatlabLexer
        return rv


class ECLexer(CLexer):
    """
    For eC source code with preprocessor directives.

    .. versionadded:: 1.5
    """
    name = 'eC'
    aliases = ['ec']
    filenames = ['*.ec', '*.eh']
    mimetypes = ['text/x-echdr', 'text/x-ecsrc']

    tokens = {
        'statements': [
            (r'(virtual|class|private|public|property|import|delete|new|new0|'
             r'renew|renew0|define|get|set|remote|dllexport|dllimport|stdcall|'
             r'subclass|__on_register_module|namespace|using|typed_object|'
             r'any_object|incref|register|watch|stopwatching|firewatchers|'
             r'watchable|class_designer|class_fixed|class_no_expansion|isset|'
             r'class_default_property|property_category|class_data|'
             r'class_property|virtual|thisclass|'
             r'dbtable|dbindex|database_open|dbfield)\b', Keyword),
            (r'(uint|uint16|uint32|uint64|bool|byte|unichar|int64)\b',
             Keyword.Type),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'(null|value|this)\b', Name.Builtin),
            inherit,
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            # template specification
            (r'\s*(?=>)', Text, '#pop'),
        ],
    }


class NesCLexer(CLexer):
    """
    For `nesC <https://github.com/tinyos/nesc>`_ source code with preprocessor
    directives.

    .. versionadded:: 2.0
    """
    name = 'nesC'
    aliases = ['nesc']
    filenames = ['*.nc']
    mimetypes = ['text/x-nescsrc']

    tokens = {
        'statements': [
            (r'(abstract|as|async|atomic|call|command|component|components|'
             r'configuration|event|extends|generic|implementation|includes|'
             r'interface|module|new|norace|post|provides|signal|task|uses)\b',
             Keyword),
            (r'(nx_struct|nx_union|nx_int8_t|nx_int16_t|nx_int32_t|nx_int64_t|'
             r'nx_uint8_t|nx_uint16_t|nx_uint32_t|nx_uint64_t)\b',
             Keyword.Type),
            inherit,
        ],
    }


class ClayLexer(RegexLexer):
    """
    For `Clay <http://claylabs.com/clay/>`_ source.

    .. versionadded:: 2.0
    """
    name = 'Clay'
    filenames = ['*.clay']
    aliases = ['clay']
    mimetypes = ['text/x-clay']
    tokens = {
        'root': [
            (r'\s', Text),
            (r'//.*?$', Comment.Singleline),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'\b(public|private|import|as|record|variant|instance'
             r'|define|overload|default|external|alias'
             r'|rvalue|ref|forward|inline|noinline|forceinline'
             r'|enum|var|and|or|not|if|else|goto|return|while'
             r'|switch|case|break|continue|for|in|true|false|try|catch|throw'
             r'|finally|onerror|staticassert|eval|when|newtype'
             r'|__FILE__|__LINE__|__COLUMN__|__ARG__'
             r')\b', Keyword),
            (r'[~!%^&*+=|:<>/-]', Operator),
            (r'[#(){}\[\],;.]', Punctuation),
            (r'0x[0-9a-fA-F]+[LlUu]*', Number.Hex),
            (r'\d+[LlUu]*', Number.Integer),
            (r'\b(true|false)\b', Name.Builtin),
            (r'(?i)[a-z_?][a-z_?0-9]*', Name),
            (r'"""', String, 'tdqs'),
            (r'"', String, 'dqs'),
        ],
        'strings': [
            (r'(?i)\\(x[0-9a-f]{2}|.)', String.Escape),
            (r'.', String),
        ],
        'nl': [
            (r'\n', String),
        ],
        'dqs': [
            (r'"', String, '#pop'),
            include('strings'),
        ],
        'tdqs': [
            (r'"""', String, '#pop'),
            include('strings'),
            include('nl'),
        ],
    }


class DLexer(RegexLexer):
    """
    For D source.

    .. versionadded:: 1.2
    """
    name = 'D'
    filenames = ['*.d', '*.di']
    aliases = ['d']
    mimetypes = ['text/x-dsrc']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'\s+', Text),
            #(r'\\\n', Text), # line continuations
            # Comments
            (r'//(.*?)\n', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'/\+', Comment.Multiline, 'nested_comment'),
            # Keywords
            (r'(abstract|alias|align|asm|assert|auto|body|break|case|cast'
             r'|catch|class|const|continue|debug|default|delegate|delete'
             r'|deprecated|do|else|enum|export|extern|finally|final'
             r'|foreach_reverse|foreach|for|function|goto|if|immutable|import'
             r'|interface|invariant|inout|in|is|lazy|mixin|module|new|nothrow|out'
             r'|override|package|pragma|private|protected|public|pure|ref|return'
             r'|scope|shared|static|struct|super|switch|synchronized|template|this'
             r'|throw|try|typedef|typeid|typeof|union|unittest|version|volatile'
             r'|while|with|__gshared|__traits|__vector|__parameters)\b', Keyword
            ),
            (r'(bool|byte|cdouble|cent|cfloat|char|creal|dchar|double|float'
             r'|idouble|ifloat|int|ireal|long|real|short|ubyte|ucent|uint|ulong'
             r'|ushort|void|wchar)\b', Keyword.Type
            ),
            (r'(false|true|null)\b', Keyword.Constant),
            (r'(__FILE__|__MODULE__|__LINE__|__FUNCTION__|__PRETTY_FUNCTION__'
             r'|__DATE__|__EOF__|__TIME__|__TIMESTAMP__|__VENDOR__|__VERSION__)\b',
             Keyword.Pseudo),
            (r'macro\b', Keyword.Reserved),
            (r'(string|wstring|dstring|size_t|ptrdiff_t)\b', Name.Builtin),
            # FloatLiteral
            # -- HexFloat
            (r'0[xX]([0-9a-fA-F_]*\.[0-9a-fA-F_]+|[0-9a-fA-F_]+)'
             r'[pP][+\-]?[0-9_]+[fFL]?[i]?', Number.Float),
            # -- DecimalFloat
            (r'[0-9_]+(\.[0-9_]+[eE][+\-]?[0-9_]+|'
             r'\.[0-9_]*|[eE][+\-]?[0-9_]+)[fFL]?[i]?', Number.Float),
            (r'\.(0|[1-9][0-9_]*)([eE][+\-]?[0-9_]+)?[fFL]?[i]?', Number.Float),
            # IntegerLiteral
            # -- Binary
            (r'0[Bb][01_]+', Number.Bin),
            # -- Octal
            (r'0[0-7_]+', Number.Oct),
            # -- Hexadecimal
            (r'0[xX][0-9a-fA-F_]+', Number.Hex),
            # -- Decimal
            (r'(0|[1-9][0-9_]*)([LUu]|Lu|LU|uL|UL)?', Number.Integer),
            # CharacterLiteral
            (r"""'(\\['"?\\abfnrtv]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}"""
             r"""|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|\\&\w+;|.)'""",
             String.Char
            ),
            # StringLiteral
            # -- WysiwygString
            (r'r"[^"]*"[cwd]?', String),
            # -- AlternateWysiwygString
            (r'`[^`]*`[cwd]?', String),
            # -- DoubleQuotedString
            (r'"(\\\\|\\"|[^"])*"[cwd]?', String),
            # -- EscapeSequence
            (r"\\(['\"?\\abfnrtv]|x[0-9a-fA-F]{2}|[0-7]{1,3}"
             r"|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|&\w+;)",
             String
            ),
            # -- HexString
            (r'x"[0-9a-fA-F_\s]*"[cwd]?', String),
            # -- DelimitedString
            (r'q"\[', String, 'delimited_bracket'),
            (r'q"\(', String, 'delimited_parenthesis'),
            (r'q"<', String, 'delimited_angle'),
            (r'q"{', String, 'delimited_curly'),
            (r'q"([a-zA-Z_]\w*)\n.*?\n\1"', String),
            (r'q"(.).*?\1"', String),
            # -- TokenString
            (r'q{', String, 'token_string'),
            # Attributes
            (r'@([a-zA-Z_]\w*)?', Name.Decorator),
            # Tokens
            (r'(~=|\^=|%=|\*=|==|!>=|!<=|!<>=|!<>|!<|!>|!=|>>>=|>>>|>>=|>>|>='
             r'|<>=|<>|<<=|<<|<=|\+\+|\+=|--|-=|\|\||\|=|&&|&=|\.\.\.|\.\.|/=)'
             r'|[/.&|\-+<>!()\[\]{}?,;:$=*%^~]', Punctuation
            ),
            # Identifier
            (r'[a-zA-Z_]\w*', Name),
            # Line
            (r'#line\s.*\n', Comment.Special),
        ],
        'nested_comment': [
            (r'[^+/]+', Comment.Multiline),
            (r'/\+', Comment.Multiline, '#push'),
            (r'\+/', Comment.Multiline, '#pop'),
            (r'[+/]', Comment.Multiline),
        ],
        'token_string': [
            (r'{', Punctuation, 'token_string_nest'),
            (r'}', String, '#pop'),
            include('root'),
        ],
        'token_string_nest': [
            (r'{', Punctuation, '#push'),
            (r'}', Punctuation, '#pop'),
            include('root'),
        ],
        'delimited_bracket': [
            (r'[^\[\]]+', String),
            (r'\[', String, 'delimited_inside_bracket'),
            (r'\]"', String, '#pop'),
        ],
        'delimited_inside_bracket': [
            (r'[^\[\]]+', String),
            (r'\[', String, '#push'),
            (r'\]', String, '#pop'),
        ],
        'delimited_parenthesis': [
            (r'[^\(\)]+', String),
            (r'\(', String, 'delimited_inside_parenthesis'),
            (r'\)"', String, '#pop'),
        ],
        'delimited_inside_parenthesis': [
            (r'[^\(\)]+', String),
            (r'\(', String, '#push'),
            (r'\)', String, '#pop'),
        ],
        'delimited_angle': [
            (r'[^<>]+', String),
            (r'<', String, 'delimited_inside_angle'),
            (r'>"', String, '#pop'),
        ],
        'delimited_inside_angle': [
            (r'[^<>]+', String),
            (r'<', String, '#push'),
            (r'>', String, '#pop'),
        ],
        'delimited_curly': [
            (r'[^{}]+', String),
            (r'{', String, 'delimited_inside_curly'),
            (r'}"', String, '#pop'),
        ],
        'delimited_inside_curly': [
            (r'[^{}]+', String),
            (r'{', String, '#push'),
            (r'}', String, '#pop'),
        ],
    }


class DelphiLexer(Lexer):
    """
    For `Delphi <http://www.borland.com/delphi/>`_ (Borland Object Pascal),
    Turbo Pascal and Free Pascal source code.

    Additional options accepted:

    `turbopascal`
        Highlight Turbo Pascal specific keywords (default: ``True``).
    `delphi`
        Highlight Borland Delphi specific keywords (default: ``True``).
    `freepascal`
        Highlight Free Pascal specific keywords (default: ``True``).
    `units`
        A list of units that should be considered builtin, supported are
        ``System``, ``SysUtils``, ``Classes`` and ``Math``.
        Default is to consider all of them builtin.
    """
    name = 'Delphi'
    aliases = ['delphi', 'pas', 'pascal', 'objectpascal']
    filenames = ['*.pas']
    mimetypes = ['text/x-pascal']

    TURBO_PASCAL_KEYWORDS = [
        'absolute', 'and', 'array', 'asm', 'begin', 'break', 'case',
        'const', 'constructor', 'continue', 'destructor', 'div', 'do',
        'downto', 'else', 'end', 'file', 'for', 'function', 'goto',
        'if', 'implementation', 'in', 'inherited', 'inline', 'interface',
        'label', 'mod', 'nil', 'not', 'object', 'of', 'on', 'operator',
        'or', 'packed', 'procedure', 'program', 'record', 'reintroduce',
        'repeat', 'self', 'set', 'shl', 'shr', 'string', 'then', 'to',
        'type', 'unit', 'until', 'uses', 'var', 'while', 'with', 'xor'
    ]

    DELPHI_KEYWORDS = [
        'as', 'class', 'except', 'exports', 'finalization', 'finally',
        'initialization', 'is', 'library', 'on', 'property', 'raise',
        'threadvar', 'try'
    ]

    FREE_PASCAL_KEYWORDS = [
        'dispose', 'exit', 'false', 'new', 'true'
    ]

    BLOCK_KEYWORDS = set([
        'begin', 'class', 'const', 'constructor', 'destructor', 'end',
        'finalization', 'function', 'implementation', 'initialization',
        'label', 'library', 'operator', 'procedure', 'program', 'property',
        'record', 'threadvar', 'type', 'unit', 'uses', 'var'
    ])

    FUNCTION_MODIFIERS = set([
        'alias', 'cdecl', 'export', 'inline', 'interrupt', 'nostackframe',
        'pascal', 'register', 'safecall', 'softfloat', 'stdcall',
        'varargs', 'name', 'dynamic', 'near', 'virtual', 'external',
        'override', 'assembler'
    ])

    # XXX: those aren't global. but currently we know no way for defining
    #      them just for the type context.
    DIRECTIVES = set([
        'absolute', 'abstract', 'assembler', 'cppdecl', 'default', 'far',
        'far16', 'forward', 'index', 'oldfpccall', 'private', 'protected',
        'published', 'public'
    ])

    BUILTIN_TYPES = set([
        'ansichar', 'ansistring', 'bool', 'boolean', 'byte', 'bytebool',
        'cardinal', 'char', 'comp', 'currency', 'double', 'dword',
        'extended', 'int64', 'integer', 'iunknown', 'longbool', 'longint',
        'longword', 'pansichar', 'pansistring', 'pbool', 'pboolean',
        'pbyte', 'pbytearray', 'pcardinal', 'pchar', 'pcomp', 'pcurrency',
        'pdate', 'pdatetime', 'pdouble', 'pdword', 'pextended', 'phandle',
        'pint64', 'pinteger', 'plongint', 'plongword', 'pointer',
        'ppointer', 'pshortint', 'pshortstring', 'psingle', 'psmallint',
        'pstring', 'pvariant', 'pwidechar', 'pwidestring', 'pword',
        'pwordarray', 'pwordbool', 'real', 'real48', 'shortint',
        'shortstring', 'single', 'smallint', 'string', 'tclass', 'tdate',
        'tdatetime', 'textfile', 'thandle', 'tobject', 'ttime', 'variant',
        'widechar', 'widestring', 'word', 'wordbool'
    ])

    BUILTIN_UNITS = {
        'System': [
            'abs', 'acquireexceptionobject', 'addr', 'ansitoutf8',
            'append', 'arctan', 'assert', 'assigned', 'assignfile',
            'beginthread', 'blockread', 'blockwrite', 'break', 'chdir',
            'chr', 'close', 'closefile', 'comptocurrency', 'comptodouble',
            'concat', 'continue', 'copy', 'cos', 'dec', 'delete',
            'dispose', 'doubletocomp', 'endthread', 'enummodules',
            'enumresourcemodules', 'eof', 'eoln', 'erase', 'exceptaddr',
            'exceptobject', 'exclude', 'exit', 'exp', 'filepos', 'filesize',
            'fillchar', 'finalize', 'findclasshinstance', 'findhinstance',
            'findresourcehinstance', 'flush', 'frac', 'freemem',
            'get8087cw', 'getdir', 'getlasterror', 'getmem',
            'getmemorymanager', 'getmodulefilename', 'getvariantmanager',
            'halt', 'hi', 'high', 'inc', 'include', 'initialize', 'insert',
            'int', 'ioresult', 'ismemorymanagerset', 'isvariantmanagerset',
            'length', 'ln', 'lo', 'low', 'mkdir', 'move', 'new', 'odd',
            'olestrtostring', 'olestrtostrvar', 'ord', 'paramcount',
            'paramstr', 'pi', 'pos', 'pred', 'ptr', 'pucs4chars', 'random',
            'randomize', 'read', 'readln', 'reallocmem',
            'releaseexceptionobject', 'rename', 'reset', 'rewrite', 'rmdir',
            'round', 'runerror', 'seek', 'seekeof', 'seekeoln',
            'set8087cw', 'setlength', 'setlinebreakstyle',
            'setmemorymanager', 'setstring', 'settextbuf',
            'setvariantmanager', 'sin', 'sizeof', 'slice', 'sqr', 'sqrt',
            'str', 'stringofchar', 'stringtoolestr', 'stringtowidechar',
            'succ', 'swap', 'trunc', 'truncate', 'typeinfo',
            'ucs4stringtowidestring', 'unicodetoutf8', 'uniquestring',
            'upcase', 'utf8decode', 'utf8encode', 'utf8toansi',
            'utf8tounicode', 'val', 'vararrayredim', 'varclear',
            'widecharlentostring', 'widecharlentostrvar',
            'widechartostring', 'widechartostrvar',
            'widestringtoucs4string', 'write', 'writeln'
        ],
        'SysUtils': [
            'abort', 'addexitproc', 'addterminateproc', 'adjustlinebreaks',
            'allocmem', 'ansicomparefilename', 'ansicomparestr',
            'ansicomparetext', 'ansidequotedstr', 'ansiextractquotedstr',
            'ansilastchar', 'ansilowercase', 'ansilowercasefilename',
            'ansipos', 'ansiquotedstr', 'ansisamestr', 'ansisametext',
            'ansistrcomp', 'ansistricomp', 'ansistrlastchar', 'ansistrlcomp',
            'ansistrlicomp', 'ansistrlower', 'ansistrpos', 'ansistrrscan',
            'ansistrscan', 'ansistrupper', 'ansiuppercase',
            'ansiuppercasefilename', 'appendstr', 'assignstr', 'beep',
            'booltostr', 'bytetocharindex', 'bytetocharlen', 'bytetype',
            'callterminateprocs', 'changefileext', 'charlength',
            'chartobyteindex', 'chartobytelen', 'comparemem', 'comparestr',
            'comparetext', 'createdir', 'createguid', 'currentyear',
            'currtostr', 'currtostrf', 'date', 'datetimetofiledate',
            'datetimetostr', 'datetimetostring', 'datetimetosystemtime',
            'datetimetotimestamp', 'datetostr', 'dayofweek', 'decodedate',
            'decodedatefully', 'decodetime', 'deletefile', 'directoryexists',
            'diskfree', 'disksize', 'disposestr', 'encodedate', 'encodetime',
            'exceptionerrormessage', 'excludetrailingbackslash',
            'excludetrailingpathdelimiter', 'expandfilename',
            'expandfilenamecase', 'expanduncfilename', 'extractfiledir',
            'extractfiledrive', 'extractfileext', 'extractfilename',
            'extractfilepath', 'extractrelativepath', 'extractshortpathname',
            'fileage', 'fileclose', 'filecreate', 'filedatetodatetime',
            'fileexists', 'filegetattr', 'filegetdate', 'fileisreadonly',
            'fileopen', 'fileread', 'filesearch', 'fileseek', 'filesetattr',
            'filesetdate', 'filesetreadonly', 'filewrite', 'finalizepackage',
            'findclose', 'findcmdlineswitch', 'findfirst', 'findnext',
            'floattocurr', 'floattodatetime', 'floattodecimal', 'floattostr',
            'floattostrf', 'floattotext', 'floattotextfmt', 'fmtloadstr',
            'fmtstr', 'forcedirectories', 'format', 'formatbuf', 'formatcurr',
            'formatdatetime', 'formatfloat', 'freeandnil', 'getcurrentdir',
            'getenvironmentvariable', 'getfileversion', 'getformatsettings',
            'getlocaleformatsettings', 'getmodulename', 'getpackagedescription',
            'getpackageinfo', 'gettime', 'guidtostring', 'incamonth',
            'includetrailingbackslash', 'includetrailingpathdelimiter',
            'incmonth', 'initializepackage', 'interlockeddecrement',
            'interlockedexchange', 'interlockedexchangeadd',
            'interlockedincrement', 'inttohex', 'inttostr', 'isdelimiter',
            'isequalguid', 'isleapyear', 'ispathdelimiter', 'isvalidident',
            'languages', 'lastdelimiter', 'loadpackage', 'loadstr',
            'lowercase', 'msecstotimestamp', 'newstr', 'nextcharindex', 'now',
            'outofmemoryerror', 'quotedstr', 'raiselastoserror',
            'raiselastwin32error', 'removedir', 'renamefile', 'replacedate',
            'replacetime', 'safeloadlibrary', 'samefilename', 'sametext',
            'setcurrentdir', 'showexception', 'sleep', 'stralloc', 'strbufsize',
            'strbytetype', 'strcat', 'strcharlength', 'strcomp', 'strcopy',
            'strdispose', 'strecopy', 'strend', 'strfmt', 'stricomp',
            'stringreplace', 'stringtoguid', 'strlcat', 'strlcomp', 'strlcopy',
            'strlen', 'strlfmt', 'strlicomp', 'strlower', 'strmove', 'strnew',
            'strnextchar', 'strpas', 'strpcopy', 'strplcopy', 'strpos',
            'strrscan', 'strscan', 'strtobool', 'strtobooldef', 'strtocurr',
            'strtocurrdef', 'strtodate', 'strtodatedef', 'strtodatetime',
            'strtodatetimedef', 'strtofloat', 'strtofloatdef', 'strtoint',
            'strtoint64', 'strtoint64def', 'strtointdef', 'strtotime',
            'strtotimedef', 'strupper', 'supports', 'syserrormessage',
            'systemtimetodatetime', 'texttofloat', 'time', 'timestamptodatetime',
            'timestamptomsecs', 'timetostr', 'trim', 'trimleft', 'trimright',
            'tryencodedate', 'tryencodetime', 'tryfloattocurr', 'tryfloattodatetime',
            'trystrtobool', 'trystrtocurr', 'trystrtodate', 'trystrtodatetime',
            'trystrtofloat', 'trystrtoint', 'trystrtoint64', 'trystrtotime',
            'unloadpackage', 'uppercase', 'widecomparestr', 'widecomparetext',
            'widefmtstr', 'wideformat', 'wideformatbuf', 'widelowercase',
            'widesamestr', 'widesametext', 'wideuppercase', 'win32check',
            'wraptext'
        ],
        'Classes': [
            'activateclassgroup', 'allocatehwnd', 'bintohex', 'checksynchronize',
            'collectionsequal', 'countgenerations', 'deallocatehwnd', 'equalrect',
            'extractstrings', 'findclass', 'findglobalcomponent', 'getclass',
            'groupdescendantswith', 'hextobin', 'identtoint',
            'initinheritedcomponent', 'inttoident', 'invalidpoint',
            'isuniqueglobalcomponentname', 'linestart', 'objectbinarytotext',
            'objectresourcetotext', 'objecttexttobinary', 'objecttexttoresource',
            'pointsequal', 'readcomponentres', 'readcomponentresex',
            'readcomponentresfile', 'rect', 'registerclass', 'registerclassalias',
            'registerclasses', 'registercomponents', 'registerintegerconsts',
            'registernoicon', 'registernonactivex', 'smallpoint', 'startclassgroup',
            'teststreamformat', 'unregisterclass', 'unregisterclasses',
            'unregisterintegerconsts', 'unregistermoduleclasses',
            'writecomponentresfile'
        ],
        'Math': [
            'arccos', 'arccosh', 'arccot', 'arccoth', 'arccsc', 'arccsch', 'arcsec',
            'arcsech', 'arcsin', 'arcsinh', 'arctan2', 'arctanh', 'ceil',
            'comparevalue', 'cosecant', 'cosh', 'cot', 'cotan', 'coth', 'csc',
            'csch', 'cycletodeg', 'cycletograd', 'cycletorad', 'degtocycle',
            'degtograd', 'degtorad', 'divmod', 'doubledecliningbalance',
            'ensurerange', 'floor', 'frexp', 'futurevalue', 'getexceptionmask',
            'getprecisionmode', 'getroundmode', 'gradtocycle', 'gradtodeg',
            'gradtorad', 'hypot', 'inrange', 'interestpayment', 'interestrate',
            'internalrateofreturn', 'intpower', 'isinfinite', 'isnan', 'iszero',
            'ldexp', 'lnxp1', 'log10', 'log2', 'logn', 'max', 'maxintvalue',
            'maxvalue', 'mean', 'meanandstddev', 'min', 'minintvalue', 'minvalue',
            'momentskewkurtosis', 'netpresentvalue', 'norm', 'numberofperiods',
            'payment', 'periodpayment', 'poly', 'popnstddev', 'popnvariance',
            'power', 'presentvalue', 'radtocycle', 'radtodeg', 'radtograd',
            'randg', 'randomrange', 'roundto', 'samevalue', 'sec', 'secant',
            'sech', 'setexceptionmask', 'setprecisionmode', 'setroundmode',
            'sign', 'simpleroundto', 'sincos', 'sinh', 'slndepreciation', 'stddev',
            'sum', 'sumint', 'sumofsquares', 'sumsandsquares', 'syddepreciation',
            'tan', 'tanh', 'totalvariance', 'variance'
        ]
    }

    ASM_REGISTERS = set([
        'ah', 'al', 'ax', 'bh', 'bl', 'bp', 'bx', 'ch', 'cl', 'cr0',
        'cr1', 'cr2', 'cr3', 'cr4', 'cs', 'cx', 'dh', 'di', 'dl', 'dr0',
        'dr1', 'dr2', 'dr3', 'dr4', 'dr5', 'dr6', 'dr7', 'ds', 'dx',
        'eax', 'ebp', 'ebx', 'ecx', 'edi', 'edx', 'es', 'esi', 'esp',
        'fs', 'gs', 'mm0', 'mm1', 'mm2', 'mm3', 'mm4', 'mm5', 'mm6',
        'mm7', 'si', 'sp', 'ss', 'st0', 'st1', 'st2', 'st3', 'st4', 'st5',
        'st6', 'st7', 'xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5',
        'xmm6', 'xmm7'
    ])

    ASM_INSTRUCTIONS = set([
        'aaa', 'aad', 'aam', 'aas', 'adc', 'add', 'and', 'arpl', 'bound',
        'bsf', 'bsr', 'bswap', 'bt', 'btc', 'btr', 'bts', 'call', 'cbw',
        'cdq', 'clc', 'cld', 'cli', 'clts', 'cmc', 'cmova', 'cmovae',
        'cmovb', 'cmovbe', 'cmovc', 'cmovcxz', 'cmove', 'cmovg',
        'cmovge', 'cmovl', 'cmovle', 'cmovna', 'cmovnae', 'cmovnb',
        'cmovnbe', 'cmovnc', 'cmovne', 'cmovng', 'cmovnge', 'cmovnl',
        'cmovnle', 'cmovno', 'cmovnp', 'cmovns', 'cmovnz', 'cmovo',
        'cmovp', 'cmovpe', 'cmovpo', 'cmovs', 'cmovz', 'cmp', 'cmpsb',
        'cmpsd', 'cmpsw', 'cmpxchg', 'cmpxchg486', 'cmpxchg8b', 'cpuid',
        'cwd', 'cwde', 'daa', 'das', 'dec', 'div', 'emms', 'enter', 'hlt',
        'ibts', 'icebp', 'idiv', 'imul', 'in', 'inc', 'insb', 'insd',
        'insw', 'int', 'int01', 'int03', 'int1', 'int3', 'into', 'invd',
        'invlpg', 'iret', 'iretd', 'iretw', 'ja', 'jae', 'jb', 'jbe',
        'jc', 'jcxz', 'jcxz', 'je', 'jecxz', 'jg', 'jge', 'jl', 'jle',
        'jmp', 'jna', 'jnae', 'jnb', 'jnbe', 'jnc', 'jne', 'jng', 'jnge',
        'jnl', 'jnle', 'jno', 'jnp', 'jns', 'jnz', 'jo', 'jp', 'jpe',
        'jpo', 'js', 'jz', 'lahf', 'lar', 'lcall', 'lds', 'lea', 'leave',
        'les', 'lfs', 'lgdt', 'lgs', 'lidt', 'ljmp', 'lldt', 'lmsw',
        'loadall', 'loadall286', 'lock', 'lodsb', 'lodsd', 'lodsw',
        'loop', 'loope', 'loopne', 'loopnz', 'loopz', 'lsl', 'lss', 'ltr',
        'mov', 'movd', 'movq', 'movsb', 'movsd', 'movsw', 'movsx',
        'movzx', 'mul', 'neg', 'nop', 'not', 'or', 'out', 'outsb', 'outsd',
        'outsw', 'pop', 'popa', 'popad', 'popaw', 'popf', 'popfd', 'popfw',
        'push', 'pusha', 'pushad', 'pushaw', 'pushf', 'pushfd', 'pushfw',
        'rcl', 'rcr', 'rdmsr', 'rdpmc', 'rdshr', 'rdtsc', 'rep', 'repe',
        'repne', 'repnz', 'repz', 'ret', 'retf', 'retn', 'rol', 'ror',
        'rsdc', 'rsldt', 'rsm', 'sahf', 'sal', 'salc', 'sar', 'sbb',
        'scasb', 'scasd', 'scasw', 'seta', 'setae', 'setb', 'setbe',
        'setc', 'setcxz', 'sete', 'setg', 'setge', 'setl', 'setle',
        'setna', 'setnae', 'setnb', 'setnbe', 'setnc', 'setne', 'setng',
        'setnge', 'setnl', 'setnle', 'setno', 'setnp', 'setns', 'setnz',
        'seto', 'setp', 'setpe', 'setpo', 'sets', 'setz', 'sgdt', 'shl',
        'shld', 'shr', 'shrd', 'sidt', 'sldt', 'smi', 'smint', 'smintold',
        'smsw', 'stc', 'std', 'sti', 'stosb', 'stosd', 'stosw', 'str',
        'sub', 'svdc', 'svldt', 'svts', 'syscall', 'sysenter', 'sysexit',
        'sysret', 'test', 'ud1', 'ud2', 'umov', 'verr', 'verw', 'wait',
        'wbinvd', 'wrmsr', 'wrshr', 'xadd', 'xbts', 'xchg', 'xlat',
        'xlatb', 'xor'
    ])

    def __init__(self, **options):
        Lexer.__init__(self, **options)
        self.keywords = set()
        if get_bool_opt(options, 'turbopascal', True):
            self.keywords.update(self.TURBO_PASCAL_KEYWORDS)
        if get_bool_opt(options, 'delphi', True):
            self.keywords.update(self.DELPHI_KEYWORDS)
        if get_bool_opt(options, 'freepascal', True):
            self.keywords.update(self.FREE_PASCAL_KEYWORDS)
        self.builtins = set()
        for unit in get_list_opt(options, 'units', list(self.BUILTIN_UNITS)):
            self.builtins.update(self.BUILTIN_UNITS[unit])

    def get_tokens_unprocessed(self, text):
        scanner = Scanner(text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        stack = ['initial']
        in_function_block = False
        in_property_block = False
        was_dot = False
        next_token_is_function = False
        next_token_is_property = False
        collect_labels = False
        block_labels = set()
        brace_balance = [0, 0]

        while not scanner.eos:
            token = Error

            if stack[-1] == 'initial':
                if scanner.scan(r'\s+'):
                    token = Text
                elif scanner.scan(r'\{.*?\}|\(\*.*?\*\)'):
                    if scanner.match.startswith('$'):
                        token = Comment.Preproc
                    else:
                        token = Comment.Multiline
                elif scanner.scan(r'//.*?$'):
                    token = Comment.Single
                elif scanner.scan(r'[-+*\/=<>:;,.@\^]'):
                    token = Operator
                    # stop label highlighting on next ";"
                    if collect_labels and scanner.match == ';':
                        collect_labels = False
                elif scanner.scan(r'[\(\)\[\]]+'):
                    token = Punctuation
                    # abort function naming ``foo = Function(...)``
                    next_token_is_function = False
                    # if we are in a function block we count the open
                    # braces because ootherwise it's impossible to
                    # determine the end of the modifier context
                    if in_function_block or in_property_block:
                        if scanner.match == '(':
                            brace_balance[0] += 1
                        elif scanner.match == ')':
                            brace_balance[0] -= 1
                        elif scanner.match == '[':
                            brace_balance[1] += 1
                        elif scanner.match == ']':
                            brace_balance[1] -= 1
                elif scanner.scan(r'[A-Za-z_][A-Za-z_0-9]*'):
                    lowercase_name = scanner.match.lower()
                    if lowercase_name == 'result':
                        token = Name.Builtin.Pseudo
                    elif lowercase_name in self.keywords:
                        token = Keyword
                        # if we are in a special block and a
                        # block ending keyword occours (and the parenthesis
                        # is balanced) we end the current block context
                        if (in_function_block or in_property_block) and \
                           lowercase_name in self.BLOCK_KEYWORDS and \
                           brace_balance[0] <= 0 and \
                           brace_balance[1] <= 0:
                            in_function_block = False
                            in_property_block = False
                            brace_balance = [0, 0]
                            block_labels = set()
                        if lowercase_name in ('label', 'goto'):
                            collect_labels = True
                        elif lowercase_name == 'asm':
                            stack.append('asm')
                        elif lowercase_name == 'property':
                            in_property_block = True
                            next_token_is_property = True
                        elif lowercase_name in ('procedure', 'operator',
                                                'function', 'constructor',
                                                'destructor'):
                            in_function_block = True
                            next_token_is_function = True
                    # we are in a function block and the current name
                    # is in the set of registered modifiers. highlight
                    # it as pseudo keyword
                    elif in_function_block and \
                         lowercase_name in self.FUNCTION_MODIFIERS:
                        token = Keyword.Pseudo
                    # if we are in a property highlight some more
                    # modifiers
                    elif in_property_block and \
                         lowercase_name in ('read', 'write'):
                        token = Keyword.Pseudo
                        next_token_is_function = True
                    # if the last iteration set next_token_is_function
                    # to true we now want this name highlighted as
                    # function. so do that and reset the state
                    elif next_token_is_function:
                        # Look if the next token is a dot. If yes it's
                        # not a function, but a class name and the
                        # part after the dot a function name
                        if scanner.test(r'\s*\.\s*'):
                            token = Name.Class
                        # it's not a dot, our job is done
                        else:
                            token = Name.Function
                            next_token_is_function = False
                    # same for properties
                    elif next_token_is_property:
                        token = Name.Property
                        next_token_is_property = False
                    # Highlight this token as label and add it
                    # to the list of known labels
                    elif collect_labels:
                        token = Name.Label
                        block_labels.add(scanner.match.lower())
                    # name is in list of known labels
                    elif lowercase_name in block_labels:
                        token = Name.Label
                    elif lowercase_name in self.BUILTIN_TYPES:
                        token = Keyword.Type
                    elif lowercase_name in self.DIRECTIVES:
                        token = Keyword.Pseudo
                    # builtins are just builtins if the token
                    # before isn't a dot
                    elif not was_dot and lowercase_name in self.builtins:
                        token = Name.Builtin
                    else:
                        token = Name
                elif scanner.scan(r"'"):
                    token = String
                    stack.append('string')
                elif scanner.scan(r'\#(\d+|\$[0-9A-Fa-f]+)'):
                    token = String.Char
                elif scanner.scan(r'\$[0-9A-Fa-f]+'):
                    token = Number.Hex
                elif scanner.scan(r'\d+(?![eE]|\.[^.])'):
                    token = Number.Integer
                elif scanner.scan(r'\d+(\.\d+([eE][+-]?\d+)?|[eE][+-]?\d+)'):
                    token = Number.Float
                else:
                    # if the stack depth is deeper than once, pop
                    if len(stack) > 1:
                        stack.pop()
                    scanner.get_char()

            elif stack[-1] == 'string':
                if scanner.scan(r"''"):
                    token = String.Escape
                elif scanner.scan(r"'"):
                    token = String
                    stack.pop()
                elif scanner.scan(r"[^']*"):
                    token = String
                else:
                    scanner.get_char()
                    stack.pop()

            elif stack[-1] == 'asm':
                if scanner.scan(r'\s+'):
                    token = Text
                elif scanner.scan(r'end'):
                    token = Keyword
                    stack.pop()
                elif scanner.scan(r'\{.*?\}|\(\*.*?\*\)'):
                    if scanner.match.startswith('$'):
                        token = Comment.Preproc
                    else:
                        token = Comment.Multiline
                elif scanner.scan(r'//.*?$'):
                    token = Comment.Single
                elif scanner.scan(r"'"):
                    token = String
                    stack.append('string')
                elif scanner.scan(r'@@[A-Za-z_][A-Za-z_0-9]*'):
                    token = Name.Label
                elif scanner.scan(r'[A-Za-z_][A-Za-z_0-9]*'):
                    lowercase_name = scanner.match.lower()
                    if lowercase_name in self.ASM_INSTRUCTIONS:
                        token = Keyword
                    elif lowercase_name in self.ASM_REGISTERS:
                        token = Name.Builtin
                    else:
                        token = Name
                elif scanner.scan(r'[-+*\/=<>:;,.@\^]+'):
                    token = Operator
                elif scanner.scan(r'[\(\)\[\]]+'):
                    token = Punctuation
                elif scanner.scan(r'\$[0-9A-Fa-f]+'):
                    token = Number.Hex
                elif scanner.scan(r'\d+(?![eE]|\.[^.])'):
                    token = Number.Integer
                elif scanner.scan(r'\d+(\.\d+([eE][+-]?\d+)?|[eE][+-]?\d+)'):
                    token = Number.Float
                else:
                    scanner.get_char()
                    stack.pop()

            # save the dot!!!11
            if scanner.match.strip():
                was_dot = scanner.match == '.'
            yield scanner.start_pos, token, scanner.match or ''


class DylanLexer(RegexLexer):
    """
    For the `Dylan <http://www.opendylan.org/>`_ language.

    .. versionadded:: 0.7
    """

    name = 'Dylan'
    aliases = ['dylan']
    filenames = ['*.dylan', '*.dyl', '*.intr']
    mimetypes = ['text/x-dylan']

    flags = re.IGNORECASE

    builtins = set([
        'subclass', 'abstract', 'block', 'concrete', 'constant', 'class',
        'compiler-open', 'compiler-sideways', 'domain', 'dynamic',
        'each-subclass', 'exception', 'exclude', 'function', 'generic',
        'handler', 'inherited', 'inline', 'inline-only', 'instance',
        'interface', 'import', 'keyword', 'library', 'macro', 'method',
        'module', 'open', 'primary', 'required', 'sealed', 'sideways',
        'singleton', 'slot', 'thread', 'variable', 'virtual'])

    keywords = set([
        'above', 'afterwards', 'begin', 'below', 'by', 'case', 'cleanup',
        'create', 'define', 'else', 'elseif', 'end', 'export', 'finally',
        'for', 'from', 'if', 'in', 'let', 'local', 'otherwise', 'rename',
        'select', 'signal', 'then', 'to', 'unless', 'until', 'use', 'when',
        'while'])

    operators = set([
        '~', '+', '-', '*', '|', '^', '=', '==', '~=', '~==', '<', '<=',
        '>', '>=', '&', '|'])

    functions = set([
        'abort', 'abs', 'add', 'add!', 'add-method', 'add-new', 'add-new!',
        'all-superclasses', 'always', 'any?', 'applicable-method?', 'apply',
        'aref', 'aref-setter', 'as', 'as-lowercase', 'as-lowercase!',
        'as-uppercase', 'as-uppercase!', 'ash', 'backward-iteration-protocol',
        'break', 'ceiling', 'ceiling/', 'cerror', 'check-type', 'choose',
        'choose-by', 'complement', 'compose', 'concatenate', 'concatenate-as',
        'condition-format-arguments', 'condition-format-string', 'conjoin',
        'copy-sequence', 'curry', 'default-handler', 'dimension', 'dimensions',
        'direct-subclasses', 'direct-superclasses', 'disjoin', 'do',
        'do-handlers', 'element', 'element-setter', 'empty?', 'error', 'even?',
        'every?', 'false-or', 'fill!', 'find-key', 'find-method', 'first',
        'first-setter', 'floor', 'floor/', 'forward-iteration-protocol',
        'function-arguments', 'function-return-values',
        'function-specializers', 'gcd', 'generic-function-mandatory-keywords',
        'generic-function-methods', 'head', 'head-setter', 'identity',
        'initialize', 'instance?', 'integral?', 'intersection',
        'key-sequence', 'key-test', 'last', 'last-setter', 'lcm', 'limited',
        'list', 'logand', 'logbit?', 'logior', 'lognot', 'logxor', 'make',
        'map', 'map-as', 'map-into', 'max', 'member?', 'merge-hash-codes',
        'min', 'modulo', 'negative', 'negative?', 'next-method',
        'object-class', 'object-hash', 'odd?', 'one-of', 'pair', 'pop',
        'pop-last', 'positive?', 'push', 'push-last', 'range', 'rank',
        'rcurry', 'reduce', 'reduce1', 'remainder', 'remove', 'remove!',
        'remove-duplicates', 'remove-duplicates!', 'remove-key!',
        'remove-method', 'replace-elements!', 'replace-subsequence!',
        'restart-query', 'return-allowed?', 'return-description',
        'return-query', 'reverse', 'reverse!', 'round', 'round/',
        'row-major-index', 'second', 'second-setter', 'shallow-copy',
        'signal', 'singleton', 'size', 'size-setter', 'slot-initialized?',
        'sort', 'sort!', 'sorted-applicable-methods', 'subsequence-position',
        'subtype?', 'table-protocol', 'tail', 'tail-setter', 'third',
        'third-setter', 'truncate', 'truncate/', 'type-error-expected-type',
        'type-error-value', 'type-for-copy', 'type-union', 'union', 'values',
        'vector', 'zero?'])

    valid_name = '\\\\?[a-z0-9' + re.escape('!&*<>|^$%@_-+~?/=') + ']+'

    def get_tokens_unprocessed(self, text):
        for index, token, value in RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name:
                lowercase_value = value.lower()
                if lowercase_value in self.builtins:
                    yield index, Name.Builtin, value
                    continue
                if lowercase_value in self.keywords:
                    yield index, Keyword, value
                    continue
                if lowercase_value in self.functions:
                    yield index, Name.Builtin, value
                    continue
                if lowercase_value in self.operators:
                    yield index, Operator, value
                    continue
            yield index, token, value

    tokens = {
        'root': [
            # Whitespace
            (r'\s+', Text),

            # single line comment
            (r'//.*?\n', Comment.Single),

            # lid header
            (r'([a-z0-9-]+)(:)([ \t]*)(.*(?:\n[ \t].+)*)',
                bygroups(Name.Attribute, Operator, Text, String)),

            ('', Text, 'code') # no header match, switch to code
        ],
        'code': [
            # Whitespace
            (r'\s+', Text),

            # single line comment
            (r'//.*?\n', Comment.Single),

            # multi-line comment
            (r'/\*', Comment.Multiline, 'comment'),

            # strings and characters
            (r'"', String, 'string'),
            (r"'(\\.|\\[0-7]{1,3}|\\x[a-f0-9]{1,2}|[^\\\'\n])'", String.Char),

            # binary integer
            (r'#[bB][01]+', Number.Bin),

            # octal integer
            (r'#[oO][0-7]+', Number.Oct),

            # floating point
            (r'[-+]?(\d*\.\d+(e[-+]?\d+)?|\d+(\.\d*)?e[-+]?\d+)', Number.Float),

            # decimal integer
            (r'[-+]?\d+', Number.Integer),

            # hex integer
            (r'#[xX][0-9a-f]+', Number.Hex),

            # Macro parameters
            (r'(\?' + valid_name + ')(:)'
             r'(token|name|variable|expression|body|case-body|\*)',
                bygroups(Name.Tag, Operator, Name.Builtin)),
            (r'(\?)(:)(token|name|variable|expression|body|case-body|\*)',
                bygroups(Name.Tag, Operator, Name.Builtin)),
            (r'\?' + valid_name, Name.Tag),

            # Punctuation
            (r'(=>|::|#\(|#\[|##|\?|\?\?|\?=|[(){}\[\],\.;])', Punctuation),

            # Most operators are picked up as names and then re-flagged.
            # This one isn't valid in a name though, so we pick it up now.
            (r':=', Operator),

            # Pick up #t / #f before we match other stuff with #.
            (r'#[tf]', Literal),

            # #"foo" style keywords
            (r'#"', String.Symbol, 'keyword'),

            # #rest, #key, #all-keys, etc.
            (r'#[a-z0-9-]+', Keyword),

            # required-init-keyword: style keywords.
            (valid_name + ':', Keyword),

            # class names
            (r'<' + valid_name + '>', Name.Class),

            # define variable forms.
            (r'\*' + valid_name + '\*', Name.Variable.Global),

            # define constant forms.
            (r'\$' + valid_name, Name.Constant),

            # everything else. We re-flag some of these in the method above.
            (valid_name, Name),
        ],
        'comment': [
            (r'[^*/]', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline)
        ],
        'keyword': [
            (r'"', String.Symbol, '#pop'),
            (r'[^\\"]+', String.Symbol), # all other characters
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-f0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # stray backslash
        ]
    }


class DylanLidLexer(RegexLexer):
    """
    For Dylan LID (Library Interchange Definition) files.

    .. versionadded:: 1.6
    """

    name = 'DylanLID'
    aliases = ['dylan-lid', 'lid']
    filenames = ['*.lid', '*.hdp']
    mimetypes = ['text/x-dylan-lid']

    flags = re.IGNORECASE

    tokens = {
        'root': [
            # Whitespace
            (r'\s+', Text),

            # single line comment
            (r'//.*?\n', Comment.Single),

            # lid header
            (r'(.*?)(:)([ \t]*)(.*(?:\n[ \t].+)*)',
             bygroups(Name.Attribute, Operator, Text, String)),
        ]
    }


class DylanConsoleLexer(Lexer):
    """
    For Dylan interactive console output like:

    .. sourcecode:: dylan-console

        ? let a = 1;
        => 1
        ? a
        => 1

    This is based on a copy of the RubyConsoleLexer.

    .. versionadded:: 1.6
    """
    name = 'Dylan session'
    aliases = ['dylan-console', 'dylan-repl']
    filenames = ['*.dylan-console']
    mimetypes = ['text/x-dylan-console']

    _line_re  = re.compile('.*?\n')
    _prompt_re = re.compile('\?| ')

    def get_tokens_unprocessed(self, text):
        dylexer = DylanLexer(**self.options)

        curcode = ''
        insertions = []
        for match in self._line_re.finditer(text):
            line = match.group()
            m = self._prompt_re.match(line)
            if m is not None:
                end = m.end()
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, line[:end])]))
                curcode += line[end:]
            else:
                if curcode:
                    for item in do_insertions(insertions,
                                    dylexer.get_tokens_unprocessed(curcode)):
                        yield item
                    curcode = ''
                    insertions = []
                yield match.start(), Generic.Output, line
        if curcode:
            for item in do_insertions(insertions,
                                      dylexer.get_tokens_unprocessed(curcode)):
                yield item


def objective(baselexer):
    """
    Generate a subclass of baselexer that accepts the Objective-C syntax
    extensions.
    """

    # Have to be careful not to accidentally match JavaDoc/Doxygen syntax here,
    # since that's quite common in ordinary C/C++ files.  It's OK to match
    # JavaDoc/Doxygen keywords that only apply to Objective-C, mind.
    #
    # The upshot of this is that we CANNOT match @class or @interface
    _oc_keywords = re.compile(r'@(?:end|implementation|protocol)')

    # Matches [ <ws>? identifier <ws> ( identifier <ws>? ] |  identifier? : )
    # (note the identifier is *optional* when there is a ':'!)
    _oc_message = re.compile(r'\[\s*[a-zA-Z_]\w*\s+'
                             r'(?:[a-zA-Z_]\w*\s*\]|'
                             r'(?:[a-zA-Z_]\w*)?:)')

    class GeneratedObjectiveCVariant(baselexer):
        """
        Implements Objective-C syntax on top of an existing C family lexer.
        """

        tokens = {
            'statements': [
                (r'@"', String, 'string'),
                (r'@(YES|NO)', Number),
                (r"@'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
                (r'@(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
                (r'@(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
                (r'@0x[0-9a-fA-F]+[Ll]?', Number.Hex),
                (r'@0[0-7]+[Ll]?', Number.Oct),
                (r'@\d+[Ll]?', Number.Integer),
                (r'@\(', Literal, 'literal_number'),
                (r'@\[', Literal, 'literal_array'),
                (r'@\{', Literal, 'literal_dictionary'),
                (r'(@selector|@private|@protected|@public|@encode|'
                 r'@synchronized|@try|@throw|@catch|@finally|@end|@property|@synthesize|'
                 r'__bridge|__bridge_transfer|__autoreleasing|__block|__weak|__strong|'
                 r'weak|strong|copy|retain|assign|unsafe_unretained|atomic|nonatomic|'
                 r'readonly|readwrite|setter|getter|typeof|in|out|inout|release|class|'
                 r'@dynamic|@optional|@required|@autoreleasepool)\b', Keyword),
                (r'(id|instancetype|Class|IMP|SEL|BOOL|IBOutlet|IBAction|unichar)\b',
                 Keyword.Type),
                (r'@(true|false|YES|NO)\n', Name.Builtin),
                (r'(YES|NO|nil|self|super)\b', Name.Builtin),
                # Carbon types
                (r'(Boolean|UInt8|SInt8|UInt16|SInt16|UInt32|SInt32)\b', Keyword.Type),
                # Carbon built-ins
                (r'(TRUE|FALSE)\b', Name.Builtin),
                (r'(@interface|@implementation)(\s+)', bygroups(Keyword, Text),
                 ('#pop', 'oc_classname')),
                (r'(@class|@protocol)(\s+)', bygroups(Keyword, Text),
                 ('#pop', 'oc_forward_classname')),
                # @ can also prefix other expressions like @{...} or @(...)
                (r'@', Punctuation),
                inherit,
            ],
            'oc_classname' : [
                # interface definition that inherits
                ('([a-zA-Z$_][\w$]*)(\s*:\s*)([a-zA-Z$_][\w$]*)?(\s*)({)',
                 bygroups(Name.Class, Text, Name.Class, Text, Punctuation),
                 ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)(\s*:\s*)([a-zA-Z$_][\w$]*)?',
                 bygroups(Name.Class, Text, Name.Class), '#pop'),
                # interface definition for a category
                ('([a-zA-Z$_][\w$]*)(\s*)(\([a-zA-Z$_][\w$]*\))(\s*)({)',
                 bygroups(Name.Class, Text, Name.Label, Text, Punctuation),
                 ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)(\s*)(\([a-zA-Z$_][\w$]*\))',
                 bygroups(Name.Class, Text, Name.Label), '#pop'),
                # simple interface / implementation
                ('([a-zA-Z$_][\w$]*)(\s*)({)',
                 bygroups(Name.Class, Text, Punctuation), ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)', Name.Class, '#pop')
            ],
            'oc_forward_classname' : [
              ('([a-zA-Z$_][\w$]*)(\s*,\s*)',
               bygroups(Name.Class, Text), 'oc_forward_classname'),
              ('([a-zA-Z$_][\w$]*)(\s*;?)',
               bygroups(Name.Class, Text), '#pop')
            ],
            'oc_ivars' : [
              include('whitespace'),
              include('statements'),
              (';', Punctuation),
              ('{', Punctuation, '#push'),
              ('}', Punctuation, '#pop'),
            ],
            'root': [
              # methods
              (r'^([-+])(\s*)'                         # method marker
               r'(\(.*?\))?(\s*)'                      # return type
               r'([a-zA-Z$_][\w$]*:?)',        # begin of method name
               bygroups(Punctuation, Text, using(this),
                        Text, Name.Function),
               'method'),
              inherit,
            ],
            'method': [
                include('whitespace'),
                # TODO unsure if ellipses are allowed elsewhere, see
                # discussion in Issue 789
                (r',', Punctuation),
                (r'\.\.\.', Punctuation),
                (r'(\(.*?\))(\s*)([a-zA-Z$_][\w$]*)',
                 bygroups(using(this), Text, Name.Variable)),
                (r'[a-zA-Z$_][\w$]*:', Name.Function),
                (';', Punctuation, '#pop'),
                ('{', Punctuation, 'function'),
                ('', Text, '#pop'),
            ],
            'literal_number': [
                (r'\(', Punctuation, 'literal_number_inner'),
                (r'\)', Literal, '#pop'),
                include('statement'),
            ],
            'literal_number_inner': [
                (r'\(', Punctuation, '#push'),
                (r'\)', Punctuation, '#pop'),
                include('statement'),
            ],
            'literal_array': [
                (r'\[', Punctuation, 'literal_array_inner'),
                (r'\]', Literal, '#pop'),
                include('statement'),
            ],
            'literal_array_inner': [
                (r'\[', Punctuation, '#push'),
                (r'\]', Punctuation, '#pop'),
                include('statement'),
            ],
            'literal_dictionary': [
                (r'\}', Literal, '#pop'),
                include('statement'),
            ],
        }

        def analyse_text(text):
            if _oc_keywords.search(text):
                return 1.0
            elif '@"' in text: # strings
                return 0.8
            elif re.search('@[0-9]+', text):
                return 0.7
            elif _oc_message.search(text):
                return 0.8
            return 0

        def get_tokens_unprocessed(self, text):
            from ..lexers._cocoabuiltins import COCOA_INTERFACES, \
                COCOA_PROTOCOLS, COCOA_PRIMITIVES

            for index, token, value in \
                baselexer.get_tokens_unprocessed(self, text):
                if token is Name or token is Name.Class:
                    if value in COCOA_INTERFACES or value in COCOA_PROTOCOLS \
                       or value in COCOA_PRIMITIVES:
                        token = Name.Builtin.Pseudo

                yield index, token, value

    return GeneratedObjectiveCVariant


class ObjectiveCLexer(objective(CLexer)):
    """
    For Objective-C source code with preprocessor directives.
    """

    name = 'Objective-C'
    aliases = ['objective-c', 'objectivec', 'obj-c', 'objc']
    filenames = ['*.m', '*.h']
    mimetypes = ['text/x-objective-c']
    priority = 0.05    # Lower than C


class ObjectiveCppLexer(objective(CppLexer)):
    """
    For Objective-C++ source code with preprocessor directives.
    """

    name = 'Objective-C++'
    aliases = ['objective-c++', 'objectivec++', 'obj-c++', 'objc++']
    filenames = ['*.mm', '*.hh']
    mimetypes = ['text/x-objective-c++']
    priority = 0.05    # Lower than C++


class FortranLexer(RegexLexer):
    """
    Lexer for FORTRAN 90 code.

    .. versionadded:: 0.10
    """
    name = 'Fortran'
    aliases = ['fortran']
    filenames = ['*.f', '*.f90', '*.F', '*.F90']
    mimetypes = ['text/x-fortran']
    flags = re.IGNORECASE

    # Data Types: INTEGER, REAL, COMPLEX, LOGICAL, CHARACTER and DOUBLE PRECISION
    # Operators: **, *, +, -, /, <, >, <=, >=, ==, /=
    # Logical (?): NOT, AND, OR, EQV, NEQV

    # Builtins:
    # http://gcc.gnu.org/onlinedocs/gcc-3.4.6/g77/Table-of-Intrinsic-Functions.html

    tokens = {
        'root': [
            (r'!.*\n', Comment),
            include('strings'),
            include('core'),
            (r'[a-z]\w*', Name.Variable),
            include('nums'),
            (r'[\s]+', Text),
        ],
        'core': [
            # Statements
            (r'\b(ABSTRACT|ACCEPT|ALLOCATABLE|ALLOCATE|ARRAY|ASSIGN|ASYNCHRONOUS|'
             r'BACKSPACE|BIND|BLOCK( DATA)?|BYTE|CALL|CASE|CLASS|CLOSE|COMMON|CONTAINS|'
             r'CONTINUE|CYCLE|DATA|DEALLOCATE|DECODE|DEFERRED|DIMENSION|DO|'
             r'ELEMENTAL|ELSE|ENCODE|END( FILE)?|ENDIF|ENTRY|ENUMERATOR|EQUIVALENCE|'
             r'EXIT|EXTERNAL|EXTRINSIC|FINAL|FORALL|FORMAT|FUNCTION|GENERIC|'
             r'GOTO|IF|IMPLICIT|IMPORT|INCLUDE|INQUIRE|INTENT|INTERFACE|'
             r'INTRINSIC|MODULE|NAMELIST|NULLIFY|NONE|NON_INTRINSIC|'
             r'NON_OVERRIDABLE|NOPASS|OPEN|OPTIONAL|OPTIONS|PARAMETER|PASS|'
             r'PAUSE|POINTER|PRINT|PRIVATE|PROGRAM|PROTECTED|PUBLIC|PURE|READ|'
             r'RECURSIVE|RESULT|RETURN|REWIND|SAVE|SELECT|SEQUENCE|STOP|SUBROUTINE|'
             r'TARGET|THEN|TYPE|USE|VALUE|VOLATILE|WHERE|WRITE|WHILE)\s*\b',
             Keyword),

            # Data Types
            (r'\b(CHARACTER|COMPLEX|DOUBLE PRECISION|DOUBLE COMPLEX|INTEGER|'
             r'LOGICAL|REAL|C_INT|C_SHORT|C_LONG|C_LONG_LONG|C_SIGNED_CHAR|'
             r'C_SIZE_T|C_INT8_T|C_INT16_T|C_INT32_T|C_INT64_T|C_INT_LEAST8_T|'
             r'C_INT_LEAST16_T|C_INT_LEAST32_T|C_INT_LEAST64_T|C_INT_FAST8_T|'
             r'C_INT_FAST16_T|C_INT_FAST32_T|C_INT_FAST64_T|C_INTMAX_T|'
             r'C_INTPTR_T|C_FLOAT|C_DOUBLE|C_LONG_DOUBLE|C_FLOAT_COMPLEX|'
             r'C_DOUBLE_COMPLEX|C_LONG_DOUBLE_COMPLEX|C_BOOL|C_CHAR|C_PTR|'
             r'C_FUNPTR)\s*\b',
             Keyword.Type),

            # Operators
            (r'(\*\*|\*|\+|-|\/|<|>|<=|>=|==|\/=|=)', Operator),

            (r'(::)', Keyword.Declaration),

            (r'[()\[\],:&%;]', Punctuation),

            # Intrinsics
            (r'\b(Abort|Abs|Access|AChar|ACos|AdjustL|AdjustR|AImag|AInt|Alarm|'
             r'All|Allocated|ALog|AMax|AMin|AMod|And|ANInt|Any|ASin|Associated|'
             r'ATan|BesJ|BesJN|BesY|BesYN|Bit_Size|BTest|CAbs|CCos|Ceiling|'
             r'CExp|Char|ChDir|ChMod|CLog|Cmplx|Command_Argument_Count|Complex|'
             r'Conjg|Cos|CosH|Count|CPU_Time|CShift|CSin|CSqRt|CTime|C_Funloc|'
             r'C_Loc|C_Associated|C_Null_Ptr|C_Null_Funptr|C_F_Pointer|'
             r'C_Null_Char|C_Alert|C_Backspace|C_Form_Feed|C_New_Line|'
             r'C_Carriage_Return|C_Horizontal_Tab|C_Vertical_Tab|'
             r'DAbs|DACos|DASin|DATan|Date_and_Time|DbesJ|'
             r'DbesJ|DbesJN|DbesY|DbesY|DbesYN|Dble|DCos|DCosH|DDiM|DErF|DErFC|'
             r'DExp|Digits|DiM|DInt|DLog|DLog|DMax|DMin|DMod|DNInt|Dot_Product|'
             r'DProd|DSign|DSinH|DSin|DSqRt|DTanH|DTan|DTime|EOShift|Epsilon|'
             r'ErF|ErFC|ETime|Exit|Exp|Exponent|Extends_Type_Of|FDate|FGet|'
             r'FGetC|Float|Floor|Flush|FNum|FPutC|FPut|Fraction|FSeek|FStat|'
             r'FTell|GError|GetArg|Get_Command|Get_Command_Argument|'
             r'Get_Environment_Variable|GetCWD|GetEnv|GetGId|GetLog|GetPId|'
             r'GetUId|GMTime|HostNm|Huge|IAbs|IAChar|IAnd|IArgC|IBClr|IBits|'
             r'IBSet|IChar|IDate|IDiM|IDInt|IDNInt|IEOr|IErrNo|IFix|Imag|'
             r'ImagPart|Index|Int|IOr|IRand|IsaTty|IShft|IShftC|ISign|'
             r'Iso_C_Binding|Is_Iostat_End|Is_Iostat_Eor|ITime|Kill|Kind|'
             r'LBound|Len|Len_Trim|LGe|LGt|Link|LLe|LLt|LnBlnk|Loc|Log|'
             r'Logical|Long|LShift|LStat|LTime|MatMul|Max|MaxExponent|MaxLoc|'
             r'MaxVal|MClock|Merge|Move_Alloc|Min|MinExponent|MinLoc|MinVal|'
             r'Mod|Modulo|MvBits|Nearest|New_Line|NInt|Not|Or|Pack|PError|'
             r'Precision|Present|Product|Radix|Rand|Random_Number|Random_Seed|'
             r'Range|Real|RealPart|Rename|Repeat|Reshape|RRSpacing|RShift|'
             r'Same_Type_As|Scale|Scan|Second|Selected_Int_Kind|'
             r'Selected_Real_Kind|Set_Exponent|Shape|Short|Sign|Signal|SinH|'
             r'Sin|Sleep|Sngl|Spacing|Spread|SqRt|SRand|Stat|Sum|SymLnk|'
             r'System|System_Clock|Tan|TanH|Time|Tiny|Transfer|Transpose|Trim|'
             r'TtyNam|UBound|UMask|Unlink|Unpack|Verify|XOr|ZAbs|ZCos|ZExp|'
             r'ZLog|ZSin|ZSqRt)\s*\b',
             Name.Builtin),

            # Booleans
            (r'\.(true|false)\.', Name.Builtin),
            # Comparing Operators
            (r'\.(eq|ne|lt|le|gt|ge|not|and|or|eqv|neqv)\.', Operator.Word),
        ],

        'strings': [
            (r'(?s)"(\\\\|\\[0-7]+|\\.|[^"\\])*"', String.Double),
            (r"(?s)'(\\\\|\\[0-7]+|\\.|[^'\\])*'", String.Single),
        ],

        'nums': [
            (r'\d+(?![.e])(_[a-z]\w+)?', Number.Integer),
            (r'[+-]?\d*\.\d+(e[-+]?\d+)?(_[a-z]\w+)?', Number.Float),
            (r'[+-]?\d+\.\d*(e[-+]?\d+)?(_[a-z]\w+)?', Number.Float),
        ],
    }


class GLShaderLexer(RegexLexer):
    """
    GLSL (OpenGL Shader) lexer.

    .. versionadded:: 1.1
    """
    name = 'GLSL'
    aliases = ['glsl']
    filenames = ['*.vert', '*.frag', '*.geo']
    mimetypes = ['text/x-glslsrc']

    tokens = {
        'root': [
            (r'^#.*', Comment.Preproc),
            (r'//.*', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'\+|-|~|!=?|\*|/|%|<<|>>|<=?|>=?|==?|&&?|\^|\|\|?',
             Operator),
            (r'[?:]', Operator), # quick hack for ternary
            (r'\bdefined\b', Operator),
            (r'[;{}(),\[\]]', Punctuation),
            #FIXME when e is present, no decimal point needed
            (r'[+-]?\d*\.\d+([eE][-+]?\d+)?', Number.Float),
            (r'[+-]?\d+\.\d*([eE][-+]?\d+)?', Number.Float),
            (r'0[xX][0-9a-fA-F]*', Number.Hex),
            (r'0[0-7]*', Number.Oct),
            (r'[1-9][0-9]*', Number.Integer),
            (r'\b(attribute|const|uniform|varying|centroid|break|continue|'
             r'do|for|while|if|else|in|out|inout|float|int|void|bool|true|'
             r'false|invariant|discard|return|mat[234]|mat[234]x[234]|'
             r'vec[234]|[ib]vec[234]|sampler[123]D|samplerCube|'
             r'sampler[12]DShadow|struct)\b', Keyword),
            (r'\b(asm|class|union|enum|typedef|template|this|packed|goto|'
             r'switch|default|inline|noinline|volatile|public|static|extern|'
             r'external|interface|long|short|double|half|fixed|unsigned|'
             r'lowp|mediump|highp|precision|input|output|hvec[234]|'
             r'[df]vec[234]|sampler[23]DRect|sampler2DRectShadow|sizeof|'
             r'cast|namespace|using)\b', Keyword), #future use
            (r'[a-zA-Z_][a-zA-Z_0-9]*', Name),
            (r'\.', Punctuation),
            (r'\s+', Text),
        ],
    }


class PrologLexer(RegexLexer):
    """
    Lexer for Prolog files.
    """
    name = 'Prolog'
    aliases = ['prolog']
    filenames = ['*.prolog', '*.pro', '*.pl']
    mimetypes = ['text/x-prolog']

    flags = re.UNICODE

    tokens = {
        'root': [
            (r'^#.*', Comment.Single),
            (r'/\*', Comment.Multiline, 'nested-comment'),
            (r'%.*', Comment.Single),
            # character literal
            (r'0\'.', String.Char),
            (r'0b[01]+', Number.Bin),
            (r'0o[0-7]+', Number.Oct),
            (r'0x[0-9a-fA-F]+', Number.Hex),
            # literal with prepended base
            (r'\d\d?\'[a-zA-Z0-9]+', Number.Integer),
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'\d+', Number.Integer),
            (r'[\[\](){}|.,;!]', Punctuation),
            (r':-|-->', Punctuation),
            (r'"(?:\\x[0-9a-fA-F]+\\|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|'
             r'\\[0-7]+\\|\\["\nabcefnrstv]|[^\\"])*"', String.Double),
            (r"'(?:''|[^'])*'", String.Atom), # quoted atom
            # Needs to not be followed by an atom.
            #(r'=(?=\s|[a-zA-Z\[])', Operator),
            (r'is\b', Operator),
            (r'(<|>|=<|>=|==|=:=|=|/|//|\*|\+|-)(?=\s|[a-zA-Z0-9\[])',
             Operator),
            (r'(mod|div|not)\b', Operator),
            (r'_', Keyword), # The don't-care variable
            (r'([a-z]+)(:)', bygroups(Name.Namespace, Punctuation)),
            (u'([a-z\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]'
             u'[\w$\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]*)'
             u'(\\s*)(:-|-->)',
             bygroups(Name.Function, Text, Operator)), # function defn
            (u'([a-z\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]'
             u'[\w$\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]*)'
             u'(\\s*)(\\()',
             bygroups(Name.Function, Text, Punctuation)),
            (u'[a-z\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]'
             u'[\w$\u00c0-\u1fff\u3040-\ud7ff\ue000-\uffef]*',
             String.Atom), # atom, characters
            # This one includes !
            (u'[#&*+\\-./:<=>?@\\\\^~\u00a1-\u00bf\u2010-\u303f]+',
             String.Atom), # atom, graphics
            (r'[A-Z_]\w*', Name.Variable),
            (u'\\s+|[\u2000-\u200f\ufff0-\ufffe\uffef]', Text),
        ],
        'nested-comment': [
            (r'\*/', Comment.Multiline, '#pop'),
            (r'/\*', Comment.Multiline, '#push'),
            (r'[^*/]+', Comment.Multiline),
            (r'[*/]', Comment.Multiline),
        ],
    }

    def analyse_text(text):
        return ':-' in text


class CythonLexer(RegexLexer):
    """
    For Pyrex and `Cython <http://cython.org>`_ source code.

    .. versionadded:: 1.1
    """

    name = 'Cython'
    aliases = ['cython', 'pyx', 'pyrex']
    filenames = ['*.pyx', '*.pxd', '*.pxi']
    mimetypes = ['text/x-cython', 'application/x-cython']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)("""(?:.|\n)*?""")', bygroups(Text, String.Doc)),
            (r"^(\s*)('''(?:.|\n)*?''')", bygroups(Text, String.Doc)),
            (r'[^\S\n]+', Text),
            (r'#.*$', Comment),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'(in|is|and|or|not)\b', Operator.Word),
            (r'(<)([a-zA-Z0-9.?]+)(>)',
             bygroups(Punctuation, Keyword.Type, Punctuation)),
            (r'!=|==|<<|>>|[-~+/*%=<>&^|.?]', Operator),
            (r'(from)(\d+)(<=)(\s+)(<)(\d+)(:)',
             bygroups(Keyword, Number.Integer, Operator, Name, Operator,
                      Name, Punctuation)),
            include('keywords'),
            (r'(def|property)(\s+)', bygroups(Keyword, Text), 'funcname'),
            (r'(cp?def)(\s+)', bygroups(Keyword, Text), 'cdef'),
            (r'(class|struct)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)(\s+)', bygroups(Keyword, Text), 'fromimport'),
            (r'(c?import)(\s+)', bygroups(Keyword, Text), 'import'),
            include('builtins'),
            include('backtick'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"""', String, 'tdqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'''", String, 'tsqs'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"', String, 'dqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'", String, 'sqs'),
            ('[uU]?"""', String, combined('stringescape', 'tdqs')),
            ("[uU]?'''", String, combined('stringescape', 'tsqs')),
            ('[uU]?"', String, combined('stringescape', 'dqs')),
            ("[uU]?'", String, combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (r'(assert|break|by|continue|ctypedef|del|elif|else|except\??|exec|'
             r'finally|for|gil|global|if|include|lambda|nogil|pass|print|raise|'
             r'return|try|while|yield|as|with)\b', Keyword),
            (r'(DEF|IF|ELIF|ELSE)\b', Comment.Preproc),
        ],
        'builtins': [
            (r'(?<!\.)(__import__|abs|all|any|apply|basestring|bin|bool|buffer|'
             r'bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|'
             r'complex|delattr|dict|dir|divmod|enumerate|eval|execfile|exit|'
             r'file|filter|float|frozenset|getattr|globals|hasattr|hash|hex|id|'
             r'input|int|intern|isinstance|issubclass|iter|len|list|locals|'
             r'long|map|max|min|next|object|oct|open|ord|pow|property|range|'
             r'raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|'
             r'sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|'
             r'vars|xrange|zip)\b', Name.Builtin),
            (r'(?<!\.)(self|None|Ellipsis|NotImplemented|False|True|NULL'
             r')\b', Name.Builtin.Pseudo),
            (r'(?<!\.)(ArithmeticError|AssertionError|AttributeError|'
             r'BaseException|DeprecationWarning|EOFError|EnvironmentError|'
             r'Exception|FloatingPointError|FutureWarning|GeneratorExit|IOError|'
             r'ImportError|ImportWarning|IndentationError|IndexError|KeyError|'
             r'KeyboardInterrupt|LookupError|MemoryError|NameError|'
             r'NotImplemented|NotImplementedError|OSError|OverflowError|'
             r'OverflowWarning|PendingDeprecationWarning|ReferenceError|'
             r'RuntimeError|RuntimeWarning|StandardError|StopIteration|'
             r'SyntaxError|SyntaxWarning|SystemError|SystemExit|TabError|'
             r'TypeError|UnboundLocalError|UnicodeDecodeError|'
             r'UnicodeEncodeError|UnicodeError|UnicodeTranslateError|'
             r'UnicodeWarning|UserWarning|ValueError|Warning|ZeroDivisionError'
             r')\b', Name.Exception),
        ],
        'numbers': [
            (r'(\d+\.?\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'0\d+', Number.Oct),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+', Number.Integer)
        ],
        'backtick': [
            ('`.*?`', String.Backtick),
        ],
        'name': [
            (r'@\w+', Name.Decorator),
            ('[a-zA-Z_]\w*', Name),
        ],
        'funcname': [
            ('[a-zA-Z_]\w*', Name.Function, '#pop')
        ],
        'cdef': [
            (r'(public|readonly|extern|api|inline)\b', Keyword.Reserved),
            (r'(struct|enum|union|class)\b', Keyword),
            (r'([a-zA-Z_]\w*)(\s*)(?=[(:#=]|$)',
             bygroups(Name.Function, Text), '#pop'),
            (r'([a-zA-Z_]\w*)(\s*)(,)',
             bygroups(Name.Function, Text, Punctuation)),
            (r'from\b', Keyword, '#pop'),
            (r'as\b', Keyword),
            (r':', Punctuation, '#pop'),
            (r'(?=["\'])', Text, '#pop'),
            (r'[a-zA-Z_]\w*', Keyword.Type),
            (r'.', Text),
        ],
        'classname': [
            ('[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'[a-zA-Z_][\w.]*', Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop') # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(c?import)\b', bygroups(Text, Keyword), '#pop'),
            (r'[a-zA-Z_.][\w.]*', Name.Namespace),
            # ``cdef foo from "header"``, or ``for foo from 0 < i < 10``
            default('#pop'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N{.*?}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings': [
            (r'%(\([a-zA-Z0-9]+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[diouxXeEfFgGcrs%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String)
            # newlines are an error (use "nl" state)
        ],
        'nl': [
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape), # included here again for raw strings
            include('strings')
        ],
        'sqs': [
            (r"'", String, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape), # included here again for raw strings
            include('strings')
        ],
        'tdqs': [
            (r'"""', String, '#pop'),
            include('strings'),
            include('nl')
        ],
        'tsqs': [
            (r"'''", String, '#pop'),
            include('strings'),
            include('nl')
        ],
    }


class ValaLexer(RegexLexer):
    """
    For Vala source code with preprocessor directives.

    .. versionadded:: 1.1
    """
    name = 'Vala'
    aliases = ['vala', 'vapi']
    filenames = ['*.vala', '*.vapi']
    mimetypes = ['text/x-vala']

    tokens = {
        'whitespace': [
            (r'^\s*#if\s+0', Comment.Preproc, 'if0'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text), # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
        ],
        'statements': [
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'",
             String.Char),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[Ll]?', Number.Hex),
            (r'0[0-7]+[Ll]?', Number.Oct),
            (r'\d+[Ll]?', Number.Integer),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'(\[)(Compact|Immutable|(?:Boolean|Simple)Type)(\])',
             bygroups(Punctuation, Name.Decorator, Punctuation)),
            # TODO: "correctly" parse complex code attributes
            (r'(\[)(CCode|(?:Integer|Floating)Type)',
             bygroups(Punctuation, Name.Decorator)),
            (r'[()\[\],.]', Punctuation),
            (r'(as|base|break|case|catch|construct|continue|default|delete|do|'
             r'else|enum|finally|for|foreach|get|if|in|is|lock|new|out|params|'
             r'return|set|sizeof|switch|this|throw|try|typeof|while|yield)\b',
             Keyword),
            (r'(abstract|const|delegate|dynamic|ensures|extern|inline|internal|'
             r'override|owned|private|protected|public|ref|requires|signal|'
             r'static|throws|unowned|var|virtual|volatile|weak|yields)\b',
             Keyword.Declaration),
            (r'(namespace|using)(\s+)', bygroups(Keyword.Namespace, Text),
             'namespace'),
            (r'(class|errordomain|interface|struct)(\s+)',
             bygroups(Keyword.Declaration, Text), 'class'),
            (r'(\.)([a-zA-Z_]\w*)',
             bygroups(Operator, Name.Attribute)),
            # void is an actual keyword, others are in glib-2.0.vapi
            (r'(void|bool|char|double|float|int|int8|int16|int32|int64|long|'
             r'short|size_t|ssize_t|string|time_t|uchar|uint|uint8|uint16|'
             r'uint32|uint64|ulong|unichar|ushort)\b', Keyword.Type),
            (r'(true|false|null)\b', Name.Builtin),
            ('[a-zA-Z_]\w*', Name),
        ],
        'root': [
            include('whitespace'),
            ('', Text, 'statement'),
        ],
        'statement' : [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String), # all other characters
            (r'\\\n', String), # line continuation
            (r'\\', String), # stray backslash
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment.Preproc, '#push'),
            (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
            (r'.*?\n', Comment),
        ],
        'class': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'namespace': [
            (r'[a-zA-Z_][\w.]*', Name.Namespace, '#pop')
        ],
    }


class OocLexer(RegexLexer):
    """
    For `Ooc <http://ooc-lang.org/>`_ source code

    .. versionadded:: 1.2
    """
    name = 'Ooc'
    aliases = ['ooc']
    filenames = ['*.ooc']
    mimetypes = ['text/x-ooc']

    tokens = {
        'root': [
            (r'\b(class|interface|implement|abstract|extends|from|'
             r'this|super|new|const|final|static|import|use|extern|'
             r'inline|proto|break|continue|fallthrough|operator|if|else|for|'
             r'while|do|switch|case|as|in|version|return|true|false|null)\b',
             Keyword),
            (r'include\b', Keyword, 'include'),
            (r'(cover)([ \t]+)(from)([ \t]+)(\w+[*@]?)',
             bygroups(Keyword, Text, Keyword, Text, Name.Class)),
            (r'(func)((?:[ \t]|\\\n)+)(~[a-z_]\w*)',
             bygroups(Keyword, Text, Name.Function)),
            (r'\bfunc\b', Keyword),
            # Note: %= and ^= not listed on http://ooc-lang.org/syntax
            (r'//.*', Comment),
            (r'(?s)/\*.*?\*/', Comment.Multiline),
            (r'(==?|\+=?|-[=>]?|\*=?|/=?|:=|!=?|%=?|\?|>{1,3}=?|<{1,3}=?|\.\.|'
             r'&&?|\|\|?|\^=?)', Operator),
            (r'(\.)([ \t]*)([a-z]\w*)', bygroups(Operator, Text,
                                                 Name.Function)),
            (r'[A-Z][A-Z0-9_]+', Name.Constant),
            (r'[A-Z]\w*([@*]|\[[ \t]*\])?', Name.Class),

            (r'([a-z]\w*(?:~[a-z]\w*)?)((?:[ \t]|\\\n)*)(?=\()',
             bygroups(Name.Function, Text)),
            (r'[a-z]\w*', Name.Variable),

            # : introduces types
            (r'[:(){}\[\];,]', Punctuation),

            (r'0x[0-9a-fA-F]+', Number.Hex),
            (r'0c[0-9]+', Number.Oct),
            (r'0b[01]+', Number.Bin),
            (r'[0-9_]\.[0-9_]*(?!\.)', Number.Float),
            (r'[0-9_]+', Number.Decimal),

            (r'"(?:\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\"])*"',
             String.Double),
            (r"'(?:\\.|\\[0-9]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'",
             String.Char),
            (r'@', Punctuation), # pointer dereference
            (r'\.', Punctuation), # imports or chain operator

            (r'\\[ \t\n]', Text),
            (r'[ \t]+', Text),
        ],
        'include': [
            (r'[\w/]+', Name),
            (r',', Punctuation),
            (r'[ \t]', Text),
            (r'[;\n]', Text, '#pop'),
        ],
    }


class GoLexer(RegexLexer):
    """
    For `Go <http://golang.org>`_ source.
    """
    name = 'Go'
    filenames = ['*.go']
    aliases = ['go']
    mimetypes = ['text/x-gosrc']

    flags = re.MULTILINE | re.UNICODE

    tokens = {
        'root': [
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text), # line continuations
            (r'//(.*?)\n', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'(import|package)\b', Keyword.Namespace),
            (r'(var|func|struct|map|chan|type|interface|const)\b', Keyword.Declaration),
            (r'(break|default|select|case|defer|go'
             r'|else|goto|switch|fallthrough|if|range'
             r'|continue|for|return)\b', Keyword),
            (r'(true|false|iota|nil)\b', Keyword.Constant),
            # It seems the builtin types aren't actually keywords, but
            # can be used as functions. So we need two declarations.
            (r'(uint|uint8|uint16|uint32|uint64'
             r'|int|int8|int16|int32|int64'
             r'|float|float32|float64'
             r'|complex64|complex128|byte|rune'
             r'|string|bool|error|uintptr'
             r'|print|println|panic|recover|close|complex|real|imag'
             r'|len|cap|append|copy|delete|new|make)\b(\()',
             bygroups(Name.Builtin, Punctuation)),
            (r'(uint|uint8|uint16|uint32|uint64'
             r'|int|int8|int16|int32|int64'
             r'|float|float32|float64'
             r'|complex64|complex128|byte|rune'
             r'|string|bool|error|uintptr)\b', Keyword.Type),
            # imaginary_lit
            (r'\d+i', Number),
            (r'\d+\.\d*([Ee][-+]\d+)?i', Number),
            (r'\.\d+([Ee][-+]\d+)?i', Number),
            (r'\d+[Ee][-+]\d+i', Number),
            # float_lit
            (r'\d+(\.\d+[eE][+\-]?\d+|'
             r'\.\d*|[eE][+\-]?\d+)', Number.Float),
            (r'\.\d+([eE][+\-]?\d+)?', Number.Float),
            # int_lit
            # -- octal_lit
            (r'0[0-7]+', Number.Oct),
            # -- hex_lit
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            # -- decimal_lit
            (r'(0|[1-9][0-9]*)', Number.Integer),
            # char_lit
            (r"""'(\\['"\\abfnrtv]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}"""
             r"""|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|[^\\])'""",
             String.Char
            ),
            # StringLiteral
            # -- raw_string_lit
            (r'`[^`]*`', String),
            # -- interpreted_string_lit
            (r'"(\\\\|\\"|[^"])*"', String),
            # Tokens
            (r'(<<=|>>=|<<|>>|<=|>=|&\^=|&\^|\+=|-=|\*=|/=|%=|&=|\|=|&&|\|\|'
             r'|<-|\+\+|--|==|!=|:=|\.\.\.|[+\-*/%&])', Operator),
            (r'[|^<>=!()\[\]{}.,;:]', Punctuation),
            # identifier
            (r'[^\W\d]\w*', Name.Other),
        ]
    }


class FelixLexer(RegexLexer):
    """
    For `Felix <http://www.felix-lang.org>`_ source code.

    .. versionadded:: 1.2
    """

    name = 'Felix'
    aliases = ['felix', 'flx']
    filenames = ['*.flx', '*.flxh']
    mimetypes = ['text/x-felix']

    preproc = [
        'elif', 'else', 'endif', 'if', 'ifdef', 'ifndef',
    ]

    keywords = [
        '_', '_deref', 'all', 'as',
        'assert', 'attempt', 'call', 'callback', 'case', 'caseno', 'cclass',
        'code', 'compound', 'ctypes', 'do', 'done', 'downto', 'elif', 'else',
        'endattempt', 'endcase', 'endif', 'endmatch', 'enum', 'except',
        'exceptions', 'expect', 'finally', 'for', 'forall', 'forget', 'fork',
        'functor', 'goto', 'ident', 'if', 'incomplete', 'inherit', 'instance',
        'interface', 'jump', 'lambda', 'loop', 'match', 'module', 'namespace',
        'new', 'noexpand', 'nonterm', 'obj', 'of', 'open', 'parse', 'raise',
        'regexp', 'reglex', 'regmatch', 'rename', 'return', 'the', 'then',
        'to', 'type', 'typecase', 'typedef', 'typematch', 'typeof', 'upto',
        'when', 'whilst', 'with', 'yield',
    ]

    keyword_directives = [
        '_gc_pointer', '_gc_type', 'body', 'comment', 'const', 'export',
        'header', 'inline', 'lval', 'macro', 'noinline', 'noreturn',
        'package', 'private', 'pod', 'property', 'public', 'publish',
        'requires', 'todo', 'virtual', 'use',
    ]

    keyword_declarations = [
        'def', 'let', 'ref', 'val', 'var',
    ]

    keyword_types = [
        'unit', 'void', 'any', 'bool',
        'byte',  'offset',
        'address', 'caddress', 'cvaddress', 'vaddress',
        'tiny', 'short', 'int', 'long', 'vlong',
        'utiny', 'ushort', 'vshort', 'uint', 'ulong', 'uvlong',
        'int8', 'int16', 'int32', 'int64',
        'uint8', 'uint16', 'uint32', 'uint64',
        'float', 'double', 'ldouble',
        'complex', 'dcomplex', 'lcomplex',
        'imaginary', 'dimaginary', 'limaginary',
        'char', 'wchar', 'uchar',
        'charp', 'charcp', 'ucharp', 'ucharcp',
        'string', 'wstring', 'ustring',
        'cont',
        'array', 'varray', 'list',
        'lvalue', 'opt', 'slice',
    ]

    keyword_constants = [
        'false', 'true',
    ]

    operator_words = [
        'and', 'not', 'in', 'is', 'isin', 'or', 'xor',
    ]

    name_builtins = [
        '_svc', 'while',
    ]

    name_pseudo = [
        'root', 'self', 'this',
    ]

    decimal_suffixes = '([tTsSiIlLvV]|ll|LL|([iIuU])(8|16|32|64))?'

    tokens = {
        'root': [
            include('whitespace'),

            # Keywords
            (r'(axiom|ctor|fun|gen|proc|reduce|union)\b', Keyword,
             'funcname'),
            (r'(class|cclass|cstruct|obj|struct)\b', Keyword, 'classname'),
            (r'(instance|module|typeclass)\b', Keyword, 'modulename'),

            (r'(%s)\b' % '|'.join(keywords), Keyword),
            (r'(%s)\b' % '|'.join(keyword_directives), Name.Decorator),
            (r'(%s)\b' % '|'.join(keyword_declarations), Keyword.Declaration),
            (r'(%s)\b' % '|'.join(keyword_types), Keyword.Type),
            (r'(%s)\b' % '|'.join(keyword_constants), Keyword.Constant),

            # Operators
            include('operators'),

            # Float Literal
            # -- Hex Float
            (r'0[xX]([0-9a-fA-F_]*\.[0-9a-fA-F_]+|[0-9a-fA-F_]+)'
             r'[pP][+\-]?[0-9_]+[lLfFdD]?', Number.Float),
            # -- DecimalFloat
            (r'[0-9_]+(\.[0-9_]+[eE][+\-]?[0-9_]+|'
             r'\.[0-9_]*|[eE][+\-]?[0-9_]+)[lLfFdD]?', Number.Float),
            (r'\.(0|[1-9][0-9_]*)([eE][+\-]?[0-9_]+)?[lLfFdD]?',
             Number.Float),

            # IntegerLiteral
            # -- Binary
            (r'0[Bb][01_]+%s' % decimal_suffixes, Number.Bin),
            # -- Octal
            (r'0[0-7_]+%s' % decimal_suffixes, Number.Oct),
            # -- Hexadecimal
            (r'0[xX][0-9a-fA-F_]+%s' % decimal_suffixes, Number.Hex),
            # -- Decimal
            (r'(0|[1-9][0-9_]*)%s' % decimal_suffixes, Number.Integer),

            # Strings
            ('([rR][cC]?|[cC][rR])"""', String, 'tdqs'),
            ("([rR][cC]?|[cC][rR])'''", String, 'tsqs'),
            ('([rR][cC]?|[cC][rR])"', String, 'dqs'),
            ("([rR][cC]?|[cC][rR])'", String, 'sqs'),
            ('[cCfFqQwWuU]?"""', String, combined('stringescape', 'tdqs')),
            ("[cCfFqQwWuU]?'''", String, combined('stringescape', 'tsqs')),
            ('[cCfFqQwWuU]?"', String, combined('stringescape', 'dqs')),
            ("[cCfFqQwWuU]?'", String, combined('stringescape', 'sqs')),

            # Punctuation
            (r'[\[\]{}:(),;?]', Punctuation),

            # Labels
            (r'[a-zA-Z_]\w*:>', Name.Label),

            # Identifiers
            (r'(%s)\b' % '|'.join(name_builtins), Name.Builtin),
            (r'(%s)\b' % '|'.join(name_pseudo), Name.Builtin.Pseudo),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'whitespace': [
            (r'\n', Text),
            (r'\s+', Text),

            include('comment'),

            # Preprocessor
            (r'#\s*if\s+0', Comment.Preproc, 'if0'),
            (r'#', Comment.Preproc, 'macro'),
        ],
        'operators': [
            (r'(%s)\b' % '|'.join(operator_words), Operator.Word),
            (r'!=|==|<<|>>|\|\||&&|[-~+/*%=<>&^|.$]', Operator),
        ],
        'comment': [
            (r'//(.*?)\n', Comment.Single),
            (r'/[*]', Comment.Multiline, 'comment2'),
        ],
        'comment2': [
            (r'[^\/*]', Comment.Multiline),
            (r'/[*]', Comment.Multiline, '#push'),
            (r'[*]/', Comment.Multiline, '#pop'),
            (r'[\/*]', Comment.Multiline),
        ],
        'if0': [
            (r'^\s*#if.*?(?<!\\)\n', Comment, '#push'),
            (r'^\s*#endif.*?(?<!\\)\n', Comment, '#pop'),
            (r'.*?\n', Comment),
        ],
        'macro': [
            include('comment'),
            (r'(import|include)(\s+)(<[^>]*?>)',
             bygroups(Comment.Preproc, Text, String), '#pop'),
            (r'(import|include)(\s+)("[^"]*?")',
             bygroups(Comment.Preproc, Text, String), '#pop'),
            (r"(import|include)(\s+)('[^']*?')",
             bygroups(Comment.Preproc, Text, String), '#pop'),
            (r'[^/\n]+', Comment.Preproc),
            ##(r'/[*](.|\n)*?[*]/', Comment),
            ##(r'//.*?\n', Comment, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Comment.Preproc, '#pop'),
        ],
        'funcname': [
            include('whitespace'),
            (r'[a-zA-Z_]\w*', Name.Function, '#pop'),
            # anonymous functions
            (r'(?=\()', Text, '#pop'),
        ],
        'classname': [
            include('whitespace'),
            (r'[a-zA-Z_]\w*', Name.Class, '#pop'),
            # anonymous classes
            (r'(?=\{)', Text, '#pop'),
        ],
        'modulename': [
            include('whitespace'),
            (r'\[', Punctuation, ('modulename2', 'tvarlist')),
            default('modulename2'),
        ],
        'modulename2': [
            include('whitespace'),
            (r'([a-zA-Z_]\w*)', Name.Namespace, '#pop:2'),
        ],
        'tvarlist': [
            include('whitespace'),
            include('operators'),
            (r'\[', Punctuation, '#push'),
            (r'\]', Punctuation, '#pop'),
            (r',', Punctuation),
            (r'(with|where)\b', Keyword),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N{.*?}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings': [
            (r'%(\([a-zA-Z0-9]+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[diouxXeEfFgGcrs%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String)
            # newlines are an error (use "nl" state)
        ],
        'nl': [
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop'),
            # included here again for raw strings
            (r'\\\\|\\"|\\\n', String.Escape),
            include('strings')
        ],
        'sqs': [
            (r"'", String, '#pop'),
            # included here again for raw strings
            (r"\\\\|\\'|\\\n", String.Escape),
            include('strings')
        ],
        'tdqs': [
            (r'"""', String, '#pop'),
            include('strings'),
            include('nl')
        ],
        'tsqs': [
            (r"'''", String, '#pop'),
            include('strings'),
            include('nl')
        ],
     }


class AdaLexer(RegexLexer):
    """
    For Ada source code.

    .. versionadded:: 1.3
    """

    name = 'Ada'
    aliases = ['ada', 'ada95' 'ada2005']
    filenames = ['*.adb', '*.ads', '*.ada']
    mimetypes = ['text/x-ada']

    flags = re.MULTILINE | re.I  # Ignore case

    tokens = {
        'root': [
            (r'[^\S\n]+', Text),
            (r'--.*?\n', Comment.Single),
            (r'[^\S\n]+', Text),
            (r'function|procedure|entry', Keyword.Declaration, 'subprogram'),
            (r'(subtype|type)(\s+)([a-z0-9_]+)',
             bygroups(Keyword.Declaration, Text, Keyword.Type), 'type_def'),
            (r'task|protected', Keyword.Declaration),
            (r'(subtype)(\s+)', bygroups(Keyword.Declaration, Text)),
            (r'(end)(\s+)', bygroups(Keyword.Reserved, Text), 'end'),
            (r'(pragma)(\s+)(\w+)', bygroups(Keyword.Reserved, Text,
                                                       Comment.Preproc)),
            (r'(true|false|null)\b', Keyword.Constant),
            (r'(Address|Byte|Boolean|Character|Controlled|Count|Cursor|'
             r'Duration|File_Mode|File_Type|Float|Generator|Integer|Long_Float|'
             r'Long_Integer|Long_Long_Float|Long_Long_Integer|Natural|Positive|'
             r'Reference_Type|Short_Float|Short_Integer|Short_Short_Float|'
             r'Short_Short_Integer|String|Wide_Character|Wide_String)\b',
             Keyword.Type),
            (r'(and(\s+then)?|in|mod|not|or(\s+else)|rem)\b', Operator.Word),
            (r'generic|private', Keyword.Declaration),
            (r'package', Keyword.Declaration, 'package'),
            (r'array\b', Keyword.Reserved, 'array_def'),
            (r'(with|use)(\s+)', bygroups(Keyword.Namespace, Text), 'import'),
            (r'([a-z0-9_]+)(\s*)(:)(\s*)(constant)',
             bygroups(Name.Constant, Text, Punctuation, Text,
                      Keyword.Reserved)),
            (r'<<[a-z0-9_]+>>', Name.Label),
            (r'([a-z0-9_]+)(\s*)(:)(\s*)(declare|begin|loop|for|while)',
             bygroups(Name.Label, Text, Punctuation, Text, Keyword.Reserved)),
            (r'\b(abort|abs|abstract|accept|access|aliased|all|array|at|begin|'
             r'body|case|constant|declare|delay|delta|digits|do|else|elsif|end|'
             r'entry|exception|exit|interface|for|goto|if|is|limited|loop|new|'
             r'null|of|or|others|out|overriding|pragma|protected|raise|range|'
             r'record|renames|requeue|return|reverse|select|separate|subtype|'
             r'synchronized|task|tagged|terminate|then|type|until|when|while|'
             r'xor)\b',
             Keyword.Reserved),
            (r'"[^"]*"', String),
            include('attribute'),
            include('numbers'),
            (r"'[^']'", String.Character),
            (r'([a-z0-9_]+)(\s*|[(,])', bygroups(Name, using(this))),
            (r"(<>|=>|:=|[()|:;,.'])", Punctuation),
            (r'[*<>+=/&-]', Operator),
            (r'\n+', Text),
        ],
        'numbers' : [
            (r'[0-9_]+#[0-9a-f]+#', Number.Hex),
            (r'[0-9_]+\.[0-9_]*', Number.Float),
            (r'[0-9_]+', Number.Integer),
        ],
        'attribute' : [
            (r"(')(\w+)", bygroups(Punctuation, Name.Attribute)),
        ],
        'subprogram' : [
            (r'\(', Punctuation, ('#pop', 'formal_part')),
            (r';', Punctuation, '#pop'),
            (r'is\b', Keyword.Reserved, '#pop'),
            (r'"[^"]+"|[a-z0-9_]+', Name.Function),
            include('root'),
        ],
        'end' : [
            ('(if|case|record|loop|select)', Keyword.Reserved),
            ('"[^"]+"|[\w.]+', Name.Function),
            ('\s+', Text),
            (';', Punctuation, '#pop'),
        ],
        'type_def': [
            (r';', Punctuation, '#pop'),
            (r'\(', Punctuation, 'formal_part'),
            (r'with|and|use', Keyword.Reserved),
            (r'array\b', Keyword.Reserved, ('#pop', 'array_def')),
            (r'record\b', Keyword.Reserved, ('record_def')),
            (r'(null record)(;)', bygroups(Keyword.Reserved, Punctuation), '#pop'),
            include('root'),
        ],
        'array_def' : [
            (r';', Punctuation, '#pop'),
            (r'([a-z0-9_]+)(\s+)(range)', bygroups(Keyword.Type, Text,
                                                   Keyword.Reserved)),
            include('root'),
        ],
        'record_def' : [
            (r'end record', Keyword.Reserved, '#pop'),
            include('root'),
        ],
        'import': [
            (r'[a-z0-9_.]+', Name.Namespace, '#pop'),
            default('#pop'),
        ],
        'formal_part' : [
            (r'\)', Punctuation, '#pop'),
            (r'[a-z0-9_]+', Name.Variable),
            (r',|:[^=]', Punctuation),
            (r'(in|not|null|out|access)\b', Keyword.Reserved),
            include('root'),
        ],
        'package': [
            ('body', Keyword.Declaration),
            ('is\s+new|renames', Keyword.Reserved),
            ('is', Keyword.Reserved, '#pop'),
            (';', Punctuation, '#pop'),
            ('\(', Punctuation, 'package_instantiation'),
            ('([\w.]+)', Name.Class),
            include('root'),
        ],
        'package_instantiation': [
            (r'("[^"]+"|[a-z0-9_]+)(\s+)(=>)', bygroups(Name.Variable,
                                                        Text, Punctuation)),
            (r'[a-z0-9._\'"]', Text),
            (r'\)', Punctuation, '#pop'),
            include('root'),
        ],
    }


class Modula2Lexer(RegexLexer):
    """
    For `Modula-2 <http://www.modula2.org/>`_ source code.

    Additional options that determine which keywords are highlighted:

    `pim`
        Select PIM Modula-2 dialect (default: True).
    `iso`
        Select ISO Modula-2 dialect (default: False).
    `objm2`
        Select Objective Modula-2 dialect (default: False).
    `gm2ext`
        Also highlight GNU extensions (default: False).

    .. versionadded:: 1.3
    """
    name = 'Modula-2'
    aliases = ['modula2', 'm2']
    filenames = ['*.def', '*.mod']
    mimetypes = ['text/x-modula2']

    flags = re.MULTILINE | re.DOTALL

    tokens = {
        'whitespace': [
            (r'\n+', Text), # blank lines
            (r'\s+', Text), # whitespace
        ],
        'identifiers': [
            (r'([a-zA-Z_\$][\w\$]*)', Name),
        ],
        'numliterals': [
            (r'[01]+B', Number.Bin),           # binary number (ObjM2)
            (r'[0-7]+B', Number.Oct),          # octal number (PIM + ISO)
            (r'[0-7]+C', Number.Oct),          # char code (PIM + ISO)
            (r'[0-9A-F]+C', Number.Hex),       # char code (ObjM2)
            (r'[0-9A-F]+H', Number.Hex),       # hexadecimal number
            (r'[0-9]+\.[0-9]+E[+-][0-9]+', Number.Float), # real number
            (r'[0-9]+\.[0-9]+', Number.Float), # real number
            (r'[0-9]+', Number.Integer),       # decimal whole number
        ],
        'strings': [
            (r"'(\\\\|\\'|[^'])*'", String), # single quoted string
            (r'"(\\\\|\\"|[^"])*"', String), # double quoted string
        ],
        'operators': [
            (r'[*/+=#~&<>\^-]', Operator),
            (r':=', Operator),   # assignment
            (r'@', Operator),    # pointer deref (ISO)
            (r'\.\.', Operator), # ellipsis or range
            (r'`', Operator),    # Smalltalk message (ObjM2)
            (r'::', Operator),   # type conversion (ObjM2)
        ],
        'punctuation': [
            (r'[\(\)\[\]{},.:;|]', Punctuation),
        ],
        'comments': [
            (r'//.*?\n', Comment.Single),       # ObjM2
            (r'/\*(.*?)\*/', Comment.Multiline), # ObjM2
            (r'\(\*([^\$].*?)\*\)', Comment.Multiline),
            # TO DO: nesting of (* ... *) comments
        ],
        'pragmas': [
            (r'\(\*\$(.*?)\*\)', Comment.Preproc), # PIM
            (r'<\*(.*?)\*>', Comment.Preproc),     # ISO + ObjM2
        ],
        'root': [
            include('whitespace'),
            include('comments'),
            include('pragmas'),
            include('identifiers'),
            include('numliterals'),
            include('strings'),
            include('operators'),
            include('punctuation'),
        ]
    }

    pim_reserved_words = [
        # 40 reserved words
        'AND', 'ARRAY', 'BEGIN', 'BY', 'CASE', 'CONST', 'DEFINITION',
        'DIV', 'DO', 'ELSE', 'ELSIF', 'END', 'EXIT', 'EXPORT', 'FOR',
        'FROM', 'IF', 'IMPLEMENTATION', 'IMPORT', 'IN', 'LOOP', 'MOD',
        'MODULE', 'NOT', 'OF', 'OR', 'POINTER', 'PROCEDURE', 'QUALIFIED',
        'RECORD', 'REPEAT', 'RETURN', 'SET', 'THEN', 'TO', 'TYPE',
        'UNTIL', 'VAR', 'WHILE', 'WITH',
    ]

    pim_pervasives = [
        # 31 pervasives
        'ABS', 'BITSET', 'BOOLEAN', 'CAP', 'CARDINAL', 'CHAR', 'CHR', 'DEC',
        'DISPOSE', 'EXCL', 'FALSE', 'FLOAT', 'HALT', 'HIGH', 'INC', 'INCL',
        'INTEGER', 'LONGINT', 'LONGREAL', 'MAX', 'MIN', 'NEW', 'NIL', 'ODD',
        'ORD', 'PROC', 'REAL', 'SIZE', 'TRUE', 'TRUNC', 'VAL',
    ]

    iso_reserved_words = [
        # 46 reserved words
        'AND', 'ARRAY', 'BEGIN', 'BY', 'CASE', 'CONST', 'DEFINITION', 'DIV',
        'DO', 'ELSE', 'ELSIF', 'END', 'EXCEPT', 'EXIT', 'EXPORT', 'FINALLY',
        'FOR', 'FORWARD', 'FROM', 'IF', 'IMPLEMENTATION', 'IMPORT', 'IN',
        'LOOP', 'MOD', 'MODULE', 'NOT', 'OF', 'OR', 'PACKEDSET', 'POINTER',
        'PROCEDURE', 'QUALIFIED', 'RECORD', 'REPEAT', 'REM', 'RETRY',
        'RETURN', 'SET', 'THEN', 'TO', 'TYPE', 'UNTIL', 'VAR', 'WHILE',
        'WITH',
    ]

    iso_pervasives = [
        # 42 pervasives
        'ABS', 'BITSET', 'BOOLEAN', 'CAP', 'CARDINAL', 'CHAR', 'CHR', 'CMPLX',
        'COMPLEX', 'DEC', 'DISPOSE', 'EXCL', 'FALSE', 'FLOAT', 'HALT', 'HIGH',
        'IM', 'INC', 'INCL', 'INT', 'INTEGER', 'INTERRUPTIBLE', 'LENGTH',
        'LFLOAT', 'LONGCOMPLEX', 'LONGINT', 'LONGREAL', 'MAX', 'MIN', 'NEW',
        'NIL', 'ODD', 'ORD', 'PROC', 'PROTECTION', 'RE', 'REAL', 'SIZE',
        'TRUE', 'TRUNC', 'UNINTERRUBTIBLE', 'VAL',
    ]

    objm2_reserved_words = [
        # base language, 42 reserved words
        'AND', 'ARRAY', 'BEGIN', 'BY', 'CASE', 'CONST', 'DEFINITION', 'DIV',
        'DO', 'ELSE', 'ELSIF', 'END', 'ENUM', 'EXIT', 'FOR', 'FROM', 'IF',
        'IMMUTABLE', 'IMPLEMENTATION', 'IMPORT', 'IN', 'IS', 'LOOP', 'MOD',
        'MODULE', 'NOT', 'OF', 'OPAQUE', 'OR', 'POINTER', 'PROCEDURE',
        'RECORD', 'REPEAT', 'RETURN', 'SET', 'THEN', 'TO', 'TYPE',
        'UNTIL', 'VAR', 'VARIADIC', 'WHILE',
        # OO extensions, 16 reserved words
        'BYCOPY', 'BYREF', 'CLASS', 'CONTINUE', 'CRITICAL', 'INOUT', 'METHOD',
        'ON', 'OPTIONAL', 'OUT', 'PRIVATE', 'PROTECTED', 'PROTOCOL', 'PUBLIC',
        'SUPER', 'TRY',
    ]

    objm2_pervasives = [
        # base language, 38 pervasives
        'ABS', 'BITSET', 'BOOLEAN', 'CARDINAL', 'CHAR', 'CHR', 'DISPOSE',
        'FALSE', 'HALT', 'HIGH', 'INTEGER', 'INRANGE', 'LENGTH', 'LONGCARD',
        'LONGINT', 'LONGREAL', 'MAX', 'MIN', 'NEG', 'NEW', 'NEXTV', 'NIL',
        'OCTET', 'ODD', 'ORD', 'PRED', 'PROC', 'READ', 'REAL', 'SUCC', 'TMAX',
        'TMIN', 'TRUE', 'TSIZE', 'UNICHAR', 'VAL', 'WRITE', 'WRITEF',
        # OO extensions, 3 pervasives
        'OBJECT', 'NO', 'YES',
    ]

    gnu_reserved_words = [
        # 10 additional reserved words
        'ASM', '__ATTRIBUTE__', '__BUILTIN__', '__COLUMN__', '__DATE__',
        '__FILE__', '__FUNCTION__', '__LINE__', '__MODULE__', 'VOLATILE',
    ]

    gnu_pervasives = [
        # 21 identifiers, actually from pseudo-module SYSTEM
        # but we will highlight them as if they were pervasives
        'BITSET8', 'BITSET16', 'BITSET32', 'CARDINAL8', 'CARDINAL16',
        'CARDINAL32', 'CARDINAL64', 'COMPLEX32', 'COMPLEX64', 'COMPLEX96',
        'COMPLEX128', 'INTEGER8', 'INTEGER16', 'INTEGER32', 'INTEGER64',
        'REAL8', 'REAL16', 'REAL32', 'REAL96', 'REAL128', 'THROW',
    ]

    def __init__(self, **options):
        self.reserved_words = set()
        self.pervasives = set()
        # ISO Modula-2
        if get_bool_opt(options, 'iso', False):
            self.reserved_words.update(self.iso_reserved_words)
            self.pervasives.update(self.iso_pervasives)
        # Objective Modula-2
        elif get_bool_opt(options, 'objm2', False):
            self.reserved_words.update(self.objm2_reserved_words)
            self.pervasives.update(self.objm2_pervasives)
        # PIM Modula-2 (DEFAULT)
        else:
            self.reserved_words.update(self.pim_reserved_words)
            self.pervasives.update(self.pim_pervasives)
        # GNU extensions
        if get_bool_opt(options, 'gm2ext', False):
            self.reserved_words.update(self.gnu_reserved_words)
            self.pervasives.update(self.gnu_pervasives)
        # initialise
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
            RegexLexer.get_tokens_unprocessed(self, text):
            # check for reserved words and pervasives
            if token is Name:
                if value in self.reserved_words:
                    token = Keyword.Reserved
                elif value in self.pervasives:
                    token = Keyword.Pervasive
            # return result
            yield index, token, value


class BlitzMaxLexer(RegexLexer):
    """
    For `BlitzMax <http://blitzbasic.com>`_ source code.

    .. versionadded:: 1.4
    """

    name = 'BlitzMax'
    aliases = ['blitzmax', 'bmax']
    filenames = ['*.bmx']
    mimetypes = ['text/x-bmx']

    bmax_vopwords = r'\b(Shl|Shr|Sar|Mod)\b'
    bmax_sktypes = r'@{1,2}|[!#$%]'
    bmax_lktypes = r'\b(Int|Byte|Short|Float|Double|Long)\b'
    bmax_name = r'[a-z_]\w*'
    bmax_var = (r'(%s)(?:(?:([ \t]*)(%s)|([ \t]*:[ \t]*\b(?:Shl|Shr|Sar|Mod)\b)'
                r'|([ \t]*)(:)([ \t]*)(?:%s|(%s)))(?:([ \t]*)(Ptr))?)') % \
                (bmax_name, bmax_sktypes, bmax_lktypes, bmax_name)
    bmax_func = bmax_var + r'?((?:[ \t]|\.\.\n)*)([(])'

    flags = re.MULTILINE | re.IGNORECASE
    tokens = {
        'root': [
            # Text
            (r'[ \t]+', Text),
            (r'\.\.\n', Text), # Line continuation
            # Comments
            (r"'.*?\n", Comment.Single),
            (r'([ \t]*)\bRem\n(\n|.)*?\s*\bEnd([ \t]*)Rem', Comment.Multiline),
            # Data types
            ('"', String.Double, 'string'),
            # Numbers
            (r'[0-9]+\.[0-9]*(?!\.)', Number.Float),
            (r'\.[0-9]*(?!\.)', Number.Float),
            (r'[0-9]+', Number.Integer),
            (r'\$[0-9a-f]+', Number.Hex),
            (r'\%[10]+', Number.Bin),
            # Other
            (r'(?:(?:(:)?([ \t]*)(:?%s|([+\-*/&|~]))|Or|And|Not|[=<>^]))' %
             (bmax_vopwords), Operator),
            (r'[(),.:\[\]]', Punctuation),
            (r'(?:#[\w \t]*)', Name.Label),
            (r'(?:\?[\w \t]*)', Comment.Preproc),
            # Identifiers
            (r'\b(New)\b([ \t]?)([(]?)(%s)' % (bmax_name),
             bygroups(Keyword.Reserved, Text, Punctuation, Name.Class)),
            (r'\b(Import|Framework|Module)([ \t]+)(%s\.%s)' %
             (bmax_name, bmax_name),
             bygroups(Keyword.Reserved, Text, Keyword.Namespace)),
            (bmax_func, bygroups(Name.Function, Text, Keyword.Type,
                                 Operator, Text, Punctuation, Text,
                                 Keyword.Type, Name.Class, Text,
                                 Keyword.Type, Text, Punctuation)),
            (bmax_var, bygroups(Name.Variable, Text, Keyword.Type, Operator,
                                Text, Punctuation, Text, Keyword.Type,
                                Name.Class, Text, Keyword.Type)),
            (r'\b(Type|Extends)([ \t]+)(%s)' % (bmax_name),
             bygroups(Keyword.Reserved, Text, Name.Class)),
            # Keywords
            (r'\b(Ptr)\b', Keyword.Type),
            (r'\b(Pi|True|False|Null|Self|Super)\b', Keyword.Constant),
            (r'\b(Local|Global|Const|Field)\b', Keyword.Declaration),
            (r'\b(TNullMethodException|TNullFunctionException|'
             r'TNullObjectException|TArrayBoundsException|'
             r'TRuntimeException)\b', Name.Exception),
            (r'\b(Strict|SuperStrict|Module|ModuleInfo|'
             r'End|Return|Continue|Exit|Public|Private|'
             r'Var|VarPtr|Chr|Len|Asc|SizeOf|Sgn|Abs|Min|Max|'
             r'New|Release|Delete|'
             r'Incbin|IncbinPtr|IncbinLen|'
             r'Framework|Include|Import|Extern|EndExtern|'
             r'Function|EndFunction|'
             r'Type|EndType|Extends|'
             r'Method|EndMethod|'
             r'Abstract|Final|'
             r'If|Then|Else|ElseIf|EndIf|'
             r'For|To|Next|Step|EachIn|'
             r'While|Wend|EndWhile|'
             r'Repeat|Until|Forever|'
             r'Select|Case|Default|EndSelect|'
             r'Try|Catch|EndTry|Throw|Assert|'
             r'Goto|DefData|ReadData|RestoreData)\b', Keyword.Reserved),
            # Final resolve (for variable names and such)
            (r'(%s)' % (bmax_name), Name.Variable),
        ],
        'string': [
            (r'""', String.Double),
            (r'"C?', String.Double, '#pop'),
            (r'[^"]+', String.Double),
        ],
    }


class BlitzBasicLexer(RegexLexer):
    """
    For `BlitzBasic <http://blitzbasic.com>`_ source code.

    .. versionadded:: 2.0
    """

    name = 'BlitzBasic'
    aliases = ['blitzbasic', 'b3d', 'bplus']
    filenames = ['*.bb', '*.decls']
    mimetypes = ['text/x-bb']

    bb_vopwords = (r'\b(Shl|Shr|Sar|Mod|Or|And|Not|'
                   r'Abs|Sgn|Handle|Int|Float|Str|'
                   r'First|Last|Before|After)\b')
    bb_sktypes = r'@{1,2}|[#$%]'
    bb_name = r'[a-z]\w*'
    bb_var = (r'(%s)(?:([ \t]*)(%s)|([ \t]*)([.])([ \t]*)(?:(%s)))?') % \
                (bb_name, bb_sktypes, bb_name)

    flags = re.MULTILINE | re.IGNORECASE
    tokens = {
        'root': [
            # Text
            (r'[ \t]+', Text),
            # Comments
            (r";.*?\n", Comment.Single),
            # Data types
            ('"', String.Double, 'string'),
            # Numbers
            (r'[0-9]+\.[0-9]*(?!\.)', Number.Float),
            (r'\.[0-9]+(?!\.)', Number.Float),
            (r'[0-9]+', Number.Integer),
            (r'\$[0-9a-f]+', Number.Hex),
            (r'\%[10]+', Number.Bin),
            # Other
            (r'(?:%s|([+\-*/~=<>^]))' % (bb_vopwords), Operator),
            (r'[(),:\[\]\\]', Punctuation),
            (r'\.([ \t]*)(%s)' % bb_name, Name.Label),
            # Identifiers
            (r'\b(New)\b([ \t]+)(%s)' % (bb_name),
             bygroups(Keyword.Reserved, Text, Name.Class)),
            (r'\b(Gosub|Goto)\b([ \t]+)(%s)' % (bb_name),
             bygroups(Keyword.Reserved, Text, Name.Label)),
            (r'\b(Object)\b([ \t]*)([.])([ \t]*)(%s)\b' % (bb_name),
             bygroups(Operator, Text, Punctuation, Text, Name.Class)),
            (r'\b%s\b([ \t]*)(\()' % bb_var,
             bygroups(Name.Function, Text, Keyword.Type,Text, Punctuation,
                      Text, Name.Class, Text, Punctuation)),
            (r'\b(Function)\b([ \t]+)%s' % bb_var,
             bygroups(Keyword.Reserved, Text, Name.Function, Text, Keyword.Type,
                              Text, Punctuation, Text, Name.Class)),
            (r'\b(Type)([ \t]+)(%s)' % (bb_name),
             bygroups(Keyword.Reserved, Text, Name.Class)),
            # Keywords
            (r'\b(Pi|True|False|Null)\b', Keyword.Constant),
            (r'\b(Local|Global|Const|Field|Dim)\b', Keyword.Declaration),
            (r'\b(End|Return|Exit|'
             r'Chr|Len|Asc|'
             r'New|Delete|Insert|'
             r'Include|'
             r'Function|'
             r'Type|'
             r'If|Then|Else|ElseIf|EndIf|'
             r'For|To|Next|Step|Each|'
             r'While|Wend|'
             r'Repeat|Until|Forever|'
             r'Select|Case|Default|'
             r'Goto|Gosub|Data|Read|Restore)\b', Keyword.Reserved),
            # Final resolve (for variable names and such)
#            (r'(%s)' % (bb_name), Name.Variable),
            (bb_var, bygroups(Name.Variable, Text, Keyword.Type,
                              Text, Punctuation, Text, Name.Class)),
        ],
        'string': [
            (r'""', String.Double),
            (r'"C?', String.Double, '#pop'),
            (r'[^"]+', String.Double),
        ],
    }


class NimrodLexer(RegexLexer):
    """
    For `Nimrod <http://nimrod-code.org/>`_ source code.

    .. versionadded:: 1.5
    """

    name = 'Nimrod'
    aliases = ['nimrod', 'nim']
    filenames = ['*.nim', '*.nimrod']
    mimetypes = ['text/x-nimrod']

    flags = re.MULTILINE | re.IGNORECASE | re.UNICODE

    def underscorize(words):
        newWords = []
        new = ""
        for word in words:
            for ch in word:
                new += (ch + "_?")
            newWords.append(new)
            new = ""
        return "|".join(newWords)

    keywords = [
        'addr', 'and', 'as', 'asm', 'atomic', 'bind', 'block', 'break',
        'case', 'cast', 'const', 'continue', 'converter', 'discard',
        'distinct', 'div', 'elif', 'else', 'end', 'enum', 'except', 'finally',
        'for', 'generic', 'if', 'implies', 'in', 'yield',
        'is', 'isnot', 'iterator', 'lambda', 'let', 'macro', 'method',
        'mod', 'not', 'notin', 'object', 'of', 'or', 'out', 'proc',
        'ptr', 'raise', 'ref', 'return', 'shl', 'shr', 'template', 'try',
        'tuple', 'type' , 'when', 'while', 'with', 'without', 'xor'
    ]

    keywordsPseudo = [
        'nil', 'true', 'false'
    ]

    opWords = [
        'and', 'or', 'not', 'xor', 'shl', 'shr', 'div', 'mod', 'in',
        'notin', 'is', 'isnot'
    ]

    types = [
        'int', 'int8', 'int16', 'int32', 'int64', 'float', 'float32', 'float64',
        'bool', 'char', 'range', 'array', 'seq', 'set', 'string'
    ]

    tokens = {
        'root': [
            (r'##.*$', String.Doc),
            (r'#.*$', Comment),
            (r'\*|=|>|<|\+|-|/|@|\$|~|&|%|\!|\?|\||\\|\[|\]', Operator),
            (r'\.\.|\.|,|\[\.|\.\]|{\.|\.}|\(\.|\.\)|{|}|\(|\)|:|\^|`|;',
             Punctuation),

            # Strings
            (r'(?:[\w]+)"', String, 'rdqs'),
            (r'"""', String, 'tdqs'),
            ('"', String, 'dqs'),

            # Char
            ("'", String.Char, 'chars'),

            # Keywords
            (r'(%s)\b' % underscorize(opWords), Operator.Word),
            (r'(p_?r_?o_?c_?\s)(?![\(\[\]])', Keyword, 'funcname'),
            (r'(%s)\b' % underscorize(keywords), Keyword),
            (r'(%s)\b' % underscorize(['from', 'import', 'include']),
             Keyword.Namespace),
            (r'(v_?a_?r)\b', Keyword.Declaration),
            (r'(%s)\b' % underscorize(types), Keyword.Type),
            (r'(%s)\b' % underscorize(keywordsPseudo), Keyword.Pseudo),
            # Identifiers
            (r'\b((?![_\d])\w)(((?!_)\w)|(_(?!_)\w))*', Name),
            # Numbers
            (r'[0-9][0-9_]*(?=([eE.]|\'[fF](32|64)))',
              Number.Float, ('float-suffix', 'float-number')),
            (r'0[xX][a-f0-9][a-f0-9_]*', Number.Hex, 'int-suffix'),
            (r'0[bB][01][01_]*', Number.Bin, 'int-suffix'),
            (r'0o[0-7][0-7_]*', Number.Oct, 'int-suffix'),
            (r'[0-9][0-9_]*', Number.Integer, 'int-suffix'),
            # Whitespace
            (r'\s+', Text),
            (r'.+$', Error),
        ],
        'chars': [
          (r'\\([\\abcefnrtvl"\']|x[a-f0-9]{2}|[0-9]{1,3})', String.Escape),
          (r"'", String.Char, '#pop'),
          (r".", String.Char)
        ],
        'strings': [
            (r'(?<!\$)\$(\d+|#|\w+)+', String.Interpol),
            (r'[^\\\'"\$\n]+', String),
            # quotes, dollars and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'\$', String)
            # newlines are an error (use "nl" state)
        ],
        'dqs': [
            (r'\\([\\abcefnrtvl"\']|\n|x[a-f0-9]{2}|[0-9]{1,3})',
             String.Escape),
            (r'"', String, '#pop'),
            include('strings')
        ],
        'rdqs': [
            (r'"(?!")', String, '#pop'),
            (r'""', String.Escape),
            include('strings')
        ],
        'tdqs': [
            (r'"""(?!")', String, '#pop'),
            include('strings'),
            include('nl')
        ],
        'funcname': [
            (r'((?![\d_])\w)(((?!_)\w)|(_(?!_)\w))*', Name.Function, '#pop'),
            (r'`.+`', Name.Function, '#pop')
        ],
        'nl': [
            (r'\n', String)
        ],
        'float-number': [
          (r'\.(?!\.)[0-9_]*', Number.Float),
          (r'[eE][+-]?[0-9][0-9_]*', Number.Float),
          default('#pop')
        ],
        'float-suffix': [
          (r'\'[fF](32|64)', Number.Float),
          default('#pop')
        ],
        'int-suffix': [
          (r'\'[iI](32|64)', Number.Integer.Long),
          (r'\'[iI](8|16)', Number.Integer),
          default('#pop')
        ],
    }


class FantomLexer(RegexLexer):
    """
    For Fantom source code.

    .. versionadded:: 1.5
    """
    name = 'Fantom'
    aliases = ['fan']
    filenames = ['*.fan']
    mimetypes = ['application/x-fantom']

    # often used regexes
    def s(str):
        return Template(str).substitute(
            dict (
                pod = r'[\"\w\.]+',
                eos = r'\n|;',
                id = r'[a-zA-Z_]\w*',
                # all chars which can be part of type definition. Starts with
                # either letter, or [ (maps), or | (funcs)
                type = r'(?:\[|[a-zA-Z_]|\|)[:\w\[\]\|\->\?]*?',
                )
            )


    tokens = {
        'comments': [
            (r'(?s)/\*.*?\*/', Comment.Multiline),           #Multiline
            (r'//.*?\n', Comment.Single),                    #Single line
            #todo: highlight references in fandocs
            (r'\*\*.*?\n', Comment.Special),                 #Fandoc
            (r'#.*\n', Comment.Single)                       #Shell-style
        ],
        'literals': [
            (r'\b-?[\d_]+(ns|ms|sec|min|hr|day)', Number),   #Duration
            (r'\b-?[\d_]*\.[\d_]+(ns|ms|sec|min|hr|day)', Number),
                                                             #Duration with dot
            (r'\b-?(\d+)?\.\d+(f|F|d|D)?', Number.Float),    #Float/Decimal
            (r'\b-?0x[0-9a-fA-F_]+', Number.Hex),            #Hex
            (r'\b-?[\d_]+', Number.Integer),                 #Int
            (r"'\\.'|'[^\\]'|'\\u[0-9a-f]{4}'", String.Char), #Char
            (r'"', Punctuation, 'insideStr'),                #Opening quote
            (r'`', Punctuation, 'insideUri'),                #Opening accent
            (r'\b(true|false|null)\b', Keyword.Constant),    #Bool & null
            (r'(?:(\w+)(::))?(\w+)(<\|)(.*?)(\|>)',          #DSL
             bygroups(Name.Namespace, Punctuation, Name.Class,
                      Punctuation, String, Punctuation)),
            (r'(?:(\w+)(::))?(\w+)?(#)(\w+)?',               #Type/slot literal
             bygroups(Name.Namespace, Punctuation, Name.Class,
                      Punctuation, Name.Function)),
            (r'\[,\]', Literal),                             # Empty list
            (s(r'($type)(\[,\])'),                           # Typed empty list
             bygroups(using(this, state = 'inType'), Literal)),
            (r'\[:\]', Literal),                             # Empty Map
            (s(r'($type)(\[:\])'),
             bygroups(using(this, state = 'inType'), Literal)),
        ],
        'insideStr': [
            (r'\\\\', String.Escape),                        #Escaped backslash
            (r'\\"', String.Escape),                         #Escaped "
            (r'\\`', String.Escape),                         #Escaped `
            (r'\$\w+', String.Interpol),                     #Subst var
            (r'\${.*?}', String.Interpol),                   #Subst expr
            (r'"', Punctuation, '#pop'),                     #Closing quot
            (r'.', String)                                   #String content
        ],
        'insideUri': [  #TODO: remove copy/paste str/uri
            (r'\\\\', String.Escape),                        #Escaped backslash
            (r'\\"', String.Escape),                         #Escaped "
            (r'\\`', String.Escape),                         #Escaped `
            (r'\$\w+', String.Interpol),                     #Subst var
            (r'\${.*?}', String.Interpol),                   #Subst expr
            (r'`', Punctuation, '#pop'),                     #Closing tick
            (r'.', String.Backtick)                          #URI content
        ],
        'protectionKeywords': [
            (r'\b(public|protected|private|internal)\b', Keyword),
        ],
        'typeKeywords': [
            (r'\b(abstract|final|const|native|facet|enum)\b', Keyword),
        ],
        'methodKeywords': [
            (r'\b(abstract|native|once|override|static|virtual|final)\b',
             Keyword),
        ],
        'fieldKeywords': [
            (r'\b(abstract|const|final|native|override|static|virtual|'
             r'readonly)\b', Keyword)
        ],
        'otherKeywords': [
            (r'\b(try|catch|throw|finally|for|if|else|while|as|is|isnot|'
             r'switch|case|default|continue|break|do|return|get|set)\b',
             Keyword),
            (r'\b(it|this|super)\b', Name.Builtin.Pseudo),
        ],
        'operators': [
            (r'\+\+|\-\-|\+|\-|\*|/|\|\||&&|<=>|<=|<|>=|>|=|!|\[|\]', Operator)
        ],
        'inType': [
            (r'[\[\]\|\->:\?]', Punctuation),
            (s(r'$id'), Name.Class),
            default('#pop'),

        ],
        'root': [
            include('comments'),
            include('protectionKeywords'),
            include('typeKeywords'),
            include('methodKeywords'),
            include('fieldKeywords'),
            include('literals'),
            include('otherKeywords'),
            include('operators'),
            (r'using\b', Keyword.Namespace, 'using'),         # Using stmt
            (r'@\w+', Name.Decorator, 'facet'),               # Symbol
            (r'(class|mixin)(\s+)(\w+)', bygroups(Keyword, Text, Name.Class),
             'inheritance'),                                  # Inheritance list


            ### Type var := val
            (s(r'($type)([ \t]+)($id)(\s*)(:=)'),
             bygroups(using(this, state = 'inType'), Text,
                      Name.Variable, Text, Operator)),

            ### var := val
            (s(r'($id)(\s*)(:=)'),
             bygroups(Name.Variable, Text, Operator)),

            ### .someId( or ->someId( ###
            (s(r'(\.|(?:\->))($id)(\s*)(\()'),
             bygroups(Operator, Name.Function, Text, Punctuation),
             'insideParen'),

            ### .someId  or ->someId
            (s(r'(\.|(?:\->))($id)'),
             bygroups(Operator, Name.Function)),

            ### new makeXXX ( ####
            (r'(new)(\s+)(make\w*)(\s*)(\()',
             bygroups(Keyword, Text, Name.Function, Text, Punctuation),
             'insideMethodDeclArgs'),

            ### Type name (  ####
            (s(r'($type)([ \t]+)' #Return type and whitespace
               r'($id)(\s*)(\()'), #method name + open brace
             bygroups(using(this, state = 'inType'), Text,
                      Name.Function, Text, Punctuation),
             'insideMethodDeclArgs'),

            ### ArgType argName, #####
            (s(r'($type)(\s+)($id)(\s*)(,)'),
             bygroups(using(this, state='inType'), Text, Name.Variable,
                      Text, Punctuation)),

            #### ArgType argName) ####
            ## Covered in 'insideParen' state

            ### ArgType argName -> ArgType| ###
            (s(r'($type)(\s+)($id)(\s*)(\->)(\s*)($type)(\|)'),
             bygroups(using(this, state='inType'), Text, Name.Variable,
                      Text, Punctuation, Text, using(this, state = 'inType'),
                      Punctuation)),

            ### ArgType argName|  ###
            (s(r'($type)(\s+)($id)(\s*)(\|)'),
             bygroups(using(this, state='inType'), Text, Name.Variable,
                      Text, Punctuation)),

            ### Type var
            (s(r'($type)([ \t]+)($id)'),
             bygroups(using(this, state='inType'), Text,
                      Name.Variable)),

            (r'\(', Punctuation, 'insideParen'),
            (r'\{', Punctuation, 'insideBrace'),
            (r'.', Text)
        ],
        'insideParen': [
            (r'\)', Punctuation, '#pop'),
            include('root'),
        ],
        'insideMethodDeclArgs': [
            (r'\)', Punctuation, '#pop'),
            (s(r'($type)(\s+)($id)(\s*)(\))'),
             bygroups(using(this, state='inType'), Text, Name.Variable,
                      Text, Punctuation), '#pop'),
            include('root'),
        ],
        'insideBrace': [
            (r'\}', Punctuation, '#pop'),
            include('root'),
        ],
        'inheritance': [
            (r'\s+', Text),                                      #Whitespace
            (r':|,', Punctuation),
            (r'(?:(\w+)(::))?(\w+)',
             bygroups(Name.Namespace, Punctuation, Name.Class)),
            (r'{', Punctuation, '#pop')
        ],
        'using': [
            (r'[ \t]+', Text), # consume whitespaces
            (r'(\[)(\w+)(\])',
             bygroups(Punctuation, Comment.Special, Punctuation)), #ffi
            (r'(\")?([\w\.]+)(\")?',
             bygroups(Punctuation, Name.Namespace, Punctuation)), #podname
            (r'::', Punctuation, 'usingClass'),
            default('#pop')
        ],
        'usingClass': [
            (r'[ \t]+', Text), # consume whitespaces
            (r'(as)(\s+)(\w+)',
             bygroups(Keyword.Declaration, Text, Name.Class), '#pop:2'),
            (r'[\w\$]+', Name.Class),
            default('#pop:2') # jump out to root state
        ],
        'facet': [
            (r'\s+', Text),
            (r'{', Punctuation, 'facetFields'),
            default('#pop')
        ],
        'facetFields': [
            include('comments'),
            include('literals'),
            include('operators'),
            (r'\s+', Text),
            (r'(\s*)(\w+)(\s*)(=)', bygroups(Text, Name, Text, Operator)),
            (r'}', Punctuation, '#pop'),
            (r'.', Text)
        ],
    }


class RustLexer(RegexLexer):
    """
    Lexer for the Rust programming language (version 0.9).

    .. versionadded:: 1.6
    """
    name = 'Rust'
    filenames = ['*.rs']
    aliases = ['rust']
    mimetypes = ['text/x-rustsrc']

    tokens = {
        'root': [
            # Whitespace and Comments
            (r'\n', Text),
            (r'\s+', Text),
            (r'//[/!](.*?)\n', Comment.Doc),
            (r'//(.*?)\n', Comment.Single),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),

            # Keywords
            (r'(as|box|break|continue'
             r'|do|else|enum|extern'
             r'|fn|for|if|impl|in'
             r'|loop|match|mut|priv|proc|pub'
             r'|ref|return|static|\'static|struct|trait|true|type'
             r'|unsafe|while)\b',
             Keyword),
            (r'(alignof|be|const|offsetof|pure|sizeof|typeof|once|unsized'
             r'|yield)\b', Keyword.Reserved),
            (r'(mod|use)\b', Keyword.Namespace),
            (r'(true|false)\b', Keyword.Constant),
            (r'let\b', Keyword.Declaration),
            (r'(u8|u16|u32|u64|i8|i16|i32|i64|uint|int|f32|f64'
             r'|str|bool)\b', Keyword.Type),
            (r'self\b', Name.Builtin.Pseudo),
            # Prelude
            (r'(Freeze|Pod|Send|Sized|Add|Sub|Mul|Div|Rem|Neg|Not|BitAnd'
             r'|BitOr|BitXor|Drop|Shl|Shr|Index|Option|Some|None|Result'
             r'|Ok|Err|from_str|range|print|println|Any|AnyOwnExt|AnyRefExt'
             r'|AnyMutRefExt|Ascii|AsciiCast|OnwedAsciiCast|AsciiStr'
             r'|IntoBytes|Bool|ToCStr|Char|Clone|DeepClone|Eq|ApproxEq'
             r'|Ord|TotalEq|Ordering|Less|Equal|Greater|Equiv|Container'
             r'|Mutable|Map|MutableMap|Set|MutableSet|Default|FromStr'
             r'|Hash|FromIterator|Extendable|Iterator|DoubleEndedIterator'
             r'|RandomAccessIterator|CloneableIterator|OrdIterator'
             r'|MutableDoubleEndedIterator|ExactSize|Times|Algebraic'
             r'|Trigonometric|Exponential|Hyperbolic|Bitwise|BitCount'
             r'|Bounded|Integer|Fractional|Real|RealExt|Num|NumCast'
             r'|CheckedAdd|CheckedSub|CheckedMul|Orderable|Signed'
             r'|Unsigned|Round|Primitive|Int|Float|ToStrRadix'
             r'|ToPrimitive|FromPrimitive|GenericPath|Path|PosixPath'
             r'|WindowsPath|RawPtr|Buffer|Writer|Reader|Seek'
             r'|SendStr|SendStrOwned|SendStrStatic|IntoSendStr|Str'
             r'|StrVector|StrSlice|OwnedStr|IterBytes|ToStr|IntoStr'
             r'|CopyableTuple|ImmutableTuple|ImmutableTuple\d+'
             r'|Tuple\d+|ImmutableEqVector|ImmutableTotalOrdVector'
             r'|ImmutableCopyableVector|OwnedVector|OwnedCopyableVector'
             r'|OwnedEqVector|MutableVector|MutableTotalOrdVector'
             r'|Vector|VectorVector|CopyableVector|ImmutableVector'
             r'|Port|Chan|SharedChan|spawn|drop)\b', Name.Builtin),
            # Borrowed pointer
            (r'(&)(\'[A-Za-z_]\w*)?', bygroups(Operator, Name)),
            # Labels
            (r'\'[A-Za-z_]\w*:', Name.Label),
            # Character Literal
            (r"""'(\\['"\\nrt]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}"""
             r"""|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|.)'""",
             String.Char),
            # Lifetime
            (r"""'[a-zA-Z_]\w*""", Name.Label),
            # Binary Literal
            (r'0b[01_]+', Number.Bin, 'number_lit'),
            # Octal Literal
            (r'0o[0-7_]+', Number.Oct, 'number_lit'),
            # Hexadecimal Literal
            (r'0[xX][0-9a-fA-F_]+', Number.Hex, 'number_lit'),
            # Decimal Literal
            (r'[0-9][0-9_]*(\.[0-9_]+[eE][+\-]?[0-9_]+|'
             r'\.[0-9_]*|[eE][+\-]?[0-9_]+)', Number.Float, 'number_lit'),
            (r'[0-9][0-9_]*', Number.Integer, 'number_lit'),
            # String Literal
            (r'"', String, 'string'),
            (r'r(#*)".*?"\1', String.Raw),

            # Operators and Punctuation
            (r'[{}()\[\],.;]', Punctuation),
            (r'[+\-*/%&|<>^!~@=:?]', Operator),

            # Identifier
            (r'[a-zA-Z_]\w*', Name),

            # Attributes
            (r'#\[', Comment.Preproc, 'attribute['),
            # Macros
            (r'([A-Za-z_]\w*)!\s*([A-Za-z_]\w*)?\s*\{',
             bygroups(Comment.Preproc, Name), 'macro{'),
            (r'([A-Za-z_]\w*)!\s*([A-Za-z_]\w*)?\(',
             bygroups(Comment.Preproc, Name), 'macro('),
        ],
        'number_lit': [
            (r'(([ui](8|16|32|64)?)|(f(32|64)?))?', Keyword, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r"""\\['"\\nrt]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}"""
             r"""|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}""", String.Escape),
            (r'[^\\"]+', String),
            (r'\\', String),
        ],
        'macro{': [
            (r'\{', Operator, '#push'),
            (r'\}', Operator, '#pop'),
        ],
        'macro(': [
            (r'\(', Operator, '#push'),
            (r'\)', Operator, '#pop'),
        ],
        'attribute_common': [
            (r'"', String, 'string'),
            (r'\[', Comment.Preproc, 'attribute['),
            (r'\(', Comment.Preproc, 'attribute('),
        ],
        'attribute[': [
            include('attribute_common'),
            (r'\];?', Comment.Preproc, '#pop'),
            (r'[^"\]]+', Comment.Preproc),
        ],
        'attribute(': [
            include('attribute_common'),
            (r'\);?', Comment.Preproc, '#pop'),
            (r'[^"\)]+', Comment.Preproc),
        ],
    }


class CudaLexer(CLexer):
    """
    For NVIDIA `CUDA™ <http://developer.nvidia.com/category/zone/cuda-zone>`_
    source.

    .. versionadded:: 1.6
    """
    name = 'CUDA'
    filenames = ['*.cu', '*.cuh']
    aliases = ['cuda', 'cu']
    mimetypes = ['text/x-cuda']

    function_qualifiers = ['__device__', '__global__', '__host__',
                           '__noinline__', '__forceinline__']
    variable_qualifiers = ['__device__', '__constant__', '__shared__',
                           '__restrict__']
    vector_types = ['char1', 'uchar1', 'char2', 'uchar2', 'char3', 'uchar3',
                    'char4', 'uchar4', 'short1', 'ushort1', 'short2', 'ushort2',
                    'short3', 'ushort3', 'short4', 'ushort4', 'int1', 'uint1',
                    'int2', 'uint2', 'int3', 'uint3', 'int4', 'uint4', 'long1',
                    'ulong1', 'long2', 'ulong2', 'long3', 'ulong3', 'long4',
                    'ulong4', 'longlong1', 'ulonglong1', 'longlong2',
                    'ulonglong2', 'float1', 'float2', 'float3', 'float4',
                    'double1', 'double2', 'dim3']
    variables = ['gridDim', 'blockIdx', 'blockDim', 'threadIdx', 'warpSize']
    functions = ['__threadfence_block', '__threadfence', '__threadfence_system',
                 '__syncthreads', '__syncthreads_count', '__syncthreads_and',
                 '__syncthreads_or']
    execution_confs = ['<<<', '>>>']

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
            CLexer.get_tokens_unprocessed(self, text):
            if token is Name:
                if value in self.variable_qualifiers:
                    token = Keyword.Type
                elif value in self.vector_types:
                    token = Keyword.Type
                elif value in self.variables:
                    token = Name.Builtin
                elif value in self.execution_confs:
                    token = Keyword.Pseudo
                elif value in self.function_qualifiers:
                    token = Keyword.Reserved
                elif value in self.functions:
                    token = Name.Function
            yield index, token, value


class MonkeyLexer(RegexLexer):
    """
    For
    `Monkey <https://en.wikipedia.org/wiki/Monkey_(programming_language)>`_
    source code.

    .. versionadded:: 1.6
    """

    name = 'Monkey'
    aliases = ['monkey']
    filenames = ['*.monkey']
    mimetypes = ['text/x-monkey']

    name_variable = r'[a-z_]\w*'
    name_function = r'[A-Z]\w*'
    name_constant = r'[A-Z_][A-Z0-9_]*'
    name_class = r'[A-Z]\w*'
    name_module = r'[a-z0-9_]*'

    keyword_type = r'(?:Int|Float|String|Bool|Object|Array|Void)'
    # ? == Bool // % == Int // # == Float // $ == String
    keyword_type_special = r'[?%#$]'

    flags = re.MULTILINE

    tokens = {
        'root': [
            #Text
            (r'\s+', Text),
            # Comments
            (r"'.*", Comment),
            (r'(?i)^#rem\b', Comment.Multiline, 'comment'),
            # preprocessor directives
            (r'(?i)^(?:#If|#ElseIf|#Else|#EndIf|#End|#Print|#Error)\b', Comment.Preproc),
            # preprocessor variable (any line starting with '#' that is not a directive)
            (r'^#', Comment.Preproc, 'variables'),
            # String
            ('"', String.Double, 'string'),
            # Numbers
            (r'[0-9]+\.[0-9]*(?!\.)', Number.Float),
            (r'\.[0-9]+(?!\.)', Number.Float),
            (r'[0-9]+', Number.Integer),
            (r'\$[0-9a-fA-Z]+', Number.Hex),
            (r'\%[10]+', Number.Bin),
            # Native data types
            (r'\b%s\b' % keyword_type, Keyword.Type),
            # Exception handling
            (r'(?i)\b(?:Try|Catch|Throw)\b', Keyword.Reserved),
            (r'Throwable', Name.Exception),
            # Builtins
            (r'(?i)\b(?:Null|True|False)\b', Name.Builtin),
            (r'(?i)\b(?:Self|Super)\b', Name.Builtin.Pseudo),
            (r'\b(?:HOST|LANG|TARGET|CONFIG)\b', Name.Constant),
            # Keywords
            (r'(?i)^(Import)(\s+)(.*)(\n)',
             bygroups(Keyword.Namespace, Text, Name.Namespace, Text)),
            (r'(?i)^Strict\b.*\n', Keyword.Reserved),
            (r'(?i)(Const|Local|Global|Field)(\s+)',
             bygroups(Keyword.Declaration, Text), 'variables'),
            (r'(?i)(New|Class|Interface|Extends|Implements)(\s+)',
             bygroups(Keyword.Reserved, Text), 'classname'),
            (r'(?i)(Function|Method)(\s+)',
             bygroups(Keyword.Reserved, Text), 'funcname'),
            (r'(?i)(?:End|Return|Public|Private|Extern|Property|'
             r'Final|Abstract)\b', Keyword.Reserved),
            # Flow Control stuff
            (r'(?i)(?:If|Then|Else|ElseIf|EndIf|'
             r'Select|Case|Default|'
             r'While|Wend|'
             r'Repeat|Until|Forever|'
             r'For|To|Until|Step|EachIn|Next|'
             r'Exit|Continue)\s+', Keyword.Reserved),
            # not used yet
            (r'(?i)\b(?:Module|Inline)\b', Keyword.Reserved),
            # Array
            (r'[\[\]]', Punctuation),
            # Other
            (r'<=|>=|<>|\*=|/=|\+=|-=|&=|~=|\|=|[-&*/^+=<>|~]', Operator),
            (r'(?i)(?:Not|Mod|Shl|Shr|And|Or)', Operator.Word),
            (r'[\(\){}!#,.:]', Punctuation),
            # catch the rest
            (r'%s\b' % name_constant, Name.Constant),
            (r'%s\b' % name_function, Name.Function),
            (r'%s\b' % name_variable, Name.Variable),
        ],
        'funcname': [
            (r'(?i)%s\b' % name_function, Name.Function),
            (r':', Punctuation, 'classname'),
            (r'\s+', Text),
            (r'\(', Punctuation, 'variables'),
            (r'\)', Punctuation, '#pop')
        ],
        'classname': [
            (r'%s\.' % name_module, Name.Namespace),
            (r'%s\b' % keyword_type, Keyword.Type),
            (r'%s\b' % name_class, Name.Class),
            # array (of given size)
            (r'(\[)(\s*)(\d*)(\s*)(\])',
             bygroups(Punctuation, Text, Number.Integer, Text, Punctuation)),
            # generics
            (r'\s+(?!<)', Text, '#pop'),
            (r'<', Punctuation, '#push'),
            (r'>', Punctuation, '#pop'),
            (r'\n', Text, '#pop'),
            default('#pop')
        ],
        'variables': [
            (r'%s\b' % name_constant, Name.Constant),
            (r'%s\b' % name_variable, Name.Variable),
            (r'%s' % keyword_type_special, Keyword.Type),
            (r'\s+', Text),
            (r':', Punctuation, 'classname'),
            (r',', Punctuation, '#push'),
            default('#pop')
        ],
        'string': [
            (r'[^"~]+', String.Double),
            (r'~q|~n|~r|~t|~z|~~', String.Escape),
            (r'"', String.Double, '#pop'),
        ],
        'comment' : [
            (r'(?i)^#rem.*?', Comment.Multiline, "#push"),
            (r'(?i)^#end.*?', Comment.Multiline, "#pop"),
            (r'\n', Comment.Multiline),
            (r'.+', Comment.Multiline),
        ],
    }


class CobolLexer(RegexLexer):
    """
    Lexer for OpenCOBOL code.

    .. versionadded:: 1.6
    """
    name = 'COBOL'
    aliases = ['cobol']
    filenames = ['*.cob', '*.COB', '*.cpy', '*.CPY']
    mimetypes = ['text/x-cobol']
    flags = re.IGNORECASE | re.MULTILINE

    # Data Types: by PICTURE and USAGE
    # Operators: **, *, +, -, /, <, >, <=, >=, =, <>
    # Logical (?): NOT, AND, OR

    # Reserved words:
    # http://opencobol.add1tocobol.com/#reserved-words
    # Intrinsics:
    # http://opencobol.add1tocobol.com/#does-opencobol-implement-any-intrinsic-functions

    tokens = {
        'root': [
            include('comment'),
            include('strings'),
            include('core'),
            include('nums'),
            (r'[a-z0-9]([_a-z0-9\-]*[a-z0-9]+)?', Name.Variable),
    #       (r'[\s]+', Text),
            (r'[ \t]+', Text),
        ],
        'comment': [
            (r'(^.{6}[*/].*\n|^.{6}|\*>.*\n)', Comment),
        ],
        'core': [
            # Figurative constants
            (r'(^|(?<=[^0-9a-z_\-]))(ALL\s+)?'
             r'((ZEROES)|(HIGH-VALUE|LOW-VALUE|QUOTE|SPACE|ZERO)(S)?)'
             r'\s*($|(?=[^0-9a-z_\-]))',
             Name.Constant),

            # Reserved words STATEMENTS and other bolds
            (r'(^|(?<=[^0-9a-z_\-]))'
             r'(ACCEPT|ADD|ALLOCATE|CALL|CANCEL|CLOSE|COMPUTE|'
             r'CONFIGURATION|CONTINUE|'
             r'DATA|DELETE|DISPLAY|DIVIDE|DIVISION|ELSE|END|END-ACCEPT|'
             r'END-ADD|END-CALL|END-COMPUTE|END-DELETE|END-DISPLAY|'
             r'END-DIVIDE|END-EVALUATE|END-IF|END-MULTIPLY|END-OF-PAGE|'
             r'END-PERFORM|END-READ|END-RETURN|END-REWRITE|END-SEARCH|'
             r'END-START|END-STRING|END-SUBTRACT|END-UNSTRING|END-WRITE|'
             r'ENVIRONMENT|EVALUATE|EXIT|FD|FILE|FILE-CONTROL|FOREVER|'
             r'FREE|GENERATE|GO|GOBACK|'
             r'IDENTIFICATION|IF|INITIALIZE|'
             r'INITIATE|INPUT-OUTPUT|INSPECT|INVOKE|I-O-CONTROL|LINKAGE|'
             r'LOCAL-STORAGE|MERGE|MOVE|MULTIPLY|OPEN|'
             r'PERFORM|PROCEDURE|PROGRAM-ID|RAISE|READ|RELEASE|RESUME|'
             r'RETURN|REWRITE|SCREEN|'
             r'SD|SEARCH|SECTION|SET|SORT|START|STOP|STRING|SUBTRACT|'
             r'SUPPRESS|TERMINATE|THEN|UNLOCK|UNSTRING|USE|VALIDATE|'
             r'WORKING-STORAGE|WRITE)'
             r'\s*($|(?=[^0-9a-z_\-]))', Keyword.Reserved),

            # Reserved words
            (r'(^|(?<=[^0-9a-z_\-]))'
             r'(ACCESS|ADDRESS|ADVANCING|AFTER|ALL|'
             r'ALPHABET|ALPHABETIC|ALPHABETIC-LOWER|ALPHABETIC-UPPER|'
             r'ALPHANUMERIC|ALPHANUMERIC-EDITED|ALSO|ALTER|ALTERNATE'
             r'ANY|ARE|AREA|AREAS|ARGUMENT-NUMBER|ARGUMENT-VALUE|AS|'
             r'ASCENDING|ASSIGN|AT|AUTO|AUTO-SKIP|AUTOMATIC|AUTOTERMINATE|'
             r'BACKGROUND-COLOR|BASED|BEEP|BEFORE|BELL|'
             r'BLANK|'
             r'BLINK|BLOCK|BOTTOM|BY|BYTE-LENGTH|CHAINING|'
             r'CHARACTER|CHARACTERS|CLASS|CODE|CODE-SET|COL|COLLATING|'
             r'COLS|COLUMN|COLUMNS|COMMA|COMMAND-LINE|COMMIT|COMMON|'
             r'CONSTANT|CONTAINS|CONTENT|CONTROL|'
             r'CONTROLS|CONVERTING|COPY|CORR|CORRESPONDING|COUNT|CRT|'
             r'CURRENCY|CURSOR|CYCLE|DATE|DAY|DAY-OF-WEEK|DE|DEBUGGING|'
             r'DECIMAL-POINT|DECLARATIVES|DEFAULT|DELIMITED|'
             r'DELIMITER|DEPENDING|DESCENDING|DETAIL|DISK|'
             r'DOWN|DUPLICATES|DYNAMIC|EBCDIC|'
             r'ENTRY|ENVIRONMENT-NAME|ENVIRONMENT-VALUE|EOL|EOP|'
             r'EOS|ERASE|ERROR|ESCAPE|EXCEPTION|'
             r'EXCLUSIVE|EXTEND|EXTERNAL|'
             r'FILE-ID|FILLER|FINAL|FIRST|FIXED|FLOAT-LONG|FLOAT-SHORT|'
             r'FOOTING|FOR|FOREGROUND-COLOR|FORMAT|FROM|FULL|FUNCTION|'
             r'FUNCTION-ID|GIVING|GLOBAL|GROUP|'
             r'HEADING|HIGHLIGHT|I-O|ID|'
             r'IGNORE|IGNORING|IN|INDEX|INDEXED|INDICATE|'
             r'INITIAL|INITIALIZED|INPUT|'
             r'INTO|INTRINSIC|INVALID|IS|JUST|JUSTIFIED|KEY|LABEL|'
             r'LAST|LEADING|LEFT|LENGTH|LIMIT|LIMITS|LINAGE|'
             r'LINAGE-COUNTER|LINE|LINES|LOCALE|LOCK|'
             r'LOWLIGHT|MANUAL|MEMORY|MINUS|MODE|'
             r'MULTIPLE|NATIONAL|NATIONAL-EDITED|NATIVE|'
             r'NEGATIVE|NEXT|NO|NULL|NULLS|NUMBER|NUMBERS|NUMERIC|'
             r'NUMERIC-EDITED|OBJECT-COMPUTER|OCCURS|OF|OFF|OMITTED|ON|ONLY|'
             r'OPTIONAL|ORDER|ORGANIZATION|OTHER|OUTPUT|OVERFLOW|'
             r'OVERLINE|PACKED-DECIMAL|PADDING|PAGE|PARAGRAPH|'
             r'PLUS|POINTER|POSITION|POSITIVE|PRESENT|PREVIOUS|'
             r'PRINTER|PRINTING|PROCEDURE-POINTER|PROCEDURES|'
             r'PROCEED|PROGRAM|PROGRAM-POINTER|PROMPT|QUOTE|'
             r'QUOTES|RANDOM|RD|RECORD|RECORDING|RECORDS|RECURSIVE|'
             r'REDEFINES|REEL|REFERENCE|RELATIVE|REMAINDER|REMOVAL|'
             r'RENAMES|REPLACING|REPORT|REPORTING|REPORTS|REPOSITORY|'
             r'REQUIRED|RESERVE|RETURNING|REVERSE-VIDEO|REWIND|'
             r'RIGHT|ROLLBACK|ROUNDED|RUN|SAME|SCROLL|'
             r'SECURE|SEGMENT-LIMIT|SELECT|SENTENCE|SEPARATE|'
             r'SEQUENCE|SEQUENTIAL|SHARING|SIGN|SIGNED|SIGNED-INT|'
             r'SIGNED-LONG|SIGNED-SHORT|SIZE|SORT-MERGE|SOURCE|'
             r'SOURCE-COMPUTER|SPECIAL-NAMES|STANDARD|'
             r'STANDARD-1|STANDARD-2|STATUS|SUM|'
             r'SYMBOLIC|SYNC|SYNCHRONIZED|TALLYING|TAPE|'
             r'TEST|THROUGH|THRU|TIME|TIMES|TO|TOP|TRAILING|'
             r'TRANSFORM|TYPE|UNDERLINE|UNIT|UNSIGNED|'
             r'UNSIGNED-INT|UNSIGNED-LONG|UNSIGNED-SHORT|UNTIL|UP|'
             r'UPDATE|UPON|USAGE|USING|VALUE|VALUES|VARYING|WAIT|WHEN|'
             r'WITH|WORDS|YYYYDDD|YYYYMMDD)'
             r'\s*($|(?=[^0-9a-z_\-]))', Keyword.Pseudo),

            # inactive reserved words
            (r'(^|(?<=[^0-9a-z_\-]))'
             r'(ACTIVE-CLASS|ALIGNED|ANYCASE|ARITHMETIC|ATTRIBUTE|B-AND|'
             r'B-NOT|B-OR|B-XOR|BIT|BOOLEAN|CD|CENTER|CF|CH|CHAIN|CLASS-ID|'
             r'CLASSIFICATION|COMMUNICATION|CONDITION|DATA-POINTER|'
             r'DESTINATION|DISABLE|EC|EGI|EMI|ENABLE|END-RECEIVE|'
             r'ENTRY-CONVENTION|EO|ESI|EXCEPTION-OBJECT|EXPANDS|FACTORY|'
             r'FLOAT-BINARY-16|FLOAT-BINARY-34|FLOAT-BINARY-7|'
             r'FLOAT-DECIMAL-16|FLOAT-DECIMAL-34|FLOAT-EXTENDED|FORMAT|'
             r'FUNCTION-POINTER|GET|GROUP-USAGE|IMPLEMENTS|INFINITY|'
             r'INHERITS|INTERFACE|INTERFACE-ID|INVOKE|LC_ALL|LC_COLLATE|'
             r'LC_CTYPE|LC_MESSAGES|LC_MONETARY|LC_NUMERIC|LC_TIME|'
             r'LINE-COUNTER|MESSAGE|METHOD|METHOD-ID|NESTED|NONE|NORMAL|'
             r'OBJECT|OBJECT-REFERENCE|OPTIONS|OVERRIDE|PAGE-COUNTER|PF|PH|'
             r'PROPERTY|PROTOTYPE|PURGE|QUEUE|RAISE|RAISING|RECEIVE|'
             r'RELATION|REPLACE|REPRESENTS-NOT-A-NUMBER|RESET|RESUME|RETRY|'
             r'RF|RH|SECONDS|SEGMENT|SELF|SEND|SOURCES|STATEMENT|STEP|'
             r'STRONG|SUB-QUEUE-1|SUB-QUEUE-2|SUB-QUEUE-3|SUPER|SYMBOL|'
             r'SYSTEM-DEFAULT|TABLE|TERMINAL|TEXT|TYPEDEF|UCS-4|UNIVERSAL|'
             r'USER-DEFAULT|UTF-16|UTF-8|VAL-STATUS|VALID|VALIDATE|'
             r'VALIDATE-STATUS)\s*($|(?=[^0-9a-z_\-]))', Error),

            # Data Types
            (r'(^|(?<=[^0-9a-z_\-]))'
             r'(PIC\s+.+?(?=(\s|\.\s))|PICTURE\s+.+?(?=(\s|\.\s))|'
             r'(COMPUTATIONAL)(-[1-5X])?|(COMP)(-[1-5X])?|'
             r'BINARY-C-LONG|'
             r'BINARY-CHAR|BINARY-DOUBLE|BINARY-LONG|BINARY-SHORT|'
             r'BINARY)\s*($|(?=[^0-9a-z_\-]))', Keyword.Type),

            # Operators
            (r'(\*\*|\*|\+|-|/|<=|>=|<|>|==|/=|=)', Operator),

            # (r'(::)', Keyword.Declaration),

            (r'([(),;:&%.])', Punctuation),

            # Intrinsics
            (r'(^|(?<=[^0-9a-z_\-]))(ABS|ACOS|ANNUITY|ASIN|ATAN|BYTE-LENGTH|'
             r'CHAR|COMBINED-DATETIME|CONCATENATE|COS|CURRENT-DATE|'
             r'DATE-OF-INTEGER|DATE-TO-YYYYMMDD|DAY-OF-INTEGER|DAY-TO-YYYYDDD|'
             r'EXCEPTION-(?:FILE|LOCATION|STATEMENT|STATUS)|EXP10|EXP|E|'
             r'FACTORIAL|FRACTION-PART|INTEGER-OF-(?:DATE|DAY|PART)|INTEGER|'
             r'LENGTH|LOCALE-(?:DATE|TIME(?:-FROM-SECONDS)?)|LOG10|LOG|'
             r'LOWER-CASE|MAX|MEAN|MEDIAN|MIDRANGE|MIN|MOD|NUMVAL(?:-C)?|'
             r'ORD(?:-MAX|-MIN)?|PI|PRESENT-VALUE|RANDOM|RANGE|REM|REVERSE|'
             r'SECONDS-FROM-FORMATTED-TIME|SECONDS-PAST-MIDNIGHT|SIGN|SIN|SQRT|'
             r'STANDARD-DEVIATION|STORED-CHAR-LENGTH|SUBSTITUTE(?:-CASE)?|'
             r'SUM|TAN|TEST-DATE-YYYYMMDD|TEST-DAY-YYYYDDD|TRIM|'
             r'UPPER-CASE|VARIANCE|WHEN-COMPILED|YEAR-TO-YYYY)\s*'
             r'($|(?=[^0-9a-z_\-]))', Name.Function),

            # Booleans
            (r'(^|(?<=[^0-9a-z_\-]))(true|false)\s*($|(?=[^0-9a-z_\-]))', Name.Builtin),
            # Comparing Operators
            (r'(^|(?<=[^0-9a-z_\-]))(equal|equals|ne|lt|le|gt|ge|'
             r'greater|less|than|not|and|or)\s*($|(?=[^0-9a-z_\-]))', Operator.Word),
        ],

        # \"[^\"\n]*\"|\'[^\'\n]*\'
        'strings': [
            # apparently strings can be delimited by EOL if they are continued
            # in the next line
            (r'"[^"\n]*("|\n)', String.Double),
            (r"'[^'\n]*('|\n)", String.Single),
        ],

        'nums': [
            (r'\d+(\s*|\.$|$)', Number.Integer),
            (r'[+-]?\d*\.\d+([eE][-+]?\d+)?', Number.Float),
            (r'[+-]?\d+\.\d*([eE][-+]?\d+)?', Number.Float),
        ],
    }


class CobolFreeformatLexer(CobolLexer):
    """
    Lexer for Free format OpenCOBOL code.

    .. versionadded:: 1.6
    """
    name = 'COBOLFree'
    aliases = ['cobolfree']
    filenames = ['*.cbl', '*.CBL']
    mimetypes = []
    flags = re.IGNORECASE | re.MULTILINE

    tokens = {
        'comment': [
            (r'(\*>.*\n|^\w*\*.*$)', Comment),
        ],
    }


class LogosLexer(ObjectiveCppLexer):
    """
    For Logos + Objective-C source code with preprocessor directives.

    .. versionadded:: 1.6
    """

    name = 'Logos'
    aliases = ['logos']
    filenames = ['*.x', '*.xi', '*.xm', '*.xmi']
    mimetypes = ['text/x-logos']
    priority = 0.25

    tokens = {
        'statements': [
            (r'(%orig|%log)\b', Keyword),
            (r'(%c)\b(\()(\s*)([a-zA-Z$_][\w$]*)(\s*)(\))',
             bygroups(Keyword, Punctuation, Text, Name.Class, Text, Punctuation)),
            (r'(%init)\b(\()',
             bygroups(Keyword, Punctuation), 'logos_init_directive'),
            (r'(%init)(?=\s*;)', bygroups(Keyword)),
            (r'(%hook|%group)(\s+)([a-zA-Z$_][\w$]+)',
             bygroups(Keyword, Text, Name.Class), '#pop'),
            (r'(%subclass)(\s+)', bygroups(Keyword, Text),
            ('#pop', 'logos_classname')),
            inherit,
        ],
        'logos_init_directive' : [
            ('\s+', Text),
            (',', Punctuation, ('logos_init_directive', '#pop')),
            ('([a-zA-Z$_][\w$]*)(\s*)(=)(\s*)([^);]*)',
             bygroups(Name.Class, Text, Punctuation, Text, Text)),
            ('([a-zA-Z$_][\w$]*)', Name.Class),
            ('\)', Punctuation, '#pop'),
        ],
        'logos_classname' : [
            ('([a-zA-Z$_][\w$]*)(\s*:\s*)([a-zA-Z$_][\w$]*)?',
             bygroups(Name.Class, Text, Name.Class), '#pop'),
            ('([a-zA-Z$_][\w$]*)', Name.Class, '#pop')
        ],
        'root': [
            (r'(%subclass)(\s+)', bygroups(Keyword, Text),
             'logos_classname'),
            (r'(%hook|%group)(\s+)([a-zA-Z$_][\w$]+)',
             bygroups(Keyword, Text, Name.Class)),
            (r'(%config)(\s*\(\s*)(\w+)(\s*=\s*)(.*?)(\s*\)\s*)',
             bygroups(Keyword, Text, Name.Variable, Text, String, Text)),
            (r'(%ctor)(\s*)({)', bygroups(Keyword, Text, Punctuation),
             'function'),
            (r'(%new)(\s*)(\()(\s*.*?\s*)(\))',
             bygroups(Keyword, Text, Keyword, String, Keyword)),
            (r'(\s*)(%end)(\s*)', bygroups(Text, Keyword, Text)),
            inherit,
        ],
    }

    _logos_keywords = re.compile(r'%(?:hook|ctor|init|c\()')

    def analyse_text(text):
        if LogosLexer._logos_keywords.search(text):
            return 1.0
        return 0


class ChapelLexer(RegexLexer):
    """
    For `Chapel <http://chapel.cray.com/>`_ source.

    .. versionadded:: 2.0
    """
    name = 'Chapel'
    filenames = ['*.chpl']
    aliases = ['chapel', 'chpl']
    # mimetypes = ['text/x-chapel']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),

            (r'//(.*?)\n', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),

            (r'(config|const|in|inout|out|param|ref|type|var)\b',
             Keyword.Declaration),
            (r'(false|nil|true)\b', Keyword.Constant),
            (r'(bool|complex|imag|int|opaque|range|real|string|uint)\b',
             Keyword.Type),
            (r'(atomic|begin|break|by|cobegin|coforall|continue|iter|'
             r'delete|dmapped|do|domain|else|enum|export|extern|for|forall|'
             r'if|index|inline|label|lambda|let|local|new|on|otherwise|'
             r'reduce|return|scan|select|serial|single|sparse|'
             r'subdomain|sync|then|use|when|where|while|yield|zip)\b',
             Keyword),
            (r'(proc)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'procname'),
            (r'(class|module|record|union)(\s+)', bygroups(Keyword, Text),
             'classname'),

            # imaginary integers
            (r'\d+i', Number),
            (r'\d+\.\d*([Ee][-+]\d+)?i', Number),
            (r'\.\d+([Ee][-+]\d+)?i', Number),
            (r'\d+[Ee][-+]\d+i', Number),

            # reals cannot end with a period due to lexical ambiguity with
            # .. operator. See reference for rationale.
            (r'(\d*\.\d+)([eE][+-]?[0-9]+)?i?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+i?', Number.Float),

            # integer literals
            # -- binary
            (r'0[bB][0-1]+', Number.Bin),
            # -- hex
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            # -- decimal
            (r'(0|[1-9][0-9]*)', Number.Integer),

            # strings
            (r'["\'](\\\\|\\"|[^"\'])*["\']', String),

            # tokens
            (r'(=|\+=|-=|\*=|/=|\*\*=|%=|&=|\|=|\^=|&&=|\|\|=|<<=|>>=|'
             r'<=>|\.\.|by|#|\.\.\.|'
             r'&&|\|\||!|&|\||\^|~|<<|>>|'
             r'==|!=|<=|>=|<|>|'
             r'[+\-*/%]|\*\*)', Operator),
            (r'[:;,.?()\[\]{}]', Punctuation),

            # identifiers
            (r'[a-zA-Z_][\w$]*', Name.Other),
        ],
        'classname': [
            (r'[a-zA-Z_][\w$]*', Name.Class, '#pop'),
        ],
        'procname': [
            (r'[a-zA-Z_][\w$]*', Name.Function, '#pop'),
        ],
    }


class EiffelLexer(RegexLexer):
    """
    For `Eiffel <http://www.eiffel.com>`_ source code.

    .. versionadded:: 2.0
    """
    name = 'Eiffel'
    aliases = ['eiffel']
    filenames = ['*.e']
    mimetypes = ['text/x-eiffel']

    tokens = {
        'root': [
            (r'[^\S\n]+', Text),
            (r'--.*?\n', Comment.Single),
            (r'[^\S\n]+', Text),
                # Please note that keyword and operator are case insensitive.
            (r'(?i)(true|false|void|current|result|precursor)\b', Keyword.Constant),
            (r'(?i)(and(\s+then)?|not|xor|implies|or(\s+else)?)\b', Operator.Word),
            (r'(?i)\b(across|agent|alias|all|as|assign|attached|attribute|check|'
                r'class|convert|create|debug|deferred|detachable|do|else|elseif|'
                r'end|ensure|expanded|export|external|feature|from|frozen|if|'
                r'inherit|inspect|invariant|like|local|loop|none|note|obsolete|'
                r'old|once|only|redefine|rename|require|rescue|retry|select|'
                r'separate|then|undefine|until|variant|when)\b',Keyword.Reserved),
            (r'"\[(([^\]%]|\n)|%(.|\n)|\][^"])*?\]"', String),
            (r'"([^"%\n]|%.)*?"', String),
            include('numbers'),
            (r"'([^'%]|%'|%%)'", String.Char),
            (r"(//|\\\\|>=|<=|:=|/=|~|/~|[\\\?!#%&@|+/\-=\>\*$<|^\[\]])", Operator),
            (r"([{}():;,.])", Punctuation),
            (r'([a-z]\w*)|([A-Z][A-Z0-9_]*[a-z]\w*)', Name),
            (r'([A-Z][A-Z0-9_]*)', Name.Class),
            (r'\n+', Text),
        ],
        'numbers': [
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'0[bB][0-1]+', Number.Bin),
            (r'0[cC][0-7]+', Number.Oct),
            (r'([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)', Number.Float),
            (r'[0-9]+', Number.Integer),
        ],
    }


class Inform6Lexer(RegexLexer):
    """
    For `Inform 6 <http://inform-fiction.org/>`_ source code.

    .. versionadded:: 2.0
    """

    name = 'Inform 6'
    aliases = ['inform6', 'i6']
    filenames = ['*.inf']

    flags = re.MULTILINE | re.DOTALL | re.UNICODE

    _name = r'[a-zA-Z_][a-zA-Z_0-9]*'

    # Inform 7 maps these four character classes to their ASCII
    # equivalents. To support Inform 6 inclusions within Inform 7,
    # Inform6Lexer maps them too.
    _dash = u'\\-\u2010-\u2014'
    _dquote = u'"\u201c\u201d'
    _squote = u"'\u2018\u2019"
    _newline = u'\\n\u0085\u2028\u2029'

    tokens = {
        'root': [
            (r'(\A(!%%[^%s]*[%s])+)?' % (_newline, _newline), Comment.Preproc,
             'directive')
        ],
        '_whitespace': [
            (r'\s+', Text),
            (r'![^%s]*' % _newline, Comment.Single)
        ],
        'default': [
            include('_whitespace'),
            (r'\[', Punctuation, 'many-values'),  # Array initialization
            (r':|(?=;)', Punctuation, '#pop'),
            (r'<', Punctuation),  # Second angle bracket in an action statement
            default(('expression', '_expression'))
        ],

        # Expressions
        '_expression': [
            include('_whitespace'),
            (r'(?=sp\b)', Text, '#pop'),
            (r'(?=[%s%s$0-9#a-zA-Z_])' % (_dquote, _squote), Text,
             ('#pop', 'value')),
            (r'\+\+|[%s]{1,2}(?!>)|~~?' % _dash, Operator),
            (r'(?=[()\[%s,?@{:;])' % _dash, Text, '#pop')
        ],
        'expression': [
            include('_whitespace'),
            (r'\(', Punctuation, ('expression', '_expression')),
            (r'\)', Punctuation, '#pop'),
            (r'\[', Punctuation, ('#pop', 'statements', 'locals')),
            (r'>(?=(\s+|(![^%s]*))*[>;])' % _newline, Punctuation),
            (r'\+\+|[%s]{2}(?!>)' % _dash, Operator),
            (r',', Punctuation, '_expression'),
            (r'&&?|\|\|?|[=~><]?=|[%s]{1,2}>?|\.\.?[&#]?|::|[<>+*/%%]' % _dash,
             Operator, '_expression'),
            (r'(has|hasnt|in|notin|ofclass|or|provides)\b', Operator.Word,
             '_expression'),
            (r'sp\b', Name),
            (r'\?~?', Name.Label, 'label?'),
            (r'[@{]', Error),
            default('#pop')
        ],
        '_assembly-expression': [
            (r'\(', Punctuation, ('#push', '_expression')),
            (r'[\[\]]', Punctuation),
            (r'[%s]>' % _dash, Punctuation, '_expression'),
            (r'sp\b', Keyword.Pseudo),
            (r';', Punctuation, '#pop:3'),
            include('expression')
        ],
        '_for-expression': [
            (r'\)', Punctuation, '#pop:2'),
            (r':', Punctuation, '#pop'),
            include('expression')
        ],
        '_keyword-expression': [
            (r'(from|near|to)\b', Keyword, '_expression'),
            include('expression')
        ],
        '_list-expression': [
            (r',', Punctuation, '#pop'),
            include('expression')
        ],
        '_object-expression': [
            (r'has\b', Keyword.Declaration, '#pop'),
            include('_list-expression')
        ],

        # Values
        'value': [
            include('_whitespace'),
            # Strings
            (r'[%s][^@][%s]' % (_squote, _squote), String.Char, '#pop'),
            (r'([%s])(@{[0-9a-fA-F]{1,4}})([%s])' % (_squote, _squote),
             bygroups(String.Char, String.Escape, String.Char), '#pop'),
            (r'([%s])(@..)([%s])' % (_squote, _squote),
             bygroups(String.Char, String.Escape, String.Char), '#pop'),
            (r'[%s]' % _squote, String.Single, ('#pop', 'dictionary-word')),
            (r'[%s]' % _dquote, String.Double, ('#pop', 'string')),
            # Numbers
            (r'\$[+%s][0-9]*\.?[0-9]*([eE][+%s]?[0-9]+)?' % (_dash, _dash),
             Number.Float, '#pop'),
            (r'\$[0-9a-fA-F]+', Number.Hex, '#pop'),
            (r'\$\$[01]+', Number.Bin, '#pop'),
            (r'[0-9]+', Number.Integer, '#pop'),
            # Values prefixed by hashes
            (r'(##|#a\$)(%s)' % _name, bygroups(Operator, Name), '#pop'),
            (r'(#g\$)(%s)' % _name,
             bygroups(Operator, Name.Variable.Global), '#pop'),
            (r'#[nw]\$', Operator, ('#pop', 'obsolete-dictionary-word')),
            (r'(#r\$)(%s)' % _name, bygroups(Operator, Name.Function), '#pop'),
            (r'#', Name.Builtin, ('#pop', 'system-constant')),
            # System functions
            (r'(child|children|elder|eldest|glk|indirect|metaclass|parent|'
             r'random|sibling|younger|youngest)\b', Name.Builtin, '#pop'),
            # Metaclasses
            (r'(?i)(Class|Object|Routine|String)\b', Name.Builtin, '#pop'),
            # Veneer routines
            (r'(?i)(Box__Routine|CA__Pr|CDefArt|CInDefArt|Cl__Ms|'
             r'Copy__Primitive|CP__Tab|DA__Pr|DB__Pr|DefArt|Dynam__String|'
             r'EnglishNumber|Glk__Wrap|IA__Pr|IB__Pr|InDefArt|Main__|'
             r'Meta__class|OB__Move|OB__Remove|OC__Cl|OP__Pr|Print__Addr|'
             r'Print__PName|PrintShortName|RA__Pr|RA__Sc|RL__Pr|R_Process|'
             r'RT__ChG|RT__ChGt|RT__ChLDB|RT__ChLDW|RT__ChPR|RT__ChPrintA|'
             r'RT__ChPrintC|RT__ChPrintO|RT__ChPrintS|RT__ChPS|RT__ChR|'
             r'RT__ChSTB|RT__ChSTW|RT__ChT|RT__Err|RT__TrPS|RV__Pr|'
             r'Symb__Tab|Unsigned__Compare|WV__Pr|Z__Region)\b', Name.Builtin,
             '#pop'),
            # Other built-in symbols
            (r'(?i)(call|copy|create|DEBUG|destroy|DICT_CHAR_SIZE|'
             r'DICT_ENTRY_BYTES|DICT_IS_UNICODE|DICT_WORD_SIZE|false|'
             r'FLOAT_INFINITY|FLOAT_NAN|FLOAT_NINFINITY|GOBJFIELD_CHAIN|'
             r'GOBJFIELD_CHILD|GOBJFIELD_NAME|GOBJFIELD_PARENT|'
             r'GOBJFIELD_PROPTAB|GOBJFIELD_SIBLING|GOBJ_EXT_START|'
             r'GOBJ_TOTAL_LENGTH|Grammar__Version|INDIV_PROP_START|INFIX|'
             r'infix__watching|MODULE_MODE|name|nothing|NUM_ATTR_BYTES|print|'
             r'print_to_array|recreate|remaining|self|sender|STRICT_MODE|'
             r'sw__var|sys__glob0|sys__glob1|sys__glob2|sys_statusline_flag|'
             r'TARGET_GLULX|TARGET_ZCODE|temp__global2|temp__global3|'
             r'temp__global4|temp_global|true|USE_MODULES|WORDSIZE)\b',
             Name.Builtin, '#pop'),
            # Other values
            (_name, Name, '#pop')
        ],
        # Strings
        'dictionary-word': [
            (r'[~^]+', String.Escape),
            (r'[^~^\\@({%s]+' % _squote, String.Single),
            (r'[({]', String.Single),
            (r'@{[0-9a-fA-F]{,4}}', String.Escape),
            (r'@..', String.Escape),
            (r'[%s]' % _squote, String.Single, '#pop')
        ],
        'string': [
            (r'[~^]+', String.Escape),
            (r'[^~^\\@({%s]+' % _dquote, String.Double),
            (r'[({]', String.Double),
            (r'\\', String.Escape),
            (r'@(\\\s*[%s]\s*)*@((\\\s*[%s]\s*)*[0-9])*' %
             (_newline, _newline), String.Escape),
            (r'@(\\\s*[%s]\s*)*{((\\\s*[%s]\s*)*[0-9a-fA-F]){,4}'
             r'(\\\s*[%s]\s*)*}' % (_newline, _newline, _newline),
             String.Escape),
            (r'@(\\\s*[%s]\s*)*.(\\\s*[%s]\s*)*.' % (_newline, _newline),
             String.Escape),
            (r'[%s]' % _dquote, String.Double, '#pop')
        ],
        'plain-string': [
            (r'[^~^\\({\[\]%s]+' % _dquote, String.Double),
            (r'[~^({\[\]]', String.Double),
            (r'\\', String.Escape),
            (r'[%s]' % _dquote, String.Double, '#pop')
        ],
        # Names
        '_constant': [
            include('_whitespace'),
            (_name, Name.Constant, '#pop'),
            include('value')
        ],
        '_global': [
            include('_whitespace'),
            (_name, Name.Variable.Global, '#pop'),
            include('value')
        ],
        'label?': [
            include('_whitespace'),
            (r'(%s)?' % _name, Name.Label, '#pop')
        ],
        'variable?': [
            include('_whitespace'),
            (r'(%s)?' % _name, Name.Variable, '#pop')
        ],
        # Values after hashes
        'obsolete-dictionary-word': [
            (r'\S[a-zA-Z_0-9]*', String.Other, '#pop')
        ],
        'system-constant': [
            include('_whitespace'),
            (_name, Name.Builtin, '#pop')
        ],

        # Directives
        'directive': [
            include('_whitespace'),
            (r'#', Punctuation),
            (r';', Punctuation, '#pop'),
            (r'\[', Punctuation,
             ('default', 'statements', 'locals', 'routine-name?')),
            (r'(?i)(abbreviate|endif|dictionary|ifdef|iffalse|ifndef|ifnot|'
             r'iftrue|ifv3|ifv5|release|serial|switches|system_file|version)'
             r'\b', Keyword, 'default'),
            (r'(?i)(array|global)\b', Keyword,
             ('default', 'directive-keyword?', '_global')),
            (r'(?i)attribute\b', Keyword, ('default', 'alias?', '_constant')),
            (r'(?i)class\b', Keyword,
             ('object-body', 'duplicates', 'class-name')),
            (r'(?i)(constant|default)\b', Keyword,
             ('default', 'expression', '_constant')),
            (r'(?i)(end\b)(.*)', bygroups(Keyword, Text)),
            (r'(?i)(extend|verb)\b', Keyword, 'grammar'),
            (r'(?i)fake_action\b', Keyword, ('default', '_constant')),
            (r'(?i)import\b', Keyword, 'manifest'),
            (r'(?i)(include|link)\b', Keyword,
             ('default', 'before-plain-string')),
            (r'(?i)(lowstring|undef)\b', Keyword, ('default', '_constant')),
            (r'(?i)message\b', Keyword, ('default', 'diagnostic')),
            (r'(?i)(nearby|object)\b', Keyword,
             ('object-body', '_object-head')),
            (r'(?i)property\b', Keyword,
             ('default', 'alias?', '_constant', 'property-keyword*')),
            (r'(?i)replace\b', Keyword,
             ('default', 'routine-name?', 'routine-name?')),
            (r'(?i)statusline\b', Keyword, ('default', 'directive-keyword?')),
            (r'(?i)stub\b', Keyword, ('default', 'routine-name?')),
            (r'(?i)trace\b', Keyword,
             ('default', 'trace-keyword?', 'trace-keyword?')),
            (r'(?i)zcharacter\b', Keyword,
             ('default', 'directive-keyword?', 'directive-keyword?')),
            (_name, Name.Class, ('object-body', '_object-head'))
        ],
        # [, Replace, Stub
        'routine-name?': [
            include('_whitespace'),
            (r'(%s)?' % _name, Name.Function, '#pop')
        ],
        'locals': [
            include('_whitespace'),
            (r';', Punctuation, '#pop'),
            (r'\*', Punctuation),
            (_name, Name.Variable)
        ],
        # Array
        'many-values': [
            include('_whitespace'),
            (r';', Punctuation),
            (r'\]', Punctuation, '#pop'),
            (r':', Error),
            default(('expression', '_expression'))
        ],
        # Attribute, Property
        'alias?': [
            include('_whitespace'),
            (r'alias\b', Keyword, ('#pop', '_constant')),
            default('#pop')
        ],
        # Class, Object, Nearby
        'class-name': [
            include('_whitespace'),
            (r'(?=[,;]|(class|has|private|with)\b)', Text, '#pop'),
            (_name, Name.Class, '#pop')
        ],
        'duplicates': [
            include('_whitespace'),
            (r'\(', Punctuation, ('#pop', 'expression', '_expression')),
            default('#pop')
        ],
        '_object-head': [
            (r'[%s]>' % _dash, Punctuation),
            (r'(class|has|private|with)\b', Keyword.Declaration, '#pop'),
            include('_global')
        ],
        'object-body': [
            include('_whitespace'),
            (r';', Punctuation, '#pop:2'),
            (r',', Punctuation),
            (r'class\b', Keyword.Declaration, 'class-segment'),
            (r'(has|private|with)\b', Keyword.Declaration),
            (r':', Error),
            default(('_object-expression', '_expression'))
        ],
        'class-segment': [
            include('_whitespace'),
            (r'(?=[,;]|(class|has|private|with)\b)', Text, '#pop'),
            (_name, Name.Class),
            default('value')
        ],
        # Extend, Verb
        'grammar': [
            include('_whitespace'),
            (r'=', Punctuation, ('#pop', 'default')),
            (r'\*', Punctuation, ('#pop', 'grammar-line')),
            default('_directive-keyword')
        ],
        'grammar-line': [
            include('_whitespace'),
            (r';', Punctuation, '#pop'),
            (r'[/*]', Punctuation),
            (r'[%s]>' % _dash, Punctuation, 'value'),
            (r'(noun|scope)\b', Keyword, '=routine'),
            default('_directive-keyword')
        ],
        '=routine': [
            include('_whitespace'),
            (r'=', Punctuation, 'routine-name?'),
            default('#pop')
        ],
        # Import
        'manifest': [
            include('_whitespace'),
            (r';', Punctuation, '#pop'),
            (r',', Punctuation),
            (r'(?i)(global\b)?', Keyword, '_global')
        ],
        # Include, Link, Message
        'diagnostic': [
            include('_whitespace'),
            (r'[%s]' % _dquote, String.Double, ('#pop', 'message-string')),
            default(('#pop', 'before-plain-string', 'directive-keyword?'))
        ],
        'before-plain-string': [
            include('_whitespace'),
            (r'[%s]' % _dquote, String.Double, ('#pop', 'plain-string'))
        ],
        'message-string': [
            (r'[~^]+', String.Escape),
            include('plain-string')
        ],

        # Keywords used in directives
        '_directive-keyword!': [
            include('_whitespace'),
            (r'(additive|alias|buffer|class|creature|data|error|fatalerror|'
             r'first|has|held|initial|initstr|last|long|meta|multi|'
             r'multiexcept|multiheld|multiinside|noun|number|only|private|'
             r'replace|reverse|scope|score|special|string|table|terminating|'
             r'time|topic|warning|with)\b', Keyword, '#pop'),
            (r'[%s]{1,2}>|[+=]' % _dash, Punctuation, '#pop')
        ],
        '_directive-keyword': [
            include('_directive-keyword!'),
            include('value')
        ],
        'directive-keyword?': [
            include('_directive-keyword!'),
            default('#pop')
        ],
        'property-keyword*': [
            include('_whitespace'),
            (r'(additive|long)\b', Keyword),
            default('#pop')
        ],
        'trace-keyword?': [
            include('_whitespace'),
            (r'(assembly|dictionary|expressions|lines|linker|objects|off|on|'
             r'symbols|tokens|verbs)\b', Keyword, '#pop'),
            default('#pop')
        ],

        # Statements
        'statements': [
            include('_whitespace'),
            (r'\]', Punctuation, '#pop'),
            (r'[;{}]', Punctuation),
            (r'(box|break|continue|default|give|inversion|new_line|quit|read|'
             r'remove|return|rfalse|rtrue|spaces|string|until)\b', Keyword,
             'default'),
            (r'(do|else)\b', Keyword),
            (r'(font|style)\b', Keyword,
             ('default', 'miscellaneous-keyword?')),
            (r'for\b', Keyword, ('for', '(?')),
            (r'(if|switch|while)', Keyword,
             ('expression', '_expression', '(?')),
            (r'(jump|save|restore)\b', Keyword, ('default', 'label?')),
            (r'objectloop\b', Keyword,
             ('_keyword-expression', 'variable?', '(?')),
            (r'print(_ret)?\b|(?=[%s])' % _dquote, Keyword, 'print-list'),
            (r'\.', Name.Label, 'label?'),
            (r'@', Keyword, 'opcode'),
            (r'#(?![agrnw]\$|#)', Punctuation, 'directive'),
            (r'<', Punctuation, 'default'),
            (r'(move\b)?', Keyword,
             ('default', '_keyword-expression', '_expression'))
        ],
        'miscellaneous-keyword?': [
            include('_whitespace'),
            (r'(bold|fixed|from|near|off|on|reverse|roman|to|underline)\b',
             Keyword, '#pop'),
            (r'(a|A|an|address|char|name|number|object|property|string|the|'
             r'The)\b(?=(\s+|(![^%s]*))*\))' % _newline, Keyword.Pseudo,
             '#pop'),
            (r'%s(?=(\s+|(![^%s]*))*\))' % (_name, _newline), Name.Function,
             '#pop'),
            default('#pop')
        ],
        '(?': [
            include('_whitespace'),
            (r'\(?', Punctuation, '#pop')
        ],
        'for': [
            include('_whitespace'),
            (r';?', Punctuation, ('_for-expression', '_expression'))
        ],
        'print-list': [
            include('_whitespace'),
            (r';', Punctuation, '#pop'),
            (r':', Error),
            default(('_list-expression', '_expression', '_list-expression', 'form'))
        ],
        'form': [
            include('_whitespace'),
            (r'\(', Punctuation, ('#pop', 'miscellaneous-keyword?')),
            default('#pop')
        ],

        # Assembly
        'opcode': [
            include('_whitespace'),
            (r'[%s]' % _dquote, String.Double, ('operands', 'plain-string')),
            (_name, Keyword, 'operands')
        ],
        'operands': [
            (r':', Error),
            default(('_assembly-expression', '_expression'))
        ]
    }

    def get_tokens_unprocessed(self, text):
        # 'in' is either a keyword or an operator.
        # If the token two tokens after 'in' is ')', 'in' is a keyword:
        #   objectloop(a in b)
        # Otherwise, it is an operator:
        #   objectloop(a in b && true)
        objectloop_queue = []
        objectloop_token_count = -1
        previous_token = None
        for index, token, value in RegexLexer.get_tokens_unprocessed(self,
                                                                     text):
            if previous_token is Name.Variable and value == 'in':
                objectloop_queue = [[index, token, value]]
                objectloop_token_count = 2
            elif objectloop_token_count > 0:
                if token not in Comment and token not in Text:
                    objectloop_token_count -= 1
                objectloop_queue.append((index, token, value))
            else:
                if objectloop_token_count == 0:
                    if objectloop_queue[-1][2] == ')':
                        objectloop_queue[0][1] = Keyword
                    while objectloop_queue:
                        yield objectloop_queue.pop(0)
                    objectloop_token_count = -1
                yield index, token, value
            if token not in Comment and token not in Text:
                previous_token = token
        while objectloop_queue:
            yield objectloop_queue.pop(0)


class Inform7Lexer(RegexLexer):
    """
    For `Inform 7 <http://inform7.com/>`_ source code.

    .. versionadded:: 2.0
    """

    name = 'Inform 7'
    aliases = ['inform7', 'i7']
    filenames = ['*.ni', '*.i7x']

    flags = re.MULTILINE | re.DOTALL | re.UNICODE

    _dash = Inform6Lexer._dash
    _dquote = Inform6Lexer._dquote
    _newline = Inform6Lexer._newline
    _start = r'\A|(?<=[%s])' % _newline

    # There are three variants of Inform 7, differing in how to
    # interpret at signs and braces in I6T. In top-level inclusions, at
    # signs in the first column are inweb syntax. In phrase definitions
    # and use options, tokens in braces are treated as I7. Use options
    # also interpret "{N}".
    tokens = {}
    token_variants = ['+i6t-not-inline', '+i6t-inline', '+i6t-use-option']

    for level in token_variants:
        tokens[level] = {
            '+i6-root': list(Inform6Lexer.tokens['root']),
            '+i6t-root': [  # For Inform6TemplateLexer
                (r'[^%s]*' % Inform6Lexer._newline, Comment.Preproc,
                 ('directive', '+p'))
            ],
            'root': [
                (r'(\|?\s)+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'[%s]' % _dquote, Generic.Heading,
                 ('+main', '+titling', '+titling-string')),
                default(('+main', '+heading?'))
            ],
            '+titling-string': [
                (r'[^%s]+' % _dquote, Generic.Heading),
                (r'[%s]' % _dquote, Generic.Heading, '#pop')
            ],
            '+titling': [
                (r'\[', Comment.Multiline, '+comment'),
                (r'[^%s.;:|%s]+' % (_dquote, _newline), Generic.Heading),
                (r'[%s]' % _dquote, Generic.Heading, '+titling-string'),
                (r'[%s]{2}|(?<=[\s%s])\|[\s%s]' % (_newline, _dquote, _dquote),
                 Text, ('#pop', '+heading?')),
                (r'[.;:]|(?<=[\s%s])\|' % _dquote, Text, '#pop'),
                (r'[|%s]' % _newline, Generic.Heading)
            ],
            '+main': [
                (r'(?i)[^%s:a\[(|%s]+' % (_dquote, _newline), Text),
                (r'[%s]' % _dquote, String.Double, '+text'),
                (r':', Text, '+phrase-definition'),
                (r'(?i)\bas\b', Text, '+use-option'),
                (r'\[', Comment.Multiline, '+comment'),
                (r'(\([%s])(.*?)([%s]\))' % (_dash, _dash),
                 bygroups(Punctuation,
                          using(this, state=('+i6-root', 'directive'),
                                i6t='+i6t-not-inline'), Punctuation)),
                (r'(%s|(?<=[\s;:.%s]))\|\s|[%s]{2,}' %
                 (_start, _dquote, _newline), Text, '+heading?'),
                (r'(?i)[a(|%s]' % _newline, Text)
            ],
            '+phrase-definition': [
                (r'\s+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'(\([%s])(.*?)([%s]\))' % (_dash, _dash),
                 bygroups(Punctuation,
                          using(this, state=('+i6-root', 'directive',
                                             'default', 'statements'),
                                i6t='+i6t-inline'), Punctuation), '#pop'),
                default('#pop')
            ],
            '+use-option': [
                (r'\s+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'(\([%s])(.*?)([%s]\))' % (_dash, _dash),
                 bygroups(Punctuation,
                          using(this, state=('+i6-root', 'directive'),
                                i6t='+i6t-use-option'), Punctuation), '#pop'),
                default('#pop')
            ],
            '+comment': [
                (r'[^\[\]]+', Comment.Multiline),
                (r'\[', Comment.Multiline, '#push'),
                (r'\]', Comment.Multiline, '#pop')
            ],
            '+text': [
                (r'[^\[%s]+' % _dquote, String.Double),
                (r'\[.*?\]', String.Interpol),
                (r'[%s]' % _dquote, String.Double, '#pop')
            ],
            '+heading?': [
                (r'(\|?\s)+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'[%s]{4}\s+' % _dash, Text, '+documentation-heading'),
                (r'[%s]{1,3}' % _dash, Text),
                (r'(?i)(volume|book|part|chapter|section)\b[^%s]*' % _newline,
                 Generic.Heading, '#pop'),
                default('#pop')
            ],
            '+documentation-heading': [
                (r'\s+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'(?i)documentation\s+', Text, '+documentation-heading2'),
                default('#pop')
            ],
            '+documentation-heading2': [
                (r'\s+', Text),
                (r'\[', Comment.Multiline, '+comment'),
                (r'[%s]{4}\s' % _dash, Text, '+documentation'),
                default('#pop:2')
            ],
            '+documentation': [
                (r'(?i)(%s)\s*(chapter|example)\s*:[^%s]*' %
                 (_start, _newline), Generic.Heading),
                (r'(?i)(%s)\s*section\s*:[^%s]*' % (_start, _newline),
                 Generic.Subheading),
                (r'((%s)\t.*?[%s])+' % (_start, _newline),
                 using(this, state='+main')),
                (r'[^%s\[]+|[%s\[]' % (_newline, _newline), Text),
                (r'\[', Comment.Multiline, '+comment'),
            ],
            '+i6t-not-inline': [
                (r'(%s)@c( .*?)?([%s]|\Z)' % (_start, _newline),
                 Comment.Preproc),
                (r'(%s)@([%s]+|Purpose:)[^%s]*' % (_start, _dash, _newline),
                 Comment.Preproc),
                (r'(%s)@p( .*?)?([%s]|\Z)' % (_start, _newline),
                 Generic.Heading, '+p')
            ],
            '+i6t-use-option': [
                include('+i6t-not-inline'),
                (r'({)(N)(})', bygroups(Punctuation, Text, Punctuation))
            ],
            '+i6t-inline': [
                (r'({)(\S[^}]*)?(})',
                 bygroups(Punctuation, using(this, state='+main'),
                          Punctuation))
            ],
            '+i6t': [
                (r'({[%s])(![^}]*)(}?)' % _dash,
                 bygroups(Punctuation, Comment.Single, Punctuation)),
                (r'({[%s])(lines)(:)([^}]*)(}?)' % _dash,
                 bygroups(Punctuation, Keyword, Punctuation, Text,
                          Punctuation), '+lines'),
                (r'({[%s])([^:}]*)(:?)([^}]*)(}?)' % _dash,
                 bygroups(Punctuation, Keyword, Punctuation, Text,
                          Punctuation)),
                (r'(\(\+)(.*?)(\+\)|\Z)',
                 bygroups(Punctuation, using(this, state='+main'),
                          Punctuation))
            ],
            '+p': [
                (r'[^@]+', Comment.Preproc),
                (r'(%s)@c( .*?)?([%s]|\Z)' % (_start, _newline),
                 Comment.Preproc, '#pop'),
                (r'(%s)@([%s]|Purpose:)' % (_start, _dash), Comment.Preproc),
                (r'(%s)@p( .*?)?([%s]|\Z)' % (_start, _newline),
                 Generic.Heading),
                (r'@', Comment.Preproc)
            ],
            '+lines': [
                (r'(%s)@c( .*?)?([%s]|\Z)' % (_start, _newline),
                 Comment.Preproc),
                (r'(%s)@([%s]|Purpose:)[^%s]*' % (_start, _dash, _newline),
                 Comment.Preproc),
                (r'(%s)@p( .*?)?([%s]|\Z)' % (_start, _newline),
                 Generic.Heading, '+p'),
                (r'(%s)@[a-zA-Z_0-9]*[ %s]' % (_start, _newline), Keyword),
                (r'![^%s]*' % _newline, Comment.Single),
                (r'({)([%s]endlines)(})' % _dash,
                 bygroups(Punctuation, Keyword, Punctuation), '#pop'),
                (r'[^@!{]+?([%s]|\Z)|.' % _newline, Text)
            ]
        }
        # Inform 7 can include snippets of Inform 6 template language,
        # so all of Inform6Lexer's states are copied here, with
        # modifications to account for template syntax. Inform7Lexer's
        # own states begin with '+' to avoid name conflicts. Some of
        # Inform6Lexer's states begin with '_': these are not modified.
        # They deal with template syntax either by including modified
        # states, or by matching r'' then pushing to modified states.
        for token in Inform6Lexer.tokens:
            if token == 'root':
                continue
            tokens[level][token] = list(Inform6Lexer.tokens[token])
            if not token.startswith('_'):
                tokens[level][token][:0] = [include('+i6t'), include(level)]

    def __init__(self, **options):
        level = options.get('i6t', '+i6t-not-inline')
        if level not in self._all_tokens:
            self._tokens = self.__class__.process_tokendef(level)
        else:
            self._tokens = self._all_tokens[level]
        RegexLexer.__init__(self, **options)


class Inform6TemplateLexer(Inform7Lexer):
    """
    For `Inform 6 template
    <http://inform7.com/sources/src/i6template/Woven/index.html>`_ code.

    .. versionadded:: 2.0
    """

    name = 'Inform 6 template'
    aliases = ['i6t']
    filenames = ['*.i6t']

    def get_tokens_unprocessed(self, text, stack=('+i6t-root',)):
        return Inform7Lexer.get_tokens_unprocessed(self, text, stack)


class MqlLexer(CppLexer):
    """
    For `MQL4 <http://docs.mql4.com/>`_ and
    `MQL5 <http://www.mql5.com/en/docs>`_ source code.

    .. versionadded:: 2.0
    """
    name = 'MQL'
    aliases = ['mql', 'mq4', 'mq5', 'mql4', 'mql5']
    filenames = ['*.mq4', '*.mq5', '*.mqh']
    mimetypes = ['text/x-mql']

    tokens = {
        'statements': [
            (r'(input|_Digits|_Point|_LastError|_Period|_RandomSeed|'
             r'_StopFlag|_Symbol|_UninitReason|'
             r'Ask|Bars|Bid|Close|Digits|High|Low|Open|Point|Time|Volume)\b',
             Keyword),
            (r'(void|char|uchar|bool|short|ushort|int|uint|color|long|ulong|datetime|'
             r'float|double|string)\b',
             Keyword.Type),
            (r'(Alert|CheckPointer|Comment|DebugBreak|ExpertRemove|'
             r'GetPointer|GetTickCount|MessageBox|PeriodSeconds|PlaySound|'
             r'Print|PrintFormat|ResetLastError|ResourceCreate|ResourceFree|'
             r'ResourceReadImage|ResourceSave|SendFTP|SendMail|SendNotification|'
             r'Sleep|TerminalClose|TesterStatistics|ZeroMemory|'
             r'ArrayBsearch|ArrayCopy|ArrayCompare|ArrayFree|ArrayGetAsSeries|'
             r'ArrayInitialize|ArrayFill|ArrayIsSeries|ArrayIsDynamic|'
             r'ArrayMaximum|ArrayMinimum|ArrayRange|ArrayResize|'
             r'ArraySetAsSeries|ArraySize|ArraySort|ArrayCopyRates|'
             r'ArrayCopySeries|ArrayDimension|'
             r'CharToString|DoubleToString|EnumToString|NormalizeDouble|'
             r'StringToDouble|StringToInteger|StringToTime|TimeToString|'
             r'IntegerToString|ShortToString|ShortArrayToString|'
             r'StringToShortArray|CharArrayToString|StringToCharArray|'
             r'ColorToARGB|ColorToString|StringToColor|StringFormat|'
             r'CharToStr|DoubleToStr|StrToDouble|StrToInteger|StrToTime|TimeToStr|'
             r'MathAbs|MathArccos|MathArcsin|MathArctan|MathCeil|MathCos|MathExp|'
             r'MathFloor|MathLog|MathMax|MathMin|MathMod|MathPow|MathRand|'
             r'MathRound|MathSin|MathSqrt|MathSrand|MathTan|MathIsValidNumber|'
             r'StringAdd|StringBufferLen|StringCompare|StringConcatenate|StringFill|'
             r'StringFind|StringGetCharacter|StringInit|StringLen|StringReplace|'
             r'StringSetCharacter|StringSplit|StringSubstr|StringToLower|StringToUpper|'
             r'StringTrimLeft|StringTrimRight|StringGetChar|StringSetChar|'
             r'TimeCurrent|TimeTradeServer|TimeLocal|TimeGMT|TimeDaylightSavings|'
             r'TimeGMTOffset|TimeToStruct|StructToTime|Day|DayOfWeek|DayOfYear|'
             r'Hour|Minute|Month|Seconds|TimeDay|TimeDayOfWeek|TimeDayOfYear|TimeHour|'
             r'TimeMinute|TimeMonth|TimeSeconds|TimeYear|Year|'
             r'AccountInfoDouble|AccountInfoInteger|AccountInfoString|AccountBalance|'
             r'AccountCredit|AccountCompany|AccountCurrency|AccountEquity|'
             r'AccountFreeMargin|AccountFreeMarginCheck|AccountFreeMarginMode|'
             r'AccountLeverage|AccountMargin|AccountName|AccountNumber|AccountProfit|'
             r'AccountServer|AccountStopoutLevel|AccountStopoutMode|'
             r'GetLastError|IsStopped|UninitializeReason|MQLInfoInteger|MQLInfoString|'
             r'Symbol|Period|Digits|Point|IsConnected|IsDemo|IsDllsAllowed|'
             r'IsExpertEnabled|IsLibrariesAllowed|IsOptimization|IsTesting|'
             r'IsTradeAllowed|'
             r'IsTradeContextBusy|IsVisualMode|TerminalCompany|TerminalName|'
             r'TerminalPath|'
             r'SymbolsTotal|SymbolName|SymbolSelect|SymbolIsSynchronized|'
             r'SymbolInfoDouble|'
             r'SymbolInfoInteger|SymbolInfoString|SymbolInfoTick|'
             r'SymbolInfoSessionQuote|'
             r'SymbolInfoSessionTrade|MarketInfo|'
             r'SeriesInfoInteger|CopyRates|CopyTime|CopyOpen|'
             r'CopyHigh|CopyLow|CopyClose|'
             r'CopyTickVolume|CopyRealVolume|CopySpread|iBars|iBarShift|iClose|'
             r'iHigh|iHighest|iLow|iLowest|iOpen|iTime|iVolume|'
             r'HideTestIndicators|Period|RefreshRates|Symbol|WindowBarsPerChart|'
             r'WindowExpertName|WindowFind|WindowFirstVisibleBar|WindowHandle|'
             r'WindowIsVisible|WindowOnDropped|WindowPriceMax|WindowPriceMin|'
             r'WindowPriceOnDropped|WindowRedraw|WindowScreenShot|'
             r'WindowTimeOnDropped|WindowsTotal|WindowXOnDropped|WindowYOnDropped|'
             r'OrderClose|OrderCloseBy|OrderClosePrice|OrderCloseTime|OrderComment|'
             r'OrderCommission|OrderDelete|OrderExpiration|OrderLots|OrderMagicNumber|'
             r'OrderModify|OrderOpenPrice|OrderOpenTime|OrderPrint|OrderProfit|'
             r'OrderSelect|OrderSend|OrdersHistoryTotal|OrderStopLoss|OrdersTotal|'
             r'OrderSwap|OrderSymbol|OrderTakeProfit|OrderTicket|OrderType|'
             r'GlobalVariableCheck|GlobalVariableTime|'
             r'GlobalVariableDel|GlobalVariableGet|GlobalVariableName|'
             r'GlobalVariableSet|GlobalVariablesFlush|GlobalVariableTemp|'
             r'GlobalVariableSetOnCondition|GlobalVariablesDeleteAll|'
             r'GlobalVariablesTotal|GlobalVariableCheck|GlobalVariableTime|'
             r'GlobalVariableDel|GlobalVariableGet|'
             r'GlobalVariableName|GlobalVariableSet|GlobalVariablesFlush|'
             r'GlobalVariableTemp|GlobalVariableSetOnCondition|'
             r'GlobalVariablesDeleteAll|GlobalVariablesTotal|'
             r'GlobalVariableCheck|GlobalVariableTime|GlobalVariableDel|'
             r'GlobalVariableGet|GlobalVariableName|GlobalVariableSet|'
             r'GlobalVariablesFlush|GlobalVariableTemp|'
             r'GlobalVariableSetOnCondition|GlobalVariablesDeleteAll|'
             r'GlobalVariablesTotal|'
             r'FileFindFirst|FileFindNext|FileFindClose|FileOpen|FileDelete|'
             r'FileFlush|FileGetInteger|FileIsEnding|FileIsLineEnding|'
             r'FileClose|FileIsExist|FileCopy|FileMove|FileReadArray|'
             r'FileReadBool|FileReadDatetime|FileReadDouble|FileReadFloat|'
             r'FileReadInteger|FileReadLong|FileReadNumber|FileReadString|'
             r'FileReadStruct|FileSeek|FileSize|FileTell|FileWrite|'
             r'FileWriteArray|FileWriteDouble|FileWriteFloat|FileWriteInteger|'
             r'FileWriteLong|FileWriteString|FileWriteStruct|FolderCreate|'
             r'FolderDelete|FolderClean|FileOpenHistory|'
             r'IndicatorSetDouble|IndicatorSetInteger|IndicatorSetString|'
             r'SetIndexBuffer|IndicatorBuffers|IndicatorCounted|IndicatorDigits|'
             r'IndicatorShortName|SetIndexArrow|SetIndexDrawBegin|'
             r'SetIndexEmptyValue|SetIndexLabel|SetIndexShift|'
             r'SetIndexStyle|SetLevelStyle|SetLevelValue|'
             r'ObjectCreate|ObjectName|ObjectDelete|ObjectsDeleteAll|'
             r'ObjectFind|ObjectGetTimeByValue|ObjectGetValueByTime|'
             r'ObjectMove|ObjectsTotal|ObjectGetDouble|ObjectGetInteger|'
             r'ObjectGetString|ObjectSetDouble|ObjectSetInteger|'
             r'ObjectSetString|TextSetFont|TextOut|TextGetSize|'
             r'ObjectDescription|ObjectGet|ObjectGetFiboDescription|'
             r'ObjectGetShiftByValue|ObjectGetValueByShift|ObjectSet|'
             r'ObjectSetFiboDescription|ObjectSetText|ObjectType|'
             r'iAC|iAD|iADX|iAlligator|iAO|iATR|iBearsPower|'
             r'iBands|iBandsOnArray|iBullsPower|iCCI|iCCIOnArray|'
             r'iCustom|iDeMarker|iEnvelopes|iEnvelopesOnArray|'
             r'iForce|iFractals|iGator|iIchimoku|iBWMFI|iMomentum|'
             r'iMomentumOnArray|iMFI|iMA|iMAOnArray|iOsMA|iMACD|'
             r'iOBV|iSAR|iRSI|iRSIOnArray|iRVI|iStdDev|iStdDevOnArray|'
             r'iStochastic|iWPR|'
             r'EventSetMillisecondTimer|EventSetTimer|'
             r'EventKillTimer|EventChartCustom)\b', Name.Function),
            (r'(CHARTEVENT_KEYDOWN|CHARTEVENT_MOUSE_MOVE|'
             r'CHARTEVENT_OBJECT_CREATE|'
             r'CHARTEVENT_OBJECT_CHANGE|CHARTEVENT_OBJECT_DELETE|'
             r'CHARTEVENT_CLICK|'
             r'CHARTEVENT_OBJECT_CLICK|CHARTEVENT_OBJECT_DRAG|'
             r'CHARTEVENT_OBJECT_ENDEDIT|'
             r'CHARTEVENT_CHART_CHANGE|CHARTEVENT_CUSTOM|'
             r'CHARTEVENT_CUSTOM_LAST|'
             r'PERIOD_CURRENT|PERIOD_M1|PERIOD_M2|PERIOD_M3|'
             r'PERIOD_M4|PERIOD_M5|'
             r'PERIOD_M6|PERIOD_M10|PERIOD_M12|PERIOD_M15|'
             r'PERIOD_M20|PERIOD_M30|'
             r'PERIOD_H1|PERIOD_H2|PERIOD_H3|PERIOD_H4|'
             r'PERIOD_H6|PERIOD_H8|'
             r'PERIOD_H12|PERIOD_D1|PERIOD_W1|PERIOD_MN1|'
             r'CHART_IS_OBJECT|CHART_BRING_TO_TOP|'
             r'CHART_MOUSE_SCROLL|CHART_EVENT_MOUSE_MOVE|'
             r'CHART_EVENT_OBJECT_CREATE|'
             r'CHART_EVENT_OBJECT_DELETE|CHART_MODE|CHART_FOREGROUND|'
             r'CHART_SHIFT|'
             r'CHART_AUTOSCROLL|CHART_SCALE|CHART_SCALEFIX|'
             r'CHART_SCALEFIX_11|'
             r'CHART_SCALE_PT_PER_BAR|CHART_SHOW_OHLC|'
             r'CHART_SHOW_BID_LINE|'
             r'CHART_SHOW_ASK_LINE|CHART_SHOW_LAST_LINE|'
             r'CHART_SHOW_PERIOD_SEP|'
             r'CHART_SHOW_GRID|CHART_SHOW_VOLUMES|'
             r'CHART_SHOW_OBJECT_DESCR|'
             r'CHART_VISIBLE_BARS|CHART_WINDOWS_TOTAL|'
             r'CHART_WINDOW_IS_VISIBLE|'
             r'CHART_WINDOW_HANDLE|CHART_WINDOW_YDISTANCE|'
             r'CHART_FIRST_VISIBLE_BAR|'
             r'CHART_WIDTH_IN_BARS|CHART_WIDTH_IN_PIXELS|'
             r'CHART_HEIGHT_IN_PIXELS|'
             r'CHART_COLOR_BACKGROUND|CHART_COLOR_FOREGROUND|'
             r'CHART_COLOR_GRID|'
             r'CHART_COLOR_VOLUME|CHART_COLOR_CHART_UP|'
             r'CHART_COLOR_CHART_DOWN|'
             r'CHART_COLOR_CHART_LINE|CHART_COLOR_CANDLE_BULL|'
             r'CHART_COLOR_CANDLE_BEAR|'
             r'CHART_COLOR_BID|CHART_COLOR_ASK|CHART_COLOR_LAST|'
             r'CHART_COLOR_STOP_LEVEL|'
             r'CHART_SHOW_TRADE_LEVELS|CHART_DRAG_TRADE_LEVELS|'
             r'CHART_SHOW_DATE_SCALE|'
             r'CHART_SHOW_PRICE_SCALE|CHART_SHIFT_SIZE|'
             r'CHART_FIXED_POSITION|'
             r'CHART_FIXED_MAX|CHART_FIXED_MIN|CHART_POINTS_PER_BAR|'
             r'CHART_PRICE_MIN|'
             r'CHART_PRICE_MAX|CHART_COMMENT|CHART_BEGIN|'
             r'CHART_CURRENT_POS|CHART_END|'
             r'CHART_BARS|CHART_CANDLES|CHART_LINE|CHART_VOLUME_HIDE|'
             r'CHART_VOLUME_TICK|CHART_VOLUME_REAL|'
             r'OBJ_VLINE|OBJ_HLINE|OBJ_TREND|OBJ_TRENDBYANGLE|OBJ_CYCLES|'
             r'OBJ_CHANNEL|OBJ_STDDEVCHANNEL|OBJ_REGRESSION|OBJ_PITCHFORK|'
             r'OBJ_GANNLINE|OBJ_GANNFAN|OBJ_GANNGRID|OBJ_FIBO|'
             r'OBJ_FIBOTIMES|OBJ_FIBOFAN|OBJ_FIBOARC|OBJ_FIBOCHANNEL|'
             r'OBJ_EXPANSION|OBJ_RECTANGLE|OBJ_TRIANGLE|OBJ_ELLIPSE|'
             r'OBJ_ARROW_THUMB_UP|OBJ_ARROW_THUMB_DOWN|'
             r'OBJ_ARROW_UP|OBJ_ARROW_DOWN|'
             r'OBJ_ARROW_STOP|OBJ_ARROW_CHECK|OBJ_ARROW_LEFT_PRICE|'
             r'OBJ_ARROW_RIGHT_PRICE|OBJ_ARROW_BUY|OBJ_ARROW_SELL|'
             r'OBJ_ARROW|'
             r'OBJ_TEXT|OBJ_LABEL|OBJ_BUTTON|OBJ_BITMAP|'
             r'OBJ_BITMAP_LABEL|'
             r'OBJ_EDIT|OBJ_EVENT|OBJ_RECTANGLE_LABEL|'
             r'OBJPROP_TIME1|OBJPROP_PRICE1|OBJPROP_TIME2|'
             r'OBJPROP_PRICE2|OBJPROP_TIME3|'
             r'OBJPROP_PRICE3|OBJPROP_COLOR|OBJPROP_STYLE|'
             r'OBJPROP_WIDTH|'
             r'OBJPROP_BACK|OBJPROP_RAY|OBJPROP_ELLIPSE|'
             r'OBJPROP_SCALE|'
             r'OBJPROP_ANGLE|OBJPROP_ARROWCODE|OBJPROP_TIMEFRAMES|'
             r'OBJPROP_DEVIATION|OBJPROP_FONTSIZE|OBJPROP_CORNER|'
             r'OBJPROP_XDISTANCE|OBJPROP_YDISTANCE|OBJPROP_FIBOLEVELS|'
             r'OBJPROP_LEVELCOLOR|OBJPROP_LEVELSTYLE|OBJPROP_LEVELWIDTH|'
             r'OBJPROP_FIRSTLEVEL|OBJPROP_COLOR|OBJPROP_STYLE|OBJPROP_WIDTH|'
             r'OBJPROP_BACK|OBJPROP_ZORDER|OBJPROP_FILL|OBJPROP_HIDDEN|'
             r'OBJPROP_SELECTED|OBJPROP_READONLY|OBJPROP_TYPE|OBJPROP_TIME|'
             r'OBJPROP_SELECTABLE|OBJPROP_CREATETIME|OBJPROP_LEVELS|'
             r'OBJPROP_LEVELCOLOR|OBJPROP_LEVELSTYLE|OBJPROP_LEVELWIDTH|'
             r'OBJPROP_ALIGN|OBJPROP_FONTSIZE|OBJPROP_RAY_RIGHT|OBJPROP_RAY|'
             r'OBJPROP_ELLIPSE|OBJPROP_ARROWCODE|OBJPROP_TIMEFRAMES|OBJPROP_ANCHOR|'
             r'OBJPROP_XDISTANCE|OBJPROP_YDISTANCE|OBJPROP_DRAWLINES|OBJPROP_STATE|'
             r'OBJPROP_CHART_ID|OBJPROP_XSIZE|OBJPROP_YSIZE|OBJPROP_XOFFSET|'
             r'OBJPROP_YOFFSET|OBJPROP_PERIOD|OBJPROP_DATE_SCALE|OBJPROP_PRICE_SCALE|'
             r'OBJPROP_CHART_SCALE|OBJPROP_BGCOLOR|OBJPROP_CORNER|OBJPROP_BORDER_TYPE|'
             r'OBJPROP_BORDER_COLOR|OBJPROP_PRICE|OBJPROP_LEVELVALUE|OBJPROP_SCALE|'
             r'OBJPROP_ANGLE|OBJPROP_DEVIATION|'
             r'OBJPROP_NAME|OBJPROP_TEXT|OBJPROP_TOOLTIP|OBJPROP_LEVELTEXT|'
             r'OBJPROP_FONT|OBJPROP_BMPFILE|OBJPROP_SYMBOL|'
             r'BORDER_FLAT|BORDER_RAISED|BORDER_SUNKEN|ALIGN_LEFT|ALIGN_CENTER|'
             r'ALIGN_RIGHT|ANCHOR_LEFT_UPPER|ANCHOR_LEFT|ANCHOR_LEFT_LOWER|'
             r'ANCHOR_LOWER|ANCHOR_RIGHT_LOWER|ANCHOR_RIGHT|ANCHOR_RIGHT_UPPER|'
             r'ANCHOR_UPPER|ANCHOR_CENTER|ANCHOR_TOP|ANCHOR_BOTTOM|'
             r'CORNER_LEFT_UPPER|CORNER_LEFT_LOWER|CORNER_RIGHT_LOWER|'
             r'CORNER_RIGHT_UPPER|'
             r'OBJ_NO_PERIODS|EMPTY|OBJ_PERIOD_M1|OBJ_PERIOD_M5|OBJ_PERIOD_M15|'
             r'OBJ_PERIOD_M30|OBJ_PERIOD_H1|OBJ_PERIOD_H4|OBJ_PERIOD_D1|'
             r'OBJ_PERIOD_W1|OBJ_PERIOD_MN1|OBJ_ALL_PERIODS|'
             r'GANN_UP_TREND|GANN_DOWN_TREND|'
             r'((clr)?(Black|DarkGreen|DarkSlateGray|Olive|'
             r'Green|Teal|Navy|Purple|'
             r'Maroon|Indigo|MidnightBlue|DarkBlue|'
             r'DarkOliveGreen|SaddleBrown|'
             r'ForestGreen|OliveDrab|SeaGreen|'
             r'DarkGoldenrod|DarkSlateBlue|'
             r'Sienna|MediumBlue|Brown|DarkTurquoise|'
             r'DimGray|LightSeaGreen|'
             r'DarkViolet|FireBrick|MediumVioletRed|'
             r'MediumSeaGreen|Chocolate|'
             r'Crimson|SteelBlue|Goldenrod|MediumSpringGreen|'
             r'LawnGreen|CadetBlue|'
             r'DarkOrchid|YellowGreen|LimeGreen|OrangeRed|'
             r'DarkOrange|Orange|'
             r'Gold|Yellow|Chartreuse|Lime|SpringGreen|'
             r'Aqua|DeepSkyBlue|Blue|'
             r'Magenta|Red|Gray|SlateGray|Peru|BlueViolet|'
             r'LightSlateGray|DeepPink|'
             r'MediumTurquoise|DodgerBlue|Turquoise|RoyalBlue|'
             r'SlateBlue|DarkKhaki|'
             r'IndianRed|MediumOrchid|GreenYellow|'
             r'MediumAquamarine|DarkSeaGreen|'
             r'Tomato|RosyBrown|Orchid|MediumPurple|'
             r'PaleVioletRed|Coral|CornflowerBlue|'
             r'DarkGray|SandyBrown|MediumSlateBlue|'
             r'Tan|DarkSalmon|BurlyWood|'
             r'HotPink|Salmon|Violet|LightCoral|SkyBlue|'
             r'LightSalmon|Plum|'
             r'Khaki|LightGreen|Aquamarine|Silver|'
             r'LightSkyBlue|LightSteelBlue|'
             r'LightBlue|PaleGreen|Thistle|PowderBlue|'
             r'PaleGoldenrod|PaleTurquoise|'
             r'LightGray|Wheat|NavajoWhite|Moccasin|'
             r'LightPink|Gainsboro|PeachPuff|'
             r'Pink|Bisque|LightGoldenrod|BlanchedAlmond|'
             r'LemonChiffon|Beige|'
             r'AntiqueWhite|PapayaWhip|Cornsilk|'
             r'LightYellow|LightCyan|Linen|'
             r'Lavender|MistyRose|OldLace|WhiteSmoke|'
             r'Seashell|Ivory|Honeydew|'
             r'AliceBlue|LavenderBlush|MintCream|Snow|White))|'
             r'SYMBOL_THUMBSUP|SYMBOL_THUMBSDOWN|'
             r'SYMBOL_ARROWUP|SYMBOL_ARROWDOWN|'
             r'SYMBOL_STOPSIGN|SYMBOL_CHECKSIGN|'
             r'SYMBOL_LEFTPRICE|SYMBOL_RIGHTPRICE|'
             r'PRICE_CLOSE|PRICE_OPEN|PRICE_HIGH|PRICE_LOW|'
             r'PRICE_MEDIAN|PRICE_TYPICAL|PRICE_WEIGHTED|'
             r'VOLUME_TICK|VOLUME_REAL|'
             r'STO_LOWHIGH|STO_CLOSECLOSE|'
             r'MODE_OPEN|MODE_LOW|MODE_HIGH|MODE_CLOSE|MODE_VOLUME|MODE_TIME|'
             r'MODE_SMA|MODE_EMA|MODE_SMMA|MODE_LWMA|'
             r'MODE_MAIN|MODE_SIGNAL|MODE_MAIN|'
             r'MODE_PLUSDI|MODE_MINUSDI|MODE_UPPER|'
             r'MODE_LOWER|MODE_GATORJAW|MODE_GATORTEETH|'
             r'MODE_GATORLIPS|MODE_TENKANSEN|'
             r'MODE_KIJUNSEN|MODE_SENKOUSPANA|'
             r'MODE_SENKOUSPANB|MODE_CHINKOUSPAN|'
             r'DRAW_LINE|DRAW_SECTION|DRAW_HISTOGRAM|'
             r'DRAW_ARROW|DRAW_ZIGZAG|DRAW_NONE|'
             r'STYLE_SOLID|STYLE_DASH|STYLE_DOT|'
             r'STYLE_DASHDOT|STYLE_DASHDOTDOT|'
             r'DRAW_NONE|DRAW_LINE|DRAW_SECTION|DRAW_HISTOGRAM|'
             r'DRAW_ARROW|DRAW_ZIGZAG|DRAW_FILLING|'
             r'INDICATOR_DATA|INDICATOR_COLOR_INDEX|'
             r'INDICATOR_CALCULATIONS|INDICATOR_DIGITS|'
             r'INDICATOR_HEIGHT|INDICATOR_LEVELS|'
             r'INDICATOR_LEVELCOLOR|INDICATOR_LEVELSTYLE|'
             r'INDICATOR_LEVELWIDTH|INDICATOR_MINIMUM|'
             r'INDICATOR_MAXIMUM|INDICATOR_LEVELVALUE|'
             r'INDICATOR_SHORTNAME|INDICATOR_LEVELTEXT|'
             r'TERMINAL_BUILD|TERMINAL_CONNECTED|'
             r'TERMINAL_DLLS_ALLOWED|TERMINAL_TRADE_ALLOWED|'
             r'TERMINAL_EMAIL_ENABLED|'
             r'TERMINAL_FTP_ENABLED|TERMINAL_MAXBARS|'
             r'TERMINAL_CODEPAGE|TERMINAL_CPU_CORES|'
             r'TERMINAL_DISK_SPACE|TERMINAL_MEMORY_PHYSICAL|'
             r'TERMINAL_MEMORY_TOTAL|'
             r'TERMINAL_MEMORY_AVAILABLE|TERMINAL_MEMORY_USED|'
             r'TERMINAL_X64|'
             r'TERMINAL_OPENCL_SUPPORT|TERMINAL_LANGUAGE|'
             r'TERMINAL_COMPANY|TERMINAL_NAME|'
             r'TERMINAL_PATH|TERMINAL_DATA_PATH|'
             r'TERMINAL_COMMONDATA_PATH|'
             r'MQL_PROGRAM_TYPE|MQL_DLLS_ALLOWED|'
             r'MQL_TRADE_ALLOWED|MQL_DEBUG|'
             r'MQL_PROFILER|MQL_TESTER|MQL_OPTIMIZATION|'
             r'MQL_VISUAL_MODE|'
             r'MQL_FRAME_MODE|MQL_LICENSE_TYPE|MQL_PROGRAM_NAME|'
             r'MQL_PROGRAM_PATH|'
             r'PROGRAM_SCRIPT|PROGRAM_EXPERT|'
             r'PROGRAM_INDICATOR|LICENSE_FREE|'
             r'LICENSE_DEMO|LICENSE_FULL|LICENSE_TIME|'
             r'MODE_LOW|MODE_HIGH|MODE_TIME|MODE_BID|'
             r'MODE_ASK|MODE_POINT|'
             r'MODE_DIGITS|MODE_SPREAD|MODE_STOPLEVEL|'
             r'MODE_LOTSIZE|MODE_TICKVALUE|'
             r'MODE_TICKSIZE|MODE_SWAPLONG|'
             r'MODE_SWAPSHORT|MODE_STARTING|'
             r'MODE_EXPIRATION|MODE_TRADEALLOWED|'
             r'MODE_MINLOT|MODE_LOTSTEP|MODE_MAXLOT|'
             r'MODE_SWAPTYPE|MODE_PROFITCALCMODE|'
             r'MODE_MARGINCALCMODE|MODE_MARGININIT|'
             r'MODE_MARGINMAINTENANCE|MODE_MARGINHEDGED|'
             r'MODE_MARGINREQUIRED|MODE_FREEZELEVEL|'
             r'SUNDAY|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|'
             r'FRIDAY|SATURDAY|'
             r'ACCOUNT_LOGIN|ACCOUNT_TRADE_MODE|'
             r'ACCOUNT_LEVERAGE|'
             r'ACCOUNT_LIMIT_ORDERS|ACCOUNT_MARGIN_SO_MODE|'
             r'ACCOUNT_TRADE_ALLOWED|ACCOUNT_TRADE_EXPERT|'
             r'ACCOUNT_BALANCE|'
             r'ACCOUNT_CREDIT|ACCOUNT_PROFIT|ACCOUNT_EQUITY|'
             r'ACCOUNT_MARGIN|'
             r'ACCOUNT_FREEMARGIN|ACCOUNT_MARGIN_LEVEL|'
             r'ACCOUNT_MARGIN_SO_CALL|'
             r'ACCOUNT_MARGIN_SO_SO|ACCOUNT_NAME|'
             r'ACCOUNT_SERVER|ACCOUNT_CURRENCY|'
             r'ACCOUNT_COMPANY|ACCOUNT_TRADE_MODE_DEMO|'
             r'ACCOUNT_TRADE_MODE_CONTEST|'
             r'ACCOUNT_TRADE_MODE_REAL|ACCOUNT_STOPOUT_MODE_PERCENT|'
             r'ACCOUNT_STOPOUT_MODE_MONEY|'
             r'STAT_INITIAL_DEPOSIT|STAT_WITHDRAWAL|STAT_PROFIT|'
             r'STAT_GROSS_PROFIT|'
             r'STAT_GROSS_LOSS|STAT_MAX_PROFITTRADE|'
             r'STAT_MAX_LOSSTRADE|STAT_CONPROFITMAX|'
             r'STAT_CONPROFITMAX_TRADES|STAT_MAX_CONWINS|'
             r'STAT_MAX_CONPROFIT_TRADES|'
             r'STAT_CONLOSSMAX|STAT_CONLOSSMAX_TRADES|'
             r'STAT_MAX_CONLOSSES|'
             r'STAT_MAX_CONLOSS_TRADES|STAT_BALANCEMIN|'
             r'STAT_BALANCE_DD|'
             r'STAT_BALANCEDD_PERCENT|STAT_BALANCE_DDREL_PERCENT|'
             r'STAT_BALANCE_DD_RELATIVE|STAT_EQUITYMIN|'
             r'STAT_EQUITY_DD|'
             r'STAT_EQUITYDD_PERCENT|STAT_EQUITY_DDREL_PERCENT|'
             r'STAT_EQUITY_DD_RELATIVE|STAT_EXPECTED_PAYOFF|'
             r'STAT_PROFIT_FACTOR|'
             r'STAT_RECOVERY_FACTOR|STAT_SHARPE_RATIO|'
             r'STAT_MIN_MARGINLEVEL|'
             r'STAT_CUSTOM_ONTESTER|STAT_DEALS|STAT_TRADES|'
             r'STAT_PROFIT_TRADES|'
             r'STAT_LOSS_TRADES|STAT_SHORT_TRADES|STAT_LONG_TRADES|'
             r'STAT_PROFIT_SHORTTRADES|STAT_PROFIT_LONGTRADES|'
             r'STAT_PROFITTRADES_AVGCON|STAT_LOSSTRADES_AVGCON|'
             r'SERIES_BARS_COUNT|SERIES_FIRSTDATE|SERIES_LASTBAR_DATE|'
             r'SERIES_SERVER_FIRSTDATE|SERIES_TERMINAL_FIRSTDATE|'
             r'SERIES_SYNCHRONIZED|'
             r'OP_BUY|OP_SELL|OP_BUYLIMIT|OP_SELLLIMIT|'
             r'OP_BUYSTOP|OP_SELLSTOP|'
             r'TRADE_ACTION_DEAL|TRADE_ACTION_PENDING|'
             r'TRADE_ACTION_SLTP|'
             r'TRADE_ACTION_MODIFY|TRADE_ACTION_REMOVE|'
             r'__DATE__|__DATETIME__|__LINE__|__FILE__|'
             r'__PATH__|__FUNCTION__|'
             r'__FUNCSIG__|__MQLBUILD__|__MQL4BUILD__|'
             r'M_E|M_LOG2E|M_LOG10E|M_LN2|M_LN10|'
             r'M_PI|M_PI_2|M_PI_4|M_1_PI|'
             r'M_2_PI|M_2_SQRTPI|M_SQRT2|M_SQRT1_2|'
             r'CHAR_MIN|CHAR_MAX|UCHAR_MAX|'
             r'SHORT_MIN|SHORT_MAX|USHORT_MAX|'
             r'INT_MIN|INT_MAX|UINT_MAX|'
             r'LONG_MIN|LONG_MAX|ULONG_MAX|'
             r'DBL_MIN|DBL_MAX|DBL_EPSILON|DBL_DIG|DBL_MANT_DIG|'
             r'DBL_MAX_10_EXP|DBL_MAX_EXP|DBL_MIN_10_EXP|DBL_MIN_EXP|'
             r'FLT_MIN|FLT_MAX|FLT_EPSILON|'
             r'FLT_DIG|FLT_MANT_DIG|FLT_MAX_10_EXP|'
             r'FLT_MAX_EXP|FLT_MIN_10_EXP|FLT_MIN_EXP|REASON_PROGRAM'
             r'REASON_REMOVE|REASON_RECOMPILE|'
             r'REASON_CHARTCHANGE|REASON_CHARTCLOSE|'
             r'REASON_PARAMETERS|REASON_ACCOUNT|'
             r'REASON_TEMPLATE|REASON_INITFAILED|'
             r'REASON_CLOSE|POINTER_INVALID'
             r'POINTER_DYNAMIC|POINTER_AUTOMATIC|'
             r'NULL|EMPTY|EMPTY_VALUE|CLR_NONE|WHOLE_ARRAY|'
             r'CHARTS_MAX|clrNONE|EMPTY_VALUE|INVALID_HANDLE|'
             r'IS_DEBUG_MODE|IS_PROFILE_MODE|NULL|WHOLE_ARRAY|WRONG_VALUE|'
             r'ERR_NO_ERROR|ERR_NO_RESULT|ERR_COMMON_ERROR|'
             r'ERR_INVALID_TRADE_PARAMETERS|'
             r'ERR_SERVER_BUSY|ERR_OLD_VERSION|ERR_NO_CONNECTION|'
             r'ERR_NOT_ENOUGH_RIGHTS|'
             r'ERR_TOO_FREQUENT_REQUESTS|ERR_MALFUNCTIONAL_TRADE|'
             r'ERR_ACCOUNT_DISABLED|'
             r'ERR_INVALID_ACCOUNT|ERR_TRADE_TIMEOUT|'
             r'ERR_INVALID_PRICE|ERR_INVALID_STOPS|'
             r'ERR_INVALID_TRADE_VOLUME|ERR_MARKET_CLOSED|'
             r'ERR_TRADE_DISABLED|'
             r'ERR_NOT_ENOUGH_MONEY|ERR_PRICE_CHANGED|'
             r'ERR_OFF_QUOTES|ERR_BROKER_BUSY|'
             r'ERR_REQUOTE|ERR_ORDER_LOCKED|'
             r'ERR_LONG_POSITIONS_ONLY_ALLOWED|ERR_TOO_MANY_REQUESTS|'
             r'ERR_TRADE_MODIFY_DENIED|ERR_TRADE_CONTEXT_BUSY|'
             r'ERR_TRADE_EXPIRATION_DENIED|'
             r'ERR_TRADE_TOO_MANY_ORDERS|ERR_TRADE_HEDGE_PROHIBITED|'
             r'ERR_TRADE_PROHIBITED_BY_FIFO|'
             r'FILE_READ|FILE_WRITE|FILE_BIN|FILE_CSV|FILE_TXT|'
             r'FILE_ANSI|FILE_UNICODE|'
             r'FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_REWRITE|'
             r'FILE_COMMON|FILE_EXISTS|'
             r'FILE_CREATE_DATE|FILE_MODIFY_DATE|'
             r'FILE_ACCESS_DATE|FILE_SIZE|FILE_POSITION|'
             r'FILE_END|FILE_LINE_END|FILE_IS_COMMON|'
             r'FILE_IS_TEXT|FILE_IS_BINARY|'
             r'FILE_IS_CSV|FILE_IS_ANSI|FILE_IS_READABLE|FILE_IS_WRITABLE|'
             r'SEEK_SET|SEEK_CUR|SEEK_END|CP_ACP|'
             r'CP_OEMCP|CP_MACCP|CP_THREAD_ACP|'
             r'CP_SYMBOL|CP_UTF7|CP_UTF8|IDOK|IDCANCEL|IDABORT|'
             r'IDRETRY|IDIGNORE|IDYES|IDNO|IDTRYAGAIN|IDCONTINUE|'
             r'MB_OK|MB_OKCANCEL|MB_ABORTRETRYIGNORE|MB_YESNOCANCEL|'
             r'MB_YESNO|MB_RETRYCANCEL|'
             r'MB_CANCELTRYCONTINUE|MB_ICONSTOP|MB_ICONERROR|'
             r'MB_ICONHAND|MB_ICONQUESTION|'
             r'MB_ICONEXCLAMATION|MB_ICONWARNING|'
             r'MB_ICONINFORMATION|MB_ICONASTERISK|'
             r'MB_DEFBUTTON1|MB_DEFBUTTON2|MB_DEFBUTTON3|MB_DEFBUTTON4)\b',
                Name.Constant),
            inherit,
        ],
    }

class SwiftLexer(ObjectiveCLexer):
    """
    For `Swift <https://developer.apple.com/swift/>`_ source.
    """
    name = 'Swift'
    filenames = ['*.swift']
    aliases = ['swift']
    mimetypes = ['text/x-swift']

    keywords_decl = ['class', 'deinit', 'enum', 'extension', 'func', 'import',
                      'init', 'let', 'protocol', 'static', 'struct', 'subscript',
                      'typealias', 'var']
    keywords_stmt = ['break', 'case', 'continue', 'default', 'do', 'else',
                     'fallthrough', 'if', 'in', 'for', 'return', 'switch',
                     'where', 'while']
    keywords_type = ['as', 'dynamicType', 'is', 'new', 'super', 'self', 'Self',
                     'Type', '__COLUMN__', '__FILE__', '__FUNCTION__',
                     '__LINE__']
    keywords_resrv = ['associativity', 'didSet', 'get', 'infix', 'inout', 'left',
                      'mutating', 'none', 'nonmutating', 'operator', 'override',
                      'postfix', 'precedence', 'prefix', 'right', 'set',
                      'unowned', 'unowned(safe)', 'unowned(unsafe)', 'weak',
                      'willSet']
    operators = ['->']

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
            ObjectiveCLexer.get_tokens_unprocessed(self, text):
            if token is Name:
                if value in self.keywords_decl:
                    token = Keyword
                elif value in self.keywords_stmt:
                    token = Keyword
                elif value in self.keywords_type:
                    token = Keyword.Type
                elif value in self.keywords_resrv:
                    token = Keyword.Reserved
                elif value in self.operators:
                    token = Operator
            yield index, token, value
