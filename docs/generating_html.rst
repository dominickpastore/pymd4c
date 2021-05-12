Generating HTML
===============

TODO Document HTMLRenderer

Advanced Manipulations
----------------------

If the available options for :class:`HTMLRenderer` do not provide enough
flexibility for your needs, it's possible to use a :class:`DOMParser` instead.
See :doc:`dom_generation` for more information.

The advantage of that method is it yields the entire Markdown AST, which you
can then do transformations and manipulations on. Want to delete all but the
first paragraph under every heading? You can do that.

The tradeoff for this flexibility is speed. :class:`HTMLRenderer` is a thin
layer on top of MD4C, which is heavily optimized C code that avoids memory
allocation (which is slow) when at all possible. :class:`DOMParser` is
implemented on top of :class:`GenericParser` in Python and is heavy on object
creation. That said, if you are using Python in the first place, chances are
that speed is more of a "nice to have" than a critical requirement.
