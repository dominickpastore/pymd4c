#
# PyMD4C
# Python bindings for MD4C
#
# md4c.domparser.domparser - A md4c.ParserObject that produces a DOM
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

from ..parser import ParserObject
from .domtypes import DOMObject


class DOMParser(ParserObject):
    """A subclass of :class:`ParserObject` that produces document object
    model-like output. In other words, it produces a tree representation of
    the Markdown document's block and inline elements.

    If the goal is simply to render a Markdown document in a suitable output
    format, this is a slow way to do it (in fact, `that was one of the main
    motivations behind the underlying MD4C library`__). You should consider
    using an :class:`HTMLRenderer`, a :class:`GenericParser`, or subclasssing
    :class:`ParserObject` instead. However, certain tasks, such as
    transformations on the document structure, can be difficult without a full
    abstract syntax tree, as produced by objects of this class.

    Arguments to the constructor are passed through to :class:`GenericParser`.
    Check that class and :ref:`options` for more information about that.

    .. _whyfast: https://talk.commonmark.org/t/why-is-md4c-so-fast-c/2520/2

    __ whyfast_
    """

    def enter_block(self, block_type, details):
        """Enter block callback. Creates a new DOMObject for the block and add
        it to the DOM.

        :param block_type: An instance of the :class:`md4c.BlockType` enum
                           representing the type of block being entered
        :param details: A dict containing details about the block
        """
        block = DOMObject(block_type, **details)
        if self.root is None:
            self.root = block
            self._current = block
        else:
            self._current.append(block)
            self._current = block

    def leave_block(self, block_type, details):
        """Leave block callback. Backtrack to the parent of the current block.
        (Parameters are ignored.)

        :param block_type: An instance of the :class:`md4c.BlockType` enum
                           representing the type of block being entered
        :param details: A dict containing details about the block
        """
        self._current = self._current.parent

    def enter_span(self, span_type, details):
        """Enter span callback. Creates a new DOMObject for the span and add it
        to the DOM.

        :param span_type: An instance of the :class:`md4c.SpanType` enum
                           representing the type of span being entered
        :param details: A dict containing details about the span
        """
        span = DOMObject(span_type, **details)
        self._current.append(span)
        self._current = span

    def leave_span(self, span_type, details):
        """Leave span callback. Backtrack to the parent of the current span.
        (Parameters are ignored.)

        :param span_type: An instance of the :class:`md4c.SpanType` enum
                           representing the type of span being entered
        :param details: A dict containing details about the span
        """
        self._current = self._current.parent

    def text(self, text_type, text):
        """Text callback. Create a new DOMObject for the text and add it to the
        DOM.

        :param text_type: An instance of the :class:`md4c.TextType` enum
                          representing the type of span being entered
        :param text: The actual text to be added
        """
        text_element = DOMObject(text_type, text)
        self._current.append(text_element)

    def parse(self, markdown):
        """Produce a DOM from the given Markdown document.

        :param markdown: The Markdown text to parse
        :type markdown: str or bytes

        :returns: The root :class:`DOMObject` of the document, by default a
                  :class:`Document`
        :rtype: DOMObject
        """
        self.root = None
        self._current = None
        super().parse(markdown)
        return self.root
