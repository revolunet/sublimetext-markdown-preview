# -*- coding: utf-8 -*-
"""
    pygments.lexers.math
    ~~~~~~~~~~~~~~~~~~~~

    Just export lexers that were contained in this module.

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
from ..lexers.python import NumPyLexer
from ..lexers.matlab import MatlabLexer, MatlabSessionLexer, \
    OctaveLexer, ScilabLexer
from ..lexers.julia import JuliaLexer, JuliaConsoleLexer
from ..lexers.r import RConsoleLexer, SLexer, RdLexer
from ..lexers.modeling import BugsLexer, JagsLexer, StanLexer
from ..lexers.idl import IDLLexer
from ..lexers.algebra import MuPADLexer

__all__ = []
