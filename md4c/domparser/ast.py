#
# PyMD4C
# Python bindings for MD4C
#
# md4c.domparser.ast - The classes for the AST output from DOMParser
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

import urllib.parse as _url_parse
from collections.abc import ByteString as _ByteString

from .. import lookup_entity as _lookup_entity
from ..enums import BlockType as _BlockType
from ..enums import SpanType as _SpanType
from ..enums import TextType as _TextType
from ..enums import Align as _Align


###############################################################################
# Abstract base classes                                                       #
###############################################################################


# For more information on this technique, see:
# https://stackoverflow.com/a/28076300
class ASTNode:
    """Base class for all AST nodes. When constructed, automatically constructs
    the appropriate subtype instead.

    The default classes for particular Markdown element types can be replaced
    by subclassing with the appropriate class argument. (Since every other node
    class in this module already inherits from
    :class:`~md4c.domparser.ASTNode`, this works with any of them as well.) For
    example, to use a custom class to handle :attr:`md4c.BlockType.HR`::

        class MyHorzontalRule(md4c.domparser.HorizontalRule,
                              element_type=md4c.BlockType.HR):
            '''My custom horizonal rule class'''

    :param element_type: A :class:`md4c.BlockType`, :class:`md4c.SpanType`, or
                         :class:`md4c.TextType` representing the type of this
                         element
    :param use_bytes: True if this node should render as :class:`bytes`, False
                      if it should render as :class:`str`. Defaults to False.
    :type use_bytes: bool, optional
    """
    _registry = dict()

    @classmethod
    def __init_subclass__(cls, element_type, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register cls as the class to create for element_type
        if element_type is not None:
            cls._registry[element_type] = cls

    def __new__(cls, element_type, use_bytes=False, **kwargs):
        # Select the appropriate subclass. There should never be a KeyError,
        # and if there is, it means we forgot to add a class in this module for
        # one of the BlockType/SpanType/TextType members.
        subcls = cls._registry[element_type]
        return object.__new__(subcls)

    # This isn't strictly necessary--the type of element is encoded in the type
    # of the object. But if a user decides to replace one of the built-in
    # classes for a particular element, isinstance() won't work so well, but
    # comparing self.type will.
    def __init__(self, element_type, use_bytes=False):
        #: A :class:`md4c.BlockType`, :class:`md4c.SpanType`, or
        #: :class:`md4c.TextType` representing the type of element this object
        #: represents
        self.type = element_type

        #: True if this node should render as :class:`bytes`, False if it
        #: should render as :class:`str`. Normally gets set according to
        #: whether the Markdown input was a :class:`str` or :class:`bytes`.
        self.bytes = use_bytes

        #: The parent of this node, or None (for the root Document node and
        #: attribute nodes)
        self.parent = None

    def attr_to_ast(self, attribute):
        """:class:`md4c.GenericParser` represents :ref:`attributes <attribute>`
        as lists of 2-tuples (or None). This static method converts them to a
        list of text :class:`ASTNode`.

        :param attribute: List of tuples or None

        :returns: List of text :class:`ASTNode` or None
        """
        if attribute is None:
            return None
        result = []
        for text_type, text in attribute:
            result.append(ASTNode(text_type, use_bytes=self.bytes, text=text))
        return result

    def render_attr(self, attribute, url_escape=False):
        """Render an attribute given as a list of :class:`ASTNode` or None

        :param attribute: List of :class:`ASTNode` or None
        :param url_escape: If True, perform URL escaping on the text.
                           Otherwise, perform the default (HTML) escaping.
        :type url_escape: bool, optional

        :returns: Rendered output.
        :rtype: str or bytes
        """
        if attribute is None:
            return b'' if self.bytes else ''
        renderings = []
        for text in attribute:
            renderings.append(text.render(url_escape=url_escape))
        return b''.join(renderings) if self.bytes else ''.join(renderings)

    def render(self, **kwargs):
        """Render this node and its children. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering. Non-leaf nodes should also pass this data on
                       to their own children.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str or bytes
        """
        return b'' if self.bytes else ''


class ContainerNode(ASTNode, element_type=None):
    """ContainerNode(element_type, **kwargs)

    Base class for all AST nodes that may have children (blocks and spans
    except :class:`HorizontalRule`).

    :param element_type: A :class:`md4c.BlockType`, or :class:`md4c.SpanType`
                         representing the type of this element
    """
    def __init__(self, element_type, **kwargs):
        super().__init__(element_type, **kwargs)

        #: A list of this node's children.
        self.children = []

    def append(self, node):
        """Add a new child to the node and set its parent to this object

        :param node: The child to add
        """
        if self.bytes and not node.bytes:
            raise ValueError("Cannot add a str node to a bytes node")
        if not self.bytes and node.bytes:
            raise ValueError("Cannot add a bytes node to a str node")
        node.parent = self
        self.children.append(node)

    def insert(self, i, node):
        """Insert a new child into the node at index *i*

        :param i: The new child will be at this index.
        :param node: The child to insert
        """
        if self.bytes and not node.bytes:
            raise ValueError("Cannot add a str node to a bytes node")
        if not self.bytes and node.bytes:
            raise ValueError("Cannot add a bytes node to a str node")
        node.parent = self
        self.children.insert(i, node)

    def render_pre(self, **kwargs):
        """Render the opening for this node. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str or bytes
        """
        return b'' if self.bytes else ''

    def render_post(self, **kwargs):
        """Render the closing for this node. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str or bytes
        """
        return b'' if self.bytes else ''

    def render(self, **kwargs):
        """A render implementation that should suit elements with children
        well: Renders the opening for this node, then all its children, then
        the closing for this node.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering. This data is also passed on to children.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str or bytes
        """
        renderings = [self.render_pre(**kwargs)]
        for child in self.children:
            renderings.append(child.render(**kwargs))
        renderings.append(self.render_post(**kwargs))

        return b''.join(renderings) if self.bytes else ''.join(renderings)


class TextNode(ASTNode, element_type=None):
    """TextNode(element_type, text, **kwargs)

    Base class for all AST nodes representing text.

    :param element_type: A :class:`md4c.TextType` representing the type of this
                         element
    :param text: The text this node represents, unprocessed
    :type text: str or bytes
    """
    def __init__(self, element_type, text, **kwargs):
        super().__init__(element_type, **kwargs)

        # Verify text type matches use_bytes parameter
        if self.bytes and not isinstance(text, _ByteString):
            raise TypeError("Must set use_bytes=True when text is bytes")
        if not self.bytes and not isinstance(text, str):
            raise TypeError("Must not set use_bytes=True when text is str")

        #: The unprocessed text for this node
        self.text = text

    html_escape_table = {
        ord('&'): '&amp;',
        ord('<'): '&lt;',
        ord('>'): '&gt;',
        ord('"'): '&quot;',
    }

    @classmethod
    def html_escape(cls, text):
        """Escape HTML special characters (``&<>"``)

        :param text: Text to escape
        :type text: str or bytes
        :return: Escaped string or bytes
        """
        if isinstance(text, str):
            return text.translate(cls.html_escape_table)
        # Hacky workaround since the bytes translate() function is not as
        # flexible as the string one
        string = text.decode('latin_1').translate(cls.html_escape_table)
        return string.encode('latin_1')

    @classmethod
    def url_escape(cls, text):
        """Percent-escape special characters in URLs

        :param text: URL to percent-escape
        :type text: str or bytes
        :return: Escaped string or bytes
        """
        translated = (_url_parse.quote(text, safe='-_.!*(),%#@?=;:/,+$&')
                      .replace('&', '&amp;'))
        if isinstance(text, str):
            return translated
        return translated.encode('ascii')

    def render(self, url_escape=False, **kwargs):
        """Render the text for this node, performing HTML or URL escaping in
        the process. HTML escaping translates ``<``, ``>``, ``&``, and ``"`` to
        HTML entities. URL escaping translates special characters to ``%xx``.

        :param url_escape: If True, perform URL escaping on the text.
                           Otherwise, perform the default HTML escaping.
        :type url_escape: bool, optional
        :param kwargs: Other data passed from the parent node that may be
                       useful for rendering.

        :returns: Rendered output, suitable for inclusion in an HTML document.
        :rtype: str or bytes
        """
        if url_escape:
            return self.url_escape(self.text)
        return self.html_escape(self.text)


###############################################################################
# Default AST nodes (render() methods produce HTML) - Blocks                  #
###############################################################################


class Document(ContainerNode, element_type=_BlockType.DOC):
    """Document(element_type, **kwargs)

    Document block. Root node of the AST. Inherits from
    :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.DOC`
    """


class Quote(ContainerNode, element_type=_BlockType.QUOTE):
    """Quote(element_type, **kwargs)

    Quote block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.QUOTE`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this quote block.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<blockquote>\n' if self.bytes else '<blockquote>\n'

    def render_post(self, **kwargs):
        """Render the closing for this quote block.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</blockquote>\n' if self.bytes else '</blockquote>\n'


class UnorderedList(ContainerNode, element_type=_BlockType.UL):
    """UnorderedList(element_type, is_tight, mark, **kwargs)

    Unordered list block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.UL`
    :param is_tight: Whether the list is tight_ or not
    :type is_tight: bool
    :param mark: The character used as a bullet point
    :type mark: str

    .. _tight: https://spec.commonmark.org/0.29/#tight
    """
    def __init__(self, element_type, is_tight, mark, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Whether the list is tight_ or not
        self.is_tight = is_tight
        #: The character used as a bullet point
        self.mark = mark

    def render_pre(self, **kwargs):
        """Render the opening for this unordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<ul>\n' if self.bytes else '<ul>\n'

    def render_post(self, **kwargs):
        """Render the closing for this unordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</ul>\n' if self.bytes else '</ul>\n'


class OrderedList(ContainerNode, element_type=_BlockType.OL):
    """OrderedList(element_type, start, is_tight, mark, **kwargs)

    Ordered list block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.OL`
    :param start: Start index of the ordered list
    :type start: int
    :param is_tight: Whether the list is tight_ or not
    :type is_tight: bool
    :param mark_delimiter: The character used as the number delimiter
    :type mark_delimiter: str

    .. _tight: https://spec.commonmark.org/0.29/#tight
    """
    def __init__(self, element_type, start, is_tight, mark_delimiter,
                 **kwargs):
        super().__init__(element_type, **kwargs)
        #: Start index of the ordered list
        self.start = start
        #: Whether the list is tight_ or not
        self.is_tight = is_tight
        #: The character used as the number delimiter
        self.mark_delimiter = mark_delimiter

    def render_pre(self, **kwargs):
        """Render the opening for this ordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.start == 1:
            return b'<ol>\n' if self.bytes else '<ol>\n'
        else:
            if self.bytes:
                return b'<ol start="%d">\n' % self.start
            else:
                return '<ol start="%d">\n' % self.start

    def render_post(self, **kwargs):
        """Render the closing for this ordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</ol>\n' if self.bytes else '</ol>\n'


class ListItem(ContainerNode, element_type=_BlockType.LI):
    """ListItem(element_type, is_task, task_mark, task_mark_offset, **kwargs)

    List item block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.LI`
    :param is_task: Whether the list item is a task list item
    :type is_task: bool
    :param task_mark: The character used to mark the task. Not required if not
                      a task list item.
    :type task_mark: str, optional
    :param task_mark_offset: The offset of the task mark between the ``[]``.
                             Not required if not a task list item.
    :type task_mark_offset: int, optional
    """
    def __init__(self, element_type, is_task,
                 task_mark=None, task_mark_offset=None, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Whether the list item is a task list item
        self.is_task = is_task
        #: The character used to mark the task (if a task list item)
        self.task_mark = task_mark
        #: The offset of the task mark between the ``[]`` (if a task list item)
        self.task_mark_offset = task_mark_offset

    def render_pre(self, **kwargs):
        """Render the opening for this list item.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.is_task:
            if self.task_mark in ('x', 'X'):
                return (b'<li class="task-list-item"><input type="checkbox" '
                        b'class="task-list-item-checkbox" disabled checked>'
                        if self.bytes else
                        '<li class="task-list-item"><input type="checkbox" '
                        'class="task-list-item-checkbox" disabled checked>')
            else:
                return (b'<li class="task-list-item"><input type="checkbox" '
                        b'class="task-list-item-checkbox" disabled>'
                        if self.bytes else
                        '<li class="task-list-item"><input type="checkbox" '
                        'class="task-list-item-checkbox" disabled>')
        return b'<li>' if self.bytes else '<li>'

    def render_post(self, **kwargs):
        """Render the closing for this list item.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</li>\n' if self.bytes else '</li>\n'


class HorizontalRule(ASTNode, element_type=_BlockType.HR):
    """HorizontalRule(element_type, **kwargs)

    Horizontal rule block. Inherits from :class:`ASTNode`.

    :param element_type: :attr:`md4c.BlockType.HR`
    """

    def render(self, **kwargs):
        """Render this horizontal rule.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<hr>\n' if self.bytes else '<hr>\n'


class Heading(ContainerNode, element_type=_BlockType.H):
    """Heading(element_type, level, **kwargs)

    Heading block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.H`
    :param level: Heading level (1-6)
    :type level: int
    """
    def __init__(self, element_type, level, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Heading level (1-6)
        self.level = level

    def render_pre(self, **kwargs):
        """Render the opening for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.bytes:
            return b'<h%d>' % self.level
        return f'<h{self.level}>'

    def render_post(self, **kwargs):
        """Render the closing for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.bytes:
            return b'</h%d>\n' % self.level
        return f'</h{self.level}>\n'


class CodeBlock(ContainerNode, element_type=_BlockType.CODE):
    """CodeBlock(element_type, fence_char, info, lang, **kwargs)

    Code block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.CODE`
    :param fence_char: Fence character. None for indented code blocks.
    :type fence_char: str or None
    :param info: Info string, if present.
    :type info: :ref:`Attribute <attribute>` or None, optional
    :param lang: Language, if present.
    :type lang: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, fence_char=None, info=None, lang=None,
                 **kwargs):
        super().__init__(element_type, **kwargs)
        #: Fence character, if a fenced code block. None otherwise.
        self.fence_char = fence_char
        #: Info string, as a list of :class:`ASTNode` (if a fenced code block)
        self.info = self.attr_to_ast(info)
        #: Language, as a list of :class:`ASTNode` (if a fenced code block)
        self.lang = self.attr_to_ast(lang)

    def render_pre(self, **kwargs):
        """Render the opening for this code block.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.lang is None:
            return b'<pre><code>' if self.bytes else '<pre><code>'
        else:
            lang = self.render_attr(self.lang)
            if self.bytes:
                return b'<pre><code class="language-%b">' % lang
            return f'<pre><code class="language-{lang}">'

    def render_post(self, **kwargs):
        """Render the closing for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</code></pre>\n' if self.bytes else '</code></pre>\n'


class RawHTMLBlock(ContainerNode, element_type=_BlockType.HTML):
    """RawHTMLBlock(element_type, **kwargs)

    Raw HTML block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.HTML`
    """


class Paragraph(ContainerNode, element_type=_BlockType.P):
    """Paragraph(element_type, **kwargs)

    Paragraph.

    :param element_type: :attr:`md4c.BlockType.P`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this paragraph.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<p>' if self.bytes else '<p>'

    def render_post(self, **kwargs):
        """Render the closing for this paragraph.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</p>\n' if self.bytes else '</p>\n'


class Table(ContainerNode, element_type=_BlockType.TABLE):
    """Table(element_type, col_count, head_row_count, bod_row_count, **kwargs)

    Table. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TABLE`
    :param col_count: Number of columns in the table
    :type col_count: int
    :param head_row_count: Number of rows in the table head
    :type head_row_count: int
    :param body_row_count: Number of rows in the table body
    :type body_row_count: int
    """
    def __init__(self, element_type,
                 col_count, head_row_count, body_row_count, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Number of columns in the table
        self.col_count = col_count
        #: Number of rows in the table head
        self.head_row_count = head_row_count
        #: Number of rows in the table body
        self.body_row_count = body_row_count

    def render_pre(self, **kwargs):
        """Render the opening for this table.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<table>\n' if self.bytes else '<table>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</table>\n' if self.bytes else '</table>\n'


class TableHead(ContainerNode, element_type=_BlockType.THEAD):
    """TableHead(element_type, **kwargs)

    Table heading. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.THEAD`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<thead>\n' if self.bytes else '<thead>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</thead>\n' if self.bytes else '</thead>\n'


class TableBody(ContainerNode, element_type=_BlockType.TBODY):
    """TableBody(element_type, **kwargs)

    Table body. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TBODY`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table body.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<tbody>\n' if self.bytes else '<tbody>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table body.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</tbody>\n' if self.bytes else '</tbody>\n'


class TableRow(ContainerNode, element_type=_BlockType.TR):
    """TableRow(element_type, **kwargs)

    Table row. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TR`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table row.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'<tr>\n' if self.bytes else '<tr>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table row.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</tr>\n' if self.bytes else '</tr>\n'


class TableHeaderCell(ContainerNode, element_type=_BlockType.TH):
    """TableHeaderCell(element_type, align, **kwargs)

    Table header cell. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TH`
    :param align: Text alignment for the cell
    :type align: :class:`md4c.Align`
    """
    def __init__(self, element_type, align, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Text alignment for the cell (a :attr:`md4c.BlockType.TH`)
        self.align = align

    def render_pre(self, **kwargs):
        """Render the opening for this table header cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.align is _Align.LEFT:
            return b'<th align="left">' if self.bytes else '<th align="left">'
        elif self.align is _Align.CENTER:
            return (b'<th align="center">' if self.bytes
                    else '<th align="center">')
        elif self.align is _Align.RIGHT:
            return (b'<th align="right">' if self.bytes
                    else '<th align="right">')
        else:
            return b'<th>' if self.bytes else '<th>'

    def render_post(self, **kwargs):
        """Render the closing for this table header cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</th>\n' if self.bytes else '</th>\n'


class TableCell(ContainerNode, element_type=_BlockType.TD):
    """TableCell(element_type, align, **kwargs)

    Table cell. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TD`
    :param align: Text alignment for the cell
    :type align: :class:`md4c.Align`
    """
    def __init__(self, element_type, align, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Text alignment for the cell (a :attr:`md4c.BlockType.TH`)
        self.align = align

    def render_pre(self, **kwargs):
        """Render the opening for this table cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if self.align is _Align.LEFT:
            return b'<td align="left">' if self.bytes else '<td align="left">'
        elif self.align is _Align.CENTER:
            return (b'<td align="center">' if self.bytes
                    else '<td align="center">')
        elif self.align is _Align.RIGHT:
            return (b'<td align="right">' if self.bytes
                    else '<td align="right">')
        else:
            return b'<td>' if self.bytes else '<td>'

    def render_post(self, **kwargs):
        """Render the closing for this table cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        return b'</td>\n' if self.bytes else '</td>\n'


###############################################################################
# Default AST nodes (render() methods produce HTML) - Inlines                 #
###############################################################################


class Emphasis(ContainerNode, element_type=_SpanType.EM):
    """Emphasis(element_type, **kwargs)

    Emphasis inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.EM`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<em>' if self.bytes else '<em>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</em>' if self.bytes else '</em>'
        return b'' if self.bytes else ''


class Strong(ContainerNode, element_type=_SpanType.STRONG):
    """Strong(element_type, **kwargs)

    Strong emphasis inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.STRONG`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this strong emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<strong>' if self.bytes else '<strong>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this strong emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</strong>' if self.bytes else '</strong>'
        return b'' if self.bytes else ''


class Underline(ContainerNode, element_type=_SpanType.U):
    """Underline(element_type, **kwargs)

    Underline inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.U`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this underline inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<u>' if self.bytes else '<u>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this underline inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</u>' if self.bytes else '</u>'
        return b'' if self.bytes else ''


class Link(ContainerNode, element_type=_SpanType.A):
    """Link(element_type, href, title, **kwargs)

    Hyperlink inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.A`
    :param href: Link URL
    :type href: :ref:`Attribute <attribute>`
    :param title: Link title, if present
    :type title: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, href, title=None, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Link URL, as a list of text :class:`ASTNode`
        self.href = self.attr_to_ast(href)
        #: Link title, as a list of text :class:`ASTNode` (or None if not
        #: present)
        self.title = self.attr_to_ast(title)

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            href = self.render_attr(self.href, url_escape=True)
            if self.title is not None:
                title = self.render_attr(self.title)
                if self.bytes:
                    return b'<a href="%b" title="%b">' % (href, title)
                return f'<a href="{href}" title="{title}">'
            else:
                if self.bytes:
                    return b'<a href="%b">' % href
                return f'<a href="{href}">'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</a>' if self.bytes else '</a>'
        return b'' if self.bytes else ''


class Image(ContainerNode, element_type=_SpanType.IMG):
    """Image(element_type, src, title, **kwargs)

    Image inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.IMG`
    :param src: Image URL
    :type src: :ref:`Attribute <attribute>`
    :param title: Image title, if present
    :type title: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, src, title=None, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Image URL, as a list of :class:`ASTNode`
        self.src = self.attr_to_ast(src)
        #: Image title, as a list of :class:`ASTNode` (or None if not present)
        self.title = self.attr_to_ast(title)

    def render_pre(self, image_nesting_level, **kwargs):
        """Render the opening for this image inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline, plus one for this image. HTML tags
                                    are not rendered inside image elements.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 1:
            src = self.render_attr(self.src, url_escape=True)
            if self.bytes:
                return b'<img src="%b" alt="' % src
            return f'<img src="{src}" alt="'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level, **kwargs):
        """Render the closing for this image inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline, plus one for this image. HTML tags
                                    are not rendered inside image elements.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 1:
            if self.title is not None:
                title = self.render_attr(self.title)
                if self.bytes:
                    return b'" title="%b">' % title
                return f'" title="{title}">'
            else:
                return b'">' if self.bytes else '">'
        return b'' if self.bytes else ''

    def render(self, image_nesting_level=0, **kwargs):
        """Render this image element and the alt text within.

        :param image_nesting_level: Number of image elements enclosing this
                                    image. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        image_nesting_level += 1
        return super().render(image_nesting_level=image_nesting_level,
                              **kwargs)


class Code(ContainerNode, element_type=_SpanType.CODE):
    """Code(element_type, **kwargs)

    Code inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.CODE`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this code inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<code>' if self.bytes else '<code>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this code inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</code>' if self.bytes else '</code>'
        return b'' if self.bytes else ''


class Strikethrough(ContainerNode, element_type=_SpanType.DEL):
    """Strikethrough(element_type, **kwargs)

    Strikethrough inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.DEL`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this strikethrough inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<del>' if self.bytes else '<del>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this strikethrough inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</del>' if self.bytes else '</del>'
        return b'' if self.bytes else ''


class InlineMath(ContainerNode, element_type=_SpanType.LATEXMATH):
    """InlineMath(element_type, **kwargs)

    Inline math. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.LATEXMATH`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this inline math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'<x-equation>' if self.bytes else '<x-equation>'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this inline math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</x-equation>' if self.bytes else '</x-equation>'
        return b'' if self.bytes else ''


class DisplayMath(ContainerNode, element_type=_SpanType.LATEXMATH_DISPLAY):
    """DisplayMath(element_type, **kwargs)

    Display math. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.LATEXMATH_DISPLAY`
    """

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this display math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return (b'<x-equation type="display">' if self.bytes
                    else '<x-equation type="display">')
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this display math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</x-equation>' if self.bytes else '</x-equation>'
        return b'' if self.bytes else ''


class WikiLink(ContainerNode, element_type=_SpanType.WIKILINK):
    """WikiLink(element_type, target, **kwargs)

    Wiki link inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.WIKILINK`
    :param target: Link target
    :type target: :ref:`Attribute <attribute>`
    """
    def __init__(self, element_type, target, **kwargs):
        super().__init__(element_type, **kwargs)
        #: Link target, as a list of :class:`ASTNode`
        self.target = self.attr_to_ast(target)

    def render_pre(self, image_nesting_level=0, **kwargs):
        """Render the opening for this wiki link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            target = self.render_attr(self.target)
            if self.bytes:
                return b'<x-wikilink data-target="%b">' % target
            return f'<x-wikilink data-target="{target}">'
        return b'' if self.bytes else ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this wiki link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            return b'</x-wikilink>' if self.bytes else '</x-wikilink>'
        return b'' if self.bytes else ''


###############################################################################
# Default AST nodes (render() methods produce HTML) - Text nodes              #
###############################################################################


class NormalText(TextNode, element_type=_TextType.NORMAL):
    """NormalText(element_type, text, **kwargs)

    Normal text. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.NORMAL`
    :param text: The actual text
    :type text: str or bytes
    """


class NullChar(TextNode, element_type=_TextType.NULLCHAR):
    """NullChar(element_type, text, **kwargs)

    Null character. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.NULLCHAR`
    :param text: Should be a null character, but this class assumes it is and
                 ignores it.
    :type text: str or bytes
    """

    def render(self, **kwargs):
        """Render this null character (as the Unicode replacement character,
        codepoint 0xFFFD)

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Null character
        :rtype: str or bytes
        """
        if isinstance(self.text, str):
            return '\ufffd'
        return '\ufffd'.encode()


class LineBreak(TextNode, element_type=_TextType.BR):
    """LineBreak(element_type, text, **kwargs)

    Line break. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.BR`
    :param text: Should be a newline character, but this class assumes it is
                 and ignores it.
    :type text: str or bytes
    """

    def render(self, image_nesting_level=0, **kwargs):
        """Render this line break.

        :param image_nesting_level: Number of image elements enclosing this
                                    line break. HTML tags are not rendered
                                    inside image elements. 0 assumed if not
                                    provided.
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Rendered line break tag or space
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            ret_val = '<br>\n'
        else:
            ret_val = ' '
        if isinstance(self.text, str):
            return ret_val
        return ret_val.encode()


class SoftLineBreak(TextNode, element_type=_TextType.SOFTBR):
    """SoftLineBreak(element_type, text, **kwargs)

    Soft line break. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.SOFTBR`
    :param text: Should be a newline character, but this class assumes it is
                 and ignores it.
    :type text: str or bytes
    """

    def render(self, image_nesting_level=0, **kwargs):
        """Render this soft line break.

        :param image_nesting_level: Number of image elements enclosing this
                                    line break. Line breaks are not rendered
                                    inside image elements. 0 assumed if not
                                    provided.
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Newline or space
        :rtype: str or bytes
        """
        if image_nesting_level == 0:
            ret_val = '\n'
        else:
            ret_val = ' '
        if isinstance(self.text, str):
            return ret_val
        return ret_val.encode()


class HTMLEntity(TextNode, element_type=_TextType.ENTITY):
    """HTMLEntity(element_type, text, **kwargs)

    HTML entity. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.ENTITY`
    :param text: The entity, including ampersand and semicolon
    :type text: str or bytes
    """

    def render(self, url_escape=False, **kwargs):
        """Render this HTML entity.

        :param url_escape: If True, perform URL escaping on the translated
                           entity. Otherwise, perform the default HTML
                           escaping.
        :type url_escape: bool, optional
        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Corresponding UTF-8 text for the entity.
        :rtype: str or bytes
        """
        entity = _lookup_entity(self.text)
        if isinstance(entity, str):
            # Need to check for null characters in case the entity was '&#0;'
            entity = entity.replace('\x00', '\ufffd')
            if isinstance(self.text, _ByteString):
                entity = entity.encode()
        if url_escape:
            return self.url_escape(entity)
        return self.html_escape(entity)


class CodeText(TextNode, element_type=_TextType.CODE):
    """CodeText(element_type, text, **kwargs)

    Text in a code block or code span. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.CODE`
    :param text: The actual code
    :type text: str or bytes
    """


class HTMLText(TextNode, element_type=_TextType.HTML):
    """HTMLText(element_type, text, **kwargs)

    Raw HTML text. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.HTML`
    :param text: The raw HTML
    :type text: str or bytes
    """

    def render(self, **kwargs):
        """Render this HTML text.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Raw HTML text
        :rtype: str or bytes
        """
        return self.text


class MathText(TextNode, element_type=_TextType.LATEXMATH):
    """MathText(element_type, text, **kwargs)

    Text in an equation. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.LATEXMATH`
    :param text: The actual text
    :type text: str or bytes
    """
