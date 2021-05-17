#
# PyMD4C
# Python bindings for MD4C
#
# md4c.enums - Python enum types for the C enum constants
#
# Copyright (c) 2020-2021 Dominick C. Pastore
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

from enum import Enum

from . import _enum_consts


# NOTE When adding a new element to any of these Enums, make sure to add an
# appropriate class to domparser/domtypes.py.

class BlockType(Enum):
    """Represents a type of Markdown block"""

    #: Document
    DOC = _enum_consts.MD_BLOCK_DOC

    #: Block quote
    QUOTE = _enum_consts.MD_BLOCK_QUOTE

    #: Unordered list
    UL = _enum_consts.MD_BLOCK_UL

    #: Ordered list
    OL = _enum_consts.MD_BLOCK_OL

    #: List item
    LI = _enum_consts.MD_BLOCK_LI

    #: Horizontal rule
    HR = _enum_consts.MD_BLOCK_HR

    #: Heading
    H = _enum_consts.MD_BLOCK_H

    #: Code block
    CODE = _enum_consts.MD_BLOCK_CODE

    #: Raw HTML block
    HTML = _enum_consts.MD_BLOCK_HTML

    #: Paragraph
    P = _enum_consts.MD_BLOCK_P

    #: Table
    TABLE = _enum_consts.MD_BLOCK_TABLE

    #: Table header row
    THEAD = _enum_consts.MD_BLOCK_THEAD

    #: Table body
    TBODY = _enum_consts.MD_BLOCK_TBODY

    #: Table row
    TR = _enum_consts.MD_BLOCK_TR

    #: Table header cell
    TH = _enum_consts.MD_BLOCK_TH

    #: Table cell
    TD = _enum_consts.MD_BLOCK_TD


class SpanType(Enum):
    """Represents a type of Markdown span/inline"""

    #: Emphasis
    EM = _enum_consts.MD_SPAN_EM

    #: Strong emphasis
    STRONG = _enum_consts.MD_SPAN_STRONG

    #: Link
    A = _enum_consts.MD_SPAN_A

    #: Image
    IMG = _enum_consts.MD_SPAN_IMG

    #: Inline code
    CODE = _enum_consts.MD_SPAN_CODE

    #: Strikethrough
    DEL = _enum_consts.MD_SPAN_DEL

    #: Inline math
    LATEXMATH = _enum_consts.MD_SPAN_LATEXMATH

    #: Display math
    LATEXMATH_DISPLAY = _enum_consts.MD_SPAN_LATEXMATH_DISPLAY

    #: Wiki link
    WIKILINK = _enum_consts.MD_SPAN_WIKILINK

    #: Underline
    U = _enum_consts.MD_SPAN_U


class TextType(Enum):
    """Represents a type of Markdown text"""

    #: Normal text
    NORMAL = _enum_consts.MD_TEXT_NORMAL

    #: Null character
    NULLCHAR = _enum_consts.MD_TEXT_NULLCHAR

    #: Line break
    BR = _enum_consts.MD_TEXT_BR

    #: Soft line break
    SOFTBR = _enum_consts.MD_TEXT_SOFTBR

    #: HTML entity
    ENTITY = _enum_consts.MD_TEXT_ENTITY

    #: Text inside a code block or inline code block
    CODE = _enum_consts.MD_TEXT_CODE

    #: Raw HTML (inside an HTML block or simply inline HTML)
    HTML = _enum_consts.MD_TEXT_HTML

    #: Text inside an equation
    LATEXMATH = _enum_consts.MD_TEXT_LATEXMATH


class Align(Enum):
    """Represents a table cell alignment"""

    #: Default alignment
    DEFAULT = _enum_consts.MD_ALIGN_DEFAULT

    #: Left alignment
    LEFT = _enum_consts.MD_ALIGN_LEFT

    #: Centering
    CENTER = _enum_consts.MD_ALIGN_CENTER

    #: Right alignment
    RIGHT = _enum_consts.MD_ALIGN_RIGHT
