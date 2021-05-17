DOM API
=======

.. module:: md4c.domparser

DOM Parser
----------

.. autoclass:: DOMParser
   :members:

AST Objects
-----------

.. TODO Many of these have attributes matching what was set on the constructor.
   These should be documented somehow, whether by a note here saying additional
   parameters are exposed as members (with additional clarification for
   attributes, which are transformed) or by documenting the attributes in each
   class.

Base Classes
~~~~~~~~~~~~

.. autoclass:: ASTNode
   :members:

.. autoclass:: ContainerNode
   :members:

.. autoclass:: TextNode
   :members:

Block Elements
~~~~~~~~~~~~~~

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

Inline Elements
~~~~~~~~~~~~~~~

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

Text Elements
~~~~~~~~~~~~~

.. autoclass:: NormalText
   :members:

.. autoclass:: NullChar
   :members:

.. autoclass:: LineBreak
   :members:

.. autoclass:: SoftLineBreak
   :members:

.. autoclass:: HTMLEntity
   :members:

.. autoclass:: CodeText
   :members:

.. autoclass:: HTMLText
   :members:

.. autoclass:: MathText
   :members:
