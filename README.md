![Release Status](https://github.com/dominickpastore/pymd4c/workflows/Release/badge.svg?branch=master)
![Test Status](https://github.com/dominickpastore/pymd4c/workflows/Test/badge.svg?branch=dev)

PyMD4C
======

Python bindings for the very fast [MD4C] Markdown parsing and rendering
library.

- GitHub: [https://github.com/dominickpastore/pymd4c][GitHub]
- PyPI: [https://pypi.org/project/pymd4c/][PyPI]
- Changelog: [https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md][changelog]
- Issues: [https://github.com/dominickpastore/pymd4c/issues][issues]

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

Install from PyPI
-----------------

PyMD4C is available on PyPI under the name [`pymd4c`][PyPI]. Install it with
pip like this:

    pip install pymd4c

This is the recommended method to obtain PyMD4C. It should work well on most
Linux distributions. It will probably work well on Windows and macOS (but
these platforms are not as well-tested).

If this does not work, there are a couple potential reasons:

1. You do not have pip installed, or your version is too old. See [Installing
   Packages - Python Packaging User Guide][python-packaging].

2. Your version of Python is too old. This is a platform wheel, so it is built
   for each Python version separately. Python versions older than 3.6 are not
   supported. If your Python version is older than that, try upgrading.

3. Your platform is incompatible. Again, since it is a platform wheel, it is
   built for each supported platform separately.
   - If you are running Windows, you may be running 32-bit (x86) Python.
     Currently, only packages for 64-bit (x86-64) Python are built. If you can,
     try running 64-bit Python.
   - If you are on macOS, your macOS version might be too old.
   - If you are on Linux, you may be running on an architecture other than
     x86-64, a distribution that is too old, or a more esoteric distribution
     unsupported by [manylinux2014][manylinux]. (Note that many architectures
     supported by manylinux2014 are not built at this time, including x86,
     arm64, ppc64le, and s390x.)
   - If you are on some other platform, unfortunately, it is not supported by
     the pre-built packages.

If a build is not available for your platform (or you simply want to), you can
build and install from source. The instructions below should assist.

If a build is not available or not working for your platform and you think it
should be, consider opening a [GitHub issue][issues].

Build and Install from Source
-----------------------------

### Prerequisites

This package depends on the MD4C library. It may be available through your
package manager. Otherwise, it can be built from source as follows:

1. Make sure you have [CMake] and a C compiler installed.
2. Download and extract the matching release from the [MD4C releases
   page][md4c-releases] (e.g. for PyMD4C version W.X.Y.Z, download MD4C version
   W.X.Y).
3. On Unix-like systems (including macOS):
   - Inside the extracted file, run the following:

         mkdir build
         cd build
         cmake ..
         make
         # Do as root:
         make install

     The install step must be run as root. The library will install to
     /usr/local by default.
   - You may need to rebuild the ldconfig cache (also as root): `ldconfig`
4. On Windows:
   - Inside the extracted file, run the following:

         mkdir build
         cd build
         cmake -DCMAKE_BUILD_TYPE=Release ..
         cmake --build . --config Release
         cmake --install .

In addition, on Unix-like systems (including macOS), the `pkg-config` tool must
be available to build PyMD4C. After PyMD4C is built, it is no longer required
(that is, it is not a prerequisite for actually *using* PyMD4C). This tool is
likely available on your system already, so this should not be an issue in most
cases.

Finally, note that since this package uses C extensions, development headers
for Python must be installed for the build to succeed. If you are using Linux,
some distributions split these off from the main Python package. Install
`python-dev` or `python-devel` to get them.

### Build/Install

Build and install as you would for any Python source repository. Download and
extract a release or clone the repository, and run the following inside:

    pip install .

Alternatively, you can have pip fetch and build from the latest source
distribution on PyPI:

    pip install --no-binary pymd4c pymd4c

Note that on Windows, setup.py assumes the MD4C library was installed at
"C:/Program Files (x86)/MD4C/" (this is the default location when building MD4C
from source, as described above). If this is not the case, installation will
fail.

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
  tuples.

  See the `MD_BLOCK_*_DETAIL` and `MD_SPAN_*_DETAIL` structs in MD4C's `md4c.h`
  for information on exactly what this `dict` will contain.

  Regarding `MD_ATTRIBUTE`s: These are used where a block or span can contain
  some associated text, such as link titles and code block language references.
  Such attributes may contain multiple text sub-elements (e.g. some regular
  text, an HTML entity, and then some more regular text). Thus, an
  `MD_ATTRIBUTE` value in `details` consists of a list of 2-tuples:
  `(text_type, text)` where `text_type` is an `md4c.TextType` (see "Enums"
  below) and `text` is the actual text as a `str`.

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
html_renderer.parse(input)
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
named constants. These are made available as module-level constants in PyMD4C.

### Parser Option Flags

Basic option flags:

* `md4c.MD_FLAG_COLLAPSEWHITESPACE` - In normal text, collapse non-trivial
  whitespace into a single space.
* `md4c.MD_FLAG_PERMISSIVEATXHEADERS` - Do not requite a space in ATX headers
  (e.g. `###Header`).
* `md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS` - Convert URLs to links even without
  `<` and `>`.
* `md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS` - Convert email addresses to links
  even without `<`, `>`, and `mailto:`.
* `md4c.MD_FLAG_NOINDENTEDCODEBLOCKS` - Disable indented code blocks. (Only
  allow fenced code blocks.)
* `md4c.MD_FLAG_NOHTMLBLOCKS` - Disable raw HTML blocks.
* `md4c.MD_FLAG_NOHTMLSPANS` - Disable raw HTML inlines.
* `md4c.MD_FLAG_TABLES` - Enable tables extension.
* `md4c.MD_FLAG_STRIKETHROUGH` - Enable strikethrough extension.
* `md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS` - Enable www autolinks (even without
  any scheme prefix, as long as they begin with `www.`).
* `md4c.MD_FLAG_TASKLISTS` - Enable task lists extension.
* `md4c.MD_FLAG_LATEXMATHSPANS` - Enable `$` and `$$` containing LaTeX
  equations.
* `md4c.MD_FLAG_WIKILINKS` - Enable wiki links extension.
* `md4c.MD_FLAG_UNDERLINE` - Enable underline extension (and disable `_` for
  regular emphasis).

Combination option flags:

* `md4c.MD_FLAG_PERMISSIVEAUTOLINKS` - Enables all varieties of autolinks:
  `MD_FLAG_PERMISSIVEURLAUTOLINKS`, `MD_FLAG_PERMISSIVEEMAILAUTOLINKS`, and
  `MD_FLAG_PERMISSIVEWWWAUTOLINKS`
* `md4c.MD_FLAG_NOHTML` - Disables all raw HTML tags: `MD_FLAG_NOHTMLBLOCKS`
  and `MD_FLAG_NOHTMLSPANS`

Dialect option flags (note that not all features of a dialect may be supported,
but these flags will cause MD4C to parse as many features of the dialect as it
supports):

* `md4c.MD_DIALECT_COMMONMARK` - This is the default behavior of MD4C, so no
  additional flags are enabled.
* `md4c.MD_DIALECT_GITHUB` - Parse GitHub-Flavored Markdown, which enables the
  following flags:

  - `MD_FLAG_PERMISSIVEAUTOLINKS`
  - `MD_FLAG_TABLES`
  - `MD_FLAG_STRIKETHROUGH`
  - `MD_FLAG_TASKLISTS`

### HTML Renderer Option Flags

* `md4c.MD_HTML_FLAG_DEBUG` - For development use, send MD4C debug output to
  stderr.
* `md4c.MD_HTML_FLAG_VERBATIM_ENTITIES` - Do not replace HTML entities with the
  actual character (e.g. `&copy;` with ©).
* `md4c.MD_HTML_FLAG_SKIP_UTF8_BOM` - Omit BOM from start of UTF-8 input.
* `md4c.MD_HTML_FLAG_XHTML` - Generate XHTML instead of HTML.

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
