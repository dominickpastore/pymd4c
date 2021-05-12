![Release Status](https://github.com/dominickpastore/pymd4c/workflows/Release/badge.svg)
![Test Status](https://github.com/dominickpastore/pymd4c/workflows/Test/badge.svg?branch=dev)

PyMD4C
======

Python bindings for the very fast [MD4C] Markdown parsing and rendering
library.

- Documentation: [TODO][docs]
- GitHub: [https://github.com/dominickpastore/pymd4c][GitHub]
- PyPI: [https://pypi.org/project/pymd4c/][PyPI]
- Changelog: [https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md][changelog]
- Issues: [https://github.com/dominickpastore/pymd4c/issues][issues]

Overview
--------

The [MD4C] C library provides a SAX-like parser that uses callbacks to return
the various blocks, inlines, and text it parses from the Markdown input. In
addition, it provides an HTML renderer built on top of the parser to provide
HTML output directly.

PyMD4C provides Python bindings for both. The goal is to provide a simple and
fast interface for applications that just need to translate Markdown to HTML,
while providing flexibility for applications that need to do more.

Brief installation instructions and examples are below, but see the [full
documentation][docs] for more detail.

Installation from PyPI
----------------------

PyMD4C is available on PyPI under the name [`pymd4c`][PyPI]. Install it with
pip as you would any other Python package:

    pip install pymd4c

This is the recommended method to obtain PyMD4C. It should work well on most
Linux distributions, Windows, and macOS, but since it contains a C module, it
must be built for each platform specifically. Those running on uncommon
architectures or old versions of their OS may find that a prebuilt module isn't
available. (If a build is not available or working for your platform and you
think it should be, consider opening a [GitHub issue][issues].)

For more detailed installation instructions, including building from source
(which should work on virtually any platform), see the "Installation" page in
the [full documentation][docs].

Basic Usage
-----------

Once PyMD4C is installed, generating HTML from Markdown is as simple as the
following:

```python
import md4c

with open('README.md', 'r') as f:
    markdown = f.read()

renderer = md4c.HTMLRenderer()
html = renderer.parse(markdown)
```

This is just the most basic example to get you up and running ASAP. There are
several options for customizing MD4C's parsing and HTML generation behavior, as
well as other APIs for tasks other than generating HTML. The [full
documentation][docs] walks through all of those features.

Contributions
-------------

Thank you for your interest in contributing to PyMD4C! The "Contributing to
PyMD4C" page in the [documentation][docs] has some information that should
prove helpful.

License
-------

This project is licensed under the MIT license. See the `LICENSE.md` file for
details.

[MD4C]: https://github.com/mity/md4c
[GitHub]: https://github.com/dominickpastore/pymd4c
[PyPI]: https://pypi.org/project/pymd4c/
[changelog]: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md
[issues]: https://github.com/dominickpastore/pymd4c/issues
[docs]: ...







Introduction
------------

The MD4C C library provides a SAX-like parser that uses callbacks to return the
various blocks, inlines, and text it parses from the Markdown input. In
addition, it provides an HTML renderer that wraps the generic parser to provide
HTML output directly.

Accordingly, this Python module provides two classes:

* `md4c.GenericParser` - Wraps the generic SAX-like MD4C parser. Requires
  Python functions (or other callables) as callbacks.
* `md4c.HTMLRenderer` - Wraps the HTML renderer. Produces HTML output directly.

If other renderers are added to MD4C, they will get their own Python class as
well, similar to the `HTMLRenderer`.

Class `GenericParser`
---------------------

```python
import md4c
generic_parser = md4c.GenericParser(parser_flags)
```

Initialize a new `GenericParser`. Parameters:

* `parser_flags` - An `int` made up of some combination of the parser option
  flags or'd together, e.g.
  `md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH`. For the default options,
  use `0`, which will parse according to the base CommonMark specification. See
  the "Module-Wide Constants" section below for a full list of parser option
  flags.

**Note:** If the end goal of parsing is to produce HTML, strongly consider
using an `HTMLRenderer` instead. All rendering will be performed by native C
code, which will be much faster.

### Parse Method

```python
import md4c
generic_parser = md4c.GenericParser(...)
generic_parser.parse(input,
                     enter_block_callback,
                     leave_block_callback,
                     enter_span_callback,
                     leave_span_callback,
                     text_callback)
```

Parse markdown text using the provided callbacks. Parameters:

* `input` - A `str` or `bytes` containing the Markdown document to parse. If a
  `bytes`, it must be UTF-8 encoded.
* `enter_block_callback` - A function (or other callable) to be called whenever
  the parser enters a new block element in the Markdown source.
* `leave_block_callback` - A function (or other callable) to be called whenever
  the parser leaves a block element in the Markdown source.
* `enter_span_callback` - A function (or other callable) to be called whenever
  the parser enters a new inline element in the Markdown source.
* `leave_span_callback` - A function (or other callable) to be called whenever
  the parser leaves an inline element in the Markdown source.
* `text_callback` - A function (or other callable) to be called whenever the
  parser has text to add to the current block or inline element.

The `parse()` method will raise `md4c.ParseError` in the event of a problem
during parsing, such as running out of memory. This does not signal invalid
syntax, as there is no such thing in Markdown. It can also emit any exception
raised by any of the callbacks (except `md4c.StopParsing`, which is caught and
handled quietly).

#### Callback Details

`enter_block_callback`, `leave_block_callback`, `enter_span_callback`, and
`leave_span_callback` all must accept two parameters:

* `type` - An `md4c.BlockType` or `md4c.SpanType` representing the type of
  block or span. See the "Enums" section for more info.
* `details` - A `dict` that contains extra information for certain types of
  blocks and spans, for example, the level of a heading. Keys are `str`s.
  Values are `int`s, single-character `str`s, or (for `MD_ATTRIBUTE`) lists of
  tuples or None.

  This dict will contain the information provided by `MD_BLOCK_*_DETAIL` and
  `MD_SPAN_*_DETAIL` structs in MD4C's `md4c.h`, with the following exceptions:

  * Non-task `MD_BLOCK_LI` blocks (when `is_task` is `False`) do not include
    `task_mark` and `task_mark_offset` keys.
  * Indented `MD_BLOCK_CODE` blocks do not include the `fence_char` key.

  Regarding `MD_ATTRIBUTE`s: These are used where a block or span can contain
  some associated text, such as link titles and code block language references.
  Such attributes may contain multiple text sub-elements (e.g. some regular
  text, an HTML entity, and then some more regular text). Thus, an
  `MD_ATTRIBUTE` value in `details` consists of a list of 2-tuples:
  `(text_type, text)` where `text_type` is an `md4c.TextType` (see "Enums"
  below) and `text` is the actual text as a `str`.

  Note that attributes may not always be provided. For example, an indented
  code block will not contain `info` or `lang` attributes. In those cases, the
  value will be `None`.

`text_callback` must also accept two parameters, but they are different:

* `type` - An `md4c.TextType` representing the type of text element. See the
  "Enums" section for more info.
* `text` - The actual text, as a `str`.

Callbacks need not return anything specific; their return values are ignored.
To cancel parsing, callbacks can raise `md4c.StopParsing`. This will be caught
by the `parse()` method and immediately halt parsing quietly. All other
exceptions raised by callbacks will abort parsing and will be propagated back
to the caller of `parse()`.

Class `HTMLRenderer`
--------------------

```python
import md4c
html_renderer = md4c.HTMLRenderer(parser_flags, renderer_flags)
```

Initialize a new `HTMLRenderer`. Parameters:

* `parser_flags` - An `int` made up of some combination of the parser option
  flags or'd together, e.g.
  `md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH`. For the default options,
  use `0`, which will parse according to the base CommonMark standard. See the
  "Module-Wide Constants" section below for a full list of parser option flags.
* `renderer_flags` - An `int` made up of some combination of the HTML renderer
  option flags or'd together. These are also listed in the "Module-Wide
  Constants" section below.

### Parse Method

```python
import md4c
html_renderer = md4c.HTMLRenderer(...)
output = html_renderer.parse(input)
```

Parse markdown text and return a `str` with rendered HTML. Parameters:

* `input` - A `str` or `bytes` containing the Markdown document to parse. If a
  `bytes`, it must be UTF-8 encoded.

This method will raise `md4c.ParseError` in the event of a problem during
parsing, such as running out of memory. This does not signal invalid syntax, as
there is no such thing in Markdown.

Module-Wide Constants
---------------------

The MD4C library provides various option flags for parsers and renderers as
named constants. These are made available as module-level constants in PyMD4C. Also, each constant has a correspondent optional keyword argument that can be used instanciating parser and renderers.

### Parser Option Flags

Basic option flags:

| md4c flag | keyword argument | description |
| :-------- | :--------------- | :---------- |
| `md4c.MD_FLAG_COLLAPSEWHITESPACE` | `collapse_whitespace` | In normal text, collapse non-trivial whitespace into a single space. |
| `md4c.MD_FLAG_PERMISSIVEATXHEADERS` | `permissive_atx_headers` | Do not requite a space in ATX headers (e.g. `###Header`). |
| `md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS` | `permissive_url_autolinks` | Convert URLs to links even without `<` and `>`. |
| `md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS` | `permissive_email_autolinks` | Convert email addresses to links even without `<`, `>`, and `mailto:`. |
| `md4c.MD_FLAG_NOINDENTEDCODEBLOCKS` | `no_indented_code_blocks` | Disable indented code blocks (only allow fenced code blocks). |
| `md4c.MD_FLAG_NOHTMLBLOCKS` | `no_html_blocks` | Disable raw HTML blocks. |
| `md4c.MD_FLAG_NOHTMLSPANS` | `no_html_spans` | Disable raw HTML inlines. |
| `md4c.MD_FLAG_TABLES` | `tables` | Enable tables extension. |
| `md4c.MD_FLAG_STRIKETHROUGH` | `strikethrough` | Enable strikethrough extension. |
| `md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS` | `permissive_www_autolinks` | Enable www autolinks (even without any scheme prefix, as long as they begin with `www.`).
| `md4c.MD_FLAG_TASKLISTS` | `tasklists` | Enable task lists extension. |
| `md4c.MD_FLAG_LATEXMATHSPANS` | `latex_math_spans` | Enable `$` and `$$` containing LaTeX equations. |
| `md4c.MD_FLAG_WIKILINKS` | `wikilinks` | Enable wiki links extension. |
| `md4c.MD_FLAG_UNDERLINE` | `underline` | Enable underline extension (and disable `_` for regular emphasis). |

Combination option flags:

| md4c flag | keyword argument | description |
| :-------- | :--------------- | :---------- |
| `md4c.MD_FLAG_PERMISSIVEAUTOLINKS` | `permissive_auto_links` | Enables all varieties of autolinks: `MD_FLAG_PERMISSIVEURLAUTOLINKS`, `MD_FLAG_PERMISSIVEEMAILAUTOLINKS`, and `MD_FLAG_PERMISSIVEWWWAUTOLINKS`. |
| `md4c.MD_FLAG_NOHTML` | `no_html` | Disables all raw HTML tags: `MD_FLAG_NOHTMLBLOCKS` and `MD_FLAG_NOHTMLSPANS`. |

Dialect option flags (note that not all features of a dialect may be supported,
but these flags will cause MD4C to parse as many features of the dialect as it
supports):

| md4c flag | keyword argument | description |
| :-------- | :--------------- | :---------- |
| `md4c.MD_DIALECT_GITHUB` | `dialect_github` | Parse GitHub-Flavored Markdown, which enables the following flags:<br><br><ul><li><code>MD_FLAG_PERMISSIVEAUTOLINKS</code></li><li><code>MD_FLAG_TABLES</code></li><li><code>MD_FLAG_STRIKETHROUGH</code></li><li><code>MD_FLAG_TASKLISTS</code></li></ul>

### HTML Renderer Option Flags

| md4c flag | keyword argument | description |
| :-------- | :--------------- | :---------- |
| `md4c.MD_HTML_FLAG_DEBUG` | `debug` | For development use, send MD4C debug output to stderr. |
| `md4c.MD_HTML_FLAG_VERBATIM_ENTITIES` | `verbatim_entities` | Do not replace HTML entities with the actual character (e.g. `&copy;` with ©). |
| `md4c.MD_HTML_FLAG_SKIP_UTF8_BOM` | `skip_utf8_bom` | Omit BOM from start of UTF-8 input. |
| `md4c.MD_HTML_FLAG_XHTML` | `xhtml` | Generate XHTML instead of HTML. |

Enums
-----

The MD4C library uses various enums to provide data to callbacks. PyMD4C uses
`IntEnum`s to encapsulate these.

See `md4c.h` from the [MD4C project][MD4C] for more information on these enums
and associated types.

### Block Types - class `BlockType`

* `md4c.BlockType.DOC` - Document
* `md4c.BlockType.QUOTE` - Block quote
* `md4c.BlockType.UL` - Unordered list
* `md4c.BlockType.OL` - Ordered list
* `md4c.BlockType.LI` - List item
* `md4c.BlockType.HR` - Horizontal rule
* `md4c.BlockType.H` - Heading
* `md4c.BlockType.CODE` - Code block
* `md4c.BlockType.HTML` - Raw HTML block
* `md4c.BlockType.P` - Paragraph
* `md4c.BlockType.TABLE` - Table
* `md4c.BlockType.THEAD` - Table header row
* `md4c.BlockType.TBODY` - Table body
* `md4c.BlockType.TR` - Table row
* `md4c.BlockType.TH` - Table header cell
* `md4c.BlockType.TD` - Table cell

### Span Types - class `SpanType`

* `md4c.SpanType.EM` - Emphasis
* `md4c.SpanType.STRONG` - Strong
* `md4c.SpanType.A` - Link
* `md4c.SpanType.IMG` - Image
* `md4c.SpanType.CODE` - Inline code
* `md4c.SpanType.DEL` - Strikethrough
* `md4c.SpanType.LATEXMATH` - Inline math
* `md4c.SpanType.LATEXMATH_DISPLAY` - Display math
* `md4c.SpanType.WIKILINK` - Wiki link
* `md4c.SpanType.U` - Underline

### Text Types - class `TextType`

* `md4c.TextType.NORMAL` - Normal text
* `md4c.TextType.NULLCHAR` - NULL character
* `md4c.TextType.BR` - Line break
* `md4c.TextType.SOFTBR` - Soft line break
* `md4c.TextType.ENTITY` - HTML Entity
* `md4c.TextType.CODE` - Text inside a code block or inline code
* `md4c.TextType.HTML` - Raw HTML (inside an HTML block or simply inline HTML)
* `md4c.TextType.LATEXMATH` - Text inside an equation

### Table Alignments - class `Align`

* `md4c.Align.DEFAULT`
* `md4c.Align.LEFT`
* `md4c.Align.CENTER`
* `md4c.Align.RIGHT`

Exceptions
----------

* `md4c.ParseError` - Raised by one of the `parse()` methods when there is an
  error during parsing, such as running out of memory. *There is no such thing
  as invalid syntax in Markdown,* so this really only signals some sort of
  system error.

* `md4c.StopParsing` - A callback can raise this to stop parsing early.
  `GenericParser`'s `parse()` method will catch it and abort quietly.

License
-------

This project is licensed under the MIT license. See the `LICENSE.md` file for
details.

[MD4C]: https://github.com/mity/md4c
[GitHub]: https://github.com/dominickpastore/pymd4c
[PyPI]: https://pypi.org/project/pymd4c/
[changelog]: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md
[issues]: https://github.com/dominickpastore/pymd4c/issues
[python-packaging]: https://packaging.python.org/tutorials/installing-packages/
[manylinux]: https://github.com/pypa/manylinux
[md4c-releases]: https://github.com/mity/md4c/releases
[CMake]: https://cmake.org/
