DOM API
=======

.. module:: md4c.domparser

This is the API for the :mod:`md4c.domparser` module, which provides a DOM-like
parser built on top of the bindings from the main :mod:`md4c` module.

DOM Parser
----------

.. autoclass:: DOMParser
   :members: parse

.. _astobjs:

Base AST Classes
----------------

.. autoclass:: ASTNode
   :members:

.. autoclass:: ContainerNode
   :members:

.. autoclass:: TextNode
   :members:

.. NOTE The elements with details have them documented both as constructor
   arguments and as attributes of the class. This is a little redundant and
   makes the documentation more cluttered...consider doing it differently.

Block AST Classes
-----------------

.. autoclass:: Document
   :members:

.. autoclass:: Quote
   :members:

.. autoclass:: UnorderedList
   :members:

.. autoclass:: OrderedList
   :members:

.. autoclass:: ListItem
   :members:

.. autoclass:: HorizontalRule
   :members:

.. autoclass:: Heading
   :members:

.. autoclass:: CodeBlock
   :members:

.. autoclass:: RawHTMLBlock
   :members:

.. autoclass:: Paragraph
   :members:

.. autoclass:: Table
   :members:

.. autoclass:: TableHead
   :members:

.. autoclass:: TableBody
   :members:

.. autoclass:: TableRow
   :members:

.. autoclass:: TableHeaderCell
   :members:

.. autoclass:: TableCell
   :members:

Inline AST Classes
------------------

.. autoclass:: Emphasis
   :members:

.. autoclass:: Strong
   :members:

.. autoclass:: Underline
   :members:

.. autoclass:: Link
   :members:

.. autoclass:: Image
   :members:

.. autoclass:: Code
   :members:

.. autoclass:: Strikethrough
   :members:

.. autoclass:: InlineMath
   :members:

.. autoclass:: DisplayMath
   :members:

.. autoclass:: WikiLink
   :members:

Text AST Classes
----------------

.. autoclass:: NormalText
   :members: text, render

.. autoclass:: NullChar
   :members: text, render

.. autoclass:: LineBreak
   :members: text, render

.. autoclass:: SoftLineBreak
   :members: text, render

.. autoclass:: HTMLEntity
   :members: text, render

.. autoclass:: CodeText
   :members: text, render

.. autoclass:: HTMLText
   :members: text, render

.. autoclass:: MathText
   :members: text, render
