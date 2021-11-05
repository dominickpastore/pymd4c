DOM Parsing
===========

.. note::
   I am seeking feedback for this feature. If there are any changes or
   additions to the API you feel would make it more useful, or if you have any
   other suggestions, please `let me know`_ (or `via email`_ if you prefer).

   Be aware that I may make updates to the :mod:`md4c.domparser` API in
   response to feedback I receive. When that is no longer the case, I will
   remove this message and make a note in the changelog_.

.. _let me know: https://github.com/dominickpastore/pymd4c/discussions/categories/general

.. _via email: mailto:pymd4c@dcpx.org

.. _changelog: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md

What does "DOM parsing" mean?
-----------------------------

In the world of XML, there are two general types of parsers: SAX (i.e.
event-based) and DOM (i.e. tree-based). SAX parsers traverse the document, and
as each tag or bit of content is parsed, the appropriate event is emitted
(enter-element, leave-element, characters) and a callback handles it. DOM
parsers construct a tree representation of the entire document for the caller.

While the concepts were originally conceived for XML, most parsers for any
markup language usually fit into these same two categories. The MD4C C library
and the main :mod:`md4c` Python module take a definitive SAX-like approach to
parsing (and the MD4C library is proud of it). This is clear from the
:class:`~md4c.GenericParser` API.

The :mod:`md4c.domparser` module provides a DOM-like API for use cases where
that style is more appropriate. It produces an AST where each paragraph,
heading, link, block quote, etc. is represented by an
:class:`~md4c.domparser.ASTNode`.

Why use DOM-like parsing?
-------------------------

You may find that the :class:`~md4c.HTMLRenderer` and SAX-like parsers do not
provide the flexibility you need. A typical use-case would be if you want to
manipulate the input document before it is rendered. For example, maybe you
want to convert every occurrence of a certain word to a hyperlink, except in
code blocks. Or you want to delete everything after the first paragraph under
each heading.

The tradeoff for this flexibility is speed:

- DOM parsers are more resource-intensive than SAX parsers in general, due to
  the overhead from producing a tree representation of the entire document in
  memory.
- Furthermore, the SAX-like parsers in PyMD4C are a thin layer on top of MD4C,
  which is heavily optimized C code. :class:`~md4c.domparser.DOMParser` is
  implemented in Python on top of :class:`~md4c.ParserObject`.

Generating an AST
-----------------

Since many applications will not need them, the DOM-like parser and the classes
for the AST are all in a separate module: :mod:`md4c.domparser`. The parser
itself is the :class:`md4c.domparser.DOMParser` class. In the most simple case,
it is used like this::

    import md4c.domparser

    with open('README.md', 'r') as f:
        markdown = f.read()

    parser = md4c.domparser.DOMParser()
    ast = parser.parse(markdown)

At this point, ``ast`` is the root :class:`~md4c.domparser.Document` node of
the tree. You can render the tree as HTML::

    html = ast.render()

Or you can traverse the tree::

    def traverse(ast_node):
        # Do stuff on this node before traversing to children

        try:
            for child in ast_node.children:
                traverse(child)
        except AttributeError:
            # No children
            pass

        # Do stuff on this node after traversing to children

    traverse(ast)

AST Node Objects
----------------

Each type of Markdown element (i.e. each type of block, span, and text) has an
associated AST type. For example, :class:`~md4c.domparser.Paragraph` is for
:attr:`BlockType.P <md4c.BlockType.P>`. See :ref:`astobjs` for the full list.
For Markdown elements with additional details attached to them (see
:ref:`details`), each detail becomes an attribute in the object. For instance,
a :class:`~md4c.domparser.Heading` object ``hdg`` would have attribute
``hdg.level``.

There are a few base classes that the AST classes inherit from:

:class:`md4c.domparser.ASTNode`
  All AST classes inherit from this class. It provides the
  :attr:`~md4c.domparser.ASTNode.type` and
  :attr:`~md4c.domparser.ASTNode.parent` attributes. This is also the class
  that should be used to construct all AST node objects, no matter their type.
  More on that in the later sections.

:class:`md4c.domparser.ContainerNode`
  All AST classes that are not leaf nodes inherit from this class. That is,
  all blocks and inlines except :class:`~md4c.domparser.HorizontalRule`. It
  provides the :attr:`~md4c.domparser.ContainerNode.children` attribute and
  the :meth:`~md4c.domparser.ContainerNode.append` and
  :meth:`~md4c.domparser.ContainerNode.insert` methods for adding new children.

:class:`md4c.domparser.TextNode`
  All AST classes associated with :class:`md4c.TextType`\ s inherit from this.
  It provides the :attr:`~md4c.domparser.TextNode.text` attribute containing
  the unprocessed text from the parser.

AST Manipulation
----------------

One of the primary benefits of using a DOM-like parser is you can do AST
manipulations on the parsed document before rendering it in HTML. Below are a
couple examples of AST manipulations you could do.

Add a Copyright Notice
~~~~~~~~~~~~~~~~~~~~~~

Suppose you wanted to add a horizontal rule and then a copyright notice at the
end of the document. (This probably doesn't require generating the full AST,
but it serves as a simple example.) You could do that like this::

    import md4c
    import md4c.domparser

    # Parse document
    with open('document.md', 'r') as f:
        markdown = f.read()
    parser = md4c.domparser.DOMParser()
    ast = parser.parse(markdown)

    # Generate horizontal rule and copyright notice paragraph
    hr = md4c.domparser.ASTNode(md4c.BlockType.HR)
    p = md4c.domparser.ASTNode(md4c.BlockType.P)

    # Add copyright notice text to the paragraph
    p.append(md4c.domparser.ASTNode(
        md4c.TextType.NORMAL, text='Copyright '))
    p.append(md4c.domparser.ASTNode(
        md4c.TextType.ENTITY, text='&copy;'))
    p.append(md4c.domparser.ASTNode(
        md4c.TextType.NORMAL, text=' 2021 John Doe'))

    # Add the horizontal rule and copyright notice to the end of the document
    ast.append(hr)
    ast.append(p)

    # Render
    html = ast.render()

There are several important points to note:

- New nodes are always constructed using the :class:`~md4c.domparser.ASTNode`
  constructor, no matter the type. It will construct the appropriate subclass
  depending on the node type enum member passed in as the first argument.
- Additional arguments for the :class:`~md4c.domparser.ASTNode` constructor,
  when given, must be keyword-only. For text nodes, this must be a single
  ``text`` argument. For nodes with :ref:`details <details>`, these would
  correspond with the keys for the details dict.
- Nodes can be added as children by calling the
  :meth:`~md4c.domparser.ContainerNode.append` method on the parent. That
  appends the node to the parent's children list and sets the child node's
  parent.
- Neither the horizontal rule node nor any of the text nodes can accept
  children. They do not have :meth:`~md4c.domparser.ContainerNode.append` (or
  :meth:`~md4c.domparser.ContainerNode.insert`) methods.

Linkify a Keyword
~~~~~~~~~~~~~~~~~

Now a slightly more involved example: You want to replace every instance of
your company name, "Example, Inc." with a link to its homepage, but only in
normal text (i.e. not code blocks, raw HTML, etc.). You might do that as
follows::

    import md4c
    import md4c.domparser

    # Parse document
    with open('document.md', 'r') as f:
        markdown = f.read()
    parser = md4c.domparser.DOMParser()
    ast = parser.parse(markdown)

    def linkify_name(parent, i):
        """If there are any instances of the company name in child
        i of the parent, linkify them and return the index of the
        last inserted child. If there are not, return i."""
        text = parent.children[i].text
        before, name, after = text.partition('Example, Inc.')
        if name == '':
            # Name not present.
            return i

        # Remove old child
        parent.children.pop(i)

        # Add the before portion, if not empty
        if before != '':
            before_node = md4c.domparser.ASTNode(
                md4c.TextType.NORMAL, text=before)
            parent.insert(i, before_node)
            i += 1

        # Add the link
        link_node = md4c.domparser.ASTNode(
            md4c.SpanType.A,
            href=[(md4c.TextType.NORMAL,
                   'https://example.com/')])
        link_node.append(md4c.domparser.ASTNode(
            md4c.TextType.NORMAL, text=name))
        parent.insert(i, link_node)

        # Add the after portion and check for more instances,
        # if not empty
        if after != '':
            i += 1
            after_node = md4c.domparser.ASTNode(
                md4c.TextType.NORMAL, text=after)
            parent.insert(i, after_node)
            return linkify_name(parent, i)
        return i

    def find_and_linkify_name(ast_node):
        """Traverse the AST looking for normal text nodes,
        then linkify the company name"""
        try:
            i = 0
            while i < len(ast_node.children):
                child = ast_node.children[i]
                if child.type is md4c.TextType.NORMAL:
                    i = linkify_name(ast_node, i)
                else:
                    find_and_linkify_name(child)
                i += 1
        except AttributeError:
            # No children
            pass

    # Linkify company name and render
    find_and_linkify_name(ast)
    html = ast.render()

Some points to note about this example:

- The :meth:`~md4c.domparser.ContainerNode.insert` method is like
  :meth:`~md4c.domparser.ContainerNode.append`, except it lets you pick where
  in the parent's children list to insert the new child node.
- There is no special method to remove a child. Just pop it from the parent's
  children list.
- Be careful when modifying the children list as you iterate over it. It's not
  safe to use a for loop on a list that you intend to insert or remove items
  from.
- The node type is identified with ``child.type is md4c.TextType.NORMAL``, not
  ``isinstance(child, md4c.domparser.NormalText)``. The former works even if
  using a custom AST class to handle normal text, while the latter only works
  with the default :class:`~md4c.domparser.NormalText` class.

.. warning::

  This example was just a demonstration. If you wanted to do something like
  this in production code, you should consider that 1) normal text can appear
  in places where the link replacement shouldn't happen (e.g. inside the text
  of an existing link), and 2) numeric entities (e.g. ``&#x45;`` for ``E``) can
  be used to foil the matching.

Using Custom AST Classes
------------------------

You can customize the classes used for the AST. The main reason to do so is for
customizing the rendering functionality, either to tailor the HTML generation
to your particular application or generate another output format altogether.

To provide an example, suppose you wanted to use MathJax to render your
equations. The default :class:`~md4c.domparser.InlineMath` and
:class:`~md4c.domparser.DisplayMath` classes render ``<x-equation>`` tags, but
you need them to render ``\(...\)`` and ``\[...\]`` instead. Here is how you
could do that::

    import md4c
    import md4c.domparser

    # Create custom AST classes for InlineMath and DisplayMath

    class InlineMathJax(md4c.domparser.InlineMath,
                        element_type=md4c.SpanType.LATEXMATH):
        def render_pre(self, **kwargs):
            return '\\('

        def render_post(self, **kwargs):
            return '\\)'

    class DisplayMathJax(md4c.domparser.DisplayMath,
                         element_type=md4c.SpanType.LATEXMATH_DISPLAY):
        def render_pre(self, **kwargs):
            return '\\['

        def render_post(self, **kwargs):
            return '\\]'

    # Parse and render document

    with open('document.md', 'r') as f:
        markdown = f.read()
    parser = md4c.domparser.DOMParser(latex_math_spans=True)
    ast = parser.parse(markdown)
    html = ast.render()

The magic here is in the class parameters: Alongside the parent class, we have
an ``element_type`` parameter. So long as one of our class's ancestors is
:class:`~md4c.domparser.ASTNode` and ``element_type`` is provided,
:class:`~md4c.domparser.ASTNode` will register our new class as the one to
construct for that element type. This needs to be done before calling the
:meth:`~md4c.domparser.DOMParser.parse` method.

Some additional notes about the AST classes:

- Most of the block and span classes (all except
  :class:`~md4c.domparser.HorizontalRule`) inherit from
  :class:`~md4c.domparser.ContainerNode`. For these, you can almost always rely
  on the default :meth:`~md4c.domparser.ContainerNode.render` method as-is and
  just customize :meth:`~md4c.domparser.ContainerNode.render_pre` and
  :meth:`~md4c.domparser.ContainerNode.render_post`. They run before and after
  the children are rendered, respectively.
- The CommonMark spec allows most span elements to occur inside an image
  element. HTML does *not* allow this, since the image text becomes the alt
  text attribute. To handle this, most of the span and text elements accept an
  ``image_nesting_level`` argument for their
  :meth:`~md4c.domparser.ASTNode.render` method. If ``image_nesting_level >
  0``, they render without HTML tags.
- Normally, text nodes appear in the regular text of a document. But sometimes,
  they appear in URL contexts (link targets and image sources). In those
  contexts, the render function for text nodes is passed an additional keyword
  argument: ``url_escape``. When True, normal text and entities must process
  their output through their :meth:`~md4c.domparser.TextNode.url_escape`
  method.

Using :class:`bytes` as the Input
---------------------------------

All the examples above have assumed UTF-8 input. As with all the other parsers
in PyMD4C, :class:`~md4c.domparser.DOMParser` will parse :class:`bytes` objects
as well. In that case, the :meth:`~md4c.domparser.ASTNode.render` method on the
resulting AST will also return a :class:`bytes` object.

There are some additional caveats to be aware of when modifying ASTs generated
from :class:`bytes` input:

- When constructing a new :class:`~md4c.domparser.ASTNode`, you must set
  ``use_bytes=True`` in the constructor, for example::

      heading_node = md4c.domparser.ASTNode(md4c.BlockType.H,
                                            level=1,
                                            use_bytes=True)

- Text for any :class:`~md4c.domparser.TextNode` must be a :class:`bytes`
  object::

      link_node = md4c.domparser.ASTNode(
          md4c.SpanType.A,
          href=[(md4c.TextType.NORMAL, b'http://www.example.com/')],
          use_bytes=True)
      link_node.append(md4c.domparser.ASTNode(
          md4c.TextType.Normal,
          text=b'Example Link Text',
          use_bytes=True)

- When using custom :class:`~md4c.domparser.ASTNode` subclasses, make sure any
  overridden :meth:`~md4c.domparser.ASTNode.render`,
  :meth:`~md4c.domparser.ContainerNode.render_pre`, or
  :meth:`~md4c.domparser.ContainerNode.render_post` methods return
  :class:`bytes` objects when the :attr:`self.bytes
  <md4c.domparser.ASTNode.bytes>` attribute is True::

      class InlineMathJax(md4c.domparser.InlineMath,
                          element_type=md4c.SpanType.LATEXMATH):
          def render_pre(self, **kwargs):
              if self.bytes:
                  return b'\\('
              return '\\('

          def render_post(self, **kwargs):
              if self.bytes:
                  return b'\\)'
              return '\\)'
