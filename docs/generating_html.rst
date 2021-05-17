Generating HTML
===============

Basic Generation
----------------

Generating HTML is probably the most common task related to Markdown. PyMD4C
provides a class that does exactly this. It's implemented in C directly on top
of MD4C's MD4C-HTML library, for maximum efficiency. Using it is as simple as
this::

    import md4c

    with open('README.md', 'r') as f:
        markdown = f.read()

    renderer = md4c.HTMLRenderer()
    html = renderer.parse(markdown)

That is the most basic case: converting CommonMark-compliant Markdown to HTML.

Parsing and Rendering Options
-----------------------------

The :class:`~md4c.HTMLRenderer` constructor accepts options to customize the
parsing and rendering behavior. These options typically add extra parsing
features, disable undesirable parsing features, or tweak the HTML generation.
See :ref:`options` for the full list.

There are two ways to specify options. One way is to use positional arguments
containing flags OR'd together. The first argument is for parser options and
the second for HTML renderer options. For example, if you wanted to enable
strikethrough, tables, and preserve HTML entities::

    renderer = md4c.HTMLRenderer(
        md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH,
        md4c.MD_HTML_FLAG_VERBATIM_ENTITIES)

The other way is to specify options as keyword arguments. This way is generally
preferred for new code since it is more readable. The following code is
equivalent to the above::

    renderer = md4c.HTMLRenderer(tables=True,
                                 strikethrough=True,
                                 verbatim_entities=True)

For convenience, there are a few combination options that set multiple flags at
once. For example, GitHub-Flavored Markdown extends CommonMark with
strikethrough, tasklists, tables, and permissive autolinks. You can enable all
of these in one shot::

    renderer = md4c.HTMLRenderer(dialect_github=True)
    # OR
    renderer = md4c.HTMLRenderer(md4c.MD_DIALECT_GITHUB)

.. note::
   Keyword arguments only have an effect when set to ``True``. Setting a
   keyword argument to ``False`` does not unset a flag set by one of the
   combination options.

Advanced Manipulations
----------------------

If the available options for :class:`~md4c.HTMLRenderer` do not provide enough
flexibility for your needs, it's possible to use a :class:`~md4c.DOMParser`
instead. See :doc:`dom_generation` for more information.
