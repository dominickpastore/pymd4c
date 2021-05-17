DOM Generation
==============

.. note::
  I am seeking feedback for this feature. If there are any changes or additions
  to the API you feel would make it more useful, or if you have any other
  suggestions, please `let me know`_ (or `via email`_ if you prefer).

  Be aware that I may make updates to the :mod:`md4c.domparser` API in response
  to feedback I receive. When that is no longer the case, I will remove this
  message and make a note in the changelog_.

.. _let me know: https://github.com/dominickpastore/pymd4c/discussions/categories/general

.. _via email: mailto:pymd4c@dcpx.org

.. _changelog: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md

What does "DOM generation" mean?
--------------------------------

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
that style is more appropriate. It produces a tree where each paragraph,
heading, link, block quote, etc. is represented by a
:class:`~md4c.domparser.DOMObject`.

Why use DOM?
------------

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
  which is heavily optimized C code. :class:`~md4c.DOMParser` is implemented in
  Python on top of :class:`~md4c.ParserObject`.

That said, if you are using Python in the first place, chances are that speed
is more of a "nice to have" than a critical requirement.

TODO Document DOM-like parsing (DOMParser)

TODO Document DOM objects

TODO Example of DOM manipulation

TODO Example of using custom DOM classes
