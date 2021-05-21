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
    """
    _registry = dict()

    @classmethod
    def __init_subclass__(cls, element_type, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register cls as the class to create for element_type
        if element_type is not None:
            cls._registry[element_type] = cls

    def __new__(cls, element_type, **kwargs):
        # Select the appropriate subclass. There should never be a KeyError,
        # and if there is, it means we forgot to add a class in this module for
        # one of the BlockType/SpanType/TextType members.
        subcls = cls._registry[element_type]
        return object.__new__(subcls)

    # This isn't strictly necessary--the type of element is encoded in the type
    # of the object. But if a user decides to replace one of the built-in
    # classes for a particular element, isinstance() won't work so well, but
    # comparing self.type will.
    def __init__(self, element_type):
        #: A :class:`md4c.BlockType`, :class:`md4c.SpanType`, or
        #: :class:`md4c.TextType` representing the type of element this object
        #: represents
        self.type = element_type

        #: The parent of this node, or None (for the root Document node and
        #: attribute nodes)
        self.parent = None

    @staticmethod
    def attr_to_ast(attribute):
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
            result.append(ASTNode(text_type, text=text))
        return result

    @staticmethod
    def render_attr(attribute, url_escape=False):
        """Render an attribute given as a list of :class:`ASTNode` or None

        :param attribute: List of :class:`ASTNode` or None
        :param url_escape: If True, perform URL escaping on the text.
                           Otherwise, perform the default (HTML) escaping.
        :type url_escape: bool, optional

        :returns: Rendered output.
        :rtype: str
        """
        if attribute is None:
            return ''
        renderings = []
        for text in attribute:
            renderings.append(text.render(url_escape=url_escape))
        return ''.join(renderings)

    def render(self, **kwargs):
        """Render this node and its children. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering. Non-leaf nodes should also pass this data on
                       to their own children.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str
        """
        return ""


class ContainerNode(ASTNode, element_type=None):
    """Base class for all AST nodes that may have children (blocks and spans
    except :class:`HorizontalRule`).

    :param element_type: A :class:`md4c.BlockType`, or :class:`md4c.SpanType`
                         representing the type of this element
    """
    def __init__(self, element_type):
        super().__init__(element_type)

        #: A list of this node's children.
        self.children = []

    def append(self, node):
        """Add a new child to the node and set its parent to this object

        :param node: The child to add
        """
        node.parent = self
        self.children.append(node)

    def insert(self, i, node):
        """Insert a new child into the node at index *i*

        :param i: The new child will be at this index.
        :param node: The child to insert
        """
        node.parent = self
        self.children.insert(i, node)

    def render_pre(self, **kwargs):
        """Render the opening for this node. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str
        """
        return ""

    def render_post(self, **kwargs):
        """Render the closing for this node. This base implementation returns
        an empty string, but subclasses should override as appropriate.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str
        """
        return ""

    def render(self, **kwargs):
        """A render implementation that should suit elements with children
        well: Renders the opening for this node, then all its children, then
        the closing for this node.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering. This data is also passed on to children.

        :returns: Rendered output. The default AST types render HTML, but they
                  can be replaced to render any output format necessary.
        :rtype: str
        """
        renderings = [self.render_pre(**kwargs)]
        for child in self.children:
            renderings.append(child.render(**kwargs))
        renderings.append(self.render_post(**kwargs))

        return ''.join(renderings)


class TextNode(ASTNode, element_type=None):
    """Base class for all AST nodes representing text.

    :param element_type: A :class:`md4c.BlockType`, or :class:`md4c.SpanType`
                         representing the type of this element
    :param text: The text this node represents, unprocessed
    :type text: str
    """
    def __init__(self, element_type, text):
        super().__init__(element_type)

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
        :return: Escaped string
        """
        return text.translate(cls.html_escape_table)

    class _URLEscapeDict(dict):
        """Dict that does percent escaping for any item not in it"""
        def __missing__(self, cp):
            utf8 = chr(cp).encode('utf-8')
            return ''.join(f'%{b:02X}' for b in utf8)

    url_escape_table = _URLEscapeDict(
        {ord(c): c for c in "0123456789-_.+!*(),%#@?=;:/,+$"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"})
    url_escape_table[ord('&')] = '&amp;'

    @classmethod
    def url_escape(cls, text):
        """Percent-escape special characters in URLs

        :param text: URL to percent-escape
        :return: Escaped string
        """
        return text.translate(cls.url_escape_table)

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
        :rtype: str
        """
        if url_escape:
            return self.url_escape(self.text)
        return self.html_escape(self.text)


###############################################################################
# Default AST nodes (render() methods produce HTML) - Blocks                  #
###############################################################################


class Document(ContainerNode, element_type=_BlockType.DOC):
    """Document block. Root node of the AST. Inherits from
    :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.DOC`
    """


class Quote(ContainerNode, element_type=_BlockType.QUOTE):
    """Quote block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.QUOTE`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this quote block.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<blockquote>\n'

    def render_post(self, **kwargs):
        """Render the closing for this quote block.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</blockquote>\n'


class UnorderedList(ContainerNode, element_type=_BlockType.UL):
    """UnorderedList(element_type, is_tight, mark)

    Unordered list block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.UL`
    :param is_tight: Whether the list is tight_ or not
    :type is_tight: bool
    :param mark: The character used as a bullet point
    :type mark: str

    .. _tight: https://spec.commonmark.org/0.29/#tight
    """
    def __init__(self, element_type, is_tight, mark):
        super().__init__(element_type)
        #: Whether the list is tight_ or not
        self.is_tight = is_tight
        #: The character used as a bullet point
        self.mark = mark

    def render_pre(self, **kwargs):
        """Render the opening for this unordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<ul>\n'

    def render_post(self, **kwargs):
        """Render the closing for this unordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</ul>\n'


class OrderedList(ContainerNode, element_type=_BlockType.OL):
    """OrderedList(element_type, start, is_tight, mark)

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
    def __init__(self, element_type, start, is_tight, mark_delimiter):
        super().__init__(element_type)
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
        :rtype: str
        """
        if self.start == 1:
            return '<ol>\n'
        else:
            return f'<ol start="{self.start}">\n'

    def render_post(self, **kwargs):
        """Render the closing for this ordered list.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</ol>\n'


class ListItem(ContainerNode, element_type=_BlockType.LI):
    """ListItem(element_type, is_task, task_mark, task_mark_offset)

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
                 task_mark=None, task_mark_offset=None):
        super().__init__(element_type)
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
        :rtype: str
        """
        if self.is_task:
            if self.task_mark in ('x', 'X'):
                return ('<li class="task-list-item"><input type="checkbox" '
                        'class="task-list-item-checkbox" disabled checked>')
            else:
                return ('<li class="task-list-item"><input type="checkbox" '
                        'class="task-list-item-checkbox" disabled>')
        return '<li>'

    def render_post(self, **kwargs):
        """Render the closing for this list item.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</li>\n'


class HorizontalRule(ASTNode, element_type=_BlockType.HR):
    """Horizontal rule block. Inherits from :class:`ASTNode`.

    :param element_type: :attr:`md4c.BlockType.HR`
    """

    def render(self, **kwargs):
        """Render this horizontal rule.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<hr>\n'


class Heading(ContainerNode, element_type=_BlockType.H):
    """Heading(element_type, level)

    Heading block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.H`
    :param level: Heading level (1-6)
    :type level: int
    """
    def __init__(self, element_type, level):
        super().__init__(element_type)
        #: Heading level (1-6)
        self.level = level

    def render_pre(self, **kwargs):
        """Render the opening for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return f'<h{self.level}>'

    def render_post(self, **kwargs):
        """Render the closing for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return f'</h{self.level}>\n'


class CodeBlock(ContainerNode, element_type=_BlockType.CODE):
    """CodeBlock(element_type, fence_char, info, lang)

    Code block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.CODE`
    :param fence_char: Fence character. Omit for indented code blocks.
    :type fence_char: str, optional
    :param info: Info string, if present.
    :type info: :ref:`Attribute <attribute>` or None, optional
    :param lang: Language, if present.
    :type lang: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, fence_char=None, info=None, lang=None):
        super().__init__(element_type)
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
        :rtype: str
        """
        if self.lang is None:
            return '<pre><code>'
        else:
            lang = self.render_attr(self.lang)
            return f'<pre><code class="language-{lang}">'

    def render_post(self, **kwargs):
        """Render the closing for this heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</code></pre>\n'


class RawHTMLBlock(ContainerNode, element_type=_BlockType.HTML):
    """Raw HTML block. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.HTML`
    """


class Paragraph(ContainerNode, element_type=_BlockType.P):
    """Paragraph.

    :param element_type: :attr:`md4c.BlockType.P`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this paragraph.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<p>'

    def render_post(self, **kwargs):
        """Render the closing for this paragraph.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</p>\n'


class Table(ContainerNode, element_type=_BlockType.TABLE):
    """Table(element_type, col_count, head_row_count, bod_row_count)

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
                 col_count, head_row_count, body_row_count):
        super().__init__(element_type)
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
        :rtype: str
        """
        return '<table>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</table>\n'


class TableHead(ContainerNode, element_type=_BlockType.THEAD):
    """Table heading. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.THEAD`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<thead>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table heading.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</thead>\n'


class TableBody(ContainerNode, element_type=_BlockType.TBODY):
    """Table body. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TBODY`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table body.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<tbody>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table body.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</tbody>\n'


class TableRow(ContainerNode, element_type=_BlockType.TR):
    """Table row. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TR`
    """

    def render_pre(self, **kwargs):
        """Render the opening for this table row.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '<tr>\n'

    def render_post(self, **kwargs):
        """Render the closing for this table row.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</tr>\n'


class TableHeaderCell(ContainerNode, element_type=_BlockType.TH):
    """TableHeaderCell(element_type, align)

    Table header cell. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TH`
    :param align: Text alignment for the cell
    :type align: :class:`md4c.Align`
    """
    def __init__(self, element_type, align):
        super().__init__(element_type)
        #: Text alignment for the cell (a :attr:`md4c.BlockType.TH`)
        self.align = align

    def render_pre(self, **kwargs):
        """Render the opening for this table header cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if self.align is _Align.LEFT:
            return '<th align="left">'
        elif self.align is _Align.CENTER:
            return '<th align="center">'
        elif self.align is _Align.RIGHT:
            return '<th align="right">'
        else:
            return '<th>'

    def render_post(self, **kwargs):
        """Render the closing for this table header cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</th>\n'


class TableCell(ContainerNode, element_type=_BlockType.TD):
    """TableCell(element_type, align)

    Table cell. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.BlockType.TD`
    :param align: Text alignment for the cell
    :type align: :class:`md4c.Align`
    """
    def __init__(self, element_type, align):
        super().__init__(element_type)
        #: Text alignment for the cell (a :attr:`md4c.BlockType.TH`)
        self.align = align

    def render_pre(self, **kwargs):
        """Render the opening for this table cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if self.align is _Align.LEFT:
            return '<td align="left">'
        elif self.align is _Align.CENTER:
            return '<td align="center">'
        elif self.align is _Align.RIGHT:
            return '<td align="right">'
        else:
            return '<td>'

    def render_post(self, **kwargs):
        """Render the closing for this table cell.

        :param kwargs: The data passed to the :meth:`render` function from the
                       parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        return '</td>\n'


###############################################################################
# Default AST nodes (render() methods produce HTML) - Inlines                 #
###############################################################################


class Emphasis(ContainerNode, element_type=_SpanType.EM):
    """Emphasis inline. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<em>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</em>'
        return ''


class Strong(ContainerNode, element_type=_SpanType.STRONG):
    """Strong emphasis inline. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<strong>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this strong emphasis inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</strong>'
        return ''


class Underline(ContainerNode, element_type=_SpanType.U):
    """Underline inline. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<u>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this underline inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</u>'
        return ''


class Link(ContainerNode, element_type=_SpanType.A):
    """Link(element_type, href, title)

    Hyperlink inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.A`
    :param href: Link URL
    :type href: :ref:`Attribute <attribute>`
    :param title: Link title, if present
    :type title: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, href, title=None):
        super().__init__(element_type)
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
        :rtype: str
        """
        if image_nesting_level == 0:
            href = self.render_attr(self.href, url_escape=True)
            if self.title is not None:
                title = self.render_attr(self.title)
                return f'<a href="{href}" title="{title}">'
            else:
                return f'<a href="{href}">'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</a>'
        return ''


class Image(ContainerNode, element_type=_SpanType.IMG):
    """Image(element_type, src, title)

    Image inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.IMG`
    :param src: Image URL
    :type src: :ref:`Attribute <attribute>`
    :param title: Image title, if present
    :type title: :ref:`Attribute <attribute>` or None, optional
    """
    def __init__(self, element_type, src, title=None):
        super().__init__(element_type)
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
        :rtype: str
        """
        if image_nesting_level == 1:
            src = self.render_attr(self.src, url_escape=True)
            return f'<img src="{src}" alt="'
        return ''

    def render_post(self, image_nesting_level, **kwargs):
        """Render the closing for this image inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline, plus one for this image. HTML tags
                                    are not rendered inside image elements.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 1:
            if self.title is not None:
                title = self.render_attr(self.title)
                return f'" title="{title}">'
            else:
                return '">'
        return ''

    def render(self, image_nesting_level=0, **kwargs):
        """Render this image element and the alt text within.

        :param image_nesting_level: Number of image elements enclosing this
                                    image. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        image_nesting_level += 1
        return super().render(image_nesting_level=image_nesting_level,
                              **kwargs)


class Code(ContainerNode, element_type=_SpanType.CODE):
    """Code inline. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<code>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this code inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</code>'
        return ''


class Strikethrough(ContainerNode, element_type=_SpanType.DEL):
    """Strikethrough inline. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<del>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this strikethrough inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</del>'
        return ''


class InlineMath(ContainerNode, element_type=_SpanType.LATEXMATH):
    """Inline math. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<x-equation>'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this inline math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</x-equation>'
        return ''


class DisplayMath(ContainerNode, element_type=_SpanType.LATEXMATH_DISPLAY):
    """Display math. Inherits from :class:`ContainerNode`.

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
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<x-equation type="display">'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this display math.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</x-equation>'
        return ''


class WikiLink(ContainerNode, element_type=_SpanType.WIKILINK):
    """WikiLink(element_type, target)

    Wiki link inline. Inherits from :class:`ContainerNode`.

    :param element_type: :attr:`md4c.SpanType.WIKILINK`
    :param target: Link target
    :type target: :ref:`Attribute <attribute>`
    """
    def __init__(self, element_type, target):
        super().__init__(element_type)
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
        :rtype: str
        """
        if image_nesting_level == 0:
            target = self.render_attr(self.target)
            return f'<x-wikilink data-target="{target}">'
        return ''

    def render_post(self, image_nesting_level=0, **kwargs):
        """Render the closing for this wiki link inline.

        :param image_nesting_level: Number of image elements enclosing this
                                    inline. HTML tags are not rendered inside
                                    image elements. 0 assumed if not provided.
        :type image_nesting_level: int, optional
        :param kwargs: The rest of the data passed to the :meth:`render`
                       function from the parent node.

        :returns: Rendered HTML
        :rtype: str
        """
        if image_nesting_level == 0:
            return '</x-wikilink>'
        return ''


###############################################################################
# Default AST nodes (render() methods produce HTML) - Text nodes              #
###############################################################################


class NormalText(TextNode, element_type=_TextType.NORMAL):
    """NormalText(element_type, text)

    Normal text. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.NORMAL`
    :param text: The actual text
    :type text: str
    """


class NullChar(TextNode, element_type=_TextType.NULLCHAR):
    """NullChar(element_type, text)

    Null character. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.NULLCHAR`
    :param text: Should be a null character, but this class assumes it is and
                 ignores it.
    :type text: str
    """

    def render(self, **kwargs):
        """Render this null character (as the Unicode replacement character,
        codepoint 0xFFFD)

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Null character
        :rtype: str
        """
        return '\ufffd'


class LineBreak(TextNode, element_type=_TextType.BR):
    """LineBreak(element_type, text)

    Line break. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.BR`
    :param text: Should be a newline character, but this class assumes it is
                 and ignores it.
    :type text: str
    """

    def render(self, image_nesting_level=0, **kwargs):
        """Render this line break.

        :param image_nesting_level: Number of image elements enclosing this
                                    line break. HTML tags are not rendered
                                    inside image elements. 0 assumed if not
                                    provided.
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Rendered line break tag or space
        :rtype: str
        """
        if image_nesting_level == 0:
            return '<br>\n'
        return ' '


class SoftLineBreak(TextNode, element_type=_TextType.SOFTBR):
    """SoftLineBreak(element_type, text)

    Soft line break. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.SOFTBR`
    :param text: Should be a newline character, but this class assumes it is
                 and ignores it.
    :type text: str
    """

    def render(self, image_nesting_level=0, **kwargs):
        """Render this soft line break.

        :param image_nesting_level: Number of image elements enclosing this
                                    line break. Line breaks are not rendered
                                    inside image elements. 0 assumed if not
                                    provided.
        :param kwargs: The rest of the data passed from the parent node.

        :returns: Newline or space
        :rtype: str
        """
        if image_nesting_level == 0:
            return '\n'
        return ' '


class HTMLEntity(TextNode, element_type=_TextType.ENTITY):
    """HTMLEntity(element_type, text)

    HTML entity. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.ENTITY`
    :param text: The entity, including ampersand and semicolon
    :type text: str
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
        :rtype: str
        """
        entity = _lookup_entity(self.text)
        entity = entity.replace('\x00', '\ufffd')
        if url_escape:
            return self.url_escape(entity)
        return self.html_escape(entity)


class CodeText(TextNode, element_type=_TextType.CODE):
    """CodeText(element_type, text)

    Text in a code block or code span. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.CODE`
    :param text: The actual code
    :type text: str
    """


class HTMLText(TextNode, element_type=_TextType.HTML):
    """HTMLText(element_type, text)

    Raw HTML text. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.HTML`
    :param text: The raw HTML
    :type text: str
    """

    def render(self, **kwargs):
        """Render this HTML text.

        :param kwargs: Data passed from the parent node that may be useful for
                       rendering.

        :returns: Raw HTML text
        :rtype: str
        """
        return self.text


class MathText(TextNode, element_type=_TextType.LATEXMATH):
    """MathText(element_type, text)

    Text in an equation. Inherits from :class:`TextNode`.

    :param element_type: :attr:`md4c.TextType.LATEXMATH`
    :param text: The actual text
    :type text: str
    """
