API
===

Parsers and Renderers
---------------------

.. module:: md4c

.. autoclass:: HTMLRenderer
   :members:

.. autoclass:: GenericParser
   :members:

.. autoclass:: ParserObject
   :members:

.. _options:

Option Flags
------------

PyMD4C's parsers and renderers accept options in two forms: An OR'd set of
flags or as keyword arguments that accept ``True``. All parsers and renderers
accept the parsing options, but renderer options are specific to the renderer.

Parser Option Flags
~~~~~~~~~~~~~~~~~~~

Basic option flags
""""""""""""""""""

:const:`md4c.MD_FLAG_COLLAPSEWHITESPACE`
  Keyword argument: ``collapse_whitespace``

  In normal text, collapse non-trivial whitespace into a single space.

:const:`md4c.MD_FLAG_PERMISSIVEATXHEADERS`
  Keyword argument: ``permissive_atx_headers``

  Do not require a space in ATX headers (e.g. ``###Header``)

:const:`md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS`
  Keyword argument: ``permissive_url_autolinks``

  Convert URLs to links even without ``<`` and ``>``.

:const:`md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS`
  Keyword argument: ``permissive_email_autolinks``

  Convert email addresses to links even without ``<``, ``>``, and ``mailto:``.

:const:`md4c.MD_FLAG_NOINDENTEDCODEBLOCKS`
  Keyword argument: ``no_indented_code_blocks``

  Disable indented code blocks (only allow fenced code blocks).

:const:`md4c.MD_FLAG_NOHTMLBLOCKS`
  Keyword argument: ``no_html_blocks``

  Disable raw HTML blocks.

:const:`md4c.MD_FLAG_NOHTMLSPANS`
  Keyword argument: ``no_html_spans``

  Disable raw HTML inlines.

:const:`md4c.MD_FLAG_TABLES`
  Keyword argument: ``tables``

  Enable tables extension.

:const:`md4c.MD_FLAG_STRIKETHROUGH`
  Keyword argument: ``strikethrough``

  Enable strikethrough extension.

:const:`md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS`
  Keyword argument: ``permissive_www_autolinks``

  Enable www autolinks (even without any scheme prefix, as long as they begin
  with ``www.``).

:const:`md4c.MD_FLAG_TASKLISTS`
  Keyword argument: ``tasklists``

  Enable task lists extension.

:const:`md4c.MD_FLAG_LATEXMATHSPANS`
  Keyword argument: ``latex_math_spans``

  Enable ``$`` and ``$$`` containing LaTeX equations.

:const:`md4c.MD_FLAG_WIKILINKS`
  Keyword argument: ``wikilinks``

  Enable wiki links extension.

:const:`md4c.MD_FLAG_UNDERLINE`
  Keyword argument: ``underline``

  Enable underline extension (and disable ``_`` for regular emphasis).

Combination option flags
""""""""""""""""""""""""

These enable several related parser options, or options to match a particular
dialect of Markdown as closely as possible.

:const:`md4c.MD_FLAG_PERMISSIVEAUTOLINKS`
  Keyword argument: ``permissive_autolinks``

  Enables all varieties of autolinks:

  - :const:`~md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS`
  - :const:`~md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS`
  - :const:`~md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS`

:const:`md4c.MD_FLAG_NOHTML`
  Keyword argument: ``no_html``

  Disables all raw HTML tags:

  - :const:`~md4c.MD_FLAG_NOHTMLBLOCKS`
  - :const:`~md4c.MD_FLAG_NOHTMLSPANS`

:const:`md4c.MD_DIALECT_GITHUB`
  Keyword argument: ``dialect_github``

  Parse GitHub-Flavored Markdown (GFM), which enables the following flags:

  - :const:`~md4c.MD_FLAG_PERMISSIVEAUTOLINKS`
  - :const:`~md4c.MD_FLAG_TABLES`
  - :const:`~md4c.MD_FLAG_STRIKETHROUGH`
  - :const:`~md4c.MD_FLAG_TASKLISTS`

HTML Renderer Option Flags
~~~~~~~~~~~~~~~~~~~~~~~~~~

These options are only accepted by the :class:`~md4c.HTMLRenderer`.

:const:`md4c.MD_HTML_FLAG_DEBUG`
  Keyword argument: ``debug``

  For development use, send MD4C debug output to stderr.

:const:`md4c.MD_HTML_FLAG_VERBATIM_ENTITIES`
  Keyword argument: ``verbatim_entities``

  Do not replace HTML entities with the actual character (e.g. ``&copy;`` with
  "©").

:const:`md4c.MD_HTML_FLAG_SKIP_UTF8_BOM`
  Keyword argument: ``skip_utf8_bom``

  Omit BOM from the start of UTF-8 input.

:const:`md4c.MD_HTML_FLAG_XHTML`
  Keyword argument: ``xhtml``

  Generate XHTML instead of HTML.

Enums
-----

The MD4C library uses various enums to provide data to callbacks. PyMD4C uses
:class:`IntEnum`\ s to encapsulate these.

.. autoclass:: BlockType
   :members:

.. autoclass:: SpanType
   :members:

.. autoclass:: TextType
   :members:

.. autoclass:: Align
   :members:

Exceptions
----------

.. autoclass:: ParseError

.. autoclass:: StopParsing
