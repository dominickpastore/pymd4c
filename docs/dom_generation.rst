DOM Generation
==============

What does "DOM generation" mean?
--------------------------------

TODO What do I mean by DOM generation

Why use it?
-----------

You may find that the :class:`~md4c.HTMLRenderer` and SAX-like parsers do not
provide the flexibility you need. A typical use-case would be if you want to
manipulate the input document before it is rendered. For example, maybe you
want to convert every occurrence of a certain word to a hyperlink, except in
code blocks. Or you want to delete everything after the first paragraph under
each heading.

The tradeoff for this flexibility is speed. :class:`~md4c.HTMLRenderer` is a
thin layer on top of MD4C, which is heavily optimized C code that avoids memory
allocation (which is slow) when at all possible. :class:`~md4c.DOMParser` is
implemented in Python on top of :class:`~md4c.GenericParser` and is heavy on
object creation. That said, if you are using Python in the first place, chances
are that speed is more of a "nice to have" than a critical requirement.

TODO Document DOM-like parsing (DOMParser)

TODO Document DOM objects

TODO Example of DOM manipulation

TODO Example of using custom DOM classes
