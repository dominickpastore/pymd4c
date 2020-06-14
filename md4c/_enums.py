#
# PyMD4C
# Python bindings for MD4C
#
# md4c._enums - Python enum types for the C enum constants
#
# Copyright (c) 2020 Dominick C. Pastore
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from enum import IntEnum

from . import _enum_consts

class BlockType(IntEnum):
    DOC = _enum_consts.MD_BLOCK_DOC
    QUOTE = _enum_consts.MD_BLOCK_QUOTE
    UL = _enum_consts.MD_BLOCK_UL
    OL = _enum_consts.MD_BLOCK_OL
    LI = _enum_consts.MD_BLOCK_LI
    HR = _enum_consts.MD_BLOCK_HR
    H = _enum_consts.MD_BLOCK_H
    CODE = _enum_consts.MD_BLOCK_CODE
    HTML = _enum_consts.MD_BLOCK_HTML
    P = _enum_consts.MD_BLOCK_P
    TABLE = _enum_consts.MD_BLOCK_TABLE
    THEAD = _enum_consts.MD_BLOCK_THEAD
    TBODY = _enum_consts.MD_BLOCK_TBODY
    TR = _enum_consts.MD_BLOCK_TR
    TH = _enum_consts.MD_BLOCK_TH
    TD = _enum_consts.MD_BLOCK_TD

class SpanType(IntEnum):
    EM = _enum_consts.MD_SPAN_EM
    STRONG = _enum_consts.MD_SPAN_STRONG
    A = _enum_consts.MD_SPAN_A
    IMG = _enum_consts.MD_SPAN_IMG
    CODE = _enum_consts.MD_SPAN_CODE
    DEL = _enum_consts.MD_SPAN_DEL
    LATEXMATH = _enum_consts.MD_SPAN_LATEXMATH
    LATEXMATH_DISPLAY = _enum_consts.MD_SPAN_LATEXMATH_DISPLAY
    WIKILINK = _enum_consts.MD_SPAN_WIKILINK
    U = _enum_consts.MD_SPAN_U

class TextType(IntEnum):
    NORMAL = _enum_consts.MD_TEXT_NORMAL
    NULLCHAR = _enum_consts.MD_TEXT_NULLCHAR
    BR = _enum_consts.MD_TEXT_BR
    SOFTBR = _enum_consts.MD_TEXT_SOFTBR
    ENTITY = _enum_consts.MD_TEXT_ENTITY
    CODE = _enum_consts.MD_TEXT_CODE
    HTML = _enum_consts.MD_TEXT_HTML
    LATEXMATH = _enum_consts.MD_TEXT_LATEXMATH

class Align(IntEnum):
    DEFAULT = _enum_consts.MD_ALIGN_DEFAULT
    LEFT = _enum_consts.MD_ALIGN_LEFT
    CENTER = _enum_consts.MD_ALIGN_CENTER
    RIGHT = _enum_consts.MD_ALIGN_RIGHT
