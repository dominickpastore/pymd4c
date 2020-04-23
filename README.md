PyMD4C
======

Python bindings for the very fast [MD4C](https://github.com/mity/md4c) Markdown
parsing and rendering library.

The MD4C C library provides a generic parser that uses callbacks to return the
various blocks, inlines, and text it parses from the Markdown input. In
addition, it provides an HTML renderer that wraps the generic parser to provide
HTML output directly.

Accordingly, this Python module provides two classes:

* `md4c.GenericParser` - Wraps the generic MD4C parser. Requires Python
  functions (or other callables) as callbacks.
* `md4c.HTMLRenderer` - Wraps the HTML renderer. Produces HTML output directly.

If other renderers are added to MD4C, they will get their own Python class as
well, similar to the `HTMLRenderer`.

Build and Install
-----------------

Build and install with `setup.py` as you would for any Python source
repository.

API
---

### `GenericParser`

`md4c.GenericParser(parser_flags)`

Initialize a new `GenericParser`. Parameters:

* `parser_flags` - An `int` made up of some combination of the parser option
  flags or'd together, e.g.
  `md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH`. For the default options,
  use `0`, which will parse according to the base CommonMark standard. See the
  "Module-Wide Constants" section below for a full list of parser option flags.

**Note:** If the end goal of parsing is to produce HTML, strongly consider
using an `HTMLRenderer` instead. All rendering will be performed by native C
code, thus will be much faster.

#### Parse Method

`parse(input, enter_block_callback, leave_block_callback, enter_span_callback,leave_span_callback, text_callback)`

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

`enter_block_callback`, `leave_block_callback`, `enter_span_callback`, and
`leave_span_callback` all must accept two parameters:

* `type` - An `int` representing the type of block or span. Will be one of the
  block type constants or span type constants (listed in "Module-Wide
  Constants" below).
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
  `(text_type, text)` where `text_type` is one of the text type constants (see
  "Module-Wide Constants" below) and `text` is the actual text as a `str`.

`text_callback` must also accept two parameters, but they are different:

* `type` - An `int` representing the type of text element (listed in
  "Module-Wide Constants" below).
* `text` - The actual text, as a `str`.

Callbacks need not return anything specific; their return values are ignored.
To cancel parsing, callbacks can raise `md4c.StopParsing`. This will be caught
by the `parse()` method and immediately halt parsing quietly. All other
exceptions raised by callbacks will abort parsing and will be propagated back
to the caller of `parse()`.

The `parse()` method can raise `md4c.ParseError` in the event of a problem
during parsing, such as running out of memory. This does not signal invalid
syntax, as there is no such thing in Markdown. It can also emit any exception
raised by any of the callbacks (except `md4c.StopParsing`, which is caught and
handled quietly).

### `HTMLRenderer`

`md4c.HTMLRenderer(parser_flags, renderer_flags)`

Initialize a new `HTMLRenderer`. Parameters:

* `parser_flags` - An `int` made up of some combination of the parser option
  flags or'd together, e.g.
  `md4c.MD_FLAG_TABLES | md4c.MD_FLAG_STRIKETHROUGH`. For the default options,
  use `0`, which will parse according to the base CommonMark standard. See the
  "Module-Wide Constants" section below for a full list of parser option flags.
* `renderer_flags` - An `int` made up of some combination of the HTML renderer
  option flags or'd together. These are also listed in the "Module-Wide
  Constants" section below.

#### Parse Method

`parse(input)`

Parse markdown text and return a `str` with rendered HTML. Parameters:

* `input` - A `str` or `bytes` containing the Markdown document to parse. If a
  `bytes`, it must be UTF-8 encoded.

Can raise `md4c.ParseError` in the event of a problem during parsing, such as
running out of memory. This does not signal invalid syntax, as there is no such
thing in Markdown.

### Module-Wide Constants

Various flags and enum constants from the MD4C library and renderers are
provided as module-wide constants.

See the MD4C documentation or code (`md4c.h`, `md4c-html.h`) for more
information on what these flags and constants mean.

#### Parser Option Flags

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
but these flags will cause MD4C to parse as many features of the dialect it
supports):

* `md4c.MD_DIALECT_COMMONMARK` - This is the default behavior of MD4C, so no
  additional flags are enabled.
* `md4c.MD_DIALECT_GITHUB` - Parse GitHub-Flavored Markdown, which enables the
  following flags:
  - `MD_FLAG_PERMISSIVEAUTOLINKS`
  - `MD_FLAG_TABLES`
  - `MD_FLAG_STRIKETHROUGH`
  - `MD_FLAG_TASKLISTS`

#### HTML Renderer Option Flags

* `md4c.MD_HTML_FLAG_DEBUG` - For development use, send MD4C debug output to
  stderr.
* `md4c.MD_HTML_FLAG_VERBATIM_ENTITIES` - Do not replace HTML entities with the
  actual character (e.g. `&copy;` with ©).
* `md4c.MD_HTML_FLAG_SKIP_UTF8_BOM` - Omit BOM from start of UTF-8 input.

#### Block Type Constants

* `md4c.MD_BLOCK_DOC` - Document
* `md4c.MD_BLOCK_QUOTE` - Block quote
* `md4c.MD_BLOCK_UL` - Unordered list
* `md4c.MD_BLOCK_OL` - Ordered list
* `md4c.MD_BLOCK_LI` - List item
* `md4c.MD_BLOCK_HR` - Horizontal rule
* `md4c.MD_BLOCK_H` - Heading
* `md4c.MD_BLOCK_CODE` - Code block
* `md4c.MD_BLOCK_HTML` - Raw HTML block
* `md4c.MD_BLOCK_P` - Paragraph
* `md4c.MD_BLOCK_TABLE` - Table
* `md4c.MD_BLOCK_THEAD` - Table header row
* `md4c.MD_BLOCK_TBODY` - Table body
* `md4c.MD_BLOCK_TR` - Table row
* `md4c.MD_BLOCK_TH` - Table header cell
* `md4c.MD_BLOCK_TD` - Table cell

#### Span Type Constants

* `md4c.MD_SPAN_EM` - Emphasis
* `md4c.MD_SPAN_STRONG` - Strong
* `md4c.MD_SPAN_A` - Link
* `md4c.MD_SPAN_IMG` - Image
* `md4c.MD_SPAN_CODE` - Inline code
* `md4c.MD_SPAN_DEL` - Strikethrough
* `md4c.MD_SPAN_LATEXMATH` - Inline math
* `md4c.MD_SPAN_LATEXMATH_DISPLAY` - Display math
* `md4c.MD_SPAN_WIKILINK` - Wiki link
* `md4c.MD_SPAN_U` - Underline

#### Text Type Constants

* `md4c.MD_TEXT_NORMAL` - Normal text
* `md4c.MD_TEXT_NULLCHAR` - NULL character
* `md4c.MD_TEXT_BR` - Line break
* `md4c.MD_TEXT_SOFTBR` - Soft line break
* `md4c.MD_TEXT_ENTITY` - HTML Entity
* `md4c.MD_TEXT_CODE` - Text inside a code block or inline code
* `md4c.MD_TEXT_HTML` - Raw HTML (inside an HTML block or simply inline HTML)
* `md4c.MD_TEXT_LATEXMATH` - Text inside an equation

#### Table Alignment Constants

* `md4c.MD_ALIGN_DEFAULT`
* `md4c.MD_ALIGN_LEFT`
* `md4c.MD_ALIGN_CENTER`
* `md4c.MD_ALIGN_RIGHT`

### Exceptions

* `md4c.ParseError` - Raised by one of the `parse()` methods when there is an
  error during parsing, such as running out of memory. *There is no such thing
  as invalid syntax in Markdown,* so this really only signals some sort of
  system error.

* `md4c.StopParsing` - A callback can raise this to stop parsing early.
  `GenericParser`'s `parse()` method will catch it and abort quietly.
