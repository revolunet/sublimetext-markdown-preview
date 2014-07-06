"""
Reverse generated from CSS back to PY via pyg_css_convert.py
"""
from __future__ import absolute_import
from ..style import Style
from ..token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


class GithubStyle(Style):
    background_color = "#f8f8f8"  # Background
    highlight_color = "#ffffcc"   # <-- Not defined; defaulted

    styles = {
        Comment:                     "italic #999988",
        Comment.Multiline:           "#999988",
        Comment.Preproc:             "bold #999999 noitalic",
        Comment.Single:              "#999988",
        Comment.Special:             "bold #999999",
        Error:                       "bg:#e3d2d2 #a61717",
        Generic.Deleted:             "bg:#ffdddd #000000",
        Generic.Emph:                "italic",
        Generic.Error:               "#aa0000",
        Generic.Heading:             "#999999",
        Generic.Inserted:            "bg:#ddffdd #000000",
        Generic.Output:              "#888888",
        Generic.Prompt:              "#555555",
        Generic.Strong:              "bold",
        Generic.Subheading:          "bold #800080",
        Generic.Traceback:           "#aa0000",
        Keyword:                     "bold",
        Keyword.Constant:            "",
        Keyword.Declaration:         "",
        Keyword.Namespace:           "",
        Keyword.Pseudo:              "",
        Keyword.Reserved:            "",
        Keyword.Type:                "#445588",
        Literal.Number:              "#009999",
        Literal.Number.Float:        "#009999",
        Literal.Number.Hex:          "#009999",
        Literal.Number.Integer:      "#009999",
        Literal.Number.Integer.Long: "#009999",
        Literal.Number.Oct:          "#009999",
        Literal.String:              "#dd1144",
        Literal.String.Backtick:     "#dd1144",
        Literal.String.Char:         "#dd1144",
        Literal.String.Doc:          "#dd1144",
        Literal.String.Double:       "#dd1144",
        Literal.String.Escape:       "#dd1144",
        Literal.String.Heredoc:      "#dd1144",
        Literal.String.Interpol:     "#dd1144",
        Literal.String.Other:        "#dd1144",
        Literal.String.Regex:        "#009926",
        Literal.String.Single:       "#dd1144",
        Literal.String.Symbol:       "#990073",
        Name:                        "#333333",
        Name.Attribute:              "#008080",
        Name.Builtin:                "#0086b3",
        Name.Builtin.Pseudo:         "#999999",
        Name.Class:                  "bold #445588",
        Name.Constant:               "#008080",
        Name.Entity:                 "#800080",
        Name.Exception:              "bold #990000",
        Name.Function:               "bold #990000",
        Name.Namespace:              "#555555",
        Name.Tag:                    "#000080",
        Name.Variable:               "#008080",
        Name.Variable.Class:         "#008080",
        Name.Variable.Global:        "#008080",
        Name.Variable.Instance:      "#008080",
        Operator:                    "bold",
        Operator.Word:               "",
        Text:                        "#333333",  # Foreground
        Text.Whitespace:             "#bbbbbb"

        # Below are classes that could not be resolved:
        # class=.gc bold=False italic=False underline=False color=#999999 bg=#eaf2f5 border=None

        # Below are invalid rules:
        # .highlight .gd .x{color:#000000;background-color:#ffaaaa}
        # .highlight .gi .x{color:#000000;background-color:#aaffaa}
    }
