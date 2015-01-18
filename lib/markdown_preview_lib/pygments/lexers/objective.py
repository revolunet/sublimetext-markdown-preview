# -*- coding: utf-8 -*-
"""
    pygments.lexers.objective
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for Objective-C family languages.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
import re

from ..lexer import RegexLexer, include, bygroups, using, this, words, \
    inherit, default
from ..token import Text, Keyword, Name, String, Operator, \
    Number, Punctuation, Literal, Comment

from ..lexers.c_cpp import CLexer, CppLexer

__all__ = ['ObjectiveCLexer', 'ObjectiveCppLexer', 'LogosLexer', 'SwiftLexer']


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
                (words((
                    '@selector', '@private', '@protected', '@public', '@encode',
                    '@synchronized', '@try', '@throw', '@catch', '@finally',
                    '@end', '@property', '@synthesize', '__bridge', '__bridge_transfer',
                    '__autoreleasing', '__block', '__weak', '__strong', 'weak', 'strong',
                    'copy', 'retain', 'assign', 'unsafe_unretained', 'atomic', 'nonatomic',
                    'readonly', 'readwrite', 'setter', 'getter', 'typeof', 'in',
                    'out', 'inout', 'release', 'class', '@dynamic', '@optional',
                    '@required', '@autoreleasepool'), suffix=r'\b'),
                 Keyword),
                (words(('id', 'instancetype', 'Class', 'IMP', 'SEL', 'BOOL',
                        'IBOutlet', 'IBAction', 'unichar'), suffix=r'\b'),
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
            'oc_classname': [
                # interface definition that inherits
                ('([a-zA-Z$_][\w$]*)(\s*:\s*)([a-zA-Z$_][\w$]*)?(\s*)(\{)',
                 bygroups(Name.Class, Text, Name.Class, Text, Punctuation),
                 ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)(\s*:\s*)([a-zA-Z$_][\w$]*)?',
                 bygroups(Name.Class, Text, Name.Class), '#pop'),
                # interface definition for a category
                ('([a-zA-Z$_][\w$]*)(\s*)(\([a-zA-Z$_][\w$]*\))(\s*)(\{)',
                 bygroups(Name.Class, Text, Name.Label, Text, Punctuation),
                 ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)(\s*)(\([a-zA-Z$_][\w$]*\))',
                 bygroups(Name.Class, Text, Name.Label), '#pop'),
                # simple interface / implementation
                ('([a-zA-Z$_][\w$]*)(\s*)(\{)',
                 bygroups(Name.Class, Text, Punctuation), ('#pop', 'oc_ivars')),
                ('([a-zA-Z$_][\w$]*)', Name.Class, '#pop')
            ],
            'oc_forward_classname': [
                ('([a-zA-Z$_][\w$]*)(\s*,\s*)',
                 bygroups(Name.Class, Text), 'oc_forward_classname'),
                ('([a-zA-Z$_][\w$]*)(\s*;?)',
                 bygroups(Name.Class, Text), '#pop')
            ],
            'oc_ivars': [
                include('whitespace'),
                include('statements'),
                (';', Punctuation),
                (r'\{', Punctuation, '#push'),
                (r'\}', Punctuation, '#pop'),
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
                (r'\{', Punctuation, 'function'),
                default('#pop'),
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
            elif '@"' in text:  # strings
                return 0.8
            elif re.search('@[0-9]+', text):
                return 0.7
            elif _oc_message.search(text):
                return 0.8
            return 0

        def get_tokens_unprocessed(self, text):
            from ..lexers._cocoa_builtins import COCOA_INTERFACES, \
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
        'logos_init_directive': [
            ('\s+', Text),
            (',', Punctuation, ('logos_init_directive', '#pop')),
            ('([a-zA-Z$_][\w$]*)(\s*)(=)(\s*)([^);]*)',
             bygroups(Name.Class, Text, Punctuation, Text, Text)),
            ('([a-zA-Z$_][\w$]*)', Name.Class),
            ('\)', Punctuation, '#pop'),
        ],
        'logos_classname': [
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
            (r'(%ctor)(\s*)(\{)', bygroups(Keyword, Text, Punctuation),
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

class SwiftLexer(RegexLexer):
    """
    For `Swift <https://developer.apple.com/swift/>`_ source.

    .. versionadded:: 2.0
    """
    name = 'Swift'
    filenames = ['*.swift']
    aliases = ['swift']
    mimetypes = ['text/x-swift']

    tokens = {
        'root': [
            # Whitespace and Comments
            (r'\n', Text),
            (r'\s+', Text),
            (r'//', Comment.Single, 'comment-single'),
            (r'/\*', Comment.Multiline, 'comment-multi'),
            (r'#(if|elseif|else|endif)\b', Comment.Preproc, 'preproc'),

            # Keywords
            include('keywords'),

            # Global Types
            (r'(Array|AutoreleasingUnsafeMutablePointer|BidirectionalReverseView'
             r'|Bit|Bool|CFunctionPointer|COpaquePointer|CVaListPointer'
             r'|Character|ClosedInterval|CollectionOfOne|ContiguousArray'
             r'|Dictionary|DictionaryGenerator|DictionaryIndex|Double'
             r'|EmptyCollection|EmptyGenerator|EnumerateGenerator'
             r'|EnumerateSequence|FilterCollectionView'
             r'|FilterCollectionViewIndex|FilterGenerator|FilterSequenceView'
             r'|Float|Float80|FloatingPointClassification|GeneratorOf'
             r'|GeneratorOfOne|GeneratorSequence|HalfOpenInterval|HeapBuffer'
             r'|HeapBufferStorage|ImplicitlyUnwrappedOptional|IndexingGenerator'
             r'|Int|Int16|Int32|Int64|Int8|LazyBidirectionalCollection'
             r'|LazyForwardCollection|LazyRandomAccessCollection'
             r'|LazySequence|MapCollectionView|MapSequenceGenerator'
             r'|MapSequenceView|MirrorDisposition|ObjectIdentifier|OnHeap'
             r'|Optional|PermutationGenerator|QuickLookObject'
             r'|RandomAccessReverseView|Range|RangeGenerator|RawByte|Repeat'
             r'|ReverseBidirectionalIndex|ReverseRandomAccessIndex|SequenceOf'
             r'|SinkOf|Slice|StaticString|StrideThrough|StrideThroughGenerator'
             r'|StrideTo|StrideToGenerator|String|UInt|UInt16|UInt32|UInt64'
             r'|UInt8|UTF16|UTF32|UTF8|UnicodeDecodingResult|UnicodeScalar'
             r'|Unmanaged|UnsafeBufferPointer|UnsafeBufferPointerGenerator'
             r'|UnsafeMutableBufferPointer|UnsafeMutablePointer|UnsafePointer'
             r'|Zip2|ZipGenerator2'
             # Protocols
             r'|AbsoluteValuable|AnyObject|ArrayLiteralConvertible'
             r'|BidirectionalIndexType|BitwiseOperationsType'
             r'|BooleanLiteralConvertible|BooleanType|CVarArgType'
             r'|CollectionType|Comparable|DebugPrintable'
             r'|DictionaryLiteralConvertible|Equatable'
             r'|ExtendedGraphemeClusterLiteralConvertible'
             r'|ExtensibleCollectionType|FloatLiteralConvertible'
             r'|FloatingPointType|ForwardIndexType|GeneratorType|Hashable'
             r'|IntegerArithmeticType|IntegerLiteralConvertible|IntegerType'
             r'|IntervalType|MirrorType|MutableCollectionType|MutableSliceable'
             r'|NilLiteralConvertible|OutputStreamType|Printable'
             r'|RandomAccessIndexType|RangeReplaceableCollectionType'
             r'|RawOptionSetType|RawRepresentable|Reflectable|SequenceType'
             r'|SignedIntegerType|SignedNumberType|SinkType|Sliceable'
             r'|Streamable|Strideable|StringInterpolationConvertible'
             r'|StringLiteralConvertible|UnicodeCodecType'
             r'|UnicodeScalarLiteralConvertible|UnsignedIntegerType'
             r'|_ArrayBufferType|_BidirectionalIndexType|_CocoaStringType'
             r'|_CollectionType|_Comparable|_ExtensibleCollectionType'
             r'|_ForwardIndexType|_Incrementable|_IntegerArithmeticType'
             r'|_IntegerType|_ObjectiveCBridgeable|_RandomAccessIndexType'
             r'|_RawOptionSetType|_SequenceType|_Sequence_Type'
             r'|_SignedIntegerType|_SignedNumberType|_Sliceable|_Strideable'
             r'|_SwiftNSArrayRequiredOverridesType|_SwiftNSArrayType'
             r'|_SwiftNSCopyingType|_SwiftNSDictionaryRequiredOverridesType'
             r'|_SwiftNSDictionaryType|_SwiftNSEnumeratorType'
             r'|_SwiftNSFastEnumerationType|_SwiftNSStringRequiredOverridesType'
             r'|_SwiftNSStringType|_UnsignedIntegerType'
             # Variables
             r'|C_ARGC|C_ARGV|Process'
             # Typealiases
             r'|Any|AnyClass|BooleanLiteralType|CBool|CChar|CChar16|CChar32'
             r'|CDouble|CFloat|CInt|CLong|CLongLong|CShort|CSignedChar'
             r'|CUnsignedInt|CUnsignedLong|CUnsignedShort|CWideChar'
             r'|ExtendedGraphemeClusterType|Float32|Float64|FloatLiteralType'
             r'|IntMax|IntegerLiteralType|StringLiteralType|UIntMax|UWord'
             r'|UnicodeScalarType|Void|Word'
             # Foundation/Cocoa
             r'|NSErrorPointer|NSObjectProtocol|Selector)\b', Name.Builtin),
            # Functions
            (r'(abs|advance|alignof|alignofValue|assert|assertionFailure'
             r'|contains|count|countElements|debugPrint|debugPrintln|distance'
             r'|dropFirst|dropLast|dump|enumerate|equal|extend|fatalError'
             r'|filter|find|first|getVaList|indices|insert|isEmpty|join|last'
             r'|lazy|lexicographicalCompare|map|max|maxElement|min|minElement'
             r'|numericCast|overlaps|partition|precondition|preconditionFailure'
             r'|prefix|print|println|reduce|reflect|removeAll|removeAtIndex'
             r'|removeLast|removeRange|reverse|sizeof|sizeofValue|sort|sorted'
             r'|splice|split|startsWith|stride|strideof|strideofValue|suffix'
             r'|swap|toDebugString|toString|transcode|underestimateCount'
             r'|unsafeAddressOf|unsafeBitCast|unsafeDowncast'
             r'|withExtendedLifetime|withUnsafeMutablePointer'
             r'|withUnsafeMutablePointers|withUnsafePointer|withUnsafePointers'
             r'|withVaList)\b', Name.Builtin.Pseudo),

            # Implicit Block Variables
            (r'\$\d+', Name.Variable),

            # Binary Literal
            (r'0b[01_]+', Number.Bin),
            # Octal Literal
            (r'0o[0-7_]+', Number.Oct),
            # Hexadecimal Literal
            (r'0x[0-9a-fA-F_]+', Number.Hex),
            # Decimal Literal
            (r'[0-9][0-9_]*(\.[0-9_]+[eE][+\-]?[0-9_]+|'
             r'\.[0-9_]*|[eE][+\-]?[0-9_]+)', Number.Float),
            (r'[0-9][0-9_]*', Number.Integer),
            # String Literal
            (r'"', String, 'string'),

            # Operators and Punctuation
            (r'[(){}\[\].,:;=@#`?]|->|[<&?](?=\w)|(?<=\w)[>!?]', Punctuation),
            (r'[/=\-+!*%<>&|^?~]+', Operator),

            # Identifier
            (r'[a-zA-Z_]\w*', Name)
        ],
        'keywords': [
            (r'(break|case|continue|default|do|else|fallthrough|for|if|in'
             r'|return|switch|where|while)\b', Keyword),
            (r'@availability\([^)]+\)', Keyword.Reserved),
            (r'(associativity|convenience|dynamic|didSet|final|get|infix|inout'
             r'|lazy|left|mutating|none|nonmutating|optional|override|postfix'
             r'|precedence|prefix|Protocol|required|right|set|Type|unowned|weak'
             r'|willSet|@(availability|autoclosure|noreturn'
             r'|NSApplicationMain|NSCopying|NSManaged|objc'
             r'|UIApplicationMain|IBAction|IBDesignable|IBInspectable'
             r'|IBOutlet))\b',Keyword.Reserved),
            (r'(as|dynamicType|false|is|nil|self|Self|super|true|__COLUMN__'
             r'|__FILE__|__FUNCTION__|__LINE__|_)\b', Keyword.Constant),
            (r'import\b', Keyword.Declaration, 'module'),
            (r'(class|enum|extension|struct|protocol)(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword.Declaration, Text, Name.Class)),
            (r'(func)(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword.Declaration, Text, Name.Function)),
            (r'(var|let)(\s+)([a-zA-Z_]\w*)', bygroups(Keyword.Declaration,
             Text, Name.Variable)),
            (r'(class|deinit|enum|extension|func|import|init|internal|let'
             r'|operator|private|protocol|public|static|struct|subscript'
             r'|typealias|var)\b', Keyword.Declaration)
        ],
        'comment': [
            (r':param: [a-zA-Z_]\w*|:returns?:|(FIXME|MARK|TODO):',
             Comment.Special)
        ],

        # Nested
        'comment-single': [
            (r'\n', Text, '#pop'),
            include('comment'),
            (r'[^\n]', Comment.Single)
        ],
        'comment-multi': [
            include('comment'),
            (r'[^*/]', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline)
        ],
        'module': [
            (r'\n', Text, '#pop'),
            (r'[a-zA-Z_]\w*', Name.Class),
            include('root')
        ],
        'preproc': [
            (r'\n', Text, '#pop'),
            include('keywords'),
            (r'[A-Za-z]\w*', Comment.Preproc),
            include('root')
        ],
        'string': [
            (r'\\\(', String.Interpol, 'string-intp'),
            (r'"', String, '#pop'),
            (r"""\\['"\\nrt]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}"""
             r"""|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}""", String.Escape),
            (r'[^\\"]+', String),
            (r'\\', String)
        ],
        'string-intp': [
            (r'\(', String.Interpol, '#push'),
            (r'\)', String.Interpol, '#pop'),
            include('root')
        ]
    }

    def get_tokens_unprocessed(self, text):
        from ..lexers._cocoa_builtins import COCOA_INTERFACES, \
            COCOA_PROTOCOLS, COCOA_PRIMITIVES

        for index, token, value in \
                RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name or token is Name.Class:
                if value in COCOA_INTERFACES or value in COCOA_PROTOCOLS \
                   or value in COCOA_PRIMITIVES:
                    token = Name.Builtin.Pseudo

            yield index, token, value
