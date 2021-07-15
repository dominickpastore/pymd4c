#
# PyMD4C
# Python bindings for MD4C
#
# md4c.parser - Object-oriented wrapper for md4c.GenericParser
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

from ._md4c import GenericParser


class ParserObject:
    """Object-oriented wrapper for :class:`GenericParser`. Rather than
    providing callbacks for ``enter_block``, ``leave_block``, ``enter_span``,
    ``leave_span``, and ``text`` to a ``parse`` function, this base class can
    be subclassed to provide implementations for them.

    When this class's :func:`parse` function is called, it uses its own
    :func:`enter_block`, :func:`leave_block`, :func:`enter_span`,
    :func:`leave_span`, and :func:`text` functions as callbacks.

    Arguments to the constructor are passed through to :class:`GenericParser`
    as-is to set parser options.
    """

    def __init__(self, *args, **kwargs):
        self.parser = GenericParser(*args, **kwargs)

    def enter_block(self, block_type, details):
        """Called when the parser is entering a block element. This function
        should be overridden in subclasses. By default, it does nothing.

        :param block_type: An instance of the :class:`md4c.BlockType` enum
                           representing the type of block being entered
        :param details: A dict that contains extra information for certain
                        types of blocks. For example, heading blocks provide
                        ``'level'``. Keys are strings. Values are either
                        integers, strings, lists of tuples, or ``None``. For
                        more information, see the documentation for
                        :class:`GenericParser`.
        """

    def leave_block(self, block_type, details):
        """Called when the parser is leaving a block element. This function
        should be overridden in subclasses. By default, it does nothing.

        :param block_type: An instance of the :class:`md4c.BlockType` enum
                           representing the type of block being left
        :param details: A dict that contains extra information for certain
                        types of blocks. For example, heading blocks provide
                        ``'level'``. Keys are strings. Values are either
                        integers, strings, lists of tuples, or ``None``. For
                        more information, see the documentation for
                        :class:`GenericParser`.
        """

    def enter_span(self, span_type, details):
        """Called when the parser is entering an inline element. This function
        should be overridden in subclasses. By default, it does nothing.

        :param span_type: An instance of the :class:`md4c.SpanType` enum
                          representing the type of inline being entered
        :param details: A dict that contains extra information for certain
                        types of inlines. For example, links provide ``'href'``
                        and ``'title'``. Keys are strings. Values are either
                        integers, strings, lists of tuples, or ``None``. For
                        more information, see the documentation for
                        :class:`GenericParser`.
        """

    def leave_span(self, span_type, details):
        """Called when the parser is entering an inline element. This function
        should be overridden in subclasses. By default, it does nothing.

        :param span_type: An instance of the :class:`md4c.SpanType` enum
                          representing the type of inline being entered
        :param details: A dict that contains extra information for certain
                        types of inlines. For example, links provide ``'href'``
                        and ``'title'``. Keys are strings. Values are either
                        integers, strings, lists of tuples, or ``None``. For
                        more information, see the documentation for
                        :class:`GenericParser`.
        """

    def text(self, text_type, text):
        """Called when the parser has text to add to the current block or
        inline element. This function should be overridden in subclasses. By
        default, it does nothing.

        :param text_type: An instance of the :class:`md4c.TextType` enum
                          representing the type of text element
        :param text: A string or bytes containing the actual text to add
        """

    def parse(self, markdown):
        """Parse a Markdown document using this object's :func:`enter_block`,
        :func:`leave_block`, :func:`enter_span`, :func:`leave_span`, and
        :func:`text` functions as callbacks for :class:`GenericParser`.

        :param markdown: The Markdown text to parse.
        :type markdown: str or bytes
        """
        self.parser.parse(markdown,
                          self.enter_block,
                          self.leave_block,
                          self.enter_span,
                          self.leave_span,
                          self.text)
