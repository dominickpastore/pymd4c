Pure Parsing
============

SAX-Like Parsing
----------------

Applications that want to do their own rendering or don't need to generate
output at all can use the :class:`~md4c.GenericParser` class. It is implemented
in C on top of the bare MD4C parser and provides a similar SAX-like interface.

Here is an example::

    import md4c

    # Counters

    block_counts = dict()
    span_counts = dict()
    char_count = 0

    # Callbacks

    def enter_block(block_type, details):
        try:
            block_counts[block_type] += 1
        except KeyError:
            block_counts[block_type] = 1

    def leave_block(block_type, details):
        pass

    def enter_span(span_type, details):
        try:
            span_counts[span_type] += 1
        except KeyError:
            span_counts[span_type] = 1

    def leave_span(span_type, details):
        pass

    def process_text(text_type, text):
        global char_count
        char_count += len(text)

    # Parsing

    with open('README.md', 'r') as f:
        markdown = f.read()

    parser = md4c.GenericParser()
    parser.parse(markdown,
                 enter_block, leave_block,
                 enter_span, leave_span,
                 process_text)

    for block_type, count in block_counts.items():
        print(block_type.name, ':', count)
    for span_type, count in span_counts.items():
        print(span_type.name, ':', count)
    print('Characters', ':', char_count)

This counts the number of each type of Markdown element and the total number of
displayed characters and prints a summary at the end.

There is a fair amount to digest here, so let's break it into parts.

Constructing the Parser
~~~~~~~~~~~~~~~~~~~~~~~

We will come back to the callbacks defined at the beginning of the code. The
first step in the actual parsing is to construct a parser::

    parser = md4c.GenericParser()

Much like the :class:`~md4c.HTMLRenderer`, the constructor accepts options (see
:ref:`options`), either through keyword arguments::

    parser = md4c.GenericParser(tables=True,
                                strikethrough=True)

or a positional argument::

    parser = md4c.GenericParser(
        md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH)

Note that only the parser options are accepted, since there is no rendering
(this is why there is only one positional argument).

Actual Parsing
~~~~~~~~~~~~~~

The :meth:`~md4c.GenericParser.parse` method does the actual parsing. This is
where "SAX-like" comes into play: Rather than producing an abstract syntax tree
in memory, MD4C provides a callback interface. As it digests the Markdown
document from top to bottom, it calls a callback for any of these five events:

- Entering a new block
- Leaving a block
- Entering a new inline/span
- Leaving an inline/span
- Adding text inside the current element

Accordingly, the :meth:`~md4c.GenericParser.parse` call in the example above
has six parameters. The first is the Markdown document to parse, and the other
five are the functions to use as callbacks::

    parser.parse(markdown,
                 enter_block, leave_block,
                 enter_span, leave_span,
                 process_text)

Now, let's look at how the callbacks work.

.. _callbacks:

Callbacks
~~~~~~~~~

Each :meth:`~md4c.GenericParser.parse` call requires five callbacks:

.. function:: enter_block_callback(block_type, details)

  Called whenever MD4C enters a new block.

  :param block_type: An instance of :class:`~md4c.BlockType`
  :param details: The details dict

.. function:: leave_block_callback(block_type, details)

  Called whenever MD4C leaves a block.

  :param block_type: An instance of :class:`~md4c.BlockType`
  :param details: The details dict

.. function:: enter_span_callback(span_type, details)

  Called whenever MD4C enters a new span/inline.

  :param span_type: An instance of :class:`~md4c.SpanType`
  :param details: The details dict

.. function:: leave_span_callback(span_type, details)

  Called whenever MD4C leaves a span/inline.

  :param span_type: An instance of :class:`~md4c.SpanType`
  :param details: The details dict

.. function:: text_callback(text_type, text)

  Called whenever MD4C has text to add to the current block or inline element.

  :param text_type: An instance of :class:`~md4c.TextType`
  :param text: A string containing the text to be added

The first four callbacks work similarly. All must accept a
:class:`~md4c.BlockType` or :class:`~md4c.SpanType` as their first parameter
and a details dict as their second parameter. The details dict is described
in the next section, but it is how additional properties of the element are
provided, such as a heading's label or a link's destination. If you were
writing your own rendering code, these callbacks would write opening or closing
HTML tags to the output stream.

The fifth callback accepts a :class:`~md4c.TextType` as the first parameter
and a string of text as the second parameter. The text is unprocessed; for
example, HTML entities are left in ``&...;`` form. If you were writing your own
rendering function, this callback would write the text to the output stream
(potentially after some translation).

Callbacks do not need to return anything specific—their return values are
ignored. To cancel parsing, callbacks can raise the :class:`~md4c.StopParsing`
exception. The :meth:`~md4c.GenericParser.parse` method will catch it and
immediately halt parsing quietly. All other exceptions raised in callbacks will
abort parsing and propagate back to :meth:`~md4c.GenericParser.parse`'s caller.

.. _details:

Details Dicts
~~~~~~~~~~~~~

The block and span callbacks each accept a details dict. This is where extra
properties of the block or span are provided. The details available depend on
the type of block or span (and for some, it will be empty). Keys will always be
strings, and the values to expect are listed in the tables below.

Any block or span type for which there is no table will receive an empty
details dict.

.. table:: Details dict for :attr:`~md4c.BlockType.UL`

  +----------------+--------------------+-------------------------------------+
  | Key            | Value type         | Description                         |
  +================+====================+=====================================+
  | ``'is_tight'`` | Bool               | Whether the list is tight_ or not   |
  +----------------+--------------------+-------------------------------------+
  | ``'mark'``     | Single-char string | The character (``*``, ``-``, ``+``) |
  |                |                    | used as a bullet point              |
  +----------------+--------------------+-------------------------------------+

.. table:: Details dict for :attr:`~md4c.BlockType.OL`

  +----------------------+--------------------+-------------------------------+
  | Key                  | Value type         | Description                   |
  +======================+====================+===============================+
  | ``'start'``          | Int                | Start index of the ordered    |
  |                      |                    | list                          |
  +----------------------+--------------------+-------------------------------+
  | ``'is_tight'``       | Bool               | Whether the list is tight_ or |
  |                      |                    | not                           |
  +----------------------+--------------------+-------------------------------+
  | ``'mark_delimiter'`` | Single-char string | The character (``.``, ``)``)  |
  |                      |                    | used as the number delimiter  |
  +----------------------+--------------------+-------------------------------+

.. _tight: https://spec.commonmark.org/0.29/#tight

.. table:: Details dict for :attr:`~md4c.BlockType.LI`

  +------------------------+--------------------+-----------------------------+
  | Key                    | Value type         | Description                 |
  +========================+====================+=============================+
  | ``'is_task'``          | Bool               | Whether the list item is a  |
  |                        |                    | task list item              |
  +------------------------+--------------------+-----------------------------+
  | ``'task_mark'``        | Single-char string | The character (``X``,       |
  |                        |                    | ``x``, space) used to mark  |
  |                        |                    | the task. Only present if   |
  |                        |                    | ``'is_task'`` is True.      |
  +------------------------+--------------------+-----------------------------+
  | ``'task_mark_offset'`` | Int                | The offset of the task mark |
  |                        |                    | character between the       |
  |                        |                    | ``[]``. Only present if     |
  |                        |                    | ``'is_task'`` is True.      |
  +------------------------+--------------------+-----------------------------+

.. table:: Details dict for :attr:`~md4c.BlockType.H`

  +----------------+--------------------+-------------------------------------+
  | Key            | Value type         | Description                         |
  +================+====================+=====================================+
  | ``'level'``    | Int                | Heading level (1-6)                 |
  +----------------+--------------------+-------------------------------------+

.. table:: Details dict for :attr:`~md4c.BlockType.CODE`

  +------------------+--------------------+-----------------------------------+
  | Key              | Value type         | Description                       |
  +==================+====================+===================================+
  | ``'info'``       | Attribute\*        | Info string. Only present for     |
  |                  |                    | fenced code blocks.               |
  +------------------+--------------------+-----------------------------------+
  | ``'lang'``       | Attribute\*        | Language string. Only present for |
  |                  |                    | fenced code blocks.               |
  +------------------+--------------------+-----------------------------------+
  | ``'fence_char'`` | Single-char string | Fence character (backtick or      |
  |                  |                    | tilde). None for indented code    |
  |                  |                    | blocks.                           |
  +------------------+--------------------+-----------------------------------+

.. table:: Details dict for :attr:`~md4c.BlockType.TABLE`

  +----------------------+---------------+------------------------------------+
  | Key                  | Value type    | Description                        |
  +======================+===============+====================================+
  | ``'col_count'``      | Int           | Number of columns in the table     |
  +----------------------+---------------+------------------------------------+
  | ``'head_row_count'`` | Int           | Number of rows in the table head   |
  +----------------------+---------------+------------------------------------+
  | ``'body_row_count'`` | Int           | Number of rows in the table body   |
  +----------------------+---------------+------------------------------------+

.. table:: Details dict for :attr:`~md4c.BlockType.TH` and :attr:`~md4c.BlockType.TD`

  +----------------+----------------------+-----------------------------------+
  | Key            | Value type           | Description                       |
  +================+======================+===================================+
  | ``'align'``    | :class:`md4c.Align`  | Cell alignment                    |
  +----------------+----------------------+-----------------------------------+

.. table:: Details dict for :attr:`~md4c.SpanType.A`

  +--------------+-------------+----------------------------------------------+
  | Key          | Value type  | Description                                  |
  +==============+=============+==============================================+
  | ``'href'``   | Attribute\* | Link URL                                     |
  +--------------+-------------+----------------------------------------------+
  | ``'title'``  | Attribute\* | Link title                                   |
  +--------------+-------------+----------------------------------------------+

.. table:: Details dict for :attr:`~md4c.SpanType.IMG`

  +--------------+-------------+----------------------------------------------+
  | Key          | Value type  | Description                                  |
  +==============+=============+==============================================+
  | ``'src'``    | Attribute\* | Image URL                                    |
  +--------------+-------------+----------------------------------------------+
  | ``'title'``  | Attribute\* | Image title                                  |
  +--------------+-------------+----------------------------------------------+

.. table:: Details dict for :attr:`~md4c.SpanType.WIKILINK`

  +--------------+-------------+----------------------------------------------+
  | Key          | Value type  | Description                                  |
  +==============+=============+==============================================+
  | ``'target'`` | Attribute\* | Wikilink target                              |
  +--------------+-------------+----------------------------------------------+

\* Attribute values are described below.

.. _attribute:

Attributes
~~~~~~~~~~

MD4C uses "attributes" for details that are strings, such as link URLs and
fenced code block info strings. These are not allowed to contain any
span/inline elements, but they may contain HTML entities or null characters, so
attributes are how MD4C copes with this.

PyMD4C represents attributes as either ``None`` or a list of 2-tuples
``(text_type, text)`` where ``text_type`` is a member of
:class:`~md4c.TextType` and ``text`` is the actual text as a string.

For example, this string::

    Copyright &copy; John Doe

would be represented as an attribute like this::

    [(md4c.TextType.NORMAL, 'Copyright '),
     (md4c.TextType.ENTITY, '&copy;'),
     (md4c.TextType.NORMAL, ' John Doe')]

Currently, the only :class:`~md4c.TextType` types allowed in an attribute are
:attr:`~md4c.TextType.NORMAL`, :attr:`~md4c.TextType.ENTITY`, and
:attr:`~md4c.TextType.NULLCHAR`.

Entity Helper
-------------

PyMD4C provides a helper function :func:`~md4c.lookup_entity` to assist with
translating HTML entities to their corresponding UTF-8 character(s)::

    import md4c

    md4c.lookup_entity('&lt;')  # Returns '<'

Object-Oriented Parsing
-----------------------

PyMD4C provides a more object-oriented wrapper for :class:`~md4c.GenericParser`
for applications which might find that useful: the :class:`~md4c.ParserObject`
class. This is a base class that defines the five callbacks as member
functions.

To use it, define a subclass that overrides the callback methods as necessary.
The constructor accepts the same arguments as :class:`~md4c.GenericParser`
(unless it is overridden). Then, you can call the
:meth:`~md4c.ParserObject.parse` method, which only requires the Markdown input
as an argument.

Here is the same example program as above, implemented using a
:class:`~md4c.ParserObject` instead of :class:`~md4c.GenericParser`::

    import md4c

    class CountingParser(md4c.ParserObject):
        def __init__(self, *args, **kwargs):
            # Pass parser options to ParserObject
            super().__init__(*args, **kwargs)

            self.block_counts = dict()
            self.span_counts = dict()
            self.char_count = 0

        def enter_block(self, block_type, details):
            try:
                self.block_counts[block_type] += 1
            except KeyError:
                self.block_counts[block_type] = 1

        def enter_span(self, span_type, details):
            try:
                self.span_counts[span_type] += 1
            except KeyError:
                self.span_counts[span_type] = 1

        def text(self, text_type, text):
            self.char_count += len(text)

    with open('README.md', 'r') as f:
        markdown = f.read()

    parser = CountingParser()
    parser.parse(markdown)

    for block_type, count in parser.block_counts.items():
        print(block_type.name, ':', count)
    for span_type, count in parser.span_counts.items():
        print(span_type.name, ':', count)
    print('Characters', ':', parser.char_count)

Notice that using this paradigm, the counts can be instance variables instead
of global variables. And the callbacks for leaving blocks and spans can be
omitted entirely, since they were not necessary.

For more information, see the :class:`~md4c.ParserObject` API.
